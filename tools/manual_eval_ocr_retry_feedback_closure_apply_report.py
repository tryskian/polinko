from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from contextlib import closing
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_execution_bundle_report import (
    read_json_object,
)
from tools.manual_eval_ocr_retry_feedback_closure_apply import (
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
    ocr_retry_feedback_closure_apply_mutation_boundary,
)


OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1"
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


def _sqlite_integrity_check(db_path: Path) -> str:
    with closing(_connect_readonly(db_path)) as conn:
        row = conn.execute("PRAGMA integrity_check").fetchone()
    if row is None:
        return "missing"
    return str(row[0] or "")


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


def _feedback_status_normalized(status: object) -> str:
    return str(status or "").strip().casefold()


def _feedback_status_is_open(status: object) -> bool:
    return _feedback_status_normalized(status) == "open"


def _feedback_status_is_closed(status: object) -> bool:
    return _feedback_status_normalized(status) == "closed"


def _feedback_closure_apply_report_blocker(
    code: str,
    detail: str,
) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _feedback_ids_from_apply_summary(
    summary: dict[str, Any],
) -> tuple[list[int], list[str]]:
    raw_ids = summary.get("updated_feedback_ids")
    if not isinstance(raw_ids, list) or not raw_ids:
        raw_ids = [
            item.get("feedback_id")
            for item in summary.get("apply_items", [])
            if isinstance(item, dict)
        ]
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


def _apply_summary_file_path(run_dir: Path | None) -> Path | None:
    if run_dir is None:
        return None
    return run_dir.expanduser() / "feedback_closure_apply_summary.json"


def _status_count(rows_by_id: dict[int, dict[str, Any]], status: str) -> int:
    return sum(
        1
        for row in rows_by_id.values()
        if _feedback_status_normalized(row.get("status")) == status.casefold()
    )


def _path_from_payload(value: object) -> Path | None:
    raw_path = str(value or "").strip()
    if not raw_path:
        return None
    return Path(raw_path).expanduser()


