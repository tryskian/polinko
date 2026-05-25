from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from tools.manual_eval_open_feedback import (
    build_filtered_open_feedback_actionable_rows,
    normalize_cohort_filter,
    normalize_outcome_filter,
)


FEEDBACK_SOURCE_CONTEXT_SCHEMA_VERSION = (
    "polinko.manual_eval_feedback_source_context.v1"
)


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _int_value(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return 0
        return int(value)
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def _row_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def _display_text(value: object) -> str:
    text = _normalize_text(value)
    return text if text else "none"


def _truncate_text(value: object, *, max_chars: int = 180) -> str:
    text = _normalize_text(value)
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "..."


def _source_history_db_path(source_history_db: object) -> Path:
    path = Path(str(source_history_db or "")).expanduser()
    if path.is_absolute():
        return path
    return Path.cwd() / path


def _mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "read_only",
        "source_history_db": "read_only",
        "feedback_status": "unchanged",
        "ocr_runs": "unchanged",
        "image_assets": "unchanged",
        "eval_rows": "unchanged",
        "pulse": "excluded",
    }


def _blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _fingerprint(source_context: dict[str, Any]) -> str:
    messages = source_context.get("messages")
    if not isinstance(messages, list):
        messages = []
    fingerprint_basis = [
        {
            "position": str(item.get("position") or ""),
            "message_id": str(item.get("message_id") or ""),
            "role": str(item.get("role") or ""),
            "created_at": _int_value(item.get("created_at")),
            "content_chars": _int_value(item.get("content_chars")),
            "content_sha256": str(item.get("content_sha256") or ""),
        }
        for item in messages
        if isinstance(item, dict)
    ]
    encoded = json.dumps(
        fingerprint_basis,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _message_packet(
    row: sqlite3.Row | dict[str, Any],
    *,
    position: str,
) -> dict[str, Any]:
    data = _row_dict(row) if isinstance(row, sqlite3.Row) else row
    content = _normalize_text(data.get("content"))
    return {
        "position": position,
        "message_id": str(data.get("message_id") or ""),
        "role": str(data.get("role") or ""),
        "created_at": _int_value(data.get("created_at")),
        "content_chars": len(content),
        "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "content_preview": _truncate_text(content, max_chars=260),
    }


def _source_feedback_message_context(
    row: dict[str, Any],
    *,
    before_count: int = 3,
    after_count: int = 1,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    source_history_value = str(row.get("source_history_db") or "").strip()
    if not source_history_value:
        return (
            {"state": "missing", "source_history_db": "", "messages": []},
            [
                _blocker(
                    "missing_source_history_db",
                    "feedback row does not name a source history DB.",
                )
            ],
        )
    source_db_path = _source_history_db_path(source_history_value)
    source_db_label = source_db_path.name
    if not source_db_path.is_file():
        return (
            {
                "state": "missing",
                "source_history_db": source_db_label,
                "messages": [],
            },
            [
                _blocker(
                    "source_history_db_not_found",
                    "source history DB was not found.",
                )
            ],
        )
    try:
        with closing(_connect_readonly(source_db_path)) as conn:
            target = conn.execute(
                """
                SELECT id, role, content, created_at, message_id
                FROM chat_messages
                WHERE session_id = ? AND message_id = ?
                LIMIT 1
                """,
                [
                    str(row.get("source_session_id") or ""),
                    str(row.get("message_id") or ""),
                ],
            ).fetchone()
            if target is None:
                return (
                    {
                        "state": "missing",
                        "source_history_db": source_db_label,
                        "messages": [],
                    },
                    [
                        _blocker(
                            "source_history_message_not_found",
                            "source history DB does not contain the feedback message.",
                        )
                    ],
                )
            target_id = _int_value(target["id"])
            target_created_at = _int_value(target["created_at"])
            before_rows = conn.execute(
                """
                SELECT id, role, content, created_at, message_id
                FROM chat_messages
                WHERE session_id = ?
                  AND (
                    created_at < ?
                    OR (created_at = ? AND id < ?)
                  )
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                [
                    str(row.get("source_session_id") or ""),
                    target_created_at,
                    target_created_at,
                    target_id,
                    max(0, before_count),
                ],
            ).fetchall()
            after_rows = conn.execute(
                """
                SELECT id, role, content, created_at, message_id
                FROM chat_messages
                WHERE session_id = ?
                  AND (
                    created_at > ?
                    OR (created_at = ? AND id > ?)
                  )
                ORDER BY created_at ASC, id ASC
                LIMIT ?
                """,
                [
                    str(row.get("source_session_id") or ""),
                    target_created_at,
                    target_created_at,
                    target_id,
                    max(0, after_count),
                ],
            ).fetchall()
    except sqlite3.Error as exc:
        return (
            {
                "state": "error",
                "source_history_db": source_db_label,
                "messages": [],
            },
            [
                _blocker(
                    "source_history_context_lookup_failed",
                    f"source history context lookup failed: {exc}",
                )
            ],
        )

    messages = [
        *[_message_packet(item, position="before") for item in reversed(before_rows)],
        _message_packet(target, position="target"),
        *[_message_packet(item, position="after") for item in after_rows],
    ]
    return (
        {
            "state": "found",
            "source_history_db": source_db_label,
            "messages": messages,
        },
        [],
    )


def _source_context_item(row: dict[str, Any]) -> dict[str, Any]:
    source_context, blockers = _source_feedback_message_context(row)
    source_context["fingerprint"] = _fingerprint(source_context)
    action_cohort = row.get("action_cohort")
    if not isinstance(action_cohort, dict):
        action_cohort = {}
    return {
        "feedback_id": _int_value(row.get("feedback_id")),
        "era": str(row.get("era") or ""),
        "source_label": str(row.get("source_label") or ""),
        "source_session_id": str(row.get("source_session_id") or ""),
        "session_id": str(row.get("session_id") or ""),
        "message_id": str(row.get("message_id") or ""),
        "title": str(row.get("title") or ""),
        "outcome": str(row.get("outcome") or ""),
        "status": str(row.get("status") or ""),
        "tags": row.get("tags") if isinstance(row.get("tags"), list) else [],
        "note": str(row.get("note") or ""),
        "recommended_action": str(row.get("recommended_action") or ""),
        "action_taken": str(row.get("action_taken") or ""),
        "action_cohort": {
            "id": str(action_cohort.get("id") or ""),
            "description": str(action_cohort.get("description") or ""),
        },
        "source_context": source_context,
        "state": "ok" if not blockers else "blocked",
        "blockers": blockers,
    }


def build_feedback_source_context_report(
    *,
    db_path: Path,
    outcome: str | None = "fail",
    cohort: str | None = "grounding_source_verification",
    limit: int = 20,
) -> dict[str, Any]:
    outcome_filter = normalize_outcome_filter(outcome) or "fail"
    cohort_filter = normalize_cohort_filter(cohort) or "grounding_source_verification"
    row_limit = max(1, limit)
    if not db_path.is_file():
        return {
            "schema_version": FEEDBACK_SOURCE_CONTEXT_SCHEMA_VERSION,
            "state": "error",
            "manual_evals_db": {"path": str(db_path), "exists": False},
            "filters": {
                "status": "open",
                "outcome": outcome_filter,
                "cohort": cohort_filter,
                "limit": row_limit,
            },
            "mutation_boundary": _mutation_boundary(),
            "items": [],
            "blockers": [
                _blocker(
                    "manual_evals_db_not_found",
                    "manual_evals.db is not available.",
                )
            ],
            "warnings": ["manual_evals.db is not available"],
        }

    with closing(_connect_readonly(db_path)) as conn:
        integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        actionables = build_filtered_open_feedback_actionable_rows(
            conn,
            outcome=outcome_filter,
            cohort=cohort_filter,
        )
    selected_rows = actionables[:row_limit]
    items = [_source_context_item(row) for row in selected_rows]
    item_blockers = [
        blocker
        for item in items
        if isinstance(item.get("blockers"), list)
        for blocker in item["blockers"]
        if isinstance(blocker, dict)
    ]
    found_source_messages = sum(
        1
        for item in items
        if isinstance(item.get("source_context"), dict)
        and item["source_context"].get("state") == "found"
    )
    context_messages = sum(
        len(item["source_context"].get("messages", []))
        for item in items
        if isinstance(item.get("source_context"), dict)
        and isinstance(item["source_context"].get("messages"), list)
    )
    state = "ok"
    if integrity != "ok":
        state = "error"
    elif item_blockers:
        state = "attention"
    return {
        "schema_version": FEEDBACK_SOURCE_CONTEXT_SCHEMA_VERSION,
        "state": state,
        "manual_evals_db": {
            "path": str(db_path),
            "exists": True,
            "integrity": integrity,
        },
        "filters": {
            "status": "open",
            "outcome": outcome_filter,
            "cohort": cohort_filter,
            "limit": row_limit,
        },
        "counts": {
            "total_rows": len(actionables),
            "returned_rows": len(items),
            "limit_applied": len(items) < len(actionables),
            "source_messages_found": found_source_messages,
            "context_messages": context_messages,
            "blockers": len(item_blockers),
        },
        "mutation_boundary": _mutation_boundary(),
        "items": items,
        "blockers": item_blockers,
        "warnings": [blocker["detail"] for blocker in item_blockers],
    }


def format_feedback_source_context_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    lines = [
        "manual eval feedback source context: "
        f"state={report.get('state', 'unknown')} "
        f"rows={_int_value(counts.get('returned_rows'))}/"
        f"{_int_value(counts.get('total_rows'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"source_messages={_int_value(counts.get('source_messages_found'))} "
        f"context_messages={_int_value(counts.get('context_messages'))} "
        f"warehouse_mutation={mutation.get('manual_evals_db') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]
    items = report.get("items")
    if not isinstance(items, list) or not items:
        lines.append("items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)
    for item in items:
        if not isinstance(item, dict):
            continue
        action_cohort = item.get("action_cohort")
        if not isinstance(action_cohort, dict):
            action_cohort = {}
        tags = item.get("tags")
        tag_text = ", ".join(str(tag) for tag in tags) if isinstance(tags, list) else ""
        source_context = item.get("source_context")
        if not isinstance(source_context, dict):
            source_context = {}
        messages = source_context.get("messages")
        if not isinstance(messages, list):
            messages = []
        lines.extend(
            [
                "- "
                f"feedback={_int_value(item.get('feedback_id'))} "
                f"state={item.get('state') or 'unknown'} "
                f"cohort={action_cohort.get('id') or 'unknown'} "
                f"session={item.get('session_id') or 'unknown'} "
                f"message={item.get('message_id') or 'unknown'} "
                f"source_state={source_context.get('state') or 'unknown'}",
                f"  title={_display_text(item.get('title'))}",
                f"  tags={tag_text or 'none'}",
                f"  recommended_action={_display_text(item.get('recommended_action'))}",
            ]
        )
        if messages:
            lines.append("  source_context:")
            for message in messages:
                if not isinstance(message, dict):
                    continue
                lines.append(
                    "  - "
                    f"{message.get('position') or 'context'} "
                    f"role={message.get('role') or 'unknown'} "
                    f"message={message.get('message_id') or 'none'} "
                    f"chars={_int_value(message.get('content_chars'))} "
                    f"preview={_display_text(message.get('content_preview'))}"
                )
        blockers = item.get("blockers")
        if isinstance(blockers, list) and blockers:
            lines.append("  blockers:")
            for blocker in blockers:
                if not isinstance(blocker, dict):
                    continue
                lines.append(
                    "  - "
                    f"code={blocker.get('code') or 'unknown'} "
                    f"detail={blocker.get('detail') or ''}"
                )
    blockers = report.get("blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"code={blocker.get('code') or 'unknown'} "
                f"detail={blocker.get('detail') or ''}"
            )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)
