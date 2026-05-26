from __future__ import annotations

import shlex
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_feedback_db import (
    connect_readonly,
    feedback_rows_by_id,
    feedback_status_is_open,
    int_value,
    normalize_text,
    row_dict,
    sqlite_backup_copy,
    sqlite_integrity_check,
    utc_run_timestamp,
    write_json,
)
from tools.manual_eval_open_feedback import (
    build_filtered_open_feedback_actionable_rows,
    feedback_action_cohort,
    normalize_cohort_filter,
    normalize_outcome_filter,
)


NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION = (
    "polinko.manual_eval_no_context_feedback_reclassify.v1"
)
NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN = "manual-evals-no-context-reclassify"
DEFAULT_NO_CONTEXT_RECLASSIFY_BACKUP_ROOT = Path(".local_archive")
NO_CONTEXT_RECLASSIFIED_RECOMMENDED_ACTION = (
    "Preserve as overlay-assisted OCR hypothesis evidence; attach the "
    "overlay/source image context before rerunning OCR for comparison."
)
NO_CONTEXT_SOURCE_RESPONSE_MARKER = "no new image evidence in this turn"


def no_context_reclassify_mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "feedback_recommended_action_action_taken_updated_at_only",
        "manual_eval_warehouse": "feedback_rows_only",
        "feedback_status": "unchanged",
        "ocr_runs": "unchanged",
        "image_assets": "unchanged",
        "eval_rows": "unchanged",
        "source_history_db": "unchanged",
        "pulse": "excluded",
    }


def format_no_context_feedback_reclassify_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    backup = report.get("backup")
    if not isinstance(backup, dict):
        backup = {}
    lines = [
        "manual eval no-context feedback reclassify: "
        f"state={report.get('state') or 'unknown'} "
        f"mode={report.get('mode') or 'unknown'} "
        f"feedback={int_value(counts.get('candidate_feedback'))} "
        f"ready={int_value(counts.get('ready_feedback'))} "
        f"blocked={int_value(counts.get('blocked_feedback'))} "
        f"updated={int_value(counts.get('updated_feedback_rows'))} "
        f"mutation={mutation.get('manual_evals_db') or 'none'} "
        f"backup_dir={Path(str(backup.get('dir') or '')).name}",
    ]
    items = report.get("items")
    if not isinstance(items, list):
        items = report.get("apply_items")
    if isinstance(items, list) and items:
        lines.append("feedback_rows:")
        for item in items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"feedback={item.get('feedback_id') or 'unknown'} "
                f"state={item.get('state') or report.get('state') or 'unknown'} "
                f"outcome={item.get('outcome') or ''} "
                f"message={item.get('message_id') or ''} "
                f"mutation={item.get('mutation') or 'preview'}"
            )
            blockers = item.get("blockers")
            if isinstance(blockers, list) and blockers:
                for blocker in blockers:
                    if not isinstance(blocker, dict):
                        continue
                    lines.append(
                        "  blocker="
                        f"{blocker.get('code') or 'unknown'} "
                        f"detail={blocker.get('detail') or ''}"
                    )
    blockers = report.get("apply_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("apply_blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"code={blocker.get('code') or 'unknown'} "
                f"detail={blocker.get('detail') or ''}"
            )
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def _no_context_reclassify_blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _source_history_db_path(source_history_db: object) -> Path:
    path = Path(str(source_history_db or "")).expanduser()
    if path.is_absolute():
        return path
    return Path.cwd() / path


def _truncate_text(value: object, *, max_chars: int = 180) -> str:
    text = normalize_text(value)
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "..."


