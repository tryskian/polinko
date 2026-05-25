from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from typing import Any


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


def _truncate_text(value: object, *, max_chars: int = 180) -> str:
    text = _normalize_text(value)
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "..."


def _fetch_rows(
    conn: sqlite3.Connection,
    sql: str,
    params: Sequence[object] | None = None,
) -> list[dict[str, Any]]:
    return [_row_dict(row) for row in conn.execute(sql, params or []).fetchall()]


def build_ocr_retry_evidence_rows(
    conn: sqlite3.Connection,
    *,
    session_ids: Sequence[str],
) -> dict[str, list[dict[str, Any]]]:
    clean_session_ids = [item for item in dict.fromkeys(session_ids) if item]
    if not clean_session_ids:
        return {}
    placeholders = ",".join("?" for _ in clean_session_ids)
    rows = _fetch_rows(
        conn,
        f"""
        SELECT
          o.run_id,
          o.session_id,
          o.source_name,
          o.mime_type,
          o.source_message_id,
          o.result_message_id,
          o.status,
          o.extracted_text,
          o.created_at,
          ia.source_filename AS image_source_filename,
          ia.resolved_path AS image_resolved_path,
          ia.mime_type AS image_mime_type,
          ia.status AS image_status,
          ia.error AS image_error,
          ia.source_size_bytes AS image_source_size_bytes,
          ia.thumbnail_width AS image_thumbnail_width,
          ia.thumbnail_height AS image_thumbnail_height,
          CASE WHEN ia.thumbnail_data_url IS NOT NULL AND ia.thumbnail_data_url != ''
            THEN 1 ELSE 0
          END AS image_has_thumbnail
        FROM ocr_runs o
        LEFT JOIN image_assets ia ON ia.id = o.image_asset_id
        WHERE o.session_id IN ({placeholders})
        ORDER BY o.session_id, o.created_at DESC, o.id DESC
        """,
        clean_session_ids,
    )
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        session_id = str(row.get("session_id") or "")
        extracted_text = _normalize_text(row.get("extracted_text"))
        evidence_row: dict[str, Any] = {
            "run_id": str(row.get("run_id") or ""),
            "session_id": session_id,
            "source_name": str(row.get("source_name") or ""),
            "mime_type": str(row.get("mime_type") or ""),
            "source_message_id": str(row.get("source_message_id") or ""),
            "result_message_id": str(row.get("result_message_id") or ""),
            "status": str(row.get("status") or ""),
            "created_at": _int_value(row.get("created_at")),
            "extracted_text_chars": len(extracted_text),
            "extracted_text_preview": _truncate_text(extracted_text),
            "image_asset": {
                "source_filename": str(row.get("image_source_filename") or ""),
                "resolved_path": str(row.get("image_resolved_path") or ""),
                "mime_type": str(row.get("image_mime_type") or ""),
                "status": str(row.get("image_status") or "unlinked"),
                "error": str(row.get("image_error") or ""),
                "source_size_bytes": _int_value(row.get("image_source_size_bytes")),
                "thumbnail": {
                    "available": bool(_int_value(row.get("image_has_thumbnail"))),
                    "width": _int_value(row.get("image_thumbnail_width")),
                    "height": _int_value(row.get("image_thumbnail_height")),
                },
            },
        }
        grouped.setdefault(session_id, []).append(evidence_row)
    return grouped
