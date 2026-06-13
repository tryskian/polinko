from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from contextlib import closing
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_evidence import build_ocr_retry_evidence_rows
from tools.manual_eval_open_feedback import (
    build_filtered_open_feedback_actionable_rows,
    normalize_cohort_filter,
    normalize_outcome_filter,
)
from tools.manual_eval_ocr_retry_selection_formatters import (
    display_text as _display_text,
    format_feedback_ids as _format_feedback_ids,
    format_readiness_flags as _format_readiness_flags,
    int_value as _int_value,
    truncate_text as _truncate_text,
)


OCR_RETRY_CANDIDATES_SCHEMA_VERSION = "polinko.manual_eval_ocr_retry_candidates.v2"
OCR_RETRY_TERMINAL_CONTEXT_LIMIT = 3


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _packet_feedback_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedback_id": _int_value(row.get("feedback_id")),
        "message_id": str(row.get("message_id") or ""),
        "outcome": str(row.get("outcome") or ""),
        "status": str(row.get("status") or ""),
        "tags": row.get("tags") if isinstance(row.get("tags"), list) else [],
        "note": str(row.get("note") or ""),
        "recommended_action": str(row.get("recommended_action") or ""),
        "action_taken": str(row.get("action_taken") or ""),
        "updated_at": _int_value(row.get("updated_at")),
        "ocr_context": row.get("ocr_context")
        if isinstance(row.get("ocr_context"), dict)
        else {},
    }


def _latest_run_for_row(
    row: dict[str, Any],
    evidence_rows: Sequence[dict[str, Any]],
) -> dict[str, Any] | None:
    ocr_context = row.get("ocr_context")
    if not isinstance(ocr_context, dict):
        ocr_context = {}
    latest = ocr_context.get("latest_same_session_ocr")
    if not isinstance(latest, dict):
        latest = {}
    latest_run_id = str(latest.get("run_id") or "")
    for evidence_row in evidence_rows:
        if evidence_row.get("run_id") == latest_run_id:
            return evidence_row
    return evidence_rows[0] if evidence_rows else None


def _feedback_has_ocr_result_link(row: dict[str, Any]) -> bool:
    ocr_context = row.get("ocr_context")
    if not isinstance(ocr_context, dict):
        return False
    return bool(ocr_context.get("linked_to_ocr_result"))


def _linked_ocr_run_ids(
    feedback_rows: Sequence[dict[str, Any]],
    evidence_rows: Sequence[dict[str, Any]],
) -> list[str]:
    feedback_message_ids = {
        str(row.get("message_id") or "")
        for row in feedback_rows
        if row.get("message_id")
    }
    if not feedback_message_ids:
        return []
    linked_run_ids: list[str] = []
    for evidence_row in evidence_rows:
        result_message_id = str(evidence_row.get("result_message_id") or "")
        run_id = str(evidence_row.get("run_id") or "")
        if result_message_id in feedback_message_ids and run_id:
            linked_run_ids.append(run_id)
    return linked_run_ids


def _build_readiness(
    *,
    feedback_rows: Sequence[dict[str, Any]],
    evidence_rows: Sequence[dict[str, Any]],
    latest_run: dict[str, Any],
) -> dict[str, Any]:
    linked_feedback_rows = sum(
        1 for row in feedback_rows if _feedback_has_ocr_result_link(row)
    )
    unlinked_feedback_rows = max(0, len(feedback_rows) - linked_feedback_rows)
    linked_run_ids = _linked_ocr_run_ids(feedback_rows, evidence_rows)
    latest_run_id = str(latest_run.get("run_id") or "")
    latest_run_is_linked = bool(latest_run_id and latest_run_id in linked_run_ids)
    same_session_ocr_runs = len(evidence_rows)

    flags: list[str] = []
    if same_session_ocr_runs <= 0:
        flags.append("no_same_session_ocr_context")
    elif same_session_ocr_runs > 1:
        flags.append("multiple_same_session_ocr_runs")
    if unlinked_feedback_rows > 0:
        flags.append("missing_feedback_to_result_link")
    if latest_run_id and not latest_run_is_linked:
        flags.append("latest_ocr_is_context_only")
    if not latest_run_id:
        flags.append("no_latest_same_session_ocr")

    return {
        "state": "needs_review" if flags else "ready",
        "flags": flags,
        "basis": "explicit_result_message_match_and_same_session_context",
        "explicit_feedback_to_result_links": linked_feedback_rows,
        "unlinked_feedback_rows": unlinked_feedback_rows,
        "same_session_ocr_runs": same_session_ocr_runs,
        "linked_ocr_run_ids": linked_run_ids,
        "latest_ocr_is_confirmed_feedback_result": latest_run_is_linked,
    }


