from __future__ import annotations

import shlex
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_feedback_closure_preview import (
    build_ocr_retry_feedback_closure_preview_report,
)
from tools.manual_eval_ocr_retry_feedback_db import (
    feedback_rows_by_id as _feedback_rows_by_id,
    feedback_status_is_open as _feedback_status_is_open,
    int_value as _int_value,
    sqlite_integrity_check as _sqlite_integrity_check,
    utc_run_timestamp as _utc_run_timestamp,
    write_json as _write_json,
)


OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_feedback_closure_apply.v1"
)
OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN = "ocr-retry-feedback-closure-apply"
DEFAULT_FEEDBACK_CLOSURE_APPLY_BACKUP_ROOT = Path(".local_archive")


def ocr_retry_feedback_closure_apply_mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "feedback_status_action_taken_updated_at_only",
        "feedback_closure": "applied",
        "live_eval_rows": "none",
        "manual_eval_warehouse": "feedback_rows_only",
        "ocr_run_rows": "none",
        "source_links": "none",
    }


def _closed_feedback_status_for_open_status(status: object) -> str:
    raw_status = str(status or "").strip()
    return "CLOSED" if raw_status.isupper() else "closed"


def _feedback_ids_from_closure_items(
    closure_items: Sequence[dict[str, Any]],
) -> tuple[list[int], list[str]]:
    feedback_ids: list[int] = []
    invalid_feedback_ids: list[str] = []
    seen: set[int] = set()
    for item in closure_items:
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


def _ocr_retry_feedback_closure_apply_blocker(
    code: str,
    detail: str,
) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _feedback_closure_apply_counts(
    preview_report: dict[str, Any] | None,
    *,
    target_feedback_rows: int = 0,
    updated_feedback_rows: int = 0,
    skipped_feedback_rows: int = 0,
    backups_written: int = 0,
) -> dict[str, int]:
    preview_counts = (
        preview_report.get("counts") if isinstance(preview_report, dict) else {}
    )
    if not isinstance(preview_counts, dict):
        preview_counts = {}
    return {
        "bundle_requests": _int_value(preview_counts.get("bundle_requests")),
        "bundle_responses": _int_value(preview_counts.get("bundle_responses")),
        "preview_feedback_items": _int_value(preview_counts.get("feedback_items")),
        "ready_feedback": _int_value(preview_counts.get("ready_feedback")),
        "attention_feedback": _int_value(preview_counts.get("attention_feedback")),
        "blocked_feedback": _int_value(preview_counts.get("blocked_feedback")),
        "target_feedback_rows": target_feedback_rows,
        "updated_feedback_rows": updated_feedback_rows,
        "skipped_feedback_rows": skipped_feedback_rows,
        "backups_written": backups_written,
    }


