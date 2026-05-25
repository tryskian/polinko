from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from tools.manual_eval_ocr_retry_execution_bundle_report import (
    read_json_object,
)
from tools.manual_eval_ocr_retry_feedback_closure_apply import (
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
)


OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_feedback_closure_restore.v1"
)
OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN = "ocr-retry-feedback-closure-restore"
DEFAULT_FEEDBACK_CLOSURE_RESTORE_BACKUP_ROOT = Path(".local_archive")


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


def _utc_run_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _feedback_status_normalized(status: object) -> str:
    return str(status or "").strip().casefold()


def _feedback_status_is_open(status: object) -> bool:
    return _feedback_status_normalized(status) == "open"


def _feedback_status_is_closed(status: object) -> bool:
    return _feedback_status_normalized(status) == "closed"


def _sqlite_integrity_check(db_path: Path) -> str:
    with closing(_connect_readonly(db_path)) as conn:
        row = conn.execute("PRAGMA integrity_check").fetchone()
    if row is None:
        return "missing"
    return str(row[0] or "")


def _sqlite_backup_copy(
    *,
    source_db_path: Path,
    destination_db_path: Path,
    allow_existing_destination: bool = False,
) -> None:
    if destination_db_path.exists() and not allow_existing_destination:
        raise FileExistsError(
            f"destination database already exists: {destination_db_path}"
        )
    destination_db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(f"file:{source_db_path}?mode=ro", uri=True)) as source:
        with closing(sqlite3.connect(destination_db_path)) as destination:
            source.backup(destination)


def _feedback_rows_by_id(
    *,
    db_path: Path,
    feedback_ids: Sequence[int],
) -> dict[int, dict[str, Any]]:
    if not feedback_ids:
        return {}
    placeholders = ",".join("?" for _ in feedback_ids)
    with closing(_connect_readonly(db_path)) as conn:
        rows = conn.execute(
            f"SELECT * FROM feedback WHERE id IN ({placeholders})",
            [int(feedback_id) for feedback_id in feedback_ids],
        ).fetchall()
    return {_int_value(row["id"]): _row_dict(row) for row in rows}


def _status_count(rows_by_id: dict[int, dict[str, Any]], status: str) -> int:
    return sum(
        1
        for row in rows_by_id.values()
        if _feedback_status_normalized(row.get("status")) == status.casefold()
    )


def _feedback_closure_restore_blocker(
    code: str,
    detail: str,
) -> dict[str, str]:
    return {"code": code, "detail": detail}


def ocr_retry_feedback_closure_restore_mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "restore_from_verified_apply_backup",
        "feedback_closure": "rollback_to_apply_backup",
        "live_eval_rows": "none",
        "manual_eval_warehouse": "whole_database_restore_from_verified_backup",
    }


def _feedback_ids_from_restore_manifest(
    manifest: dict[str, Any],
) -> tuple[list[int], list[str]]:
    raw_ids = manifest.get("feedback_ids")
    if not isinstance(raw_ids, list):
        raw_ids = []
    feedback_ids: list[int] = []
    invalid_feedback_ids: list[str] = []
    seen: set[int] = set()
    for raw_id in raw_ids:
        raw_text = str(raw_id or "").strip()
        try:
            feedback_id = int(raw_text)
        except ValueError:
            invalid_feedback_ids.append(raw_text or "<empty>")
            continue
        if feedback_id < 1:
            invalid_feedback_ids.append(raw_text)
            continue
        if feedback_id in seen:
            continue
        seen.add(feedback_id)
        feedback_ids.append(feedback_id)
    return feedback_ids, invalid_feedback_ids


