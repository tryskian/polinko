from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

from polinko.api.manual_eval_contracts import SOURCE_FIRST_SCHEMA_VERSION

_MANUAL_EVALS_DB_PATH = Path(".local/runtime_dbs/active/manual_evals.db")
_FILE_UPLOAD_PREFIX_RE = re.compile(r"^file[-_][^-_]+[-_](.+)$", re.IGNORECASE)


def empty_source_first_payload() -> dict[str, Any]:
    return {
        "schema_version": SOURCE_FIRST_SCHEMA_VERSION,
        "contract": {
            "chain": [
                "source_artifact",
                "row_or_case_judgment",
                "lane_summary",
            ],
            "summary_unit": "lane_summary",
            "promotion_gate": "repeated_lane_signal",
        },
        "source_artifacts": {
            "history_sources": 0,
            "sessions": 0,
            "feedback": 0,
            "checkpoints": 0,
            "ocr_runs": 0,
            "image_assets": 0,
        },
        "judgments": {
            "manual_feedback": {
                "total": 0,
                "pass": 0,
                "fail": 0,
                "other": 0,
                "open": 0,
                "closed": 0,
            },
            "checkpoints": {
                "total": 0,
                "covered_rows": 0,
                "pass": 0,
                "fail": 0,
                "other": 0,
            },
        },
        "lane_summaries": [],
        "exclusions": [],
        "evidence_rows": [],
    }


def _normalize_text(value: Any, *, max_chars: int = 520) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "..."


def _parse_json_list(value: Any) -> list[str]:
    try:
        parsed = json.loads(str(value or "[]"))
    except (TypeError, ValueError):
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item).strip() for item in parsed if str(item).strip()]


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


def _safe_query_int(conn: sqlite3.Connection, query: str) -> int:
    try:
        row = conn.execute(query).fetchone()
    except sqlite3.Error:
        return 0
    return _safe_int(row["c"]) if row is not None else 0


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


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


def _outcome_key(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized == "pass":
        return "pass"
    if normalized == "fail":
        return "fail"
    return "other"


def _source_count_from_metadata(metadata: dict[str, str]) -> int:
    source_count = _safe_int(metadata.get("source_count"))
    if source_count:
        return source_count
    raw_counts = metadata.get("source_counts_json", "")
    if not raw_counts:
        return 0
    try:
        parsed = json.loads(raw_counts)
    except (TypeError, ValueError):
        return 0
    if isinstance(parsed, dict):
        return len(parsed)
    if isinstance(parsed, list):
        return len(parsed)
    return 0


def _source_artifact_counts(
    *,
    metadata: dict[str, str],
    summary: dict[str, int],
) -> dict[str, int]:
    return {
        "history_sources": _source_count_from_metadata(metadata),
        "sessions": int(summary["sessions"]),
        "feedback": int(summary["feedback"]),
        "checkpoints": int(summary["checkpoints"]),
        "ocr_runs": int(summary["ocr_runs"]),
        "image_assets": int(summary["image_assets"]),
    }


def _load_manual_feedback_judgment_counts(conn: sqlite3.Connection) -> dict[str, int]:
    counts = {
        "total": 0,
        "pass": 0,
        "fail": 0,
        "other": 0,
        "open": 0,
        "closed": 0,
    }
    try:
        rows = conn.execute(
            """
            SELECT
              lower(outcome) AS outcome,
              lower(status) AS status,
              COUNT(*) AS c
            FROM feedback
            GROUP BY lower(outcome), lower(status)
            """
        ).fetchall()
    except sqlite3.Error:
        return counts

    for row in rows:
        count = _safe_int(row["c"])
        counts["total"] += count
        counts[_outcome_key(row["outcome"])] += count
        status = str(row["status"] or "").strip().lower()
        if status == "open":
            counts["open"] += count
        elif status in {"closed", "logged"}:
            counts["closed"] += count
    return counts


def _load_checkpoint_judgment_counts(conn: sqlite3.Connection) -> dict[str, int]:
    try:
        row = conn.execute(
            """
            SELECT
              COUNT(*) AS total,
              COALESCE(SUM(total_count), 0) AS covered_rows,
              COALESCE(SUM(pass_count), 0) AS pass,
              COALESCE(SUM(fail_count), 0) AS fail,
              COALESCE(SUM(other_count), 0) AS other
            FROM checkpoints
            """
        ).fetchone()
    except sqlite3.Error:
        row = None

    return {
        "total": _safe_int(row["total"]) if row else 0,
        "covered_rows": _safe_int(row["covered_rows"]) if row else 0,
        "pass": _safe_int(row["pass"]) if row else 0,
        "fail": _safe_int(row["fail"]) if row else 0,
        "other": _safe_int(row["other"]) if row else 0,
    }


def _load_source_labels(conn: sqlite3.Connection, table_name: str) -> list[str]:
    if table_name not in {"feedback", "ocr_runs"}:
        return []
    try:
        rows = conn.execute(
            f"""
            SELECT source_label, COUNT(*) AS c
            FROM {table_name}
            GROUP BY source_label
            ORDER BY source_label
            """
        ).fetchall()
    except sqlite3.Error:
        return []
    return [
        str(row["source_label"] or "")
        for row in rows
        if str(row["source_label"] or "").strip()
    ]


def _source_first_lane_summaries(
    conn: sqlite3.Connection,
    *,
    manual_feedback: dict[str, int],
    summary: dict[str, int],
) -> list[dict[str, Any]]:
    return [
        {
            "lane": "manual_feedback",
            "summary_unit": "lane_summary",
            "rows": manual_feedback["total"],
            "pass": manual_feedback["pass"],
            "fail": manual_feedback["fail"],
            "other": manual_feedback["other"],
            "source_labels": _load_source_labels(conn, "feedback"),
        },
        {
            "lane": "ocr_cases",
            "summary_unit": "lane_summary",
            "rows": int(summary["ocr_runs"]),
            "source_labels": _load_source_labels(conn, "ocr_runs"),
        },
    ]


def _source_first_exclusion(
    *,
    key: str,
    label: str,
    count: int,
    reason: str,
    promotion_effect: str,
) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "count": max(0, int(count)),
        "reason": reason,
        "promotion_effect": promotion_effect,
    }


