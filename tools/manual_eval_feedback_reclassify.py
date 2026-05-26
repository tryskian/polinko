from __future__ import annotations

import json
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
    sqlite_backup_copy,
    sqlite_integrity_check,
    utc_run_timestamp,
    write_json,
)
from tools.manual_eval_open_feedback import feedback_action_cohort


FEEDBACK_RECLASSIFY_SCHEMA_VERSION = "polinko.manual_eval_feedback_reclassify.v1"
FEEDBACK_RECLASSIFY_CONFIRM_TOKEN = "manual-evals-feedback-reclassify"
DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT = Path(".local_archive")
DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH = Path(
    ".local/manual_eval_decisions/feedback_reclassify.json"
)


def feedback_reclassify_mutation_boundary() -> dict[str, str]:
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


def format_feedback_reclassify_report(report: dict[str, Any]) -> str:
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
        "manual eval feedback reclassify: "
        f"state={report.get('state') or 'unknown'} "
        f"mode={report.get('mode') or 'unknown'} "
        f"planned={int_value(counts.get('planned_feedback'))} "
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
                f"from={item.get('current_cohort') or 'unknown'} "
                f"to={item.get('new_cohort') or 'unknown'} "
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
    blockers = report.get("blockers")
    if not isinstance(blockers, list):
        blockers = report.get("apply_blockers")
    if isinstance(blockers, list) and blockers:
        label = "apply_blockers" if report.get("mode") == "apply" else "blockers"
        lines.append(f"{label}:")
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


