from __future__ import annotations

import argparse
import json
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from pathlib import Path
from typing import Any

from tools.manual_evals_db_status import data_freshness_status


DEFAULT_DB_PATH = Path(".local/runtime_dbs/active/manual_evals.db")
ACTIONABLES_SCHEMA_VERSION = "polinko.manual_eval_feedback_actionables.v1"
COHORTS_SCHEMA_VERSION = "polinko.manual_eval_feedback_cohorts.v1"
OCR_RETRY_CANDIDATES_SCHEMA_VERSION = "polinko.manual_eval_ocr_retry_candidates.v2"
OCR_RETRY_TERMINAL_CONTEXT_LIMIT = 3

COHORT_DESCRIPTIONS = {
    "ocr_retry_evidence": "Retry OCR/crop and attach fresh image evidence.",
    "grounding_source_verification": (
        "Re-run with grounding constraints and verify against source evidence."
    ),
    "style_regression": "Adjust style notes and add style regression coverage.",
    "other_explicit_action": "Explicit recommended action outside known cohorts.",
    "missing_recommended_action": "Open feedback row has no recommended action.",
}
COHORT_IDS = tuple(COHORT_DESCRIPTIONS)
COHORT_FILTER_CHOICES = ("all", *COHORT_IDS)


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


def _parse_tags(value: object) -> list[str]:
    if value is None:
        return []
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if str(item).strip()]


def _feedback_action_cohort(recommended_action: object) -> str:
    action = _normalize_text(recommended_action).lower()
    if not action:
        return "missing_recommended_action"
    if (
        "retry ocr" in action
        or "tighter crop" in action
        or "fresh image evidence" in action
    ):
        return "ocr_retry_evidence"
    if "grounding constraints" in action or "source evidence" in action:
        return "grounding_source_verification"
    if "style notes" in action or "style eval regression" in action:
        return "style_regression"
    return "other_explicit_action"


def _normalize_cohort_filter(cohort: str | None) -> str | None:
    if cohort is None:
        return None
    cohort_id = cohort.strip().lower()
    if not cohort_id or cohort_id == "all":
        return None
    if cohort_id not in COHORT_DESCRIPTIONS:
        valid = ", ".join(COHORT_IDS)
        raise ValueError(f"unknown feedback cohort '{cohort_id}' (expected: {valid})")
    return cohort_id


def _normalize_outcome_filter(outcome: str | None) -> str | None:
    if outcome is None:
        return None
    outcome_filter = outcome.strip().lower()
    if not outcome_filter or outcome_filter == "all":
        return None
    return outcome_filter


def _fetch_count(conn: sqlite3.Connection, sql: str) -> int:
    row = conn.execute(sql).fetchone()
    if row is None:
        return 0
    return _int_value(row[0])


def _fetch_rows(
    conn: sqlite3.Connection,
    sql: str,
    params: Sequence[object] = (),
) -> list[dict[str, Any]]:
    return [_row_dict(row) for row in conn.execute(sql, params).fetchall()]


