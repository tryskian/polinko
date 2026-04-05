from __future__ import annotations

import argparse
import base64
import io
import json
import mimetypes
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

PILImageModule: Any | None = None
PILUnidentifiedImageError: type[Exception] = Exception
try:
    from PIL import Image as _PILImageModule
    from PIL import UnidentifiedImageError as _PILUnidentifiedImageError

    PILImageModule = _PILImageModule
    PILUnidentifiedImageError = _PILUnidentifiedImageError
except Exception:  # pragma: no cover - optional dependency
    pass

DEFAULT_EXCLUDE_PREFIXES: tuple[str, ...] = (
    "ocr-eval-",
    "ocr-recovery-eval-",
    "style-eval-",
    "hallucination-eval-",
    "response-behaviour-eval-",
    "retrieval-eval-",
    "file-search-eval-",
    "clip-ab-eval-",
    "ocr-stability-",
    "ocr-growth-batch-",
)

DEFAULT_IMAGE_ROOTS: tuple[Path, ...] = (
    Path("docs/peanut/assets/screenshots"),
    Path("docs/peanut/assets/screenshots/ocr_evals_legacy"),
    Path.home() / "Downloads",
    Path.home() / "Library/CloudStorage/Dropbox/Screenshots",
    Path.home() / "Library/CloudStorage/Dropbox/CGPT-DATA-EXPORT/assets",
)

_FILE_UPLOAD_PREFIX_RE = re.compile(r"^file[-_][^-_]+[-_](.+)$", re.IGNORECASE)


def _normalize_prefixes(values: Sequence[str]) -> list[str]:
    normalized: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if not value:
            continue
        if value.endswith("%"):
            value = value[:-1]
        if value and value not in normalized:
            normalized.append(value)
    return normalized


def _exclude_clause(prefixes: Sequence[str], *, alias: str) -> tuple[str, list[str]]:
    normalized = _normalize_prefixes(prefixes)
    if not normalized:
        return "1=1", []
    parts = [f"{alias}.session_id NOT LIKE ?" for _ in normalized]
    params = [f"{prefix}%" for prefix in normalized]
    return " AND ".join(parts), params


def _normalize_image_roots(values: Sequence[str | Path]) -> list[Path]:
    roots: list[Path] = []
    seen: set[Path] = set()
    for raw in values:
        root = Path(raw).expanduser()
        if root in seen:
            continue
        seen.add(root)
        roots.append(root)
    return roots


def _source_filename_candidates(source_name: str) -> list[str]:
    basename = Path(source_name).name.strip()
    if not basename:
        return []
    candidates: list[str] = [basename]
    match = _FILE_UPLOAD_PREFIX_RE.match(basename)
    if match:
        stripped = match.group(1).strip()
        if stripped and stripped not in candidates:
            candidates.append(stripped)
    return candidates


def _build_filename_index(
    *,
    image_roots: Sequence[Path],
    target_filenames: Sequence[str],
) -> dict[str, Path]:
    wanted = {name.casefold() for name in target_filenames if name.strip()}
    if not wanted:
        return {}

    index: dict[str, Path] = {}
    for root in image_roots:
        if not root.is_dir():
            continue
        try:
            for dirpath, _, filenames in os.walk(root):
                for filename in filenames:
                    key = filename.casefold()
                    if key not in wanted or key in index:
                        continue
                    index[key] = Path(dirpath) / filename
                    if len(index) == len(wanted):
                        return index
        except OSError:
            continue
    return index


def _resolve_source_path(source_name: str, filename_index: dict[str, Path]) -> Path | None:
    for candidate in _source_filename_candidates(source_name):
        match = filename_index.get(candidate.casefold())
        if match is not None:
            return match
    return None