def _load_source_first_exclusions(
    conn: sqlite3.Connection,
    *,
    manual_feedback: dict[str, int],
) -> list[dict[str, Any]]:
    ocr_without_manual_feedback = _safe_query_int(
        conn,
        """
        SELECT COUNT(*) AS c
        FROM ocr_runs r
        LEFT JOIN feedback f
          ON f.session_id = r.session_id
         AND f.message_id = r.result_message_id
        WHERE r.result_message_id IS NULL
           OR f.id IS NULL
        """,
    )
    sessions_without_judgment = _safe_query_int(
        conn,
        """
        SELECT COUNT(*) AS c
        FROM sessions s
        LEFT JOIN (
          SELECT session_id, COUNT(*) AS c
          FROM feedback
          GROUP BY session_id
        ) fb ON fb.session_id = s.session_id
        LEFT JOIN (
          SELECT session_id, COUNT(*) AS c
          FROM checkpoints
          GROUP BY session_id
        ) cp ON cp.session_id = s.session_id
        WHERE COALESCE(fb.c, 0) = 0
          AND COALESCE(cp.c, 0) = 0
        """,
    )
    checkpoint_rows_without_feedback = _safe_query_int(
        conn,
        """
        SELECT COALESCE(SUM(c.total_count), 0) AS c
        FROM checkpoints c
        LEFT JOIN (
          SELECT session_id, COUNT(*) AS c
          FROM feedback
          GROUP BY session_id
        ) fb ON fb.session_id = c.session_id
        WHERE COALESCE(fb.c, 0) = 0
        """,
    )

    return [
        _source_first_exclusion(
            key="ocr_without_manual_feedback",
            label="OCR run without manual feedback",
            count=ocr_without_manual_feedback,
            reason="source artifact exists without a row-level manual judgment",
            promotion_effect="not promotion evidence until a row/case judgment exists",
        ),
        _source_first_exclusion(
            key="session_without_judgment",
            label="Session without judgment",
            count=sessions_without_judgment,
            reason="chat workbench context exists without feedback or checkpoint coverage",
            promotion_effect="usable as source context, not as a lane summary input",
        ),
        _source_first_exclusion(
            key="open_manual_feedback",
            label="Open manual feedback",
            count=manual_feedback["open"],
            reason="manual judgment is still open",
            promotion_effect="not promotion evidence until closed or logged",
        ),
        _source_first_exclusion(
            key="checkpoint_without_feedback_rows",
            label="Checkpoint rows without feedback",
            count=checkpoint_rows_without_feedback,
            reason="aggregate checkpoint coverage lacks row-level manual feedback",
            promotion_effect="kept as context, not row evidence",
        ),
    ]


