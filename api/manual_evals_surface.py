from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

_MANUAL_EVALS_DB_PATH = Path(".local/runtime_dbs/active/manual_evals.db")
_FILE_UPLOAD_PREFIX_RE = re.compile(r"^file[-_][^-_]+[-_](.+)$", re.IGNORECASE)


def _normalize_text(value: Any, *, max_chars: int = 520) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "..."


def _load_metadata(conn: sqlite3.Connection) -> dict[str, str]:
    try:
        rows = conn.execute("SELECT key, value FROM metadata ORDER BY key").fetchall()
    except sqlite3.Error:
        return {}
    metadata: dict[str, str] = {}
    for row in rows:
        key = str(row["key"] or "").strip()
        if not key:
            continue
        metadata[key] = str(row["value"] or "")
    return metadata


def _safe_count(conn: sqlite3.Connection, table_name: str) -> int:
    try:
        row = conn.execute(f"SELECT COUNT(*) AS c FROM {table_name}").fetchone()
    except sqlite3.Error:
        return 0
    return int(row["c"] or 0) if row is not None else 0


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    try:
        rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    except sqlite3.Error:
        return set()
    return {str(row["name"]) for row in rows}


def _column_or_default(
    columns: set[str],
    column_name: str,
    *,
    table_alias: str | None = None,
    default_sql: str = "''",
) -> str:
    if column_name in columns:
        prefix = f"{table_alias}." if table_alias else ""
        return f"{prefix}{column_name} AS {column_name}"
    return f"{default_sql} AS {column_name}"


def _load_sessions(conn: sqlite3.Connection, *, max_sessions: int) -> list[dict[str, Any]]:
    session_columns = _table_columns(conn, "sessions")
    try:
        rows = conn.execute(
            f"""
            SELECT
              session_id,
              {_column_or_default(session_columns, "era", default_sql="'current'")},
              {_column_or_default(session_columns, "source_label", default_sql="'current'")},
              {_column_or_default(session_columns, "source_session_id", default_sql="session_id")},
              title,
              status,
              created_at,
              updated_at,
              deprecated_at,
              message_count,
              feedback_count,
              checkpoint_count,
              ocr_runs_count,
              last_feedback_at,
              last_checkpoint_at,
              last_ocr_at
            FROM sessions
            ORDER BY updated_at DESC, created_at DESC
            LIMIT ?
            """,
            (max_sessions,),
        ).fetchall()
    except sqlite3.Error:
        return []

    sessions: list[dict[str, Any]] = []
    for row in rows:
        sessions.append(
            {
                "session_id": str(row["session_id"] or ""),
                "era": str(row["era"] or "current"),
                "source_label": str(row["source_label"] or ""),
                "source_session_id": str(row["source_session_id"] or row["session_id"] or ""),
                "title": str(row["title"] or ""),
                "status": str(row["status"] or ""),
                "created_at": int(row["created_at"] or 0),
                "updated_at": int(row["updated_at"] or 0),
                "deprecated_at": int(row["deprecated_at"]) if row["deprecated_at"] is not None else None,
                "message_count": int(row["message_count"] or 0),
                "feedback_count": int(row["feedback_count"] or 0),
                "checkpoint_count": int(row["checkpoint_count"] or 0),
                "ocr_runs_count": int(row["ocr_runs_count"] or 0),
                "last_feedback_at": (
                    int(row["last_feedback_at"]) if row["last_feedback_at"] is not None else None
                ),
                "last_checkpoint_at": (
                    int(row["last_checkpoint_at"]) if row["last_checkpoint_at"] is not None else None
                ),
                "last_ocr_at": int(row["last_ocr_at"]) if row["last_ocr_at"] is not None else None,
            }
        )
    return sessions