def _build_thumbnail(path: Path, *, size: int) -> tuple[bytes, int, int]:
    if PILImageModule is None:  # pragma: no cover - tested via caller branch
        raise RuntimeError("Pillow is not installed.")

    with PILImageModule.open(path) as image:
        # Preserve transparency where available.
        working_image = image.convert("RGBA") if image.mode not in ("RGB", "RGBA") else image.copy()
        resampling_enum = getattr(PILImageModule, "Resampling", None)
        resample = (
            resampling_enum.LANCZOS
            if resampling_enum is not None
            else getattr(PILImageModule, "LANCZOS", 1)
        )
        working_image.thumbnail((size, size), resample=resample)
        width, height = working_image.size
        buffer = io.BytesIO()
        working_image.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue(), width, height


def _read_sessions(
    conn: sqlite3.Connection,
    *,
    exclude_prefixes: Sequence[str],
) -> list[sqlite3.Row]:
    where_sql, params = _exclude_clause(exclude_prefixes, alias="c")
    query = f"""
    SELECT
      c.session_id,
      c.title,
      c.status,
      c.created_at,
      c.updated_at,
      c.deprecated_at,
      COALESCE(msg.message_count, 0) AS message_count,
      COALESCE(fb.feedback_count, 0) AS feedback_count,
      COALESCE(cp.checkpoint_count, 0) AS checkpoint_count,
      COALESCE(ocr.ocr_runs_count, 0) AS ocr_runs_count,
      fb.last_feedback_at,
      cp.last_checkpoint_at,
      ocr.last_ocr_at
    FROM chats c
    LEFT JOIN (
      SELECT session_id, COUNT(*) AS message_count
      FROM chat_messages
      WHERE role IN ('user', 'assistant')
      GROUP BY session_id
    ) msg ON msg.session_id = c.session_id
    LEFT JOIN (
      SELECT session_id, COUNT(*) AS feedback_count, MAX(updated_at) AS last_feedback_at
      FROM message_feedback
      GROUP BY session_id
    ) fb ON fb.session_id = c.session_id
    LEFT JOIN (
      SELECT session_id, COUNT(*) AS checkpoint_count, MAX(created_at) AS last_checkpoint_at
      FROM eval_checkpoints
      GROUP BY session_id
    ) cp ON cp.session_id = c.session_id
    LEFT JOIN (
      SELECT session_id, COUNT(*) AS ocr_runs_count, MAX(created_at) AS last_ocr_at
      FROM ocr_runs
      GROUP BY session_id
    ) ocr ON ocr.session_id = c.session_id
    WHERE {where_sql}
      AND (
        COALESCE(fb.feedback_count, 0) > 0
        OR COALESCE(cp.checkpoint_count, 0) > 0
        OR COALESCE(ocr.ocr_runs_count, 0) > 0
      )
    ORDER BY c.updated_at DESC, c.created_at DESC;
    """
    return conn.execute(query, params).fetchall()


def _read_feedback(
    conn: sqlite3.Connection,
    *,
    exclude_prefixes: Sequence[str],
) -> list[sqlite3.Row]:
    where_sql, params = _exclude_clause(exclude_prefixes, alias="mf")
    query = f"""
    SELECT
      mf.id,
      mf.session_id,
      mf.message_id,
      mf.outcome,
      mf.tags_json,
      mf.note,
      mf.recommended_action,
      mf.action_taken,
      mf.status,
      mf.created_at,
      mf.updated_at
    FROM message_feedback mf
    JOIN chats c ON c.session_id = mf.session_id
    WHERE {where_sql}
    ORDER BY mf.updated_at ASC, mf.id ASC;
    """
    return conn.execute(query, params).fetchall()


def _read_checkpoints(
    conn: sqlite3.Connection,
    *,
    exclude_prefixes: Sequence[str],
) -> list[sqlite3.Row]:
    where_sql, params = _exclude_clause(exclude_prefixes, alias="ec")
    query = f"""
    SELECT
      ec.id,
      ec.checkpoint_id,
      ec.session_id,
      ec.total_count,
      ec.pass_count,
      ec.fail_count,
      ec.other_count,
      ec.created_at
    FROM eval_checkpoints ec
    JOIN chats c ON c.session_id = ec.session_id
    WHERE {where_sql}
    ORDER BY ec.created_at ASC, ec.id ASC;
    """
    return conn.execute(query, params).fetchall()


