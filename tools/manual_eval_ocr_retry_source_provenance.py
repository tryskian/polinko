from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from contextlib import closing
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_candidates import OCR_RETRY_TERMINAL_CONTEXT_LIMIT
from tools.manual_eval_ocr_retry_selection_formatters import (
    display_text as _display_text,
    format_feedback_ids as _format_feedback_ids,
    int_value as _int_value,
    normalize_text as _normalize_text,
    truncate_text as _truncate_text,
)
from tools.manual_eval_ocr_retry_source_verification import (
    build_ocr_retry_source_verification_report,
)


OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_source_provenance.v1"
)


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _row_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def _fetch_rows(
    conn: sqlite3.Connection,
    sql: str,
    params: Sequence[object] | None = None,
) -> list[dict[str, Any]]:
    return [_row_dict(row) for row in conn.execute(sql, params or []).fetchall()]


def _read_source_history_messages(
    *,
    source_history_db: str,
    source_session_id: str,
    message_ids: Sequence[str],
) -> dict[str, Any]:
    clean_message_ids = [
        item
        for item in dict.fromkeys(str(value or "") for value in message_ids)
        if item
    ]
    source_path = Path(source_history_db).expanduser()
    result: dict[str, Any] = {
        "path": str(source_path),
        "exists": source_path.is_file(),
        "state": "ok" if source_path.is_file() else "missing",
        "source_session_id": source_session_id,
        "requested_message_ids": clean_message_ids,
        "messages": {},
    }
    if not source_path.is_file() or not clean_message_ids:
        return result

    placeholders = ",".join("?" for _ in clean_message_ids)
    try:
        with closing(_connect_readonly(source_path)) as conn:
            rows = _fetch_rows(
                conn,
                f"""
                SELECT
                  message_id,
                  role,
                  content,
                  created_at
                FROM chat_messages
                WHERE session_id = ?
                  AND message_id IN ({placeholders})
                ORDER BY id ASC
                """,
                [source_session_id, *clean_message_ids],
            )
    except sqlite3.Error as exc:
        result["state"] = "error"
        result["error"] = str(exc)
        return result

    messages: dict[str, dict[str, Any]] = {}
    for row in rows:
        message_id = str(row.get("message_id") or "")
        content = _normalize_text(row.get("content"))
        messages[message_id] = {
            "message_id": message_id,
            "present": True,
            "state": "found",
            "role": str(row.get("role") or ""),
            "created_at": _int_value(row.get("created_at")),
            "content_chars": len(content),
            "content_preview": _truncate_text(content),
        }
    result["messages"] = messages
    return result


def source_message_reference(
    *,
    message_id: str,
    message_lookup: dict[str, Any],
) -> dict[str, Any]:
    clean_message_id = str(message_id or "")
    if not clean_message_id:
        return {
            "message_id": "",
            "present": False,
            "state": "empty",
            "role": "",
            "created_at": 0,
            "content_chars": 0,
            "content_preview": "",
        }
    messages = message_lookup.get("messages")
    if not isinstance(messages, dict):
        messages = {}
    row = messages.get(clean_message_id)
    if not isinstance(row, dict):
        return {
            "message_id": clean_message_id,
            "present": False,
            "state": "missing",
            "role": "",
            "created_at": 0,
            "content_chars": 0,
            "content_preview": "",
        }
    return {
        "message_id": clean_message_id,
        "present": bool(row.get("present")),
        "state": str(row.get("state") or "found"),
        "role": str(row.get("role") or ""),
        "created_at": _int_value(row.get("created_at")),
        "content_chars": _int_value(row.get("content_chars")),
        "content_preview": str(row.get("content_preview") or ""),
    }