def _source_feedback_message(
    row: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    source_db_path = _source_history_db_path(row.get("source_history_db"))
    if not str(row.get("source_history_db") or "").strip():
        return None, [
            _no_context_reclassify_blocker(
                "missing_source_history_db",
                "feedback row does not name a source history DB.",
            )
        ]
    if not source_db_path.is_file():
        return None, [
            _no_context_reclassify_blocker(
                "source_history_db_not_found",
                "source history DB was not found.",
            )
        ]
    try:
        with closing(connect_readonly(source_db_path)) as conn:
            source_row = conn.execute(
                """
                SELECT role, content, created_at
                FROM chat_messages
                WHERE session_id = ? AND message_id = ?
                LIMIT 1
                """,
                [
                    str(row.get("source_session_id") or ""),
                    str(row.get("message_id") or ""),
                ],
            ).fetchone()
    except sqlite3.Error as exc:
        return None, [
            _no_context_reclassify_blocker(
                "source_history_message_lookup_failed",
                f"source history message lookup failed: {exc}",
            )
        ]
    if source_row is None:
        return None, [
            _no_context_reclassify_blocker(
                "source_history_message_not_found",
                "source history DB does not contain the feedback message.",
            )
        ]
    return row_dict(source_row), []


def _no_context_reclassify_preview_item(row: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    ocr_context = row.get("ocr_context")
    if not isinstance(ocr_context, dict):
        ocr_context = {}
    if int_value(ocr_context.get("same_session_ocr_runs")) > 0:
        blockers.append(
            _no_context_reclassify_blocker(
                "same_session_ocr_exists",
                "feedback row already has same-session OCR context.",
            )
        )
    current_cohort = feedback_action_cohort(row.get("recommended_action"))
    if current_cohort not in {"ocr_retry_evidence", "ocr_overlay_hypothesis"}:
        blockers.append(
            _no_context_reclassify_blocker(
                "feedback_not_ocr_retry_cohort",
                "feedback row is not in an OCR retry or overlay-hypothesis cohort.",
            )
        )

    source_message, source_blockers = _source_feedback_message(row)
    blockers.extend(source_blockers)
    source_role = ""
    source_content = ""
    source_created_at = 0
    if source_message is not None:
        source_role = str(source_message.get("role") or "")
        source_content = str(source_message.get("content") or "")
        source_created_at = int_value(source_message.get("created_at"))
        if source_role != "assistant":
            blockers.append(
                _no_context_reclassify_blocker(
                    "source_message_not_assistant",
                    "feedback message is not an assistant response.",
                )
            )
        if NO_CONTEXT_SOURCE_RESPONSE_MARKER not in source_content.lower():
            blockers.append(
                _no_context_reclassify_blocker(
                    "source_message_not_no_image_response",
                    "feedback message is not the no-new-image-evidence response.",
                )
            )

    return {
        "feedback_id": int_value(row.get("feedback_id")),
        "session_id": str(row.get("session_id") or ""),
        "source_session_id": str(row.get("source_session_id") or ""),
        "message_id": str(row.get("message_id") or ""),
        "outcome": str(row.get("outcome") or ""),
        "status": str(row.get("status") or ""),
        "title": str(row.get("title") or ""),
        "current_recommended_action": str(row.get("recommended_action") or ""),
        "new_recommended_action": NO_CONTEXT_RECLASSIFIED_RECOMMENDED_ACTION,
        "source_message": {
            "role": source_role,
            "created_at": source_created_at,
            "content_preview": _truncate_text(source_content),
        },
        "state": "ready" if not blockers else "blocked",
        "blockers": blockers,
    }


def build_no_context_feedback_reclassify_report(
    *,
    db_path: Path,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    outcome_filter = normalize_outcome_filter(outcome)
    cohort_filter = normalize_cohort_filter(cohort) or "ocr_retry_evidence"
    row_limit = max(1, limit)
    if not db_path.is_file():
        return {
            "schema_version": NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
            "state": "error",
            "mode": "preview",
            "manual_evals_db": {"path": str(db_path), "exists": False},
            "filters": {
                "status": "open",
                "outcome": outcome_filter or "",
                "cohort": cohort_filter,
                "limit": row_limit,
            },
            "counts": {
                "candidate_feedback": 0,
                "ready_feedback": 0,
                "blocked_feedback": 0,
            },
            "mutation_boundary": no_context_reclassify_mutation_boundary(),
            "items": [],
            "warnings": ["manual_evals.db is not available"],
        }

    with closing(connect_readonly(db_path)) as conn:
        integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        all_rows = build_filtered_open_feedback_actionable_rows(
            conn,
            outcome=outcome_filter,
            cohort=cohort_filter,
        )
        rows = all_rows[:row_limit]

    items = [_no_context_reclassify_preview_item(row) for row in rows]
    ready_feedback = sum(1 for item in items if item.get("state") == "ready")
    blocked_feedback = len(items) - ready_feedback
    return {
        "schema_version": NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
        "state": "ok" if integrity == "ok" else "error",
        "mode": "preview",
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
        },
        "counts": {
            "total_feedback_rows": len(all_rows),
            "candidate_feedback": len(items),
            "ready_feedback": ready_feedback,
            "blocked_feedback": blocked_feedback,
            "limit_applied": len(rows) < len(all_rows),
        },
        "mutation_boundary": no_context_reclassify_mutation_boundary(),
        "items": items,
        "warnings": [],
    }


def _feedback_ids_from_items(
    items: Sequence[dict[str, Any]],
) -> tuple[list[int], list[str]]:
    feedback_ids: list[int] = []
    invalid_feedback_ids: list[str] = []
    seen: set[int] = set()
    for item in items:
        raw_feedback_id = str(item.get("feedback_id") or "").strip()
        try:
            feedback_id = int(raw_feedback_id)
        except ValueError:
            invalid_feedback_ids.append(raw_feedback_id or "<empty>")
            continue
        if feedback_id < 1:
            invalid_feedback_ids.append(raw_feedback_id)
            continue
        if feedback_id in seen:
            continue
        seen.add(feedback_id)
        feedback_ids.append(feedback_id)
    return feedback_ids, invalid_feedback_ids


def _backup_manual_evals_db_for_no_context_reclassify(
    *,
    db_path: Path,
    backup_root: Path,
    applied_at: str,
    feedback_ids: Sequence[int],
) -> dict[str, Any]:
    backup_dir = backup_root / f"manual-evals-feedback-no-context-{applied_at}"
    backup_db_path = backup_dir / "manual_evals.db"
    if backup_dir.exists():
        raise FileExistsError(f"backup directory already exists: {backup_dir}")
    sqlite_backup_copy(
        source_db_path=db_path,
        destination_db_path=backup_db_path,
    )
    backup_integrity = sqlite_integrity_check(backup_db_path)
    manifest_path = backup_dir / "manifest.json"
    restore_command = (
        f"cp {shlex.quote(str(backup_db_path))} {shlex.quote(str(db_path))}"
    )
    write_json(
        manifest_path,
        {
            "schema_version": NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
            "created_at": applied_at,
            "source_db_path": str(db_path),
            "backup_db_path": str(backup_db_path),
            "backup_integrity": backup_integrity,
            "feedback_ids": [int(feedback_id) for feedback_id in feedback_ids],
            "restore_command": restore_command,
        },
    )
    return {
        "written": True,
        "root": str(backup_root),
        "dir": str(backup_dir),
        "db_path": str(backup_db_path),
        "manifest_path": str(manifest_path),
        "integrity_check": backup_integrity,
        "restore_command": restore_command,
    }


def _no_context_reclassify_action_taken(
    *,
    feedback_id: int,
    backup_dir_name: str,
) -> str:
    return (
        "Reclassified by overlay-hypothesis feedback gate: feedback "
        f"{feedback_id} has no same-session OCR context and the source response "
        "requested new image evidence; preserved as overlay-assisted OCR "
        "hypothesis evidence. "
        f"Backup: {backup_dir_name}."
    )


def _blocked_no_context_reclassify_report(
    *,
    db_path: Path,
    preview_report: dict[str, Any],
    confirm_token: str,
    backup_root: Path,
    blockers: Sequence[dict[str, str]],
    backup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preview_counts = preview_report.get("counts")
    if not isinstance(preview_counts, dict):
        preview_counts = {}
    return {
        "schema_version": NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
        "state": "blocked",
        "mode": "apply",
        "manual_evals_db": {
            "path": str(db_path),
            "backup_required": True,
        },
        "confirmation": {
            "required": NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN,
            "provided": bool(confirm_token),
            "state": "ok"
            if confirm_token == NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN
            else "blocked",
        },
        "filters": preview_report.get("filters")
        if isinstance(preview_report, dict)
        else {},
        "counts": {
            "candidate_feedback": int_value(preview_counts.get("candidate_feedback")),
            "ready_feedback": int_value(preview_counts.get("ready_feedback")),
            "blocked_feedback": int_value(preview_counts.get("blocked_feedback")),
            "updated_feedback_rows": 0,
            "backups_written": 1 if backup and backup.get("written") else 0,
            "apply_blockers": len(blockers),
        },
        "mutation_boundary": no_context_reclassify_mutation_boundary(),
        "backup": backup
        or {
            "written": False,
            "root": str(backup_root),
            "dir": "",
            "db_path": "",
            "restore_command": "",
        },
        "apply_items": [],
        "apply_blockers": list(blockers),
        "warnings": [blocker["detail"] for blocker in blockers],
    }


def write_no_context_feedback_reclassify(
    *,
    db_path: Path,
    confirm_token: str,
    backup_root: Path | None = None,
    applied_at: str | None = None,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    resolved_db_path = db_path.expanduser()
    resolved_backup_root = (
        backup_root.expanduser()
        if backup_root is not None
        else DEFAULT_NO_CONTEXT_RECLASSIFY_BACKUP_ROOT
    )
    preview = build_no_context_feedback_reclassify_report(
        db_path=resolved_db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    blockers: list[dict[str, str]] = []
    if confirm_token != NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN:
        blockers.append(
            _no_context_reclassify_blocker(
                "missing_confirmation",
                "CONFIRM=manual-evals-no-context-reclassify is required before reclassification.",
            )
        )
    if not resolved_db_path.is_file():
        blockers.append(
            _no_context_reclassify_blocker(
                "manual_evals_db_not_found",
                f"manual eval warehouse was not found: {resolved_db_path}",
            )
        )
    if preview.get("state") != "ok":
        blockers.append(
            _no_context_reclassify_blocker(
                "preview_not_ok",
                f"overlay reclassification preview is {preview.get('state') or 'unknown'}.",
            )
        )
    items = preview.get("items")
    if not isinstance(items, list):
        items = []
    ready_items = [
        item
        for item in items
        if isinstance(item, dict) and item.get("state") == "ready"
    ]
    if not ready_items:
        blockers.append(
            _no_context_reclassify_blocker(
                "no_ready_feedback",
                "No ready overlay-hypothesis feedback rows are available to reclassify.",
            )
        )
    if len(ready_items) != len(items):
        blockers.append(
            _no_context_reclassify_blocker(
                "items_not_all_ready",
                "Every overlay reclassification preview item must be ready before apply.",
            )
        )

    feedback_ids, invalid_feedback_ids = _feedback_ids_from_items(ready_items)
    if invalid_feedback_ids:
        blockers.append(
            _no_context_reclassify_blocker(
                "invalid_feedback_id",
                "No-context reclassification preview contains non-integer feedback IDs: "
                + ",".join(invalid_feedback_ids),
            )
        )

    rows_by_id: dict[int, dict[str, Any]] = {}
    if not blockers and feedback_ids:
        try:
            integrity = sqlite_integrity_check(resolved_db_path)
        except sqlite3.Error as exc:
            blockers.append(
                _no_context_reclassify_blocker(
                    "manual_evals_db_integrity_check_failed",
                    f"manual eval warehouse integrity check failed: {exc}",
                )
            )
        else:
            if integrity != "ok":
                blockers.append(
                    _no_context_reclassify_blocker(
                        "manual_evals_db_integrity_not_ok",
                        f"manual eval warehouse integrity check returned {integrity}.",
                    )
                )
        if not blockers:
            rows_by_id = feedback_rows_by_id(
                db_path=resolved_db_path,
                feedback_ids=feedback_ids,
            )
            missing_feedback_ids = [
                feedback_id
                for feedback_id in feedback_ids
                if feedback_id not in rows_by_id
            ]
            if missing_feedback_ids:
                blockers.append(
                    _no_context_reclassify_blocker(
                        "feedback_rows_missing",
                        "Feedback rows are missing from the current warehouse: "
                        + ",".join(
                            str(feedback_id) for feedback_id in missing_feedback_ids
                        ),
                    )
                )
            non_open_feedback = [
                f"{feedback_id}={rows_by_id[feedback_id].get('status') or 'unknown'}"
                for feedback_id in feedback_ids
                if not feedback_status_is_open(
                    rows_by_id.get(feedback_id, {}).get("status")
                )
            ]
            if non_open_feedback:
                blockers.append(
                    _no_context_reclassify_blocker(
                        "feedback_rows_not_open",
                        "Feedback rows are no longer open: "
                        + ",".join(non_open_feedback),
                    )
                )

    if blockers:
        return _blocked_no_context_reclassify_report(
            db_path=resolved_db_path,
            preview_report=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=blockers,
        )

    actual_applied_at = applied_at or utc_run_timestamp()
    try:
        backup = _backup_manual_evals_db_for_no_context_reclassify(
            db_path=resolved_db_path,
            backup_root=resolved_backup_root,
            applied_at=actual_applied_at,
            feedback_ids=feedback_ids,
        )
    except (OSError, sqlite3.Error) as exc:
        return _blocked_no_context_reclassify_report(
            db_path=resolved_db_path,
            preview_report=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=[
                _no_context_reclassify_blocker(
                    "backup_failed",
                    f"manual eval warehouse backup failed: {exc}",
                )
            ],
        )
    if backup.get("integrity_check") != "ok":
        return _blocked_no_context_reclassify_report(
            db_path=resolved_db_path,
            preview_report=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=[
                _no_context_reclassify_blocker(
                    "backup_integrity_not_ok",
                    "manual eval warehouse backup integrity check returned "
                    f"{backup.get('integrity_check') or 'missing'}.",
                )
            ],
            backup=backup,
        )

    item_by_feedback_id = {
        int_value(item.get("feedback_id")): item for item in ready_items
    }
    backup_dir_name = Path(str(backup.get("dir") or "")).name
    updated_at = int(datetime.now(UTC).timestamp())
    apply_items: list[dict[str, Any]] = []
    with closing(sqlite3.connect(resolved_db_path)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("BEGIN IMMEDIATE")
        current_rows = conn.execute(
            "SELECT id, status FROM feedback WHERE id IN ("
            + ",".join("?" for _ in feedback_ids)
            + ")",
            feedback_ids,
        ).fetchall()
        current_statuses = {
            int_value(row["id"]): str(row["status"] or "") for row in current_rows
        }
        no_longer_open = [
            f"{feedback_id}={current_statuses.get(feedback_id) or 'missing'}"
            for feedback_id in feedback_ids
            if not feedback_status_is_open(current_statuses.get(feedback_id))
        ]
        if no_longer_open:
            conn.rollback()
            return _blocked_no_context_reclassify_report(
                db_path=resolved_db_path,
                preview_report=preview,
                confirm_token=confirm_token,
                backup_root=resolved_backup_root,
                blockers=[
                    _no_context_reclassify_blocker(
                        "feedback_rows_changed_after_backup",
                        "Feedback rows changed after backup and before apply: "
                        + ",".join(no_longer_open),
                    )
                ],
                backup=backup,
            )
        for feedback_id in feedback_ids:
            item = item_by_feedback_id[feedback_id]
            old_action = str(item.get("current_recommended_action") or "")
            new_action = str(item.get("new_recommended_action") or "")
            action_taken = _no_context_reclassify_action_taken(
                feedback_id=feedback_id,
                backup_dir_name=backup_dir_name,
            )
            conn.execute(
                """
                UPDATE feedback
                SET recommended_action = ?,
                    action_taken = ?,
                    updated_at = ?
                WHERE id = ? AND lower(status) = ?
                """,
                (new_action, action_taken, updated_at, feedback_id, "open"),
            )
            apply_items.append(
                {
                    "feedback_id": feedback_id,
                    "message_id": str(item.get("message_id") or ""),
                    "outcome": str(item.get("outcome") or ""),
                    "recommended_action_before": old_action,
                    "recommended_action_after": new_action,
                    "action_taken": action_taken,
                    "status": current_statuses.get(feedback_id) or "open",
                    "updated_at": updated_at,
                    "mutation": "recommended_action,action_taken,updated_at",
                }
            )
        conn.commit()

    return {
        "schema_version": NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
        "state": "applied",
        "mode": "apply",
        "applied_at": actual_applied_at,
        "manual_evals_db": {
            "path": str(resolved_db_path),
            "backup_required": True,
            "integrity_check": "ok",
        },
        "confirmation": {
            "required": NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN,
            "provided": True,
            "state": "ok",
        },
        "filters": preview.get("filters") if isinstance(preview, dict) else {},
        "counts": {
            "candidate_feedback": len(items),
            "ready_feedback": len(ready_items),
            "blocked_feedback": 0,
            "updated_feedback_rows": len(apply_items),
            "backups_written": 1,
            "apply_blockers": 0,
        },
        "mutation_boundary": no_context_reclassify_mutation_boundary(),
        "backup": backup,
        "apply_items": apply_items,
        "updated_feedback_ids": feedback_ids,
        "apply_blockers": [],
        "warnings": [],
    }