def _read_ocr_runs(
    conn: sqlite3.Connection,
    *,
    exclude_prefixes: Sequence[str],
) -> list[sqlite3.Row]:
    where_sql, params = _exclude_clause(exclude_prefixes, alias="o")
    query = f"""
    SELECT
      o.id,
      o.run_id,
      o.session_id,
      o.source_name,
      o.mime_type,
      o.source_message_id,
      o.result_message_id,
      o.status,
      o.extracted_text,
      o.created_at
    FROM ocr_runs o
    JOIN chats c ON c.session_id = o.session_id
    WHERE {where_sql}
    ORDER BY o.created_at ASC, o.id ASC;
    """
    return conn.execute(query, params).fetchall()


def _init_output_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE metadata (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );

        CREATE TABLE sessions (
          session_id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          status TEXT NOT NULL,
          created_at INTEGER NOT NULL,
          updated_at INTEGER NOT NULL,
          deprecated_at INTEGER,
          message_count INTEGER NOT NULL,
          feedback_count INTEGER NOT NULL,
          checkpoint_count INTEGER NOT NULL,
          ocr_runs_count INTEGER NOT NULL,
          last_feedback_at INTEGER,
          last_checkpoint_at INTEGER,
          last_ocr_at INTEGER
        );

        CREATE TABLE feedback (
          id INTEGER PRIMARY KEY,
          session_id TEXT NOT NULL,
          message_id TEXT NOT NULL,
          outcome TEXT NOT NULL,
          tags_json TEXT NOT NULL,
          note TEXT,
          recommended_action TEXT,
          action_taken TEXT,
          status TEXT NOT NULL,
          created_at INTEGER NOT NULL,
          updated_at INTEGER NOT NULL,
          FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
        );

        CREATE TABLE checkpoints (
          id INTEGER PRIMARY KEY,
          checkpoint_id TEXT UNIQUE NOT NULL,
          session_id TEXT NOT NULL,
          total_count INTEGER NOT NULL,
          pass_count INTEGER NOT NULL,
          fail_count INTEGER NOT NULL,
          other_count INTEGER NOT NULL,
          created_at INTEGER NOT NULL,
          FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
        );

        CREATE TABLE image_assets (
          id INTEGER PRIMARY KEY,
          source_name TEXT NOT NULL UNIQUE,
          source_filename TEXT,
          resolved_path TEXT,
          mime_type TEXT,
          thumbnail_png BLOB,
          thumbnail_data_url TEXT,
          thumbnail_width INTEGER,
          thumbnail_height INTEGER,
          source_size_bytes INTEGER,
          source_mtime_unix INTEGER,
          status TEXT NOT NULL,
          error TEXT
        );

        CREATE TABLE ocr_runs (
          id INTEGER PRIMARY KEY,
          run_id TEXT UNIQUE NOT NULL,
          session_id TEXT NOT NULL,
          source_name TEXT,
          mime_type TEXT,
          source_message_id TEXT,
          result_message_id TEXT,
          status TEXT NOT NULL,
          extracted_text TEXT NOT NULL,
          created_at INTEGER NOT NULL,
          image_asset_id INTEGER,
          FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
          FOREIGN KEY(image_asset_id) REFERENCES image_assets(id) ON DELETE SET NULL
        );

        CREATE INDEX idx_feedback_session_updated
          ON feedback(session_id, updated_at DESC, id DESC);
        CREATE INDEX idx_checkpoints_session_created
          ON checkpoints(session_id, created_at DESC, id DESC);
        CREATE INDEX idx_ocr_runs_session_created
          ON ocr_runs(session_id, created_at DESC, id DESC);
        CREATE INDEX idx_image_assets_status
          ON image_assets(status);
        """
    )


def _prepare_image_assets(
    *,
    ocr_runs: Sequence[sqlite3.Row],
    image_roots: Sequence[Path],
    thumbnail_size: int,
    enable_thumbnails: bool,
) -> tuple[list[tuple[Any, ...]], dict[str, int], dict[str, int]]:
    source_names = sorted({str(row["source_name"] or "").strip() for row in ocr_runs if str(row["source_name"] or "").strip()})
    if not source_names:
        return [], {}, {
            "image_assets": 0,
            "image_resolved": 0,
            "image_missing": 0,
            "thumbnails_ready": 0,
            "thumbnails_skipped": 0,
            "thumbnails_error": 0,
        }

    target_filenames: list[str] = []
    for source_name in source_names:
        target_filenames.extend(_source_filename_candidates(source_name))
    filename_index = _build_filename_index(
        image_roots=image_roots,
        target_filenames=target_filenames,
    )

    rows: list[tuple[Any, ...]] = []
    asset_id_by_source: dict[str, int] = {}
    stats = {
        "image_assets": 0,
        "image_resolved": 0,
        "image_missing": 0,
        "thumbnails_ready": 0,
        "thumbnails_skipped": 0,
        "thumbnails_error": 0,
    }

    for index, source_name in enumerate(source_names, start=1):
        source_filename = Path(source_name).name.strip() or None
        resolved_path = _resolve_source_path(source_name, filename_index)
        resolved_path_text = str(resolved_path) if resolved_path is not None else None
        mime_type = (
            mimetypes.guess_type(resolved_path_text or source_filename or "", strict=False)[0]
            if (resolved_path_text or source_filename)
            else None
        )
        source_size_bytes: int | None = None
        source_mtime_unix: int | None = None
        thumbnail_png: bytes | None = None
        thumbnail_data_url: str | None = None
        thumb_width: int | None = None
        thumb_height: int | None = None
        status = "missing"
        error_text: str | None = None

        if resolved_path is None:
            stats["image_missing"] += 1
        else:
            stats["image_resolved"] += 1
            try:
                file_stat = resolved_path.stat()
                source_size_bytes = int(file_stat.st_size)
                source_mtime_unix = int(file_stat.st_mtime)
            except OSError as exc:
                error_text = f"stat_failed: {exc}"

            if not enable_thumbnails:
                status = "resolved"
                stats["thumbnails_skipped"] += 1
            elif PILImageModule is None:
                status = "resolved_no_pillow"
                stats["thumbnails_skipped"] += 1
            else:
                try:
                    thumbnail_png, thumb_width, thumb_height = _build_thumbnail(
                        resolved_path,
                        size=thumbnail_size,
                    )
                    thumbnail_data_url = (
                        "data:image/png;base64,"
                        + base64.b64encode(thumbnail_png).decode("ascii")
                    )
                    status = "thumbnail_ready"
                    stats["thumbnails_ready"] += 1
                except (OSError, PILUnidentifiedImageError, RuntimeError) as exc:
                    status = "thumbnail_error"
                    error_text = str(exc)
                    stats["thumbnails_error"] += 1

        rows.append(
            (
                index,
                source_name,
                source_filename,
                resolved_path_text,
                mime_type,
                thumbnail_png,
                thumbnail_data_url,
                thumb_width,
                thumb_height,
                source_size_bytes,
                source_mtime_unix,
                status,
                error_text,
            )
        )
        asset_id_by_source[source_name] = index

    stats["image_assets"] = len(rows)
    return rows, asset_id_by_source, stats


def build_manual_evals_db(
    *,
    history_db: Path,
    output_db: Path,
    exclude_prefixes: Sequence[str] = DEFAULT_EXCLUDE_PREFIXES,
    image_roots: Sequence[Path] = DEFAULT_IMAGE_ROOTS,
    thumbnail_size: int = 240,
    include_thumbnails: bool = True,
) -> dict[str, int]:
    if not history_db.is_file():
        raise FileNotFoundError(f"History DB not found: {history_db}")

    history_conn = sqlite3.connect(f"file:{history_db}?mode=ro", uri=True)
    history_conn.row_factory = sqlite3.Row
    sessions = _read_sessions(history_conn, exclude_prefixes=exclude_prefixes)
    feedback = _read_feedback(history_conn, exclude_prefixes=exclude_prefixes)
    checkpoints = _read_checkpoints(history_conn, exclude_prefixes=exclude_prefixes)
    ocr_runs = _read_ocr_runs(history_conn, exclude_prefixes=exclude_prefixes)
    history_conn.close()

    output_db.parent.mkdir(parents=True, exist_ok=True)
    if output_db.exists():
        output_db.unlink()

    output_conn = sqlite3.connect(output_db)
    _init_output_db(output_conn)

    scan_roots = [root for root in _normalize_image_roots(image_roots) if root.is_dir()]
    image_asset_rows, image_asset_ids, image_stats = _prepare_image_assets(
        ocr_runs=ocr_runs,
        image_roots=scan_roots,
        thumbnail_size=max(24, int(thumbnail_size)),
        enable_thumbnails=include_thumbnails,
    )

    output_conn.executemany(
        """
        INSERT INTO sessions (
          session_id, title, status, created_at, updated_at, deprecated_at,
          message_count, feedback_count, checkpoint_count, ocr_runs_count,
          last_feedback_at, last_checkpoint_at, last_ocr_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                str(row["session_id"]),
                str(row["title"] or ""),
                str(row["status"] or "active"),
                int(row["created_at"] or 0),
                int(row["updated_at"] or 0),
                int(row["deprecated_at"]) if row["deprecated_at"] is not None else None,
                int(row["message_count"] or 0),
                int(row["feedback_count"] or 0),
                int(row["checkpoint_count"] or 0),
                int(row["ocr_runs_count"] or 0),
                int(row["last_feedback_at"]) if row["last_feedback_at"] is not None else None,
                int(row["last_checkpoint_at"]) if row["last_checkpoint_at"] is not None else None,
                int(row["last_ocr_at"]) if row["last_ocr_at"] is not None else None,
            )
            for row in sessions
        ],
    )

    output_conn.executemany(
        """
        INSERT INTO feedback (
          id, session_id, message_id, outcome, tags_json, note, recommended_action,
          action_taken, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(row["id"]),
                str(row["session_id"]),
                str(row["message_id"]),
                str(row["outcome"] or ""),
                str(row["tags_json"] or "[]"),
                str(row["note"]) if row["note"] is not None else None,
                str(row["recommended_action"]) if row["recommended_action"] is not None else None,
                str(row["action_taken"]) if row["action_taken"] is not None else None,
                str(row["status"] or ""),
                int(row["created_at"] or 0),
                int(row["updated_at"] or 0),
            )
            for row in feedback
        ],
    )

    output_conn.executemany(
        """
        INSERT INTO checkpoints (
          id, checkpoint_id, session_id, total_count, pass_count, fail_count, other_count, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(row["id"]),
                str(row["checkpoint_id"]),
                str(row["session_id"]),
                int(row["total_count"] or 0),
                int(row["pass_count"] or 0),
                int(row["fail_count"] or 0),
                int(row["other_count"] or 0),
                int(row["created_at"] or 0),
            )
            for row in checkpoints
        ],
    )

    output_conn.executemany(
        """
        INSERT INTO image_assets (
          id, source_name, source_filename, resolved_path, mime_type, thumbnail_png,
          thumbnail_data_url, thumbnail_width, thumbnail_height, source_size_bytes,
          source_mtime_unix, status, error
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        image_asset_rows,
    )

    output_conn.executemany(
        """
        INSERT INTO ocr_runs (
          id, run_id, session_id, source_name, mime_type, source_message_id, result_message_id,
          status, extracted_text, created_at, image_asset_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                int(row["id"]),
                str(row["run_id"] or ""),
                str(row["session_id"] or ""),
                str(row["source_name"]) if row["source_name"] is not None else None,
                str(row["mime_type"]) if row["mime_type"] is not None else None,
                str(row["source_message_id"]) if row["source_message_id"] is not None else None,
                str(row["result_message_id"]) if row["result_message_id"] is not None else None,
                str(row["status"] or ""),
                str(row["extracted_text"] or ""),
                int(row["created_at"] or 0),
                image_asset_ids.get(str(row["source_name"] or "").strip()),
            )
            for row in ocr_runs
        ],
    )

    normalized_prefixes = _normalize_prefixes(exclude_prefixes)
    metadata = {
        "generated_at_utc": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_history_db": str(history_db),
        "exclude_prefixes_json": json.dumps(normalized_prefixes, ensure_ascii=False),
        "image_roots_json": json.dumps([str(root) for root in _normalize_image_roots(image_roots)], ensure_ascii=False),
        "sessions_count": str(len(sessions)),
        "feedback_count": str(len(feedback)),
        "checkpoints_count": str(len(checkpoints)),
        "ocr_runs_count": str(len(ocr_runs)),
        "image_assets_count": str(image_stats["image_assets"]),
        "resolved_images_count": str(image_stats["image_resolved"]),
        "missing_images_count": str(image_stats["image_missing"]),
        "thumbnails_ready_count": str(image_stats["thumbnails_ready"]),
        "thumbnails_skipped_count": str(image_stats["thumbnails_skipped"]),
        "thumbnails_error_count": str(image_stats["thumbnails_error"]),
        "thumbnail_size_px": str(max(24, int(thumbnail_size))),
        "thumbnails_enabled": "true" if include_thumbnails else "false",
        "pillow_available": "true" if PILImageModule is not None else "false",
    }
    output_conn.executemany(
        "INSERT INTO metadata (key, value) VALUES (?, ?)",
        list(metadata.items()),
    )

    output_conn.commit()
    output_conn.close()

    return {
        "sessions": len(sessions),
        "feedback": len(feedback),
        "checkpoints": len(checkpoints),
        "ocr_runs": len(ocr_runs),
        "image_assets": image_stats["image_assets"],
        "thumbnails_ready": image_stats["thumbnails_ready"],
        "images_missing": image_stats["image_missing"],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a manual-evals-only SQLite DB from runtime history.db.",
    )
    parser.add_argument(
        "--history-db",
        default=".local/runtime_dbs/active/history.db",
        help="Path to source history DB.",
    )
    parser.add_argument(
        "--output-db",
        default=".local/runtime_dbs/active/manual_evals.db",
        help="Path to output manual eval DB.",
    )
    parser.add_argument(
        "--exclude-prefix",
        action="append",
        default=[],
        help="Session-id prefix to exclude (repeatable).",
    )
    parser.add_argument(
        "--image-root",
        action="append",
        default=[],
        help="Directory to search for OCR source images (repeatable).",
    )
    parser.add_argument(
        "--thumbnail-size",
        type=int,
        default=240,
        help="Thumbnail max width/height in pixels (default: 240).",
    )
    parser.add_argument(
        "--no-thumbnails",
        action="store_true",
        help="Disable thumbnail generation and only resolve source paths.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    custom_prefixes = _normalize_prefixes(args.exclude_prefix)
    prefixes = custom_prefixes if custom_prefixes else list(DEFAULT_EXCLUDE_PREFIXES)
    custom_image_roots = _normalize_image_roots(args.image_root)
    image_roots = custom_image_roots if custom_image_roots else list(DEFAULT_IMAGE_ROOTS)
    result = build_manual_evals_db(
        history_db=Path(args.history_db).expanduser(),
        output_db=Path(args.output_db).expanduser(),
        exclude_prefixes=prefixes,
        image_roots=image_roots,
        thumbnail_size=max(24, int(args.thumbnail_size)),
        include_thumbnails=not args.no_thumbnails,
    )
    print(
        "manual_evals.db built: "
        f"sessions={result['sessions']} feedback={result['feedback']} checkpoints={result['checkpoints']} "
        f"ocr_runs={result['ocr_runs']} image_assets={result['image_assets']} "
        f"thumbs={result['thumbnails_ready']} missing_images={result['images_missing']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