def _blocked_ocr_retry_feedback_closure_apply_report(
    *,
    db_path: Path,
    run_dir: Path | None,
    backup_root: Path,
    confirm_token: str,
    preview_report: dict[str, Any] | None,
    blockers: Sequence[dict[str, str]],
    backup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if backup is None:
        backup = {
            "written": False,
            "root": str(backup_root),
            "dir": "",
            "db_path": "",
            "restore_command": "",
        }
    preview_counts = _feedback_closure_apply_counts(
        preview_report,
        backups_written=1 if backup.get("written") else 0,
    )
    return {
        "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
        "state": "blocked",
        "run_dir": str(run_dir or ""),
        "run_id": str(preview_report.get("run_id") or "")
        if isinstance(preview_report, dict)
        else "",
        "bundle_state": str(preview_report.get("bundle_state") or "not_checked")
        if isinstance(preview_report, dict)
        else "not_checked",
        "preview_state": str(preview_report.get("state") or "not_checked")
        if isinstance(preview_report, dict)
        else "not_checked",
        "confirmation": {
            "required": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
            "provided": bool(confirm_token),
            "state": "ok"
            if confirm_token == OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN
            else "blocked",
        },
        "manual_evals_db": {
            "path": str(db_path),
            "backup_required": True,
        },
        "counts": preview_counts,
        "mutation_boundary": ocr_retry_feedback_closure_apply_mutation_boundary(),
        "backup": backup,
        "apply_items": [],
        "apply_blockers": list(blockers),
        "warnings": [blocker["detail"] for blocker in blockers],
    }


def _backup_manual_evals_db_for_feedback_closure(
    *,
    db_path: Path,
    backup_root: Path,
    applied_at: str,
    run_id: str,
    feedback_ids: Sequence[int],
) -> dict[str, Any]:
    backup_dir = backup_root / f"manual-evals-feedback-closure-apply-{applied_at}"
    backup_db_path = backup_dir / "manual_evals.db"
    if backup_dir.exists():
        raise FileExistsError(f"backup directory already exists: {backup_dir}")
    backup_dir.mkdir(parents=True)
    with closing(sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)) as source:
        with closing(sqlite3.connect(backup_db_path)) as destination:
            source.backup(destination)
    with closing(sqlite3.connect(backup_db_path)) as conn:
        row = conn.execute("PRAGMA integrity_check").fetchone()
    backup_integrity = str(row[0] or "") if row else "missing"
    manifest_path = backup_dir / "manifest.json"
    restore_command = (
        f"cp {shlex.quote(str(backup_db_path))} {shlex.quote(str(db_path))}"
    )
    _write_json(
        manifest_path,
        {
            "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
            "created_at": applied_at,
            "run_id": run_id,
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


def _feedback_closure_action_taken(
    *,
    run_id: str,
    feedback_id: int,
    evidence_count: int,
    backup_dir_name: str,
) -> str:
    evidence_text = "request" if evidence_count == 1 else "requests"
    return (
        "Closed by OCR retry feedback-closure apply: "
        f"bundle {run_id} produced successful retry evidence for feedback "
        f"{feedback_id} from {evidence_count} {evidence_text}. "
        f"Backup: {backup_dir_name}."
    )


def write_ocr_retry_feedback_closure_apply(
    *,
    db_path: Path,
    run_dir: Path | None,
    confirm_token: str,
    backup_root: Path | None = None,
    applied_at: str | None = None,
) -> dict[str, Any]:
    resolved_db_path = db_path.expanduser()
    resolved_run_dir = run_dir.expanduser() if run_dir else None
    resolved_backup_root = (
        backup_root.expanduser()
        if backup_root is not None
        else DEFAULT_FEEDBACK_CLOSURE_APPLY_BACKUP_ROOT
    )
    preview_report = build_ocr_retry_feedback_closure_preview_report(
        run_dir=resolved_run_dir
    )
    blockers: list[dict[str, str]] = []

    if confirm_token != OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN:
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "missing_confirmation",
                "CONFIRM=ocr-retry-feedback-closure-apply is required before feedback closure apply.",
            )
        )
    if not resolved_db_path.is_file():
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "manual_evals_db_not_found",
                f"manual eval warehouse was not found: {resolved_db_path}",
            )
        )
    bundle_state = str(preview_report.get("bundle_state") or "unknown")
    preview_state = str(preview_report.get("state") or "unknown")
    if bundle_state != "ok":
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "bundle_report_not_ok",
                f"OCR retry execution bundle report is {bundle_state}.",
            )
        )
    if preview_state != "ok":
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "preview_not_ok",
                f"OCR retry feedback-closure preview is {preview_state}.",
            )
        )

    closure_items = preview_report.get("closure_items")
    if not isinstance(closure_items, list):
        closure_items = []
    ready_closure_items = [
        item
        for item in closure_items
        if isinstance(item, dict) and item.get("state") == "ready"
    ]
    if not ready_closure_items:
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "no_ready_feedback",
                "No ready feedback closure items are available to apply.",
            )
        )
    if len(ready_closure_items) != len(closure_items):
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "closure_items_not_all_ready",
                "Every feedback closure preview item must be ready before apply.",
            )
        )

    feedback_ids, invalid_feedback_ids = _feedback_ids_from_closure_items(
        ready_closure_items
    )
    if invalid_feedback_ids:
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "invalid_feedback_id",
                "Feedback closure preview contains non-integer feedback IDs: "
                + ",".join(invalid_feedback_ids),
            )
        )

    rows_by_id: dict[int, dict[str, Any]] = {}
    if not blockers and feedback_ids:
        try:
            integrity = _sqlite_integrity_check(resolved_db_path)
        except sqlite3.Error as exc:
            blockers.append(
                _ocr_retry_feedback_closure_apply_blocker(
                    "manual_evals_db_integrity_check_failed",
                    f"manual eval warehouse integrity check failed: {exc}",
                )
            )
        else:
            if integrity != "ok":
                blockers.append(
                    _ocr_retry_feedback_closure_apply_blocker(
                        "manual_evals_db_integrity_not_ok",
                        f"manual eval warehouse integrity check returned {integrity}.",
                    )
                )
        if not blockers:
            rows_by_id = _feedback_rows_by_id(
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
                    _ocr_retry_feedback_closure_apply_blocker(
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
                if not _feedback_status_is_open(
                    rows_by_id.get(feedback_id, {}).get("status")
                )
            ]
            if non_open_feedback:
                blockers.append(
                    _ocr_retry_feedback_closure_apply_blocker(
                        "feedback_rows_not_open",
                        "Feedback rows are no longer open: "
                        + ",".join(non_open_feedback),
                    )
                )

    if blockers:
        return _blocked_ocr_retry_feedback_closure_apply_report(
            db_path=resolved_db_path,
            run_dir=resolved_run_dir,
            backup_root=resolved_backup_root,
            confirm_token=confirm_token,
            preview_report=preview_report,
            blockers=blockers,
        )

    run_id = str(preview_report.get("run_id") or "")
    actual_applied_at = applied_at or _utc_run_timestamp()
    try:
        backup = _backup_manual_evals_db_for_feedback_closure(
            db_path=resolved_db_path,
            backup_root=resolved_backup_root,
            applied_at=actual_applied_at,
            run_id=run_id,
            feedback_ids=feedback_ids,
        )
    except (OSError, sqlite3.Error) as exc:
        return _blocked_ocr_retry_feedback_closure_apply_report(
            db_path=resolved_db_path,
            run_dir=resolved_run_dir,
            backup_root=resolved_backup_root,
            confirm_token=confirm_token,
            preview_report=preview_report,
            blockers=[
                _ocr_retry_feedback_closure_apply_blocker(
                    "backup_failed",
                    f"manual eval warehouse backup failed: {exc}",
                )
            ],
        )
    if backup.get("integrity_check") != "ok":
        return _blocked_ocr_retry_feedback_closure_apply_report(
            db_path=resolved_db_path,
            run_dir=resolved_run_dir,
            backup_root=resolved_backup_root,
            confirm_token=confirm_token,
            preview_report=preview_report,
            blockers=[
                _ocr_retry_feedback_closure_apply_blocker(
                    "backup_integrity_not_ok",
                    "manual eval warehouse backup integrity check returned "
                    f"{backup.get('integrity_check') or 'missing'}.",
                )
            ],
            backup=backup,
        )

    backup_dir_name = Path(str(backup.get("dir") or "")).name
    updated_at = int(datetime.now(UTC).timestamp())
    apply_items: list[dict[str, Any]] = []
    item_by_feedback_id = {
        int(feedback_id): item
        for feedback_id, item in zip(feedback_ids, ready_closure_items, strict=True)
    }
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
            _int_value(row["id"]): str(row["status"] or "") for row in current_rows
        }
        no_longer_open = [
            f"{feedback_id}={current_statuses.get(feedback_id) or 'missing'}"
            for feedback_id in feedback_ids
            if not _feedback_status_is_open(current_statuses.get(feedback_id))
        ]
        if no_longer_open:
            conn.rollback()
            return _blocked_ocr_retry_feedback_closure_apply_report(
                db_path=resolved_db_path,
                run_dir=resolved_run_dir,
                backup_root=resolved_backup_root,
                confirm_token=confirm_token,
                preview_report=preview_report,
                blockers=[
                    _ocr_retry_feedback_closure_apply_blocker(
                        "feedback_rows_changed_after_backup",
                        "Feedback rows changed after backup and before apply: "
                        + ",".join(no_longer_open),
                    )
                ],
                backup=backup,
            )
        for feedback_id in feedback_ids:
            preview_item = item_by_feedback_id[feedback_id]
            evidence = preview_item.get("evidence")
            evidence_count = len(evidence) if isinstance(evidence, list) else 0
            status_before = current_statuses.get(feedback_id) or "open"
            status_after = _closed_feedback_status_for_open_status(status_before)
            action_taken = _feedback_closure_action_taken(
                run_id=run_id,
                feedback_id=feedback_id,
                evidence_count=evidence_count,
                backup_dir_name=backup_dir_name,
            )
            conn.execute(
                """
                UPDATE feedback
                SET status = ?,
                    action_taken = ?,
                    updated_at = ?
                WHERE id = ? AND lower(status) = ?
                """,
                (status_after, action_taken, updated_at, feedback_id, "open"),
            )
            apply_items.append(
                {
                    "feedback_id": feedback_id,
                    "status_before": status_before,
                    "status_after": status_after,
                    "action_taken": action_taken,
                    "updated_at": updated_at,
                    "evidence_count": evidence_count,
                    "mutation": "status,action_taken,updated_at",
                }
            )
        conn.commit()

    report = {
        "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
        "state": "applied",
        "run_dir": str(resolved_run_dir or ""),
        "run_id": run_id,
        "bundle_state": bundle_state,
        "preview_state": preview_state,
        "applied_at": actual_applied_at,
        "confirmation": {
            "required": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
            "provided": True,
            "state": "ok",
        },
        "manual_evals_db": {
            "path": str(resolved_db_path),
            "backup_required": True,
            "integrity_check": "ok",
        },
        "counts": _feedback_closure_apply_counts(
            preview_report,
            target_feedback_rows=len(feedback_ids),
            updated_feedback_rows=len(apply_items),
            skipped_feedback_rows=0,
            backups_written=1,
        ),
        "mutation_boundary": ocr_retry_feedback_closure_apply_mutation_boundary(),
        "backup": backup,
        "apply_items": apply_items,
        "updated_feedback_ids": feedback_ids,
        "skipped_feedback_ids": [],
        "apply_blockers": [],
        "warnings": [],
    }
    if resolved_run_dir is not None and resolved_run_dir.is_dir():
        summary_path = resolved_run_dir / "feedback_closure_apply_summary.json"
        report["output"] = {
            "summary_path": str(summary_path),
            "written": True,
        }
        _write_json(summary_path, report)
    else:
        report["output"] = {
            "summary_path": "",
            "written": False,
        }
    return report