def _image_asset_family_sql(alias: str) -> str:
    filename = f"LOWER(COALESCE({alias}.source_filename, {alias}.source_name, ''))"
    mime_type = f"LOWER(COALESCE({alias}.mime_type, ''))"
    return f"""
        CASE
          WHEN {alias}.id IS NULL THEN 'unlinked'
          WHEN {mime_type} LIKE 'text/%'
            OR {filename} GLOB '*.txt'
            OR {filename} GLOB '*.md'
          THEN 'text_fixture'
          WHEN {mime_type} LIKE 'image/%'
            OR {filename} GLOB '*.png'
            OR {filename} GLOB '*.jpg'
            OR {filename} GLOB '*.jpeg'
            OR {filename} GLOB '*.gif'
            OR {filename} GLOB '*.webp'
            OR {filename} GLOB '*.heic'
            OR {filename} GLOB '*.bmp'
            OR {filename} GLOB '*.tif'
            OR {filename} GLOB '*.tiff'
          THEN 'image_file'
          ELSE 'other'
        END
    """


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
    missing_asset_family_rows = _fetch_rows(
        conn,
        f"""
        SELECT
          {_image_asset_family_sql("ia")} AS source_family,
          COUNT(*) AS missing_assets
        FROM image_assets ia
        WHERE ia.status = 'missing'
        GROUP BY source_family
        ORDER BY missing_assets DESC, source_family
        """,
    )
    missing_run_family_rows = _fetch_rows(
        conn,
        f"""
        SELECT
          {_image_asset_family_sql("ia")} AS source_family,
          COUNT(*) AS missing_ocr_runs
        FROM ocr_runs o
        LEFT JOIN image_assets ia ON ia.id = o.image_asset_id
        WHERE COALESCE(ia.status, 'unlinked') IN ('missing', 'unlinked')
        GROUP BY source_family
        ORDER BY missing_ocr_runs DESC, source_family
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
    debt_by_family: dict[str, dict[str, Any]] = {}
    for row in missing_asset_family_rows:
        family = str(row.get("source_family") or "other")
        debt_by_family[family] = {
            "source_family": family,
            "missing_assets": _int_value(row.get("missing_assets")),
            "missing_ocr_runs": 0,
        }
    for row in missing_run_family_rows:
        family = str(row.get("source_family") or "other")
        debt_row = debt_by_family.setdefault(
            family,
            {
                "source_family": family,
                "missing_assets": 0,
                "missing_ocr_runs": 0,
            },
        )
        debt_row["missing_ocr_runs"] = _int_value(row.get("missing_ocr_runs"))
    missing_debt_by_family = sorted(
        debt_by_family.values(),
        key=lambda row: (
            -_int_value(row.get("missing_assets")),
            -_int_value(row.get("missing_ocr_runs")),
            str(row.get("source_family") or ""),
        ),
    )
    return {
        "assets_by_status": asset_rows,
        "ocr_runs_by_image_status": ocr_rows,
        "missing_debt_by_family": missing_debt_by_family,
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
    open_debt_rows = _fetch_rows(
        conn,
        """
        SELECT
          era,
          LOWER(outcome) AS outcome,
          LOWER(status) AS status,
          COUNT(*) AS rows,
          COUNT(DISTINCT session_id) AS sessions,
          SUM(CASE WHEN note IS NOT NULL AND note != '' THEN 1 ELSE 0 END)
            AS rows_with_note,
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
          ) AS rows_with_action_taken,
          SUM(
            CASE
              WHEN EXISTS (
                SELECT 1
                FROM ocr_runs o
                WHERE o.session_id = feedback.session_id
                  AND o.result_message_id = feedback.message_id
              ) THEN 1
              ELSE 0
            END
          ) AS linked_to_ocr_result,
          SUM(
            CASE
              WHEN EXISTS (
                SELECT 1
                FROM ocr_runs o
                WHERE o.session_id = feedback.session_id
              ) THEN 1
              ELSE 0
            END
          ) AS same_session_ocr
        FROM feedback
        WHERE LOWER(status) = 'open'
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
        "open_debt_by_outcome": open_debt_rows,
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


def _open_feedback_where_clause(outcome: str | None) -> tuple[str, list[str]]:
    conditions = ["LOWER(f.status) = 'open'"]
    params: list[str] = []
    if outcome:
        conditions.append("LOWER(f.outcome) = ?")
        params.append(outcome.strip().lower())
    return " AND ".join(conditions), params


def _open_feedback_actionables_total(
    conn: sqlite3.Connection,
    *,
    outcome: str | None,
) -> int:
    where_clause, params = _open_feedback_where_clause(outcome)
    row = conn.execute(
        f"""
        SELECT COUNT(*)
        FROM feedback f
        WHERE {where_clause}
        """,
        params,
    ).fetchone()
    return _int_value(row[0] if row is not None else 0)