def _load_source_first_evidence_rows(
    conn: sqlite3.Connection,
    *,
    max_rows: int,
) -> list[dict[str, Any]]:
    try:
        rows = conn.execute(
            """
            WITH linked_ocr AS (
              SELECT *
              FROM (
                SELECT
                  r.*,
                  ROW_NUMBER() OVER (
                    PARTITION BY r.session_id, r.result_message_id
                    ORDER BY r.created_at DESC, r.id DESC
                  ) AS rn
                FROM ocr_runs r
                WHERE r.result_message_id IS NOT NULL
              )
              WHERE rn = 1
            )
            SELECT
              f.id,
              f.era,
              f.source_label,
              f.source_history_db,
              f.source_session_id,
              f.session_id,
              f.message_id,
              f.outcome,
              f.tags_json,
              f.note,
              f.recommended_action,
              f.action_taken,
              f.status,
              f.created_at,
              f.updated_at,
              s.title,
              linked_ocr.run_id,
              linked_ocr.source_run_id,
              linked_ocr.source_message_id,
              linked_ocr.result_message_id,
              linked_ocr.source_name,
              linked_ocr.status AS ocr_status,
              linked_ocr.extracted_text
            FROM feedback f
            JOIN sessions s ON s.session_id = f.session_id
            LEFT JOIN linked_ocr
              ON linked_ocr.session_id = f.session_id
             AND linked_ocr.result_message_id = f.message_id
            ORDER BY f.updated_at DESC, f.id DESC
            LIMIT ?
            """,
            (max(1, min(max_rows, 300)),),
        ).fetchall()
    except sqlite3.Error:
        return []

    return [
        {
            "row_kind": "manual_feedback",
            "row_id": f"feedback-{row['id']}",
            "era": str(row["era"] or ""),
            "source_label": str(row["source_label"] or ""),
            "source_artifact": {
                "type": "chat_message",
                "history_db": str(row["source_history_db"] or ""),
                "session_id": str(row["session_id"] or ""),
                "source_session_id": str(row["source_session_id"] or ""),
                "message_id": str(row["message_id"] or ""),
                "title": _normalize_text(row["title"], max_chars=160),
            },
            "judgment": {
                "unit": "row",
                "outcome": str(row["outcome"] or "").strip().lower(),
                "status": str(row["status"] or ""),
                "tags": _parse_json_list(row["tags_json"]),
                "note": _normalize_text(row["note"], max_chars=260),
                "recommended_action": _normalize_text(
                    row["recommended_action"],
                    max_chars=180,
                ),
                "action_taken": _normalize_text(row["action_taken"], max_chars=180),
                "created_at": int(row["created_at"] or 0),
                "updated_at": int(row["updated_at"] or 0),
            },
            "linked_case": {
                "type": "ocr_run",
                "match_type": (
                    "feedback_result_message" if str(row["run_id"] or "") else ""
                ),
                "run_id": str(row["run_id"] or ""),
                "source_run_id": str(row["source_run_id"] or ""),
                "source_message_id": str(row["source_message_id"] or ""),
                "result_message_id": str(row["result_message_id"] or ""),
                "source_name": str(row["source_name"] or ""),
                "status": str(row["ocr_status"] or ""),
                "observed_text_preview": _normalize_text(
                    row["extracted_text"],
                    max_chars=220,
                ),
            },
        }
        for row in rows
    ]


