from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from tools.manual_evals_db_status import data_freshness_status


DEFAULT_DB_PATH = Path(".local/runtime_dbs/active/manual_evals.db")


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


def _fetch_count(conn: sqlite3.Connection, sql: str) -> int:
    row = conn.execute(sql).fetchone()
    if row is None:
        return 0
    return _int_value(row[0])


def _fetch_rows(conn: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    return [_row_dict(row) for row in conn.execute(sql).fetchall()]


def _build_counts(conn: sqlite3.Connection) -> dict[str, int]:
    return {
        "sessions": _fetch_count(conn, "SELECT COUNT(*) FROM sessions"),
        "feedback": _fetch_count(conn, "SELECT COUNT(*) FROM feedback"),
        "checkpoints": _fetch_count(conn, "SELECT COUNT(*) FROM checkpoints"),
        "ocr_runs": _fetch_count(conn, "SELECT COUNT(*) FROM ocr_runs"),
        "image_assets": _fetch_count(conn, "SELECT COUNT(*) FROM image_assets"),
    }


def _build_source_coverage(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return _fetch_rows(
        conn,
        """
        SELECT
          era,
          source_label,
          COUNT(*) AS sessions,
          SUM(feedback_count) AS feedback_refs,
          SUM(ocr_runs_count) AS ocr_run_refs,
          SUM(CASE WHEN feedback_count > 0 THEN 1 ELSE 0 END) AS sessions_with_feedback,
          SUM(CASE WHEN ocr_runs_count > 0 THEN 1 ELSE 0 END) AS sessions_with_ocr
        FROM sessions
        GROUP BY era, source_label
        ORDER BY era, source_label
        """,
    )


def _build_image_quality(conn: sqlite3.Connection) -> dict[str, Any]:
    asset_rows = _fetch_rows(
        conn,
        """
        SELECT status, COUNT(*) AS count
        FROM image_assets
        GROUP BY status
        ORDER BY count DESC, status
        """,
    )
    ocr_rows = _fetch_rows(
        conn,
        """
        SELECT
          o.era,
          COALESCE(ia.status, 'unlinked') AS image_status,
          COUNT(*) AS ocr_runs
        FROM ocr_runs o
        LEFT JOIN image_assets ia ON ia.id = o.image_asset_id
        GROUP BY o.era, COALESCE(ia.status, 'unlinked')
        ORDER BY o.era, image_status
        """,
    )
    total_assets = sum(_int_value(row.get("count")) for row in asset_rows)
    missing_assets = sum(
        _int_value(row.get("count"))
        for row in asset_rows
        if row.get("status") == "missing"
    )
    total_runs = sum(_int_value(row.get("ocr_runs")) for row in ocr_rows)
    missing_runs = sum(
        _int_value(row.get("ocr_runs"))
        for row in ocr_rows
        if row.get("image_status") in {"missing", "unlinked"}
    )
    return {
        "assets_by_status": asset_rows,
        "ocr_runs_by_image_status": ocr_rows,
        "missing_assets": missing_assets,
        "total_assets": total_assets,
        "missing_ocr_runs": missing_runs,
        "total_ocr_runs": total_runs,
    }


def _build_feedback_quality(conn: sqlite3.Connection) -> dict[str, Any]:
    status_rows = _fetch_rows(
        conn,
        """
        SELECT
          era,
          LOWER(outcome) AS outcome,
          LOWER(status) AS status,
          COUNT(*) AS rows,
          SUM(CASE WHEN note IS NOT NULL AND note != '' THEN 1 ELSE 0 END) AS rows_with_note,
          SUM(
            CASE
              WHEN recommended_action IS NOT NULL AND recommended_action != '' THEN 1
              ELSE 0
            END
          ) AS rows_with_recommended_action,
          SUM(
            CASE
              WHEN action_taken IS NOT NULL AND action_taken != '' THEN 1
              ELSE 0
            END
          ) AS rows_with_action_taken
        FROM feedback
        GROUP BY era, LOWER(outcome), LOWER(status)
        ORDER BY era, outcome, status
        """,
    )
    link_row = conn.execute(
        """
        SELECT
          COUNT(*) AS total,
          SUM(
            CASE
              WHEN EXISTS (
                SELECT 1
                FROM ocr_runs o
                WHERE o.session_id = f.session_id
                  AND o.result_message_id = f.message_id
              ) THEN 1
              ELSE 0
            END
          ) AS linked
        FROM feedback f
        """
    ).fetchone()
    total_feedback = _int_value(link_row["total"] if link_row else 0)
    linked_feedback = _int_value(link_row["linked"] if link_row else 0)
    open_rows = sum(
        _int_value(row.get("rows"))
        for row in status_rows
        if row.get("status") == "open"
    )
    open_fail_rows = sum(
        _int_value(row.get("rows"))
        for row in status_rows
        if row.get("status") == "open" and row.get("outcome") == "fail"
    )
    open_partial_rows = sum(
        _int_value(row.get("rows"))
        for row in status_rows
        if row.get("status") == "open" and row.get("outcome") == "partial"
    )
    return {
        "status_rows": status_rows,
        "total": total_feedback,
        "linked_to_ocr_result": linked_feedback,
        "unlinked_to_ocr_result": total_feedback - linked_feedback,
        "open": open_rows,
        "open_fail": open_fail_rows,
        "open_partial": open_partial_rows,
    }


def _build_session_mix(conn: sqlite3.Connection) -> dict[str, int]:
    row = conn.execute(
        """
        SELECT
          SUM(CASE WHEN feedback_count > 0 AND ocr_runs_count > 0 THEN 1 ELSE 0 END)
            AS sessions_with_feedback_and_ocr,
          SUM(CASE WHEN feedback_count > 0 AND ocr_runs_count = 0 THEN 1 ELSE 0 END)
            AS feedback_only_sessions,
          SUM(CASE WHEN feedback_count = 0 AND ocr_runs_count > 0 THEN 1 ELSE 0 END)
            AS ocr_only_sessions
        FROM sessions
        """
    ).fetchone()
    if row is None:
        return {
            "sessions_with_feedback_and_ocr": 0,
            "feedback_only_sessions": 0,
            "ocr_only_sessions": 0,
        }
    return {
        "sessions_with_feedback_and_ocr": _int_value(
            row["sessions_with_feedback_and_ocr"]
        ),
        "feedback_only_sessions": _int_value(row["feedback_only_sessions"]),
        "ocr_only_sessions": _int_value(row["ocr_only_sessions"]),
    }


def _health_state(
    *,
    freshness: dict[str, Any],
    integrity: str,
    image_quality: dict[str, Any],
    feedback_quality: dict[str, Any],
) -> str:
    if integrity != "ok" or freshness.get("state") in {"missing", "unknown"}:
        return "error"
    if (
        freshness.get("state") != "current"
        or _int_value(image_quality.get("missing_assets")) > 0
        or _int_value(feedback_quality.get("open")) > 0
        or _int_value(feedback_quality.get("unlinked_to_ocr_result")) > 0
    ):
        return "attention"
    return "ok"


def build_manual_evals_health_report(*, db_path: Path) -> dict[str, Any]:
    freshness = data_freshness_status(db_path=db_path)
    if not db_path.is_file():
        return {
            "state": "error",
            "manual_evals_db": {"path": str(db_path), "exists": False},
            "data_freshness": freshness,
            "warnings": ["manual_evals.db is not available"],
        }

    with closing(_connect_readonly(db_path)) as conn:
        integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        counts = _build_counts(conn)
        source_coverage = _build_source_coverage(conn)
        image_quality = _build_image_quality(conn)
        feedback_quality = _build_feedback_quality(conn)
        session_mix = _build_session_mix(conn)

    state = _health_state(
        freshness=freshness,
        integrity=integrity,
        image_quality=image_quality,
        feedback_quality=feedback_quality,
    )
    return {
        "state": state,
        "manual_evals_db": {
            "path": str(db_path),
            "exists": True,
            "integrity": integrity,
        },
        "data_freshness": freshness,
        "counts": counts,
        "source_coverage": source_coverage,
        "session_mix": session_mix,
        "image_quality": image_quality,
        "feedback_quality": feedback_quality,
    }


def _pct(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "0.0%"
    return f"{(numerator / denominator) * 100:.1f}%"


def format_manual_evals_health_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    freshness = report.get("data_freshness")
    if not isinstance(freshness, dict):
        freshness = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    image_quality = report.get("image_quality")
    if not isinstance(image_quality, dict):
        image_quality = {}
    feedback_quality = report.get("feedback_quality")
    if not isinstance(feedback_quality, dict):
        feedback_quality = {}
    session_mix = report.get("session_mix")
    if not isinstance(session_mix, dict):
        session_mix = {}

    lines = [
        "manual_evals.db health: "
        f"state={report.get('state', 'unknown')} "
        f"freshness={freshness.get('state', 'unknown')} "
        f"integrity={manual_db.get('integrity', 'unknown')} "
        f"path={manual_db.get('path', 'unknown')}",
        "counts: "
        f"sessions={_int_value(counts.get('sessions'))} "
        f"feedback={_int_value(counts.get('feedback'))} "
        f"checkpoints={_int_value(counts.get('checkpoints'))} "
        f"ocr_runs={_int_value(counts.get('ocr_runs'))} "
        f"image_assets={_int_value(counts.get('image_assets'))}",
    ]

    source_rows = report.get("source_coverage")
    if isinstance(source_rows, list) and source_rows:
        lines.append("source coverage:")
        for row in source_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- "
                f"{row.get('era', 'unknown')}: "
                f"sessions={_int_value(row.get('sessions'))} "
                f"feedback_refs={_int_value(row.get('feedback_refs'))} "
                f"ocr_refs={_int_value(row.get('ocr_run_refs'))} "
                f"sessions_with_feedback={_int_value(row.get('sessions_with_feedback'))} "
                f"sessions_with_ocr={_int_value(row.get('sessions_with_ocr'))}"
            )

    missing_assets = _int_value(image_quality.get("missing_assets"))
    total_assets = _int_value(image_quality.get("total_assets"))
    missing_runs = _int_value(image_quality.get("missing_ocr_runs"))
    total_runs = _int_value(image_quality.get("total_ocr_runs"))
    lines.append(
        "image quality: "
        f"missing_assets={missing_assets}/{total_assets} ({_pct(missing_assets, total_assets)}) "
        f"ocr_runs_without_resolved_image={missing_runs}/{total_runs} ({_pct(missing_runs, total_runs)})"
    )

    total_feedback = _int_value(feedback_quality.get("total"))
    linked_feedback = _int_value(feedback_quality.get("linked_to_ocr_result"))
    open_feedback = _int_value(feedback_quality.get("open"))
    lines.append(
        "feedback quality: "
        f"open={open_feedback}/{total_feedback} "
        f"open_fail={_int_value(feedback_quality.get('open_fail'))} "
        f"open_partial={_int_value(feedback_quality.get('open_partial'))} "
        f"linked_to_ocr_result={linked_feedback}/{total_feedback} ({_pct(linked_feedback, total_feedback)})"
    )

    lines.append(
        "session mix: "
        f"feedback_and_ocr={_int_value(session_mix.get('sessions_with_feedback_and_ocr'))} "
        f"feedback_only={_int_value(session_mix.get('feedback_only_sessions'))} "
        f"ocr_only={_int_value(session_mix.get('ocr_only_sessions'))}"
    )

    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print read-only manual eval warehouse health signals.",
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB_PATH),
        help="Path to manual eval warehouse DB.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the health report as JSON.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    report = build_manual_evals_health_report(db_path=Path(args.db).expanduser())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_manual_evals_health_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