def _build_open_feedback_actionable_rows(
    conn: sqlite3.Connection,
    *,
    outcome: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    where_clause, params = _open_feedback_where_clause(outcome)
    rows = _fetch_rows(
        conn,
        f"""
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
          EXISTS (
            SELECT 1
            FROM ocr_runs linked
            WHERE linked.session_id = f.session_id
              AND linked.result_message_id = f.message_id
          ) AS linked_to_ocr_result,
          (
            SELECT COUNT(*)
            FROM ocr_runs same_session
            WHERE same_session.session_id = f.session_id
          ) AS same_session_ocr_runs,
          (
            SELECT latest.run_id
            FROM ocr_runs latest
            WHERE latest.session_id = f.session_id
            ORDER BY latest.created_at DESC, latest.id DESC
            LIMIT 1
          ) AS latest_same_session_ocr_run_id,
          (
            SELECT latest.source_name
            FROM ocr_runs latest
            WHERE latest.session_id = f.session_id
            ORDER BY latest.created_at DESC, latest.id DESC
            LIMIT 1
          ) AS latest_same_session_ocr_source_name,
          (
            SELECT latest.status
            FROM ocr_runs latest
            WHERE latest.session_id = f.session_id
            ORDER BY latest.created_at DESC, latest.id DESC
            LIMIT 1
          ) AS latest_same_session_ocr_status
        FROM feedback f
        JOIN sessions s ON s.session_id = f.session_id
        WHERE {where_clause}
        ORDER BY
          f.era,
          CASE LOWER(f.outcome)
            WHEN 'fail' THEN 0
            WHEN 'partial' THEN 1
            ELSE 2
          END,
          f.updated_at DESC,
          f.id DESC
        LIMIT ?
        """,
        [*params, str(max(1, limit))],
    )
    actionable_rows: list[dict[str, Any]] = []
    for row in rows:
        note = _normalize_text(row.get("note"))
        recommended_action = _normalize_text(row.get("recommended_action"))
        action_taken = _normalize_text(row.get("action_taken"))
        cohort_id = _feedback_action_cohort(recommended_action)
        same_session_ocr_runs = _int_value(row.get("same_session_ocr_runs"))
        actionable_rows.append(
            {
                "feedback_id": _int_value(row.get("id")),
                "era": str(row.get("era") or ""),
                "source_label": str(row.get("source_label") or ""),
                "source_history_db": str(row.get("source_history_db") or ""),
                "source_session_id": str(row.get("source_session_id") or ""),
                "session_id": str(row.get("session_id") or ""),
                "message_id": str(row.get("message_id") or ""),
                "title": _normalize_text(row.get("title")),
                "outcome": str(row.get("outcome") or "").lower(),
                "status": str(row.get("status") or "").lower(),
                "tags": _parse_tags(row.get("tags_json")),
                "note": note,
                "recommended_action": recommended_action,
                "action_taken": action_taken,
                "has_note": bool(note),
                "has_recommended_action": bool(recommended_action),
                "has_action_taken": bool(action_taken),
                "created_at": _int_value(row.get("created_at")),
                "updated_at": _int_value(row.get("updated_at")),
                "action_cohort": {
                    "id": cohort_id,
                    "description": COHORT_DESCRIPTIONS[cohort_id],
                },
                "ocr_context": {
                    "linked_to_ocr_result": bool(
                        _int_value(row.get("linked_to_ocr_result"))
                    ),
                    "same_session_ocr_runs": same_session_ocr_runs,
                    "latest_same_session_ocr": {
                        "run_id": str(row.get("latest_same_session_ocr_run_id") or ""),
                        "source_name": str(
                            row.get("latest_same_session_ocr_source_name") or ""
                        ),
                        "status": str(row.get("latest_same_session_ocr_status") or ""),
                    },
                },
            }
        )
    return actionable_rows


def _filter_actionable_rows_by_cohort(
    rows: Sequence[dict[str, Any]],
    *,
    cohort: str | None,
) -> list[dict[str, Any]]:
    if cohort is None:
        return list(rows)
    filtered_rows: list[dict[str, Any]] = []
    for row in rows:
        action_cohort = row.get("action_cohort")
        if not isinstance(action_cohort, dict):
            action_cohort = {}
        if action_cohort.get("id") == cohort:
            filtered_rows.append(row)
    return filtered_rows


def _build_filtered_open_feedback_actionable_rows(
    conn: sqlite3.Connection,
    *,
    outcome: str | None,
    cohort: str | None,
) -> list[dict[str, Any]]:
    total_rows = _open_feedback_actionables_total(conn, outcome=outcome)
    if total_rows <= 0:
        return []
    rows = _build_open_feedback_actionable_rows(
        conn,
        outcome=outcome,
        limit=total_rows,
    )
    return _filter_actionable_rows_by_cohort(rows, cohort=cohort)


def build_open_feedback_actionables_report(
    *,
    db_path: Path,
    outcome: str | None = None,
    cohort: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    outcome_filter = _normalize_outcome_filter(outcome)
    cohort_filter = _normalize_cohort_filter(cohort)
    if not db_path.is_file():
        return {
            "schema_version": ACTIONABLES_SCHEMA_VERSION,
            "state": "error",
            "manual_evals_db": {"path": str(db_path), "exists": False},
            "filters": {
                "status": "open",
                "outcome": outcome_filter or "",
                "cohort": cohort_filter or "",
                "limit": max(1, limit),
            },
            "rows": [],
            "warnings": ["manual_evals.db is not available"],
        }

    with closing(_connect_readonly(db_path)) as conn:
        integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        all_rows = _build_filtered_open_feedback_actionable_rows(
            conn,
            outcome=outcome_filter,
            cohort=cohort_filter,
        )
        total_rows = len(all_rows)
        rows = all_rows[: max(1, limit)]

    return {
        "schema_version": ACTIONABLES_SCHEMA_VERSION,
        "state": "ok" if integrity == "ok" else "error",
        "manual_evals_db": {
            "path": str(db_path),
            "exists": True,
            "integrity": integrity,
        },
        "filters": {
            "status": "open",
            "outcome": outcome_filter or "",
            "cohort": cohort_filter or "",
            "limit": max(1, limit),
        },
        "counts": {
            "total_rows": total_rows,
            "returned_rows": len(rows),
            "limit_applied": len(rows) < total_rows,
        },
        "rows": rows,
    }


def _new_cohort_summary(cohort_id: str) -> dict[str, Any]:
    return {
        "cohort_id": cohort_id,
        "description": COHORT_DESCRIPTIONS[cohort_id],
        "rows": 0,
        "sessions": 0,
        "outcomes": {},
        "rows_with_note": 0,
        "rows_with_recommended_action": 0,
        "rows_with_action_taken": 0,
        "linked_to_ocr_result": 0,
        "same_session_ocr": 0,
        "sample_feedback_ids": [],
        "_session_ids": set(),
    }


def _finalize_cohort_summary(summary: dict[str, Any]) -> dict[str, Any]:
    session_ids = summary.pop("_session_ids", set())
    if isinstance(session_ids, set):
        summary["sessions"] = len(session_ids)
    outcomes = summary.get("outcomes")
    if isinstance(outcomes, dict):
        summary["outcomes"] = {
            key: outcomes[key]
            for key in sorted(
                outcomes,
                key=lambda item: (
                    {"fail": 0, "partial": 1}.get(str(item), 2),
                    str(item),
                ),
            )
        }
    return summary


def _summarize_open_feedback_cohort_rows(
    actionables: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for row in actionables:
        action_cohort = row.get("action_cohort")
        if not isinstance(action_cohort, dict):
            action_cohort = {}
        cohort_id = str(action_cohort.get("id") or "")
        if cohort_id not in COHORT_DESCRIPTIONS:
            cohort_id = _feedback_action_cohort(row.get("recommended_action"))
        summary = summaries.setdefault(cohort_id, _new_cohort_summary(cohort_id))
        summary["rows"] = _int_value(summary.get("rows")) + 1
        session_ids = summary.get("_session_ids")
        if isinstance(session_ids, set):
            session_ids.add(str(row.get("session_id") or ""))
        outcome_key = str(row.get("outcome") or "unknown")
        outcomes = summary.get("outcomes")
        if isinstance(outcomes, dict):
            outcomes[outcome_key] = _int_value(outcomes.get(outcome_key)) + 1
        if row.get("has_note"):
            summary["rows_with_note"] = _int_value(summary.get("rows_with_note")) + 1
        if row.get("has_recommended_action"):
            summary["rows_with_recommended_action"] = (
                _int_value(summary.get("rows_with_recommended_action")) + 1
            )
        if row.get("has_action_taken"):
            summary["rows_with_action_taken"] = (
                _int_value(summary.get("rows_with_action_taken")) + 1
            )
        ocr_context = row.get("ocr_context")
        if not isinstance(ocr_context, dict):
            ocr_context = {}
        if ocr_context.get("linked_to_ocr_result"):
            summary["linked_to_ocr_result"] = (
                _int_value(summary.get("linked_to_ocr_result")) + 1
            )
        if _int_value(ocr_context.get("same_session_ocr_runs")) > 0:
            summary["same_session_ocr"] = (
                _int_value(summary.get("same_session_ocr")) + 1
            )
        sample_ids = summary.get("sample_feedback_ids")
        if isinstance(sample_ids, list) and len(sample_ids) < 5:
            sample_ids.append(_int_value(row.get("feedback_id")))

    finalized = [_finalize_cohort_summary(summary) for summary in summaries.values()]
    return sorted(
        finalized,
        key=lambda item: (
            -_int_value(item.get("rows")),
            str(item.get("cohort_id") or ""),
        ),
    )


def build_open_feedback_cohorts_report(
    *,
    db_path: Path,
    outcome: str | None = None,
    cohort: str | None = None,
) -> dict[str, Any]:
    outcome_filter = _normalize_outcome_filter(outcome)
    cohort_filter = _normalize_cohort_filter(cohort)
    if not db_path.is_file():
        return {
            "schema_version": COHORTS_SCHEMA_VERSION,
            "state": "error",
            "manual_evals_db": {"path": str(db_path), "exists": False},
            "filters": {
                "status": "open",
                "outcome": outcome_filter or "",
                "cohort": cohort_filter or "",
                "cohort_basis": "recommended_action",
            },
            "cohorts": [],
            "warnings": ["manual_evals.db is not available"],
        }

    with closing(_connect_readonly(db_path)) as conn:
        integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        actionables = _build_filtered_open_feedback_actionable_rows(
            conn,
            outcome=outcome_filter,
            cohort=cohort_filter,
        )
        total_rows = len(actionables)
        cohorts = _summarize_open_feedback_cohort_rows(actionables)

    return {
        "schema_version": COHORTS_SCHEMA_VERSION,
        "state": "ok" if integrity == "ok" else "error",
        "manual_evals_db": {
            "path": str(db_path),
            "exists": True,
            "integrity": integrity,
        },
        "filters": {
            "status": "open",
            "outcome": outcome_filter or "",
            "cohort": cohort_filter or "",
            "cohort_basis": "recommended_action",
        },
        "counts": {
            "total_rows": total_rows,
            "cohorts": len(cohorts),
        },
        "cohorts": cohorts,
    }


def _truncate_text(value: object, *, max_chars: int = 180) -> str:
    text = _normalize_text(value)
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "..."


def _build_ocr_retry_evidence_rows(
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


def _packet_feedback_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "feedback_id": _int_value(row.get("feedback_id")),
        "message_id": str(row.get("message_id") or ""),
        "outcome": str(row.get("outcome") or ""),
        "status": str(row.get("status") or ""),
        "tags": row.get("tags") if isinstance(row.get("tags"), list) else [],
        "note": str(row.get("note") or ""),
        "recommended_action": str(row.get("recommended_action") or ""),
        "action_taken": str(row.get("action_taken") or ""),
        "updated_at": _int_value(row.get("updated_at")),
        "ocr_context": row.get("ocr_context")
        if isinstance(row.get("ocr_context"), dict)
        else {},
    }


def _latest_run_for_row(
    row: dict[str, Any],
    evidence_rows: Sequence[dict[str, Any]],
) -> dict[str, Any] | None:
    ocr_context = row.get("ocr_context")
    if not isinstance(ocr_context, dict):
        ocr_context = {}
    latest = ocr_context.get("latest_same_session_ocr")
    if not isinstance(latest, dict):
        latest = {}
    latest_run_id = str(latest.get("run_id") or "")
    for evidence_row in evidence_rows:
        if evidence_row.get("run_id") == latest_run_id:
            return evidence_row
    return evidence_rows[0] if evidence_rows else None


def _feedback_has_ocr_result_link(row: dict[str, Any]) -> bool:
    ocr_context = row.get("ocr_context")
    if not isinstance(ocr_context, dict):
        return False
    return bool(ocr_context.get("linked_to_ocr_result"))


def _linked_ocr_run_ids(
    feedback_rows: Sequence[dict[str, Any]],
    evidence_rows: Sequence[dict[str, Any]],
) -> list[str]:
    feedback_message_ids = {
        str(row.get("message_id") or "")
        for row in feedback_rows
        if row.get("message_id")
    }
    if not feedback_message_ids:
        return []
    linked_run_ids: list[str] = []
    for evidence_row in evidence_rows:
        result_message_id = str(evidence_row.get("result_message_id") or "")
        run_id = str(evidence_row.get("run_id") or "")
        if result_message_id in feedback_message_ids and run_id:
            linked_run_ids.append(run_id)
    return linked_run_ids


def _build_ocr_retry_readiness(
    *,
    feedback_rows: Sequence[dict[str, Any]],
    evidence_rows: Sequence[dict[str, Any]],
    latest_run: dict[str, Any],
) -> dict[str, Any]:
    linked_feedback_rows = sum(
        1 for row in feedback_rows if _feedback_has_ocr_result_link(row)
    )
    unlinked_feedback_rows = max(0, len(feedback_rows) - linked_feedback_rows)
    linked_run_ids = _linked_ocr_run_ids(feedback_rows, evidence_rows)
    latest_run_id = str(latest_run.get("run_id") or "")
    latest_run_is_linked = bool(latest_run_id and latest_run_id in linked_run_ids)
    same_session_ocr_runs = len(evidence_rows)

    flags: list[str] = []
    if same_session_ocr_runs <= 0:
        flags.append("no_same_session_ocr_context")
    elif same_session_ocr_runs > 1:
        flags.append("multiple_same_session_ocr_runs")
    if unlinked_feedback_rows > 0:
        flags.append("missing_feedback_to_result_link")
    if latest_run_id and not latest_run_is_linked:
        flags.append("latest_ocr_is_context_only")
    if not latest_run_id:
        flags.append("no_latest_same_session_ocr")

    return {
        "state": "needs_review" if flags else "ready",
        "flags": flags,
        "basis": "explicit_result_message_match_and_same_session_context",
        "explicit_feedback_to_result_links": linked_feedback_rows,
        "unlinked_feedback_rows": unlinked_feedback_rows,
        "same_session_ocr_runs": same_session_ocr_runs,
        "linked_ocr_run_ids": linked_run_ids,
        "latest_ocr_is_confirmed_feedback_result": latest_run_is_linked,
    }


def _build_ocr_retry_candidate_groups(
    actionables: Sequence[dict[str, Any]],
    evidence_by_session: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for row in actionables:
        session_id = str(row.get("session_id") or "")
        evidence_rows = evidence_by_session.get(session_id, [])
        latest_run = _latest_run_for_row(row, evidence_rows)
        latest_run_id = str(latest_run.get("run_id") if latest_run else "")
        group_key = (session_id, latest_run_id)
        group = groups.setdefault(
            group_key,
            {
                "group_id": f"{session_id}::{latest_run_id or 'no-ocr-run'}",
                "source_label": str(row.get("source_label") or ""),
                "source_history_db": str(row.get("source_history_db") or ""),
                "source_session_id": str(row.get("source_session_id") or ""),
                "session_id": session_id,
                "title": str(row.get("title") or ""),
                "latest_same_session_ocr": latest_run or {},
                "same_session_ocr_runs": len(evidence_rows),
                "feedback_ids": [],
                "feedback_rows": [],
                "ocr_runs": evidence_rows,
            },
        )
        feedback_id = _int_value(row.get("feedback_id"))
        group["feedback_ids"].append(feedback_id)
        group["feedback_rows"].append(_packet_feedback_row(row))

    for group in groups.values():
        feedback_rows = group.get("feedback_rows")
        if not isinstance(feedback_rows, list):
            feedback_rows = []
        group_ocr_runs = group.get("ocr_runs")
        if not isinstance(group_ocr_runs, list):
            group_ocr_runs = []
        latest_run = group.get("latest_same_session_ocr")
        if not isinstance(latest_run, dict):
            latest_run = {}
        group["readiness"] = _build_ocr_retry_readiness(
            feedback_rows=feedback_rows,
            evidence_rows=group_ocr_runs,
            latest_run=latest_run,
        )

    def sort_key(item: dict[str, Any]) -> tuple[int, str]:
        feedback_rows = item.get("feedback_rows")
        feedback_count = len(feedback_rows) if isinstance(feedback_rows, list) else 0
        return (-feedback_count, str(item.get("session_id") or ""))

    return sorted(groups.values(), key=sort_key)


def build_ocr_retry_candidates_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    outcome_filter = _normalize_outcome_filter(outcome)
    cohort_filter = _normalize_cohort_filter(cohort)
    if cohort_filter is None:
        cohort_filter = "ocr_retry_evidence"
    row_limit = max(1, limit)
    if not db_path.is_file():
        return {
            "schema_version": OCR_RETRY_CANDIDATES_SCHEMA_VERSION,
            "state": "error",
            "manual_evals_db": {"path": str(db_path), "exists": False},
            "filters": {
                "status": "open",
                "outcome": outcome_filter or "",
                "cohort": cohort_filter,
                "limit": row_limit,
                "packet_basis": "recommended_action_and_same_session_ocr",
            },
            "candidate_groups": [],
            "warnings": ["manual_evals.db is not available"],
        }

    with closing(_connect_readonly(db_path)) as conn:
        integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        all_rows = _build_filtered_open_feedback_actionable_rows(
            conn,
            outcome=outcome_filter,
            cohort=cohort_filter,
        )
        rows = all_rows[:row_limit]
        evidence_by_session = _build_ocr_retry_evidence_rows(
            conn,
            session_ids=[str(row.get("session_id") or "") for row in rows],
        )
        candidate_groups = _build_ocr_retry_candidate_groups(rows, evidence_by_session)
        needs_review_groups = sum(
            1
            for group in candidate_groups
            if isinstance(group.get("readiness"), dict)
            and group["readiness"].get("state") == "needs_review"
        )

    return {
        "schema_version": OCR_RETRY_CANDIDATES_SCHEMA_VERSION,
        "state": "ok" if integrity == "ok" else "error",
        "manual_evals_db": {
            "path": str(db_path),
            "exists": True,
            "integrity": integrity,
        },
        "filters": {
            "status": "open",
            "outcome": outcome_filter or "",
            "cohort": cohort_filter,
            "limit": row_limit,
            "packet_basis": "recommended_action_and_same_session_ocr",
        },
        "counts": {
            "total_feedback_rows": len(all_rows),
            "returned_feedback_rows": len(rows),
            "candidate_groups": len(candidate_groups),
            "ready_candidate_groups": len(candidate_groups) - needs_review_groups,
            "needs_review_candidate_groups": needs_review_groups,
            "limit_applied": len(rows) < len(all_rows),
        },
        "candidate_groups": candidate_groups,
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
    missing_debt_rows = image_quality.get("missing_debt_by_family")
    if isinstance(missing_debt_rows, list) and missing_debt_rows:
        lines.append("missing image debt:")
        for row in missing_debt_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- "
                f"{row.get('source_family', 'other')}: "
                f"assets={_int_value(row.get('missing_assets'))} "
                f"ocr_runs={_int_value(row.get('missing_ocr_runs'))}"
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
    open_debt_rows = feedback_quality.get("open_debt_by_outcome")
    if isinstance(open_debt_rows, list) and open_debt_rows:
        lines.append("open feedback debt:")
        for row in open_debt_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- "
                f"{row.get('era', 'unknown')} {row.get('outcome', 'unknown')}: "
                f"rows={_int_value(row.get('rows'))} "
                f"sessions={_int_value(row.get('sessions'))} "
                f"notes={_int_value(row.get('rows_with_note'))} "
                f"recommended_actions={_int_value(row.get('rows_with_recommended_action'))} "
                f"action_taken={_int_value(row.get('rows_with_action_taken'))} "
                f"linked_to_ocr_result={_int_value(row.get('linked_to_ocr_result'))} "
                f"same_session_ocr={_int_value(row.get('same_session_ocr'))}"
            )

    lines.append(
        "session mix: "
        f"feedback_and_ocr={_int_value(session_mix.get('sessions_with_feedback_and_ocr'))} "
        f"feedback_only={_int_value(session_mix.get('feedback_only_sessions'))} "
        f"ocr_only={_int_value(session_mix.get('ocr_only_sessions'))}"
    )

    return "\n".join(lines)


def _display_text(value: object) -> str:
    text = _normalize_text(value)
    return text if text else "none"


def format_open_feedback_actionables_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    total_rows = _int_value(counts.get("total_rows"))
    returned_rows = _int_value(counts.get("returned_rows"))
    lines = [
        "manual eval open feedback actionables: "
        f"state={report.get('state', 'unknown')} "
        f"rows={returned_rows}/{total_rows} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    rows = report.get("rows")
    if not isinstance(rows, list) or not rows:
        lines.append("rows: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in rows:
        if not isinstance(item, dict):
            continue
        ocr_context = item.get("ocr_context")
        if not isinstance(ocr_context, dict):
            ocr_context = {}
        latest_ocr = ocr_context.get("latest_same_session_ocr")
        if not isinstance(latest_ocr, dict):
            latest_ocr = {}
        tags = item.get("tags")
        tag_text = ", ".join(str(tag) for tag in tags) if isinstance(tags, list) else ""
        action_cohort = item.get("action_cohort")
        if not isinstance(action_cohort, dict):
            action_cohort = {}
        lines.extend(
            [
                "- "
                f"feedback={_int_value(item.get('feedback_id'))} "
                f"era={item.get('era', '') or 'unknown'} "
                f"outcome={item.get('outcome', '') or 'unknown'} "
                f"status={item.get('status', '') or 'unknown'} "
                f"cohort={action_cohort.get('id') or 'unknown'} "
                f"session={item.get('session_id', '') or 'unknown'} "
                f"message={item.get('message_id', '') or 'unknown'}",
                f"  title={_display_text(item.get('title'))}",
                f"  tags={tag_text or 'none'}",
                f"  note={_display_text(item.get('note'))}",
                f"  recommended_action={_display_text(item.get('recommended_action'))}",
                f"  action_taken={_display_text(item.get('action_taken'))}",
                "  ocr_context: "
                "linked_to_ocr_result="
                f"{'yes' if ocr_context.get('linked_to_ocr_result') else 'no'} "
                "same_session_ocr_runs="
                f"{_int_value(ocr_context.get('same_session_ocr_runs'))} "
                f"latest_run={latest_ocr.get('run_id') or 'none'} "
                f"latest_source={latest_ocr.get('source_name') or 'none'} "
                f"latest_status={latest_ocr.get('status') or 'none'}",
            ]
        )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)


def _format_outcomes(value: object) -> str:
    if not isinstance(value, dict) or not value:
        return "none"
    return ",".join(f"{key}={_int_value(count)}" for key, count in value.items())


def format_open_feedback_cohorts_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    lines = [
        "manual eval open feedback cohorts: "
        f"state={report.get('state', 'unknown')} "
        f"rows={_int_value(counts.get('total_rows'))} "
        f"cohorts={_int_value(counts.get('cohorts'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"basis={filters.get('cohort_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    cohorts = report.get("cohorts")
    if not isinstance(cohorts, list) or not cohorts:
        lines.append("cohorts: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in cohorts:
        if not isinstance(item, dict):
            continue
        sample_ids = item.get("sample_feedback_ids")
        if isinstance(sample_ids, list):
            sample_text = ",".join(str(_int_value(item)) for item in sample_ids)
        else:
            sample_text = "none"
        lines.extend(
            [
                "- "
                f"{item.get('cohort_id', 'unknown')}: "
                f"rows={_int_value(item.get('rows'))} "
                f"sessions={_int_value(item.get('sessions'))} "
                f"outcomes={_format_outcomes(item.get('outcomes'))} "
                f"notes={_int_value(item.get('rows_with_note'))} "
                "recommended_actions="
                f"{_int_value(item.get('rows_with_recommended_action'))} "
                f"action_taken={_int_value(item.get('rows_with_action_taken'))} "
                f"linked_to_ocr_result={_int_value(item.get('linked_to_ocr_result'))} "
                f"same_session_ocr={_int_value(item.get('same_session_ocr'))} "
                f"sample_feedback={sample_text or 'none'}",
                f"  action={_display_text(item.get('description'))}",
            ]
        )
    return "\n".join(lines)


def _format_feedback_ids(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    return ",".join(str(_int_value(item)) for item in value)


def _format_latest_ocr_line(latest_ocr: dict[str, Any]) -> str:
    image_asset = latest_ocr.get("image_asset")
    if not isinstance(image_asset, dict):
        image_asset = {}
    thumbnail = image_asset.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    thumbnail_text = "none"
    if thumbnail.get("available"):
        thumbnail_text = (
            f"{_int_value(thumbnail.get('width'))}x"
            f"{_int_value(thumbnail.get('height'))}"
        )
    return (
        f"latest_run={latest_ocr.get('run_id') or 'none'} "
        f"latest_source={latest_ocr.get('source_name') or 'none'} "
        f"latest_status={latest_ocr.get('status') or 'none'} "
        f"image_status={image_asset.get('status') or 'unknown'} "
        f"resolved={'yes' if image_asset.get('resolved_path') else 'no'} "
        f"thumbnail={thumbnail_text} "
        f"chars={_int_value(latest_ocr.get('extracted_text_chars'))}"
    )


def _format_readiness_flags(readiness: dict[str, Any]) -> str:
    flags = readiness.get("flags")
    if not isinstance(flags, list) or not flags:
        return "none"
    return ",".join(str(item) for item in flags)


def _format_ocr_context_line(ocr_run: dict[str, Any]) -> str:
    image_asset = ocr_run.get("image_asset")
    if not isinstance(image_asset, dict):
        image_asset = {}
    thumbnail = image_asset.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    thumbnail_text = "none"
    if thumbnail.get("available"):
        thumbnail_text = (
            f"{_int_value(thumbnail.get('width'))}x"
            f"{_int_value(thumbnail.get('height'))}"
        )
    preview = _truncate_text(ocr_run.get("extracted_text_preview"), max_chars=80)
    return (
        f"ocr={ocr_run.get('run_id') or 'none'} "
        f"source={ocr_run.get('source_name') or 'none'} "
        f"status={ocr_run.get('status') or 'none'} "
        f"image_status={image_asset.get('status') or 'unknown'} "
        f"resolved={'yes' if image_asset.get('resolved_path') else 'no'} "
        f"thumbnail={thumbnail_text} "
        f"preview={preview or 'none'}"
    )


def format_ocr_retry_candidates_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    lines = [
        "manual eval OCR retry candidates: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"groups={_int_value(counts.get('candidate_groups'))} "
        f"needs_review={_int_value(counts.get('needs_review_candidate_groups'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    candidate_groups = report.get("candidate_groups")
    if not isinstance(candidate_groups, list) or not candidate_groups:
        lines.append("candidate_groups: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for group in candidate_groups:
        if not isinstance(group, dict):
            continue
        latest_ocr = group.get("latest_same_session_ocr")
        if not isinstance(latest_ocr, dict):
            latest_ocr = {}
        readiness = group.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        ocr_runs = group.get("ocr_runs")
        if not isinstance(ocr_runs, list):
            ocr_runs = []
        lines.extend(
            [
                "- "
                f"session={group.get('session_id') or 'unknown'} "
                f"source_session={group.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(group.get('feedback_ids'))} "
                f"ocr_runs={_int_value(group.get('same_session_ocr_runs'))}",
                f"  title={_display_text(group.get('title'))}",
                f"  {_format_latest_ocr_line(latest_ocr)}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)} "
                "explicit_links="
                f"{_int_value(readiness.get('explicit_feedback_to_result_links'))} "
                "unlinked_feedback="
                f"{_int_value(readiness.get('unlinked_feedback_rows'))} "
                "latest_confirmed="
                f"{'yes' if readiness.get('latest_ocr_is_confirmed_feedback_result') else 'no'}",
            ]
        )
        if readiness.get("state") == "needs_review" and ocr_runs:
            context_rows = [
                item
                for item in ocr_runs[:OCR_RETRY_TERMINAL_CONTEXT_LIMIT]
                if isinstance(item, dict)
            ]
            if context_rows:
                lines.append("  same_session_ocr_context:")
                for ocr_run in context_rows:
                    lines.append(f"  - {_format_ocr_context_line(ocr_run)}")
                hidden_rows = len(ocr_runs) - len(context_rows)
                if hidden_rows > 0:
                    lines.append(f"  same_session_ocr_context_more={hidden_rows}")
        feedback_rows = group.get("feedback_rows")
        if not isinstance(feedback_rows, list):
            feedback_rows = []
        for row in feedback_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "  - "
                f"feedback={_int_value(row.get('feedback_id'))} "
                f"message={row.get('message_id') or 'unknown'} "
                f"outcome={row.get('outcome') or 'unknown'} "
                f"note={_display_text(row.get('note'))}"
            )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
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
    parser.add_argument(
        "--open-feedback-actionables",
        action="store_true",
        help="Print open feedback rows that need manual-eval triage.",
    )
    parser.add_argument(
        "--open-feedback-cohorts",
        action="store_true",
        help="Print read-only cohorts for open manual-eval feedback actionables.",
    )
    parser.add_argument(
        "--ocr-retry-candidates",
        action="store_true",
        help="Print read-only OCR retry candidate packets for selected feedback.",
    )
    parser.add_argument(
        "--outcome",
        default="",
        help="Filter open feedback actionables by outcome, such as fail or partial.",
    )
    parser.add_argument(
        "--cohort",
        choices=COHORT_FILTER_CHOICES,
        default=None,
        help="Filter open feedback actionables by cohort id.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum open feedback actionable rows to print.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    db_path = Path(args.db).expanduser()
    if args.ocr_retry_candidates:
        report = build_ocr_retry_candidates_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_candidates_report(report))
        return 0

    if args.open_feedback_cohorts:
        report = build_open_feedback_cohorts_report(
            db_path=db_path,
            outcome=args.outcome,
            cohort=args.cohort,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_open_feedback_cohorts_report(report))
        return 0

    if args.open_feedback_actionables:
        report = build_open_feedback_actionables_report(
            db_path=db_path,
            outcome=args.outcome,
            cohort=args.cohort,
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_open_feedback_actionables_report(report))
        return 0

    report = build_manual_evals_health_report(db_path=db_path)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_manual_evals_health_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