def _load_source_first_payload(
    conn: sqlite3.Connection,
    *,
    metadata: dict[str, str],
    summary: dict[str, int],
    max_rows: int,
) -> dict[str, Any]:
    payload = empty_source_first_payload()
    manual_feedback = _load_manual_feedback_judgment_counts(conn)
    payload["source_artifacts"] = _source_artifact_counts(
        metadata=metadata,
        summary=summary,
    )
    payload["judgments"] = {
        "manual_feedback": manual_feedback,
        "checkpoints": _load_checkpoint_judgment_counts(conn),
    }
    payload["lane_summaries"] = _source_first_lane_summaries(
        conn,
        manual_feedback=manual_feedback,
        summary=summary,
    )
    payload["exclusions"] = _load_source_first_exclusions(
        conn,
        manual_feedback=manual_feedback,
    )
    payload["evidence_rows"] = _load_source_first_evidence_rows(
        conn,
        max_rows=max_rows,
    )
    return payload


def _load_sessions(
    conn: sqlite3.Connection, *, max_sessions: int
) -> list[dict[str, Any]]:
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
                "source_session_id": str(
                    row["source_session_id"] or row["session_id"] or ""
                ),
                "title": str(row["title"] or ""),
                "status": str(row["status"] or ""),
                "created_at": int(row["created_at"] or 0),
                "updated_at": int(row["updated_at"] or 0),
                "deprecated_at": int(row["deprecated_at"])
                if row["deprecated_at"] is not None
                else None,
                "message_count": int(row["message_count"] or 0),
                "feedback_count": int(row["feedback_count"] or 0),
                "checkpoint_count": int(row["checkpoint_count"] or 0),
                "ocr_runs_count": int(row["ocr_runs_count"] or 0),
                "last_feedback_at": (
                    int(row["last_feedback_at"])
                    if row["last_feedback_at"] is not None
                    else None
                ),
                "last_checkpoint_at": (
                    int(row["last_checkpoint_at"])
                    if row["last_checkpoint_at"] is not None
                    else None
                ),
                "last_ocr_at": int(row["last_ocr_at"])
                if row["last_ocr_at"] is not None
                else None,
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
                "source_session_id": str(
                    row["source_session_id"] or row["session_id"] or ""
                ),
                "source_name": str(row["source_name"] or ""),
                "mime_type": str(row["mime_type"] or ""),
                "status": str(row["status"] or ""),
                "created_at": int(row["created_at"] or 0),
                "observed_text": _normalize_text(row["extracted_text"], max_chars=700),
                "observed_text_preview": _normalize_text(
                    row["extracted_text"], max_chars=220
                ),
                "image": {
                    "image_asset_id": int(row["image_asset_id"] or 0)
                    if row["image_asset_id"] is not None
                    else None,
                    "source_filename": source_filename,
                    "display_filename": display_filename,
                    "resolved_path": str(row["resolved_path"] or ""),
                    "thumbnail_data_url": str(row["thumbnail_data_url"] or ""),
                    "thumbnail_width": int(row["thumbnail_width"] or 0)
                    if row["thumbnail_width"] is not None
                    else None,
                    "thumbnail_height": int(row["thumbnail_height"] or 0)
                    if row["thumbnail_height"] is not None
                    else None,
                    "status": str(row["image_status"] or ""),
                    "error": str(row["image_error"] or ""),
                },
                "session_eval": {
                    "feedback_count": int(row["feedback_count"] or 0),
                    "feedback_pass_count": int(row["feedback_pass_count"] or 0),
                    "feedback_fail_count": int(row["feedback_fail_count"] or 0),
                    "last_feedback_at": (
                        int(row["last_feedback_at"])
                        if row["last_feedback_at"] is not None
                        else None
                    ),
                    "checkpoint_count": int(row["checkpoint_count"] or 0),
                    "last_checkpoint_at": (
                        int(row["last_checkpoint_at"])
                        if row["last_checkpoint_at"] is not None
                        else None
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
            "source_first": empty_source_first_payload(),
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
            "source_first": empty_source_first_payload(),
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

    source_first = _load_source_first_payload(
        conn,
        metadata=metadata,
        summary=summary,
        max_rows=max_runs,
    )

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
        "source_first": source_first,
        "metadata": metadata,
    }