def build_ocr_retry_feedback_closure_apply_report(
    *,
    db_path: Path,
    run_dir: Path | None,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    resolved_db_path = db_path.expanduser()
    resolved_run_dir = run_dir.expanduser() if run_dir else None
    summary_path = _apply_summary_file_path(resolved_run_dir)
    summary: dict[str, Any] | None = None

    if summary_path is None:
        blockers.append(
            _feedback_closure_apply_report_blocker(
                "missing_run_dir",
                "RUN_DIR is required before inspecting feedback-closure apply.",
            )
        )
    elif not summary_path.is_file():
        blockers.append(
            _feedback_closure_apply_report_blocker(
                "missing_apply_summary",
                "feedback_closure_apply_summary.json is required in the run bundle.",
            )
        )
    else:
        summary, parse_errors = read_json_object(summary_path)
        for error in parse_errors:
            blockers.append(
                _feedback_closure_apply_report_blocker(
                    "apply_summary_parse_error",
                    error,
                )
            )
    if summary is None:
        summary = {}

    run_id = str(summary.get("run_id") or "")
    if summary.get("schema_version") and (
        summary.get("schema_version") != OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION
    ):
        blockers.append(
            _feedback_closure_apply_report_blocker(
                "apply_summary_schema_mismatch",
                "feedback closure apply summary schema version is not supported.",
            )
        )
    if resolved_run_dir is not None and run_id and resolved_run_dir.name != run_id:
        blockers.append(
            _feedback_closure_apply_report_blocker(
                "run_id_mismatch",
                "feedback closure apply summary run_id does not match RUN_DIR.",
            )
        )

    feedback_ids, invalid_feedback_ids = _feedback_ids_from_apply_summary(summary)
    if invalid_feedback_ids:
        blockers.append(
            _feedback_closure_apply_report_blocker(
                "invalid_feedback_id",
                "feedback closure apply summary contains non-integer feedback IDs: "
                + ",".join(invalid_feedback_ids),
            )
        )
    if not feedback_ids:
        blockers.append(
            _feedback_closure_apply_report_blocker(
                "missing_feedback_ids",
                "feedback closure apply summary does not name updated feedback IDs.",
            )
        )

    mutation_boundary = summary.get("mutation_boundary")
    if not isinstance(mutation_boundary, dict):
        mutation_boundary = {}
    expected_boundary = ocr_retry_feedback_closure_apply_mutation_boundary()
    for key, expected_value in expected_boundary.items():
        if mutation_boundary.get(key) != expected_value:
            blockers.append(
                _feedback_closure_apply_report_blocker(
                    "mutation_boundary_mismatch",
                    f"mutation boundary {key} is not {expected_value}.",
                )
            )

    backup = summary.get("backup")
    if not isinstance(backup, dict):
        backup = {}
    backup_db_path = _path_from_payload(backup.get("db_path"))
    backup_manifest_path = _path_from_payload(backup.get("manifest_path"))
    backup_integrity = "not_checked"
    backup_rows_by_id: dict[int, dict[str, Any]] = {}
    if backup_db_path is None:
        blockers.append(
            _feedback_closure_apply_report_blocker(
                "missing_backup_db_path",
                "feedback closure apply summary does not name a backup DB path.",
            )
        )
    elif not backup_db_path.is_file():
        blockers.append(
            _feedback_closure_apply_report_blocker(
                "backup_db_not_found",
                "feedback closure apply backup DB was not found.",
            )
        )
    else:
        try:
            backup_integrity = _sqlite_integrity_check(backup_db_path)
        except sqlite3.Error as exc:
            backup_integrity = "error"
            blockers.append(
                _feedback_closure_apply_report_blocker(
                    "backup_integrity_check_failed",
                    f"feedback closure apply backup integrity check failed: {exc}",
                )
            )
        if backup_integrity != "ok":
            blockers.append(
                _feedback_closure_apply_report_blocker(
                    "backup_integrity_not_ok",
                    f"feedback closure apply backup integrity check returned {backup_integrity}.",
                )
            )
        elif feedback_ids:
            backup_rows_by_id = _feedback_rows_by_id(
                db_path=backup_db_path,
                feedback_ids=feedback_ids,
            )
    if backup_manifest_path is None:
        blockers.append(
            _feedback_closure_apply_report_blocker(
                "missing_backup_manifest_path",
                "feedback closure apply summary does not name a backup manifest path.",
            )
        )
    elif not backup_manifest_path.is_file():
        blockers.append(
            _feedback_closure_apply_report_blocker(
                "backup_manifest_not_found",
                "feedback closure apply backup manifest was not found.",
            )
        )

    active_integrity = "not_checked"
    active_rows_by_id: dict[int, dict[str, Any]] = {}
    if not resolved_db_path.is_file():
        blockers.append(
            _feedback_closure_apply_report_blocker(
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
                _feedback_closure_apply_report_blocker(
                    "manual_evals_db_integrity_check_failed",
                    f"manual eval warehouse integrity check failed: {exc}",
                )
            )
        if active_integrity != "ok":
            blockers.append(
                _feedback_closure_apply_report_blocker(
                    "manual_evals_db_integrity_not_ok",
                    f"manual eval warehouse integrity check returned {active_integrity}.",
                )
            )
        elif feedback_ids:
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
        action_taken = _normalize_text(active_row.get("action_taken"))
        if not _feedback_status_is_closed(active_status):
            blockers.append(
                _feedback_closure_apply_report_blocker(
                    "active_feedback_not_closed",
                    f"active feedback {feedback_id} status is {active_status}.",
                )
            )
        if not action_taken:
            blockers.append(
                _feedback_closure_apply_report_blocker(
                    "active_feedback_missing_action_taken",
                    f"active feedback {feedback_id} has no action_taken text.",
                )
            )
        if not _feedback_status_is_open(backup_status):
            blockers.append(
                _feedback_closure_apply_report_blocker(
                    "backup_feedback_not_open",
                    f"backup feedback {feedback_id} status is {backup_status}.",
                )
            )
        feedback_rows.append(
            {
                "feedback_id": feedback_id,
                "active_status": active_status,
                "backup_status": backup_status,
                "active_action_taken_present": bool(action_taken),
                "active_updated_at": _int_value(active_row.get("updated_at")),
                "backup_updated_at": _int_value(backup_row.get("updated_at")),
            }
        )

    state = "error" if blockers else "ok"
    return {
        "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION,
        "state": state,
        "run_dir": str(resolved_run_dir or ""),
        "run_id": run_id,
        "summary_path": str(summary_path or ""),
        "manual_evals_db": {
            "path": str(resolved_db_path),
            "integrity_check": active_integrity,
        },
        "backup": {
            **backup,
            "integrity_check": backup_integrity,
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
            "report_blockers": len(blockers),
        },
        "mutation_boundary": mutation_boundary,
        "feedback_rows": feedback_rows,
        "report_blockers": blockers,
        "warnings": [blocker["detail"] for blocker in blockers],
    }