def build_ocr_retry_feedback_closure_restore_preview_report(
    *,
    db_path: Path,
    backup_dir: Path | None,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    resolved_db_path = db_path.expanduser()
    resolved_backup_dir = backup_dir.expanduser() if backup_dir else None
    manifest_path: Path | None = None
    backup_db_path: Path | None = None
    manifest: dict[str, Any] = {}

    if resolved_backup_dir is None:
        blockers.append(
            _feedback_closure_restore_blocker(
                "missing_backup_dir",
                "BACKUP_DIR is required before previewing feedback-closure restore.",
            )
        )
    elif not resolved_backup_dir.is_dir():
        blockers.append(
            _feedback_closure_restore_blocker(
                "backup_dir_not_found",
                "feedback closure apply backup directory was not found.",
            )
        )
    else:
        manifest_path = resolved_backup_dir / "manifest.json"
        backup_db_path = resolved_backup_dir / "manual_evals.db"
        if not manifest_path.is_file():
            blockers.append(
                _feedback_closure_restore_blocker(
                    "backup_manifest_not_found",
                    "feedback closure apply backup manifest was not found.",
                )
            )
        else:
            parsed_manifest, parse_errors = read_json_object(manifest_path)
            if parsed_manifest is not None:
                manifest = parsed_manifest
            for error in parse_errors:
                blockers.append(
                    _feedback_closure_restore_blocker(
                        "backup_manifest_parse_error",
                        error,
                    )
                )
        if not backup_db_path.is_file():
            blockers.append(
                _feedback_closure_restore_blocker(
                    "backup_db_not_found",
                    "feedback closure apply backup DB was not found.",
                )
            )

    if manifest.get("schema_version") and (
        manifest.get("schema_version")
        != OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION
    ):
        blockers.append(
            _feedback_closure_restore_blocker(
                "backup_manifest_schema_mismatch",
                "feedback closure apply backup manifest schema version is not supported.",
            )
        )
    recorded_backup_integrity = str(manifest.get("backup_integrity") or "").strip()
    if recorded_backup_integrity and recorded_backup_integrity != "ok":
        blockers.append(
            _feedback_closure_restore_blocker(
                "recorded_backup_integrity_not_ok",
                "feedback closure apply backup manifest recorded integrity as "
                f"{recorded_backup_integrity}.",
            )
        )

    feedback_ids, invalid_feedback_ids = _feedback_ids_from_restore_manifest(manifest)
    if invalid_feedback_ids:
        blockers.append(
            _feedback_closure_restore_blocker(
                "invalid_feedback_id",
                "feedback closure apply backup manifest contains non-integer feedback IDs: "
                + ",".join(invalid_feedback_ids),
            )
        )
    if not feedback_ids:
        blockers.append(
            _feedback_closure_restore_blocker(
                "missing_feedback_ids",
                "feedback closure apply backup manifest does not name feedback IDs.",
            )
        )

    backup_integrity = "not_checked"
    backup_rows_by_id: dict[int, dict[str, Any]] = {}
    if backup_db_path is not None and backup_db_path.is_file():
        try:
            backup_integrity = _sqlite_integrity_check(backup_db_path)
        except sqlite3.Error as exc:
            backup_integrity = "error"
            blockers.append(
                _feedback_closure_restore_blocker(
                    "backup_integrity_check_failed",
                    f"feedback closure apply backup integrity check failed: {exc}",
                )
            )
        if backup_integrity != "ok":
            blockers.append(
                _feedback_closure_restore_blocker(
                    "backup_integrity_not_ok",
                    f"feedback closure apply backup integrity check returned {backup_integrity}.",
                )
            )
        elif feedback_ids:
            backup_rows_by_id = _feedback_rows_by_id(
                db_path=backup_db_path,
                feedback_ids=feedback_ids,
            )

    active_integrity = "not_checked"
    active_rows_by_id: dict[int, dict[str, Any]] = {}
    active_db_ready = False
    if not resolved_db_path.is_file():
        blockers.append(
            _feedback_closure_restore_blocker(
                "manual_evals_db_not_found",
                "manual eval warehouse was not found.",
            )
        )
    else:
        try:
            active_integrity = _sqlite_integrity_check(resolved_db_path)
        except sqlite3.Error as exc:
            active_integrity = "error"
            blockers.append(
                _feedback_closure_restore_blocker(
                    "manual_evals_db_integrity_check_failed",
                    f"manual eval warehouse integrity check failed: {exc}",
                )
            )
        if active_integrity != "ok":
            blockers.append(
                _feedback_closure_restore_blocker(
                    "manual_evals_db_integrity_not_ok",
                    f"manual eval warehouse integrity check returned {active_integrity}.",
                )
            )
        elif feedback_ids:
            active_db_ready = True
            active_rows_by_id = _feedback_rows_by_id(
                db_path=resolved_db_path,
                feedback_ids=feedback_ids,
            )

    feedback_rows: list[dict[str, Any]] = []
    for feedback_id in feedback_ids:
        active_row = active_rows_by_id.get(feedback_id, {})
        backup_row = backup_rows_by_id.get(feedback_id, {})
        active_status = str(active_row.get("status") or "missing")
        backup_status = str(backup_row.get("status") or "missing")
        active_action_taken = _normalize_text(active_row.get("action_taken"))
        if backup_db_path is not None and backup_integrity == "ok":
            if feedback_id not in backup_rows_by_id:
                blockers.append(
                    _feedback_closure_restore_blocker(
                        "backup_feedback_missing",
                        f"backup feedback {feedback_id} is missing.",
                    )
                )
            elif not _feedback_status_is_open(backup_status):
                blockers.append(
                    _feedback_closure_restore_blocker(
                        "backup_feedback_not_open",
                        f"backup feedback {feedback_id} status is {backup_status}.",
                    )
                )
        if active_db_ready:
            if feedback_id not in active_rows_by_id:
                blockers.append(
                    _feedback_closure_restore_blocker(
                        "active_feedback_missing",
                        f"active feedback {feedback_id} is missing.",
                    )
                )
            elif not _feedback_status_is_closed(active_status):
                blockers.append(
                    _feedback_closure_restore_blocker(
                        "active_feedback_not_closed",
                        f"active feedback {feedback_id} status is {active_status}.",
                    )
                )
            elif not active_action_taken:
                blockers.append(
                    _feedback_closure_restore_blocker(
                        "active_feedback_missing_action_taken",
                        f"active feedback {feedback_id} has no action_taken text.",
                    )
                )
            elif "OCR retry feedback-closure apply" not in active_action_taken:
                blockers.append(
                    _feedback_closure_restore_blocker(
                        "active_feedback_action_taken_unrecognized",
                        f"active feedback {feedback_id} action_taken is not a feedback-closure apply marker.",
                    )
                )
        feedback_rows.append(
            {
                "feedback_id": feedback_id,
                "active_status": active_status,
                "backup_status": backup_status,
                "active_action_taken_present": bool(active_action_taken),
                "active_updated_at": _int_value(active_row.get("updated_at")),
                "backup_updated_at": _int_value(backup_row.get("updated_at")),
            }
        )

    state = "error" if blockers else "ok"
    return {
        "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION,
        "state": state,
        "mode": "preview",
        "run_id": str(manifest.get("run_id") or ""),
        "created_at": str(manifest.get("created_at") or ""),
        "manual_evals_db": {
            "path": str(resolved_db_path),
            "integrity_check": active_integrity,
        },
        "source_backup": {
            "dir": str(resolved_backup_dir or ""),
            "db_path": str(backup_db_path or ""),
            "manifest_path": str(manifest_path or ""),
            "schema_version": str(manifest.get("schema_version") or ""),
            "integrity_check": backup_integrity,
            "recorded_integrity_check": recorded_backup_integrity,
        },
        "counts": {
            "target_feedback_rows": len(feedback_ids),
            "active_closed_feedback": _status_count(active_rows_by_id, "closed"),
            "backup_open_feedback": _status_count(backup_rows_by_id, "open"),
            "active_missing_feedback": max(
                0, len(feedback_ids) - len(active_rows_by_id)
            ),
            "backup_missing_feedback": max(
                0, len(feedback_ids) - len(backup_rows_by_id)
            ),
            "restored_feedback_rows": 0,
            "backups_written": 0,
            "restore_blockers": len(blockers),
        },
        "mutation_boundary": ocr_retry_feedback_closure_restore_mutation_boundary(),
        "feedback_ids": feedback_ids,
        "feedback_rows": feedback_rows,
        "restore_blockers": blockers,
        "warnings": [blocker["detail"] for blocker in blockers],
    }


def _backup_manual_evals_db_for_feedback_closure_restore(
    *,
    db_path: Path,
    restore_root: Path,
    restored_at: str,
    source_backup_dir: Path,
    run_id: str,
    feedback_ids: Sequence[int],
) -> dict[str, Any]:
    restore_dir = restore_root / f"manual-evals-feedback-closure-restore-{restored_at}"
    pre_restore_db_path = restore_dir / "manual_evals.pre_restore.db"
    if restore_dir.exists():
        raise FileExistsError(f"restore directory already exists: {restore_dir}")
    restore_dir.mkdir(parents=True)
    _sqlite_backup_copy(
        source_db_path=db_path,
        destination_db_path=pre_restore_db_path,
    )
    pre_restore_integrity = _sqlite_integrity_check(pre_restore_db_path)
    return {
        "written": True,
        "root": str(restore_root),
        "dir": str(restore_dir),
        "db_path": str(pre_restore_db_path),
        "source_backup_dir": str(source_backup_dir),
        "run_id": run_id,
        "feedback_ids": [int(feedback_id) for feedback_id in feedback_ids],
        "integrity_check": pre_restore_integrity,
    }


def write_ocr_retry_feedback_closure_restore(
    *,
    db_path: Path,
    backup_dir: Path | None,
    confirm_token: str,
    restore_root: Path | None = None,
    restored_at: str | None = None,
) -> dict[str, Any]:
    resolved_db_path = db_path.expanduser()
    resolved_backup_dir = backup_dir.expanduser() if backup_dir else None
    resolved_restore_root = (
        restore_root.expanduser()
        if restore_root is not None
        else DEFAULT_FEEDBACK_CLOSURE_RESTORE_BACKUP_ROOT
    )
    preview = build_ocr_retry_feedback_closure_restore_preview_report(
        db_path=resolved_db_path,
        backup_dir=resolved_backup_dir,
    )
    blockers = [
        blocker
        for blocker in preview.get("restore_blockers", [])
        if isinstance(blocker, dict)
    ]
    if confirm_token != OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN:
        blockers.append(
            _feedback_closure_restore_blocker(
                "missing_confirmation",
                "CONFIRM=ocr-retry-feedback-closure-restore is required before feedback closure restore.",
            )
        )
    if blockers:
        return {
            **preview,
            "state": "blocked",
            "mode": "restore",
            "confirmation": {
                "required": OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN,
                "provided": bool(confirm_token),
                "state": "ok"
                if confirm_token == OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN
                else "blocked",
            },
            "pre_restore_backup": {
                "written": False,
                "root": str(resolved_restore_root),
                "dir": "",
                "db_path": "",
            },
            "restore_blockers": blockers,
            "warnings": [blocker["detail"] for blocker in blockers],
        }

    source_backup = preview.get("source_backup")
    if not isinstance(source_backup, dict):
        source_backup = {}
    source_backup_db_path = Path(str(source_backup.get("db_path") or "")).expanduser()
    source_backup_dir = Path(str(source_backup.get("dir") or "")).expanduser()
    feedback_ids = [
        int(feedback_id)
        for feedback_id in preview.get("feedback_ids", [])
        if _int_value(feedback_id) > 0
    ]
    actual_restored_at = restored_at or _utc_run_timestamp()
    run_id = str(preview.get("run_id") or "")
    try:
        pre_restore_backup = _backup_manual_evals_db_for_feedback_closure_restore(
            db_path=resolved_db_path,
            restore_root=resolved_restore_root,
            restored_at=actual_restored_at,
            source_backup_dir=source_backup_dir,
            run_id=run_id,
            feedback_ids=feedback_ids,
        )
    except (OSError, sqlite3.Error) as exc:
        blockers.append(
            _feedback_closure_restore_blocker(
                "pre_restore_backup_failed",
                f"manual eval warehouse pre-restore backup failed: {exc}",
            )
        )
        return {
            **preview,
            "state": "blocked",
            "mode": "restore",
            "confirmation": {
                "required": OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN,
                "provided": True,
                "state": "ok",
            },
            "pre_restore_backup": {
                "written": False,
                "root": str(resolved_restore_root),
                "dir": "",
                "db_path": "",
            },
            "restore_blockers": blockers,
            "warnings": [blocker["detail"] for blocker in blockers],
        }
    if pre_restore_backup.get("integrity_check") != "ok":
        blockers.append(
            _feedback_closure_restore_blocker(
                "pre_restore_backup_integrity_not_ok",
                "manual eval warehouse pre-restore backup integrity check returned "
                f"{pre_restore_backup.get('integrity_check') or 'missing'}.",
            )
        )
        return {
            **preview,
            "state": "blocked",
            "mode": "restore",
            "confirmation": {
                "required": OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN,
                "provided": True,
                "state": "ok",
            },
            "pre_restore_backup": pre_restore_backup,
            "restore_blockers": blockers,
            "warnings": [blocker["detail"] for blocker in blockers],
        }

    try:
        _sqlite_backup_copy(
            source_db_path=source_backup_db_path,
            destination_db_path=resolved_db_path,
            allow_existing_destination=True,
        )
    except (OSError, sqlite3.Error) as exc:
        blockers.append(
            _feedback_closure_restore_blocker(
                "restore_failed",
                f"manual eval warehouse restore failed: {exc}",
            )
        )

    restored_integrity = "not_checked"
    restored_rows_by_id: dict[int, dict[str, Any]] = {}
    if not blockers:
        try:
            restored_integrity = _sqlite_integrity_check(resolved_db_path)
        except sqlite3.Error as exc:
            restored_integrity = "error"
            blockers.append(
                _feedback_closure_restore_blocker(
                    "restored_integrity_check_failed",
                    f"restored manual eval warehouse integrity check failed: {exc}",
                )
            )
        if restored_integrity != "ok":
            blockers.append(
                _feedback_closure_restore_blocker(
                    "restored_integrity_not_ok",
                    f"restored manual eval warehouse integrity check returned {restored_integrity}.",
                )
            )
        elif feedback_ids:
            restored_rows_by_id = _feedback_rows_by_id(
                db_path=resolved_db_path,
                feedback_ids=feedback_ids,
            )
            for feedback_id in feedback_ids:
                restored_status = str(
                    restored_rows_by_id.get(feedback_id, {}).get("status") or "missing"
                )
                if not _feedback_status_is_open(restored_status):
                    blockers.append(
                        _feedback_closure_restore_blocker(
                            "restored_feedback_not_open",
                            f"restored feedback {feedback_id} status is {restored_status}.",
                        )
                    )

    previous_status_by_id = {
        _int_value(row.get("feedback_id")): str(row.get("active_status") or "missing")
        for row in preview.get("feedback_rows", [])
        if isinstance(row, dict)
    }
    restore_items = [
        {
            "feedback_id": feedback_id,
            "status_before": previous_status_by_id.get(feedback_id, "unknown"),
            "status_after": str(
                restored_rows_by_id.get(feedback_id, {}).get("status") or "missing"
            ),
            "mutation": "whole_database_restore_from_verified_backup",
        }
        for feedback_id in feedback_ids
    ]
    preview_counts = preview.get("counts")
    counts = dict(
        cast(dict[str, Any], preview_counts) if isinstance(preview_counts, dict) else {}
    )
    counts.update(
        {
            "restored_feedback_rows": _status_count(restored_rows_by_id, "open"),
            "backups_written": 1,
            "restore_blockers": len(blockers),
        }
    )
    restore_dir = Path(str(pre_restore_backup.get("dir") or ""))
    summary_path = restore_dir / "restore_summary.json"
    report = {
        "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION,
        "state": "error" if blockers else "restored",
        "mode": "restore",
        "run_id": run_id,
        "created_at": str(preview.get("created_at") or ""),
        "restored_at": actual_restored_at,
        "confirmation": {
            "required": OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN,
            "provided": True,
            "state": "ok",
        },
        "manual_evals_db": {
            "path": str(resolved_db_path),
            "integrity_check": restored_integrity,
        },
        "source_backup": source_backup,
        "pre_restore_backup": pre_restore_backup,
        "counts": counts,
        "mutation_boundary": ocr_retry_feedback_closure_restore_mutation_boundary(),
        "feedback_ids": feedback_ids,
        "restore_items": restore_items,
        "restore_blockers": blockers,
        "warnings": [blocker["detail"] for blocker in blockers],
        "output": {
            "summary_path": str(summary_path),
            "written": True,
        },
    }
    _write_json(summary_path, report)
    return report