def _feedback_reclassify_blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load_feedback_reclassify_plan(
    plan_path: Path,
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    resolved_plan_path = plan_path.expanduser()
    if not resolved_plan_path.is_file():
        return None, [
            _feedback_reclassify_blocker(
                "plan_not_found",
                f"feedback reclassification plan was not found: {resolved_plan_path}",
            )
        ]
    try:
        payload = json.loads(resolved_plan_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [
            _feedback_reclassify_blocker(
                "plan_load_failed",
                f"feedback reclassification plan could not be loaded: {exc}",
            )
        ]
    except json.JSONDecodeError as exc:
        return None, [
            _feedback_reclassify_blocker(
                "plan_load_failed",
                "feedback reclassification plan is not valid JSON: "
                f"line {exc.lineno} column {exc.colno}",
            )
        ]
    if not isinstance(payload, dict):
        return None, [
            _feedback_reclassify_blocker(
                "plan_not_object",
                "feedback reclassification plan must be a JSON object.",
            )
        ]
    return payload, []


def _feedback_reclassify_decisions(
    plan_payload: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    if plan_payload is None:
        return [], []
    raw_items = plan_payload.get("decisions")
    if not isinstance(raw_items, list):
        return [], [
            _feedback_reclassify_blocker(
                "missing_decisions",
                "feedback reclassification plan must contain a decisions array.",
            )
        ]
    decisions: list[dict[str, Any]] = []
    blockers: list[dict[str, str]] = []
    seen: set[int] = set()
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            blockers.append(
                _feedback_reclassify_blocker(
                    "decision_not_object",
                    f"decision {index} must be a JSON object.",
                )
            )
            continue
        feedback_id = int_value(raw_item.get("feedback_id"))
        if feedback_id <= 0:
            blockers.append(
                _feedback_reclassify_blocker(
                    "invalid_feedback_id",
                    f"decision {index} has an invalid feedback_id.",
                )
            )
            continue
        if feedback_id in seen:
            blockers.append(
                _feedback_reclassify_blocker(
                    "duplicate_feedback_id",
                    f"feedback {feedback_id} appears more than once in the plan.",
                )
            )
            continue
        recommended_action = normalize_text(raw_item.get("recommended_action"))
        if not recommended_action:
            blockers.append(
                _feedback_reclassify_blocker(
                    "missing_recommended_action",
                    f"feedback {feedback_id} does not name a recommended_action.",
                )
            )
            continue
        rationale = normalize_text(raw_item.get("rationale"))
        seen.add(feedback_id)
        decisions.append(
            {
                "feedback_id": feedback_id,
                "recommended_action": recommended_action,
                "rationale": rationale,
            }
        )
    return decisions, blockers


def _feedback_reclassify_preview_item(
    *,
    decision: dict[str, Any],
    row: dict[str, Any] | None,
) -> dict[str, Any]:
    feedback_id = int_value(decision.get("feedback_id"))
    blockers: list[dict[str, str]] = []
    if row is None:
        blockers.append(
            _feedback_reclassify_blocker(
                "feedback_row_missing",
                f"feedback {feedback_id} was not found in the manual eval warehouse.",
            )
        )
        return {
            "feedback_id": feedback_id,
            "message_id": "",
            "outcome": "",
            "status": "",
            "current_recommended_action": "",
            "new_recommended_action": str(decision.get("recommended_action") or ""),
            "current_cohort": "",
            "new_cohort": feedback_action_cohort(decision.get("recommended_action")),
            "rationale": str(decision.get("rationale") or ""),
            "state": "blocked",
            "blockers": blockers,
        }
    if not feedback_status_is_open(row.get("status")):
        blockers.append(
            _feedback_reclassify_blocker(
                "feedback_row_not_open",
                f"feedback {feedback_id} is {row.get('status') or 'unknown'}, not open.",
            )
        )
    current_action = str(row.get("recommended_action") or "")
    new_action = str(decision.get("recommended_action") or "")
    current_cohort = feedback_action_cohort(current_action)
    new_cohort = feedback_action_cohort(new_action)
    if current_action == new_action:
        blockers.append(
            _feedback_reclassify_blocker(
                "recommended_action_unchanged",
                f"feedback {feedback_id} already has the requested recommended_action.",
            )
        )
    return {
        "feedback_id": feedback_id,
        "message_id": str(row.get("message_id") or ""),
        "outcome": str(row.get("outcome") or ""),
        "status": str(row.get("status") or ""),
        "current_recommended_action": current_action,
        "new_recommended_action": new_action,
        "current_cohort": current_cohort,
        "new_cohort": new_cohort,
        "rationale": str(decision.get("rationale") or ""),
        "state": "ready" if not blockers else "blocked",
        "blockers": blockers,
    }


def build_feedback_reclassify_report(
    *,
    db_path: Path,
    plan_path: Path | None = None,
) -> dict[str, Any]:
    resolved_plan_path = (
        plan_path.expanduser()
        if plan_path is not None
        else DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH
    )
    blockers: list[dict[str, str]] = []
    plan_payload, plan_blockers = _load_feedback_reclassify_plan(resolved_plan_path)
    blockers.extend(plan_blockers)
    decisions, decision_blockers = _feedback_reclassify_decisions(plan_payload)
    blockers.extend(decision_blockers)
    if not db_path.is_file():
        blockers.append(
            _feedback_reclassify_blocker(
                "manual_evals_db_not_found",
                f"manual eval warehouse was not found: {db_path}",
            )
        )

    integrity = "not_checked"
    rows_by_id: dict[int, dict[str, Any]] = {}
    if not blockers and decisions:
        with closing(connect_readonly(db_path)) as conn:
            integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        if integrity != "ok":
            blockers.append(
                _feedback_reclassify_blocker(
                    "manual_evals_db_integrity_not_ok",
                    f"manual eval warehouse integrity check returned {integrity}.",
                )
            )
        else:
            rows_by_id = feedback_rows_by_id(
                db_path=db_path,
                feedback_ids=[int_value(item.get("feedback_id")) for item in decisions],
            )

    items = [
        _feedback_reclassify_preview_item(
            decision=decision,
            row=rows_by_id.get(int_value(decision.get("feedback_id"))),
        )
        for decision in decisions
    ]
    ready_feedback = sum(1 for item in items if item.get("state") == "ready")
    item_blockers = [
        blocker
        for item in items
        if isinstance(item.get("blockers"), list)
        for blocker in item["blockers"]
        if isinstance(blocker, dict)
    ]
    all_blockers = [*blockers, *item_blockers]
    return {
        "schema_version": FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
        "state": "ok" if not all_blockers else "blocked",
        "mode": "preview",
        "manual_evals_db": {
            "path": str(db_path),
            "exists": db_path.is_file(),
            "integrity": integrity,
        },
        "plan": {
            "path": str(resolved_plan_path),
            "exists": resolved_plan_path.is_file(),
        },
        "counts": {
            "planned_feedback": len(decisions),
            "ready_feedback": ready_feedback,
            "blocked_feedback": len(items) - ready_feedback,
            "plan_blockers": len(blockers),
            "item_blockers": len(item_blockers),
        },
        "mutation_boundary": feedback_reclassify_mutation_boundary(),
        "items": items,
        "blockers": all_blockers,
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


def _backup_manual_evals_db_for_feedback_reclassify(
    *,
    db_path: Path,
    backup_root: Path,
    applied_at: str,
    feedback_ids: Sequence[int],
    plan_path: Path,
) -> dict[str, Any]:
    backup_dir = backup_root / f"manual-evals-feedback-reclassify-{applied_at}"
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
            "schema_version": FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
            "created_at": applied_at,
            "source_db_path": str(db_path),
            "backup_db_path": str(backup_db_path),
            "backup_integrity": backup_integrity,
            "plan_path": str(plan_path),
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


def _feedback_reclassify_action_taken(
    *,
    feedback_id: int,
    current_cohort: str,
    new_cohort: str,
    rationale: str,
    backup_dir_name: str,
) -> str:
    rationale_text = f" Rationale: {rationale}." if rationale else ""
    return (
        "Reclassified by manual feedback reclassification gate: feedback "
        f"{feedback_id} moved from {current_cohort or 'unknown'} to "
        f"{new_cohort or 'unknown'}.{rationale_text} Backup: {backup_dir_name}."
    )


def _blocked_feedback_reclassify_apply_report(
    *,
    db_path: Path,
    plan_path: Path,
    preview: dict[str, Any],
    confirm_token: str,
    backup_root: Path,
    blockers: Sequence[dict[str, str]],
    backup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preview_counts = preview.get("counts")
    if not isinstance(preview_counts, dict):
        preview_counts = {}
    return {
        "schema_version": FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
        "state": "blocked",
        "mode": "apply",
        "manual_evals_db": {"path": str(db_path), "backup_required": True},
        "plan": {"path": str(plan_path), "exists": plan_path.is_file()},
        "confirmation": {
            "required": FEEDBACK_RECLASSIFY_CONFIRM_TOKEN,
            "provided": bool(confirm_token),
            "state": "ok"
            if confirm_token == FEEDBACK_RECLASSIFY_CONFIRM_TOKEN
            else "blocked",
        },
        "counts": {
            "planned_feedback": int_value(preview_counts.get("planned_feedback")),
            "ready_feedback": int_value(preview_counts.get("ready_feedback")),
            "blocked_feedback": int_value(preview_counts.get("blocked_feedback")),
            "updated_feedback_rows": 0,
            "backups_written": 1 if backup and backup.get("written") else 0,
            "apply_blockers": len(blockers),
        },
        "mutation_boundary": feedback_reclassify_mutation_boundary(),
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


def write_feedback_reclassify(
    *,
    db_path: Path,
    plan_path: Path | None,
    confirm_token: str,
    backup_root: Path | None = None,
    applied_at: str | None = None,
) -> dict[str, Any]:
    resolved_db_path = db_path.expanduser()
    resolved_plan_path = (
        plan_path.expanduser()
        if plan_path is not None
        else DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH
    )
    resolved_backup_root = (
        backup_root.expanduser()
        if backup_root is not None
        else DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT
    )
    preview = build_feedback_reclassify_report(
        db_path=resolved_db_path,
        plan_path=resolved_plan_path,
    )
    blockers: list[dict[str, str]] = []
    if confirm_token != FEEDBACK_RECLASSIFY_CONFIRM_TOKEN:
        blockers.append(
            _feedback_reclassify_blocker(
                "missing_confirmation",
                "CONFIRM=manual-evals-feedback-reclassify is required before feedback reclassification.",
            )
        )
    if preview.get("state") != "ok":
        blockers.append(
            _feedback_reclassify_blocker(
                "preview_not_ok",
                f"feedback reclassification preview is {preview.get('state') or 'unknown'}.",
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
            _feedback_reclassify_blocker(
                "no_ready_feedback",
                "No ready feedback rows are available to reclassify.",
            )
        )
    if len(ready_items) != len(items):
        blockers.append(
            _feedback_reclassify_blocker(
                "items_not_all_ready",
                "Every feedback reclassification preview item must be ready before apply.",
            )
        )
    feedback_ids, invalid_feedback_ids = _feedback_ids_from_items(ready_items)
    if invalid_feedback_ids:
        blockers.append(
            _feedback_reclassify_blocker(
                "invalid_feedback_id",
                "Feedback reclassification preview contains non-integer feedback IDs: "
                + ",".join(invalid_feedback_ids),
            )
        )
    if blockers:
        return _blocked_feedback_reclassify_apply_report(
            db_path=resolved_db_path,
            plan_path=resolved_plan_path,
            preview=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=blockers,
        )

    actual_applied_at = applied_at or utc_run_timestamp()
    try:
        backup = _backup_manual_evals_db_for_feedback_reclassify(
            db_path=resolved_db_path,
            backup_root=resolved_backup_root,
            applied_at=actual_applied_at,
            feedback_ids=feedback_ids,
            plan_path=resolved_plan_path,
        )
    except (OSError, sqlite3.Error) as exc:
        return _blocked_feedback_reclassify_apply_report(
            db_path=resolved_db_path,
            plan_path=resolved_plan_path,
            preview=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=[
                _feedback_reclassify_blocker(
                    "backup_failed",
                    f"manual eval warehouse backup failed: {exc}",
                )
            ],
        )
    if backup.get("integrity_check") != "ok":
        return _blocked_feedback_reclassify_apply_report(
            db_path=resolved_db_path,
            plan_path=resolved_plan_path,
            preview=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=[
                _feedback_reclassify_blocker(
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
            return _blocked_feedback_reclassify_apply_report(
                db_path=resolved_db_path,
                plan_path=resolved_plan_path,
                preview=preview,
                confirm_token=confirm_token,
                backup_root=resolved_backup_root,
                blockers=[
                    _feedback_reclassify_blocker(
                        "feedback_rows_changed_after_backup",
                        "Feedback rows changed after backup and before apply: "
                        + ",".join(no_longer_open),
                    )
                ],
                backup=backup,
            )
        for feedback_id in feedback_ids:
            item = item_by_feedback_id[feedback_id]
            new_action = str(item.get("new_recommended_action") or "")
            action_taken = _feedback_reclassify_action_taken(
                feedback_id=feedback_id,
                current_cohort=str(item.get("current_cohort") or ""),
                new_cohort=str(item.get("new_cohort") or ""),
                rationale=str(item.get("rationale") or ""),
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
                    "recommended_action_before": str(
                        item.get("current_recommended_action") or ""
                    ),
                    "recommended_action_after": new_action,
                    "current_cohort": str(item.get("current_cohort") or ""),
                    "new_cohort": str(item.get("new_cohort") or ""),
                    "action_taken": action_taken,
                    "status": current_statuses.get(feedback_id) or "open",
                    "updated_at": updated_at,
                    "mutation": "recommended_action,action_taken,updated_at",
                }
            )
        conn.commit()

    return {
        "schema_version": FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
        "state": "applied",
        "mode": "apply",
        "applied_at": actual_applied_at,
        "manual_evals_db": {
            "path": str(resolved_db_path),
            "backup_required": True,
            "integrity_check": "ok",
        },
        "plan": {"path": str(resolved_plan_path), "exists": True},
        "confirmation": {
            "required": FEEDBACK_RECLASSIFY_CONFIRM_TOKEN,
            "provided": True,
            "state": "ok",
        },
        "counts": {
            "planned_feedback": len(items),
            "ready_feedback": len(ready_items),
            "blocked_feedback": 0,
            "updated_feedback_rows": len(apply_items),
            "backups_written": 1,
            "apply_blockers": 0,
        },
        "mutation_boundary": feedback_reclassify_mutation_boundary(),
        "backup": backup,
        "apply_items": apply_items,
        "updated_feedback_ids": feedback_ids,
        "apply_blockers": [],
        "warnings": [],
    }