def _build_candidate_groups(
    actionables: Sequence[dict[str, Any]],
    evidence_by_session: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for row in actionables:
        session_id = str(row.get("session_id") or "")
        evidence_rows = evidence_by_session.get(session_id, [])
        latest_run = _latest_run_for_row(row, evidence_rows)
        latest_run_id = str(latest_run.get("run_id") if latest_run else "")
        group_key = (session_id, latest_run_id)
        group = groups.setdefault(
            group_key,
            {
                "group_id": f"{session_id}::{latest_run_id or 'no-ocr-run'}",
                "source_label": str(row.get("source_label") or ""),
                "source_history_db": str(row.get("source_history_db") or ""),
                "source_session_id": str(row.get("source_session_id") or ""),
                "session_id": session_id,
                "title": str(row.get("title") or ""),
                "latest_same_session_ocr": latest_run or {},
                "same_session_ocr_runs": len(evidence_rows),
                "feedback_ids": [],
                "feedback_rows": [],
                "ocr_runs": evidence_rows,
            },
        )
        feedback_id = _int_value(row.get("feedback_id"))
        group["feedback_ids"].append(feedback_id)
        group["feedback_rows"].append(_packet_feedback_row(row))

    for group in groups.values():
        feedback_rows = group.get("feedback_rows")
        if not isinstance(feedback_rows, list):
            feedback_rows = []
        group_ocr_runs = group.get("ocr_runs")
        if not isinstance(group_ocr_runs, list):
            group_ocr_runs = []
        latest_run = group.get("latest_same_session_ocr")
        if not isinstance(latest_run, dict):
            latest_run = {}
        group["readiness"] = _build_readiness(
            feedback_rows=feedback_rows,
            evidence_rows=group_ocr_runs,
            latest_run=latest_run,
        )

    def sort_key(item: dict[str, Any]) -> tuple[int, str]:
        feedback_rows = item.get("feedback_rows")
        feedback_count = len(feedback_rows) if isinstance(feedback_rows, list) else 0
        return (-feedback_count, str(item.get("session_id") or ""))

    return sorted(groups.values(), key=sort_key)


def build_ocr_retry_candidates_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    outcome_filter = normalize_outcome_filter(outcome)
    cohort_filter = normalize_cohort_filter(cohort)
    if cohort_filter is None:
        cohort_filter = "ocr_retry_evidence"
    row_limit = max(1, limit)
    if not db_path.is_file():
        return {
            "schema_version": OCR_RETRY_CANDIDATES_SCHEMA_VERSION,
            "state": "error",
            "manual_evals_db": {"path": str(db_path), "exists": False},
            "filters": {
                "status": "open",
                "outcome": outcome_filter or "",
                "cohort": cohort_filter,
                "limit": row_limit,
                "packet_basis": "recommended_action_and_same_session_ocr",
            },
            "candidate_groups": [],
            "warnings": ["manual_evals.db is not available"],
        }

    with closing(_connect_readonly(db_path)) as conn:
        integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        all_rows = build_filtered_open_feedback_actionable_rows(
            conn,
            outcome=outcome_filter,
            cohort=cohort_filter,
        )
        rows = all_rows[:row_limit]
        evidence_by_session = build_ocr_retry_evidence_rows(
            conn,
            session_ids=[str(row.get("session_id") or "") for row in rows],
        )
        candidate_groups = _build_candidate_groups(rows, evidence_by_session)
        needs_review_groups = sum(
            1
            for group in candidate_groups
            if isinstance(group.get("readiness"), dict)
            and group["readiness"].get("state") == "needs_review"
        )

    return {
        "schema_version": OCR_RETRY_CANDIDATES_SCHEMA_VERSION,
        "state": "ok" if integrity == "ok" else "error",
        "manual_evals_db": {
            "path": str(db_path),
            "exists": True,
            "integrity": integrity,
        },
        "filters": {
            "status": "open",
            "outcome": outcome_filter or "",
            "cohort": cohort_filter,
            "limit": row_limit,
            "packet_basis": "recommended_action_and_same_session_ocr",
        },
        "counts": {
            "total_feedback_rows": len(all_rows),
            "returned_feedback_rows": len(rows),
            "candidate_groups": len(candidate_groups),
            "ready_candidate_groups": len(candidate_groups) - needs_review_groups,
            "needs_review_candidate_groups": needs_review_groups,
            "limit_applied": len(rows) < len(all_rows),
        },
        "candidate_groups": candidate_groups,
    }


def _format_latest_ocr_line(latest_ocr: dict[str, Any]) -> str:
    image_asset = latest_ocr.get("image_asset")
    if not isinstance(image_asset, dict):
        image_asset = {}
    thumbnail = image_asset.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    thumbnail_text = "none"
    if thumbnail.get("available"):
        thumbnail_text = (
            f"{_int_value(thumbnail.get('width'))}x"
            f"{_int_value(thumbnail.get('height'))}"
        )
    return (
        f"latest_run={latest_ocr.get('run_id') or 'none'} "
        f"latest_source={latest_ocr.get('source_name') or 'none'} "
        f"latest_status={latest_ocr.get('status') or 'none'} "
        f"image_status={image_asset.get('status') or 'unknown'} "
        f"resolved={'yes' if image_asset.get('resolved_path') else 'no'} "
        f"thumbnail={thumbnail_text} "
        f"chars={_int_value(latest_ocr.get('extracted_text_chars'))}"
    )


def _format_ocr_context_line(ocr_run: dict[str, Any]) -> str:
    image_asset = ocr_run.get("image_asset")
    if not isinstance(image_asset, dict):
        image_asset = {}
    thumbnail = image_asset.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    thumbnail_text = "none"
    if thumbnail.get("available"):
        thumbnail_text = (
            f"{_int_value(thumbnail.get('width'))}x"
            f"{_int_value(thumbnail.get('height'))}"
        )
    preview = _truncate_text(ocr_run.get("extracted_text_preview"), max_chars=80)
    return (
        f"ocr={ocr_run.get('run_id') or 'none'} "
        f"source={ocr_run.get('source_name') or 'none'} "
        f"status={ocr_run.get('status') or 'none'} "
        f"image_status={image_asset.get('status') or 'unknown'} "
        f"resolved={'yes' if image_asset.get('resolved_path') else 'no'} "
        f"thumbnail={thumbnail_text} "
        f"preview={preview or 'none'}"
    )


def format_ocr_retry_candidates_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry candidates: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"groups={_int_value(counts.get('candidate_groups'))} "
        f"needs_review={_int_value(counts.get('needs_review_candidate_groups'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    candidate_groups = report.get("candidate_groups")
    if not isinstance(candidate_groups, list) or not candidate_groups:
        lines.append("candidate_groups: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for group in candidate_groups:
        if not isinstance(group, dict):
            continue
        latest_ocr = group.get("latest_same_session_ocr")
        if not isinstance(latest_ocr, dict):
            latest_ocr = {}
        readiness = group.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        ocr_runs = group.get("ocr_runs")
        if not isinstance(ocr_runs, list):
            ocr_runs = []
        lines.extend(
            [
                "- "
                f"session={group.get('session_id') or 'unknown'} "
                f"source_session={group.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(group.get('feedback_ids'))} "
                f"ocr_runs={_int_value(group.get('same_session_ocr_runs'))}",
                f"  title={_display_text(group.get('title'))}",
                f"  {_format_latest_ocr_line(latest_ocr)}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)} "
                "explicit_links="
                f"{_int_value(readiness.get('explicit_feedback_to_result_links'))} "
                "unlinked_feedback="
                f"{_int_value(readiness.get('unlinked_feedback_rows'))} "
                "latest_confirmed="
                f"{'yes' if readiness.get('latest_ocr_is_confirmed_feedback_result') else 'no'}",
            ]
        )
        if readiness.get("state") == "needs_review" and ocr_runs:
            context_rows = [
                item
                for item in ocr_runs[:OCR_RETRY_TERMINAL_CONTEXT_LIMIT]
                if isinstance(item, dict)
            ]
            if context_rows:
                lines.append("  same_session_ocr_context:")
                for ocr_run in context_rows:
                    lines.append(f"  - {_format_ocr_context_line(ocr_run)}")
                hidden_rows = len(ocr_runs) - len(context_rows)
                if hidden_rows > 0:
                    lines.append(f"  same_session_ocr_context_more={hidden_rows}")
        feedback_rows = group.get("feedback_rows")
        if not isinstance(feedback_rows, list):
            feedback_rows = []
        for row in feedback_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "  - "
                f"feedback={_int_value(row.get('feedback_id'))} "
                f"message={row.get('message_id') or 'unknown'} "
                f"outcome={row.get('outcome') or 'unknown'} "
                f"note={_display_text(row.get('note'))}"
            )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)