def _load_runs(conn: sqlite3.Connection, *, max_runs: int) -> list[dict[str, Any]]:
    run_columns = _table_columns(conn, "ocr_runs")
    try:
        rows = conn.execute(
            f"""
            SELECT
              r.id,
              r.run_id,
              {_column_or_default(run_columns, "source_run_id", table_alias="r", default_sql="r.run_id")},
              {_column_or_default(run_columns, "era", table_alias="r", default_sql="'current'")},
              {_column_or_default(run_columns, "source_label", table_alias="r", default_sql="'current'")},
              {_column_or_default(run_columns, "source_session_id", table_alias="r", default_sql="r.session_id")},
              r.session_id,
              r.source_name,
              r.mime_type,
              r.status,
              r.extracted_text,
              r.created_at,
              ia.id AS image_asset_id,
              ia.source_filename,
              ia.resolved_path,
              ia.thumbnail_data_url,
              ia.thumbnail_width,
              ia.thumbnail_height,
              ia.status AS image_status,
              ia.error AS image_error,
              COALESCE(fb.feedback_count, 0) AS feedback_count,
              COALESCE(fb.pass_count, 0) AS feedback_pass_count,
              COALESCE(fb.fail_count, 0) AS feedback_fail_count,
              fb.last_feedback_at,
              COALESCE(cp.checkpoint_count, 0) AS checkpoint_count,
              cp.last_checkpoint_at
            FROM ocr_runs r
            LEFT JOIN image_assets ia ON ia.id = r.image_asset_id
            LEFT JOIN (
              SELECT
                session_id,
                COUNT(*) AS feedback_count,
                SUM(CASE WHEN lower(outcome) = 'pass' THEN 1 ELSE 0 END) AS pass_count,
                SUM(CASE WHEN lower(outcome) = 'fail' THEN 1 ELSE 0 END) AS fail_count,
                MAX(updated_at) AS last_feedback_at
              FROM feedback
              GROUP BY session_id
            ) fb ON fb.session_id = r.session_id
            LEFT JOIN (
              SELECT
                session_id,
                COUNT(*) AS checkpoint_count,
                MAX(created_at) AS last_checkpoint_at
              FROM checkpoints
              GROUP BY session_id
            ) cp ON cp.session_id = r.session_id
            ORDER BY r.created_at DESC, r.id DESC
            LIMIT ?
            """,
            (max_runs,),
        ).fetchall()
    except sqlite3.Error:
        return []

    runs: list[dict[str, Any]] = []
    for row in rows:
        source_filename = str(row["source_filename"] or "")
        display_filename = source_filename
        match = _FILE_UPLOAD_PREFIX_RE.match(display_filename)
        if match:
            display_filename = match.group(1).strip()
        if not display_filename:
            display_filename = Path(str(row["source_name"] or "")).name
        runs.append(
            {
                "id": int(row["id"] or 0),
                "run_id": str(row["run_id"] or ""),
                "source_run_id": str(row["source_run_id"] or row["run_id"] or ""),
                "era": str(row["era"] or "current"),
                "source_label": str(row["source_label"] or ""),
                "session_id": str(row["session_id"] or ""),
                "source_session_id": str(row["source_session_id"] or row["session_id"] or ""),
                "source_name": str(row["source_name"] or ""),
                "mime_type": str(row["mime_type"] or ""),
                "status": str(row["status"] or ""),
                "created_at": int(row["created_at"] or 0),
                "observed_text": _normalize_text(row["extracted_text"], max_chars=700),
                "observed_text_preview": _normalize_text(row["extracted_text"], max_chars=220),
                "image": {
                    "image_asset_id": int(row["image_asset_id"] or 0) if row["image_asset_id"] is not None else None,
                    "source_filename": source_filename,
                    "display_filename": display_filename,
                    "resolved_path": str(row["resolved_path"] or ""),
                    "thumbnail_data_url": str(row["thumbnail_data_url"] or ""),
                    "thumbnail_width": int(row["thumbnail_width"] or 0) if row["thumbnail_width"] is not None else None,
                    "thumbnail_height": int(row["thumbnail_height"] or 0) if row["thumbnail_height"] is not None else None,
                    "status": str(row["image_status"] or ""),
                    "error": str(row["image_error"] or ""),
                },
                "session_eval": {
                    "feedback_count": int(row["feedback_count"] or 0),
                    "feedback_pass_count": int(row["feedback_pass_count"] or 0),
                    "feedback_fail_count": int(row["feedback_fail_count"] or 0),
                    "last_feedback_at": (
                        int(row["last_feedback_at"]) if row["last_feedback_at"] is not None else None
                    ),
                    "checkpoint_count": int(row["checkpoint_count"] or 0),
                    "last_checkpoint_at": (
                        int(row["last_checkpoint_at"]) if row["last_checkpoint_at"] is not None else None
                    ),
                },
            }
        )
    return runs


def build_manual_evals_surface_payload(
    *,
    db_path: Path | None = None,
    max_runs: int = 200,
    max_sessions: int = 80,
) -> dict[str, Any]:
    target_db = db_path if db_path is not None else _MANUAL_EVALS_DB_PATH
    if not target_db.is_file():
        return {
            "available": False,
            "db_path": str(target_db),
            "updated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary": {
                "sessions": 0,
                "feedback": 0,
                "checkpoints": 0,
                "ocr_runs": 0,
                "image_assets": 0,
                "thumbnails_ready": 0,
            },
            "sessions": [],
            "runs": [],
            "metadata": {},
        }

    try:
        conn = sqlite3.connect(f"file:{target_db}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        return {
            "available": False,
            "db_path": str(target_db),
            "error": f"db_open_error: {exc}",
            "updated_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary": {
                "sessions": 0,
                "feedback": 0,
                "checkpoints": 0,
                "ocr_runs": 0,
                "image_assets": 0,
                "thumbnails_ready": 0,
            },
            "sessions": [],
            "runs": [],
            "metadata": {},
        }

    conn.row_factory = sqlite3.Row
    metadata = _load_metadata(conn)
    sessions = _load_sessions(conn, max_sessions=max(1, min(max_sessions, 300)))
    runs = _load_runs(conn, max_runs=max(1, min(max_runs, 800)))

    summary = {
        "sessions": _safe_count(conn, "sessions"),
        "feedback": _safe_count(conn, "feedback"),
        "checkpoints": _safe_count(conn, "checkpoints"),
        "ocr_runs": _safe_count(conn, "ocr_runs"),
        "image_assets": _safe_count(conn, "image_assets"),
        "thumbnails_ready": 0,
    }
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM image_assets WHERE status = 'thumbnail_ready'"
        ).fetchone()
        summary["thumbnails_ready"] = int(row["c"] or 0) if row is not None else 0
    except sqlite3.Error:
        summary["thumbnails_ready"] = 0

    conn.close()

    updated_at = metadata.get("generated_at_utc")
    if not updated_at:
        updated_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "available": True,
        "db_path": str(target_db),
        "updated_at": updated_at,
        "summary": summary,
        "sessions": sessions,
        "runs": runs,
        "metadata": metadata,
    }
