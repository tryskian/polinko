from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def int_value(value: object) -> int:
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


def row_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def utc_run_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def feedback_status_normalized(status: object) -> str:
    return str(status or "").strip().casefold()


def feedback_status_is_open(status: object) -> bool:
    return feedback_status_normalized(status) == "open"


def feedback_status_is_closed(status: object) -> bool:
    return feedback_status_normalized(status) == "closed"


def sqlite_integrity_check(db_path: Path) -> str:
    with closing(connect_readonly(db_path)) as conn:
        row = conn.execute("PRAGMA integrity_check").fetchone()
    if row is None:
        return "missing"
    return str(row[0] or "")


def sqlite_backup_copy(
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


def feedback_rows_by_id(
    *,
    db_path: Path,
    feedback_ids: Sequence[int],
) -> dict[int, dict[str, Any]]:
    if not feedback_ids:
        return {}
    placeholders = ",".join("?" for _ in feedback_ids)
    with closing(connect_readonly(db_path)) as conn:
        rows = conn.execute(
            f"SELECT * FROM feedback WHERE id IN ({placeholders})",
            [int(feedback_id) for feedback_id in feedback_ids],
        ).fetchall()
    return {int_value(row["id"]): row_dict(row) for row in rows}


def status_count(rows_by_id: dict[int, dict[str, Any]], status: str) -> int:
    return sum(
        1
        for row in rows_by_id.values()
        if feedback_status_normalized(row.get("status")) == status.casefold()
    )