def build_ocr_retry_source_provenance_items(
    verification_items: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    provenance_items: list[dict[str, Any]] = []
    for item in verification_items:
        feedback_rows = item.get("feedback_rows")
        if not isinstance(feedback_rows, list):
            feedback_rows = []
        source_candidates = item.get("source_candidates")
        if not isinstance(source_candidates, list):
            source_candidates = []

        feedback_message_ids = {
            str(row.get("message_id") or "")
            for row in feedback_rows
            if isinstance(row, dict) and row.get("message_id")
        }
        ocr_message_ids: list[str] = []
        for candidate in source_candidates:
            if not isinstance(candidate, dict):
                continue
            for key in ("source_message_id", "result_message_id"):
                message_id = str(candidate.get(key) or "")
                if message_id:
                    ocr_message_ids.append(message_id)

        source_history = _read_source_history_messages(
            source_history_db=str(item.get("source_history_db") or ""),
            source_session_id=str(item.get("source_session_id") or ""),
            message_ids=[*sorted(feedback_message_ids), *ocr_message_ids],
        )

        feedback_message_rows: list[dict[str, Any]] = []
        for row in feedback_rows:
            if not isinstance(row, dict):
                continue
            message_id = str(row.get("message_id") or "")
            feedback_message_rows.append(
                {
                    "feedback_id": _int_value(row.get("feedback_id")),
                    "message_id": message_id,
                    "outcome": str(row.get("outcome") or ""),
                    "source_message": source_message_reference(
                        message_id=message_id,
                        message_lookup=source_history,
                    ),
                }
            )

        candidate_rows: list[dict[str, Any]] = []
        exact_feedback_result_links = 0
        for candidate in source_candidates:
            if not isinstance(candidate, dict):
                continue
            result_message_id = str(candidate.get("result_message_id") or "")
            exact_link = bool(
                result_message_id and result_message_id in feedback_message_ids
            )
            if exact_link:
                exact_feedback_result_links += 1
            candidate_rows.append(
                {
                    "run_id": str(candidate.get("run_id") or ""),
                    "source_image_name": str(candidate.get("source_image_name") or ""),
                    "source_name": str(candidate.get("source_name") or ""),
                    "source_message_id": str(candidate.get("source_message_id") or ""),
                    "result_message_id": result_message_id,
                    "status": str(candidate.get("status") or ""),
                    "exact_feedback_result_link": exact_link,
                    "source_message": source_message_reference(
                        message_id=str(candidate.get("source_message_id") or ""),
                        message_lookup=source_history,
                    ),
                    "result_message": source_message_reference(
                        message_id=result_message_id,
                        message_lookup=source_history,
                    ),
                }
            )

        feedback_messages_found = sum(
            1 for row in feedback_message_rows if row["source_message"].get("present")
        )
        source_message_ids_present = sum(
            1 for row in candidate_rows if row.get("source_message_id")
        )
        result_message_ids_present = sum(
            1 for row in candidate_rows if row.get("result_message_id")
        )
        source_messages_found = sum(
            1 for row in candidate_rows if row["source_message"].get("present")
        )
        result_messages_found = sum(
            1 for row in candidate_rows if row["result_message"].get("present")
        )

        provenance_items.append(
            {
                "group_id": str(item.get("group_id") or ""),
                "source_label": str(item.get("source_label") or ""),
                "source_history": {
                    "path": str(source_history.get("path") or ""),
                    "exists": bool(source_history.get("exists")),
                    "state": str(source_history.get("state") or "unknown"),
                    "source_session_id": str(
                        source_history.get("source_session_id") or ""
                    ),
                    "requested_message_ids": source_history.get("requested_message_ids")
                    if isinstance(source_history.get("requested_message_ids"), list)
                    else [],
                    "error": str(source_history.get("error") or ""),
                },
                "source_session_id": str(item.get("source_session_id") or ""),
                "session_id": str(item.get("session_id") or ""),
                "title": str(item.get("title") or ""),
                "feedback_ids": item.get("feedback_ids")
                if isinstance(item.get("feedback_ids"), list)
                else [],
                "readiness": item.get("readiness")
                if isinstance(item.get("readiness"), dict)
                else {},
                "confirmation": item.get("confirmation")
                if isinstance(item.get("confirmation"), dict)
                else {},
                "feedback_messages": feedback_message_rows,
                "ocr_message_provenance": candidate_rows,
                "counts": {
                    "feedback_messages": len(feedback_message_rows),
                    "feedback_messages_found": feedback_messages_found,
                    "ocr_runs": len(candidate_rows),
                    "ocr_source_message_ids_present": source_message_ids_present,
                    "ocr_result_message_ids_present": result_message_ids_present,
                    "ocr_source_messages_found": source_messages_found,
                    "ocr_result_messages_found": result_messages_found,
                    "exact_feedback_result_links": exact_feedback_result_links,
                },
            }
        )
    return provenance_items


def build_ocr_retry_source_provenance_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    verification_report = build_ocr_retry_source_verification_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    verification_items = verification_report.get("verification_items")
    if not isinstance(verification_items, list):
        verification_items = []
    provenance_items = build_ocr_retry_source_provenance_items(
        [item for item in verification_items if isinstance(item, dict)]
    )
    verification_counts = verification_report.get("counts")
    if not isinstance(verification_counts, dict):
        verification_counts = {}
    verification_filters = verification_report.get("filters")
    if not isinstance(verification_filters, dict):
        verification_filters = {}
    item_counts = [
        item.get("counts") for item in provenance_items if isinstance(item, dict)
    ]
    source_history_available = sum(
        1
        for item in provenance_items
        if isinstance(item.get("source_history"), dict)
        and item["source_history"].get("state") == "ok"
    )

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION,
        "verification_schema_version": verification_report.get("schema_version", ""),
        "state": verification_report.get("state", "unknown"),
        "manual_evals_db": verification_report.get("manual_evals_db", {}),
        "filters": {
            "status": verification_filters.get("status") or "open",
            "outcome": verification_filters.get("outcome") or "",
            "cohort": verification_filters.get("cohort") or "",
            "limit": _int_value(verification_filters.get("limit")),
            "packet_basis": "source_history_message_provenance",
        },
        "counts": {
            "total_feedback_rows": _int_value(
                verification_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                verification_counts.get("returned_feedback_rows")
            ),
            "provenance_items": len(provenance_items),
            "source_history_available": source_history_available,
            "feedback_messages": sum(
                _int_value(counts.get("feedback_messages"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "feedback_messages_found": sum(
                _int_value(counts.get("feedback_messages_found"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_runs": sum(
                _int_value(counts.get("ocr_runs"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_source_message_ids_present": sum(
                _int_value(counts.get("ocr_source_message_ids_present"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_result_message_ids_present": sum(
                _int_value(counts.get("ocr_result_message_ids_present"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "exact_feedback_result_links": sum(
                _int_value(counts.get("exact_feedback_result_links"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "limit_applied": bool(verification_counts.get("limit_applied")),
        },
        "provenance_items": provenance_items,
    }
    warnings = verification_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _format_source_message_ref(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    state = str(value.get("state") or "unknown")
    if state == "empty":
        return "none"
    if state != "found":
        return state
    preview = _truncate_text(value.get("content_preview"), max_chars=80)
    return (
        f"found role={value.get('role') or 'unknown'} "
        f"chars={_int_value(value.get('content_chars'))} "
        f"preview={preview or 'none'}"
    )


def _format_ocr_message_provenance_line(item: dict[str, Any]) -> str:
    return (
        f"ocr={item.get('run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"source_message={item.get('source_message_id') or 'none'} "
        f"source_state={_format_source_message_ref(item.get('source_message'))} "
        f"result_message={item.get('result_message_id') or 'none'} "
        f"result_state={_format_source_message_ref(item.get('result_message'))} "
        "exact_feedback_link="
        f"{'yes' if item.get('exact_feedback_result_link') else 'no'}"
    )


def format_ocr_retry_source_provenance_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    lines = [
        "manual eval OCR retry source provenance: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('provenance_items'))} "
        "source_history="
        f"{_int_value(counts.get('source_history_available'))}/"
        f"{_int_value(counts.get('provenance_items'))} "
        "feedback_sources="
        f"{_int_value(counts.get('feedback_messages_found'))}/"
        f"{_int_value(counts.get('feedback_messages'))} "
        f"ocr_runs={_int_value(counts.get('ocr_runs'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    provenance_items = report.get("provenance_items")
    if not isinstance(provenance_items, list) or not provenance_items:
        lines.append("provenance_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in provenance_items:
        if not isinstance(item, dict):
            continue
        source_history = item.get("source_history")
        if not isinstance(source_history, dict):
            source_history = {}
        item_counts = item.get("counts")
        if not isinstance(item_counts, dict):
            item_counts = {}
        lines.extend(
            [
                "- "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                f"source_history={source_history.get('state') or 'unknown'} "
                "feedback_sources="
                f"{_int_value(item_counts.get('feedback_messages_found'))}/"
                f"{_int_value(item_counts.get('feedback_messages'))} "
                f"ocr_runs={_int_value(item_counts.get('ocr_runs'))} "
                "exact_links="
                f"{_int_value(item_counts.get('exact_feedback_result_links'))}",
                f"  title={_display_text(item.get('title'))}",
                f"  source_history_db={source_history.get('path') or 'unknown'}",
            ]
        )
        feedback_messages = item.get("feedback_messages")
        if not isinstance(feedback_messages, list):
            feedback_messages = []
        if feedback_messages:
            lines.append("  feedback_messages:")
        for row in feedback_messages:
            if not isinstance(row, dict):
                continue
            lines.append(
                "  - "
                f"feedback={_int_value(row.get('feedback_id'))} "
                f"message={row.get('message_id') or 'unknown'} "
                f"source_state={_format_source_message_ref(row.get('source_message'))}"
            )
        ocr_rows = item.get("ocr_message_provenance")
        if not isinstance(ocr_rows, list):
            ocr_rows = []
        context_rows = [
            row
            for row in ocr_rows[:OCR_RETRY_TERMINAL_CONTEXT_LIMIT]
            if isinstance(row, dict)
        ]
        if context_rows:
            lines.append("  ocr_message_provenance:")
            for row in context_rows:
                lines.append(f"  - {_format_ocr_message_provenance_line(row)}")
            hidden_rows = len(ocr_rows) - len(context_rows)
            if hidden_rows > 0:
                lines.append(f"  ocr_message_provenance_more={hidden_rows}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)
