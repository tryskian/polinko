from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import shlex
import sqlite3
import uuid
from collections.abc import Callable, Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from tools.manual_evals_db_status import data_freshness_status


DEFAULT_DB_PATH = Path(".local/runtime_dbs/active/manual_evals.db")
ACTIONABLES_SCHEMA_VERSION = "polinko.manual_eval_feedback_actionables.v1"
COHORTS_SCHEMA_VERSION = "polinko.manual_eval_feedback_cohorts.v1"
OCR_RETRY_CANDIDATES_SCHEMA_VERSION = "polinko.manual_eval_ocr_retry_candidates.v2"
OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_source_verification.v1"
)
OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_source_provenance.v1"
)
OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION = "polinko.manual_eval_ocr_retry_input_packet.v1"
OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_rerun_manifest.v1"
)
OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION = "polinko.manual_eval_ocr_retry_rerun_plan.v1"
OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_review.v1"
)
OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_template.v1"
)
OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_decision_draft.v1"
)
OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_validation.v1"
)
OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_apply_preview.v1"
)
OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_execution_readiness.v1"
)
OCR_RETRY_EXECUTION_SCHEMA_VERSION = "polinko.manual_eval_ocr_retry_execution.v1"
OCR_RETRY_EXECUTION_CONFIRM_TOKEN = "ocr-retry-execute"
DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH = Path(
    ".local/manual_eval_decisions/ocr_retry_selection_draft.json"
)
DEFAULT_OCR_RETRY_EXECUTION_DIR = Path(".local/manual_eval_runs/ocr_retry")
DEFAULT_OCR_RETRY_MODEL = "gpt-4.1-mini"
DEFAULT_OCR_RETRY_PROMPT = (
    "Extract all readable text from this image. Preserve line breaks and symbols "
    "exactly. Do not invent letters or words; if uncertain, output [?]."
)
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

OCR_RETRY_SOURCE_VERIFICATION_REASONS = {
    "multiple_same_session_ocr_runs": (
        "same source session has multiple OCR runs, so same-session OCR remains "
        "context until an exact feedback result link is selected"
    ),
    "missing_feedback_to_result_link": (
        "feedback message_id does not match any OCR result_message_id in this "
        "candidate group"
    ),
    "latest_ocr_is_context_only": (
        "latest same-session OCR run is context only because it is not an exact "
        "feedback result link"
    ),
    "no_same_session_ocr_context": ("no OCR run is available for this source session"),
    "no_latest_same_session_ocr": (
        "no latest same-session OCR run is available for this source session"
    ),
}


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


def _ocr_retry_unconfirmed_reasons(
    readiness: dict[str, Any],
) -> list[dict[str, str]]:
    flags = readiness.get("flags")
    if not isinstance(flags, list):
        flags = []
    reasons: list[dict[str, str]] = []
    for flag in flags:
        code = str(flag)
        reasons.append(
            {
                "code": code,
                "reason": OCR_RETRY_SOURCE_VERIFICATION_REASONS.get(
                    code,
                    "candidate group needs review before it is confirmed",
                ),
            }
        )
    if readiness.get("state") == "needs_review" and not reasons:
        reasons.append(
            {
                "code": "needs_review",
                "reason": "candidate group is not confirmed by readiness signals",
            }
        )
    return reasons


def _ocr_retry_source_candidate(ocr_run: dict[str, Any]) -> dict[str, Any]:
    image_asset = ocr_run.get("image_asset")
    if not isinstance(image_asset, dict):
        image_asset = {}
    thumbnail = image_asset.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    source_image_name = str(
        image_asset.get("source_filename") or ocr_run.get("source_name") or ""
    )
    resolved_path = str(image_asset.get("resolved_path") or "")
    return {
        "run_id": str(ocr_run.get("run_id") or ""),
        "source_image_name": source_image_name,
        "source_name": str(ocr_run.get("source_name") or ""),
        "source_message_id": str(ocr_run.get("source_message_id") or ""),
        "result_message_id": str(ocr_run.get("result_message_id") or ""),
        "status": str(ocr_run.get("status") or ""),
        "created_at": _int_value(ocr_run.get("created_at")),
        "extracted_text_chars": _int_value(ocr_run.get("extracted_text_chars")),
        "extracted_text_preview": str(ocr_run.get("extracted_text_preview") or ""),
        "image_asset": {
            "source_filename": str(image_asset.get("source_filename") or ""),
            "resolved": bool(resolved_path),
            "resolved_path": resolved_path,
            "mime_type": str(image_asset.get("mime_type") or ""),
            "status": str(image_asset.get("status") or "unlinked"),
            "error": str(image_asset.get("error") or ""),
            "source_size_bytes": _int_value(image_asset.get("source_size_bytes")),
            "thumbnail": {
                "available": bool(thumbnail.get("available")),
                "width": _int_value(thumbnail.get("width")),
                "height": _int_value(thumbnail.get("height")),
            },
        },
    }


def _build_ocr_retry_source_verification_items(
    candidate_groups: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    verification_items: list[dict[str, Any]] = []
    for group in candidate_groups:
        readiness = group.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        ocr_runs = group.get("ocr_runs")
        if not isinstance(ocr_runs, list):
            ocr_runs = []
        source_candidates = [
            _ocr_retry_source_candidate(ocr_run)
            for ocr_run in ocr_runs
            if isinstance(ocr_run, dict)
        ]
        reasons = _ocr_retry_unconfirmed_reasons(readiness)
        confirmation_state = "confirmed" if not reasons else "not_confirmed"
        verification_items.append(
            {
                "group_id": str(group.get("group_id") or ""),
                "source_label": str(group.get("source_label") or ""),
                "source_history_db": str(group.get("source_history_db") or ""),
                "source_session_id": str(group.get("source_session_id") or ""),
                "session_id": str(group.get("session_id") or ""),
                "title": str(group.get("title") or ""),
                "feedback_ids": group.get("feedback_ids")
                if isinstance(group.get("feedback_ids"), list)
                else [],
                "feedback_rows": group.get("feedback_rows")
                if isinstance(group.get("feedback_rows"), list)
                else [],
                "readiness": readiness,
                "confirmation": {
                    "state": confirmation_state,
                    "basis": "explicit_feedback_result_links_before_rerun",
                    "reasons": reasons,
                },
                "latest_same_session_ocr": group.get("latest_same_session_ocr")
                if isinstance(group.get("latest_same_session_ocr"), dict)
                else {},
                "same_session_ocr_runs": _int_value(group.get("same_session_ocr_runs")),
                "source_candidates": source_candidates,
            }
        )
    return verification_items


def build_ocr_retry_source_verification_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    candidate_report = build_ocr_retry_candidates_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    candidate_groups = candidate_report.get("candidate_groups")
    if not isinstance(candidate_groups, list):
        candidate_groups = []
    verification_items = _build_ocr_retry_source_verification_items(
        [group for group in candidate_groups if isinstance(group, dict)]
    )
    needs_review_items = sum(
        1
        for item in verification_items
        if isinstance(item.get("confirmation"), dict)
        and item["confirmation"].get("state") == "not_confirmed"
    )
    source_candidate_count = 0
    for item in verification_items:
        source_candidates = item.get("source_candidates")
        if isinstance(source_candidates, list):
            source_candidate_count += len(source_candidates)
    candidate_counts = candidate_report.get("counts")
    if not isinstance(candidate_counts, dict):
        candidate_counts = {}
    candidate_filters = candidate_report.get("filters")
    if not isinstance(candidate_filters, dict):
        candidate_filters = {}

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION,
        "candidate_schema_version": candidate_report.get("schema_version", ""),
        "state": candidate_report.get("state", "unknown"),
        "manual_evals_db": candidate_report.get("manual_evals_db", {}),
        "filters": {
            "status": candidate_filters.get("status") or "open",
            "outcome": candidate_filters.get("outcome") or "",
            "cohort": candidate_filters.get("cohort") or "",
            "limit": _int_value(candidate_filters.get("limit")),
            "packet_basis": (
                "feedback_note_action_readiness_and_source_candidate_context"
            ),
        },
        "counts": {
            "total_feedback_rows": _int_value(
                candidate_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                candidate_counts.get("returned_feedback_rows")
            ),
            "verification_items": len(verification_items),
            "ready_verification_items": len(verification_items) - needs_review_items,
            "needs_review_verification_items": needs_review_items,
            "source_candidates": source_candidate_count,
            "limit_applied": bool(candidate_counts.get("limit_applied")),
        },
        "verification_items": verification_items,
    }
    warnings = candidate_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _read_source_history_messages(
    *,
    source_history_db: str,
    source_session_id: str,
    message_ids: Sequence[str],
) -> dict[str, Any]:
    clean_message_ids = [
        item
        for item in dict.fromkeys(str(value or "") for value in message_ids)
        if item
    ]
    source_path = Path(source_history_db).expanduser()
    result: dict[str, Any] = {
        "path": str(source_path),
        "exists": source_path.is_file(),
        "state": "ok" if source_path.is_file() else "missing",
        "source_session_id": source_session_id,
        "requested_message_ids": clean_message_ids,
        "messages": {},
    }
    if not source_path.is_file() or not clean_message_ids:
        return result

    placeholders = ",".join("?" for _ in clean_message_ids)
    try:
        with closing(_connect_readonly(source_path)) as conn:
            rows = _fetch_rows(
                conn,
                f"""
                SELECT
                  message_id,
                  role,
                  content,
                  created_at
                FROM chat_messages
                WHERE session_id = ?
                  AND message_id IN ({placeholders})
                ORDER BY id ASC
                """,
                [source_session_id, *clean_message_ids],
            )
    except sqlite3.Error as exc:
        result["state"] = "error"
        result["error"] = str(exc)
        return result

    messages: dict[str, dict[str, Any]] = {}
    for row in rows:
        message_id = str(row.get("message_id") or "")
        content = _normalize_text(row.get("content"))
        messages[message_id] = {
            "message_id": message_id,
            "present": True,
            "state": "found",
            "role": str(row.get("role") or ""),
            "created_at": _int_value(row.get("created_at")),
            "content_chars": len(content),
            "content_preview": _truncate_text(content),
        }
    result["messages"] = messages
    return result


def _source_message_reference(
    *,
    message_id: str,
    message_lookup: dict[str, Any],
) -> dict[str, Any]:
    clean_message_id = str(message_id or "")
    if not clean_message_id:
        return {
            "message_id": "",
            "present": False,
            "state": "empty",
            "role": "",
            "created_at": 0,
            "content_chars": 0,
            "content_preview": "",
        }
    messages = message_lookup.get("messages")
    if not isinstance(messages, dict):
        messages = {}
    row = messages.get(clean_message_id)
    if not isinstance(row, dict):
        return {
            "message_id": clean_message_id,
            "present": False,
            "state": "missing",
            "role": "",
            "created_at": 0,
            "content_chars": 0,
            "content_preview": "",
        }
    return {
        "message_id": clean_message_id,
        "present": bool(row.get("present")),
        "state": str(row.get("state") or "found"),
        "role": str(row.get("role") or ""),
        "created_at": _int_value(row.get("created_at")),
        "content_chars": _int_value(row.get("content_chars")),
        "content_preview": str(row.get("content_preview") or ""),
    }


def _build_ocr_retry_source_provenance_items(
    verification_items: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    provenance_items: list[dict[str, Any]] = []
    for item in verification_items:
        feedback_rows = item.get("feedback_rows")
        if not isinstance(feedback_rows, list):
            feedback_rows = []
        source_candidates = item.get("source_candidates")
        if not isinstance(source_candidates, list):
            source_candidates = []

        feedback_message_ids = {
            str(row.get("message_id") or "")
            for row in feedback_rows
            if isinstance(row, dict) and row.get("message_id")
        }
        ocr_message_ids: list[str] = []
        for candidate in source_candidates:
            if not isinstance(candidate, dict):
                continue
            for key in ("source_message_id", "result_message_id"):
                message_id = str(candidate.get(key) or "")
                if message_id:
                    ocr_message_ids.append(message_id)

        source_history = _read_source_history_messages(
            source_history_db=str(item.get("source_history_db") or ""),
            source_session_id=str(item.get("source_session_id") or ""),
            message_ids=[*sorted(feedback_message_ids), *ocr_message_ids],
        )

        feedback_message_rows: list[dict[str, Any]] = []
        for row in feedback_rows:
            if not isinstance(row, dict):
                continue
            message_id = str(row.get("message_id") or "")
            feedback_message_rows.append(
                {
                    "feedback_id": _int_value(row.get("feedback_id")),
                    "message_id": message_id,
                    "outcome": str(row.get("outcome") or ""),
                    "source_message": _source_message_reference(
                        message_id=message_id,
                        message_lookup=source_history,
                    ),
                }
            )

        candidate_rows: list[dict[str, Any]] = []
        exact_feedback_result_links = 0
        for candidate in source_candidates:
            if not isinstance(candidate, dict):
                continue
            result_message_id = str(candidate.get("result_message_id") or "")
            exact_link = bool(
                result_message_id and result_message_id in feedback_message_ids
            )
            if exact_link:
                exact_feedback_result_links += 1
            candidate_rows.append(
                {
                    "run_id": str(candidate.get("run_id") or ""),
                    "source_image_name": str(candidate.get("source_image_name") or ""),
                    "source_name": str(candidate.get("source_name") or ""),
                    "source_message_id": str(candidate.get("source_message_id") or ""),
                    "result_message_id": result_message_id,
                    "status": str(candidate.get("status") or ""),
                    "exact_feedback_result_link": exact_link,
                    "source_message": _source_message_reference(
                        message_id=str(candidate.get("source_message_id") or ""),
                        message_lookup=source_history,
                    ),
                    "result_message": _source_message_reference(
                        message_id=result_message_id,
                        message_lookup=source_history,
                    ),
                }
            )

        feedback_messages_found = sum(
            1 for row in feedback_message_rows if row["source_message"].get("present")
        )
        source_message_ids_present = sum(
            1 for row in candidate_rows if row.get("source_message_id")
        )
        result_message_ids_present = sum(
            1 for row in candidate_rows if row.get("result_message_id")
        )
        source_messages_found = sum(
            1 for row in candidate_rows if row["source_message"].get("present")
        )
        result_messages_found = sum(
            1 for row in candidate_rows if row["result_message"].get("present")
        )

        provenance_items.append(
            {
                "group_id": str(item.get("group_id") or ""),
                "source_label": str(item.get("source_label") or ""),
                "source_history": {
                    "path": str(source_history.get("path") or ""),
                    "exists": bool(source_history.get("exists")),
                    "state": str(source_history.get("state") or "unknown"),
                    "source_session_id": str(
                        source_history.get("source_session_id") or ""
                    ),
                    "requested_message_ids": source_history.get("requested_message_ids")
                    if isinstance(source_history.get("requested_message_ids"), list)
                    else [],
                    "error": str(source_history.get("error") or ""),
                },
                "source_session_id": str(item.get("source_session_id") or ""),
                "session_id": str(item.get("session_id") or ""),
                "title": str(item.get("title") or ""),
                "feedback_ids": item.get("feedback_ids")
                if isinstance(item.get("feedback_ids"), list)
                else [],
                "readiness": item.get("readiness")
                if isinstance(item.get("readiness"), dict)
                else {},
                "confirmation": item.get("confirmation")
                if isinstance(item.get("confirmation"), dict)
                else {},
                "feedback_messages": feedback_message_rows,
                "ocr_message_provenance": candidate_rows,
                "counts": {
                    "feedback_messages": len(feedback_message_rows),
                    "feedback_messages_found": feedback_messages_found,
                    "ocr_runs": len(candidate_rows),
                    "ocr_source_message_ids_present": source_message_ids_present,
                    "ocr_result_message_ids_present": result_message_ids_present,
                    "ocr_source_messages_found": source_messages_found,
                    "ocr_result_messages_found": result_messages_found,
                    "exact_feedback_result_links": exact_feedback_result_links,
                },
            }
        )
    return provenance_items


def build_ocr_retry_source_provenance_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    verification_report = build_ocr_retry_source_verification_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    verification_items = verification_report.get("verification_items")
    if not isinstance(verification_items, list):
        verification_items = []
    provenance_items = _build_ocr_retry_source_provenance_items(
        [item for item in verification_items if isinstance(item, dict)]
    )
    verification_counts = verification_report.get("counts")
    if not isinstance(verification_counts, dict):
        verification_counts = {}
    verification_filters = verification_report.get("filters")
    if not isinstance(verification_filters, dict):
        verification_filters = {}
    item_counts = [
        item.get("counts") for item in provenance_items if isinstance(item, dict)
    ]
    source_history_available = sum(
        1
        for item in provenance_items
        if isinstance(item.get("source_history"), dict)
        and item["source_history"].get("state") == "ok"
    )

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION,
        "verification_schema_version": verification_report.get("schema_version", ""),
        "state": verification_report.get("state", "unknown"),
        "manual_evals_db": verification_report.get("manual_evals_db", {}),
        "filters": {
            "status": verification_filters.get("status") or "open",
            "outcome": verification_filters.get("outcome") or "",
            "cohort": verification_filters.get("cohort") or "",
            "limit": _int_value(verification_filters.get("limit")),
            "packet_basis": "source_history_message_provenance",
        },
        "counts": {
            "total_feedback_rows": _int_value(
                verification_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                verification_counts.get("returned_feedback_rows")
            ),
            "provenance_items": len(provenance_items),
            "source_history_available": source_history_available,
            "feedback_messages": sum(
                _int_value(counts.get("feedback_messages"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "feedback_messages_found": sum(
                _int_value(counts.get("feedback_messages_found"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_runs": sum(
                _int_value(counts.get("ocr_runs"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_source_message_ids_present": sum(
                _int_value(counts.get("ocr_source_message_ids_present"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_result_message_ids_present": sum(
                _int_value(counts.get("ocr_result_message_ids_present"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "exact_feedback_result_links": sum(
                _int_value(counts.get("exact_feedback_result_links"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "limit_applied": bool(verification_counts.get("limit_applied")),
        },
        "provenance_items": provenance_items,
    }
    warnings = verification_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _ocr_retry_input_blocker_state(
    *,
    confirmation: dict[str, Any],
    exact_feedback_result_links: int,
    source_message_ids_present: int,
    result_message_ids_present: int,
) -> dict[str, Any]:
    if confirmation.get("state") == "confirmed" and exact_feedback_result_links > 0:
        return {
            "state": "ready",
            "reason_code": "",
            "reason": "",
            "next_action": "review_exact_link_before_feedback_closure",
        }
    if source_message_ids_present == 0 and result_message_ids_present == 0:
        return {
            "state": "blocked",
            "reason_code": "missing_ocr_source_result_message_ids",
            "reason": (
                "candidate OCR rows do not carry source/result message IDs, so "
                "the next decision is rerun input preparation or case curation"
            ),
            "next_action": "prepare_rerun_or_case_curation",
        }
    if exact_feedback_result_links == 0:
        return {
            "state": "blocked",
            "reason_code": "missing_exact_feedback_result_link",
            "reason": (
                "OCR source/result message IDs are present, but none exactly "
                "matches the feedback message"
            ),
            "next_action": "select_exact_case_or_prepare_rerun",
        }
    return {
        "state": "needs_review",
        "reason_code": "unconfirmed_source_context",
        "reason": "source context exists but confirmation is not ready for closure",
        "next_action": "review_source_verification_packet",
    }


def _build_ocr_retry_input_items(
    *,
    verification_items: Sequence[dict[str, Any]],
    provenance_items: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    provenance_by_group_id = {
        str(item.get("group_id") or ""): item
        for item in provenance_items
        if isinstance(item, dict)
    }
    input_items: list[dict[str, Any]] = []
    for item in verification_items:
        group_id = str(item.get("group_id") or "")
        provenance = provenance_by_group_id.get(group_id, {})
        if not isinstance(provenance, dict):
            provenance = {}
        provenance_counts = provenance.get("counts")
        if not isinstance(provenance_counts, dict):
            provenance_counts = {}
        source_history = provenance.get("source_history")
        if not isinstance(source_history, dict):
            source_history = {}

        feedback_messages_by_id = {
            _int_value(row.get("feedback_id")): row
            for row in provenance.get("feedback_messages", [])
            if isinstance(row, dict)
        }
        ocr_provenance_by_run_id = {
            str(row.get("run_id") or ""): row
            for row in provenance.get("ocr_message_provenance", [])
            if isinstance(row, dict)
        }

        feedback_rows = item.get("feedback_rows")
        if not isinstance(feedback_rows, list):
            feedback_rows = []
        feedback_inputs: list[dict[str, Any]] = []
        for feedback_row in feedback_rows:
            if not isinstance(feedback_row, dict):
                continue
            feedback_id = _int_value(feedback_row.get("feedback_id"))
            feedback_provenance = feedback_messages_by_id.get(feedback_id, {})
            if not isinstance(feedback_provenance, dict):
                feedback_provenance = {}
            source_message = feedback_provenance.get("source_message")
            if not isinstance(source_message, dict):
                source_message = _source_message_reference(
                    message_id=str(feedback_row.get("message_id") or ""),
                    message_lookup={},
                )
            feedback_inputs.append(
                {
                    "feedback_id": feedback_id,
                    "message_id": str(feedback_row.get("message_id") or ""),
                    "outcome": str(feedback_row.get("outcome") or ""),
                    "note": str(feedback_row.get("note") or ""),
                    "recommended_action": str(
                        feedback_row.get("recommended_action") or ""
                    ),
                    "action_taken": str(feedback_row.get("action_taken") or ""),
                    "source_message": source_message,
                }
            )

        source_candidates = item.get("source_candidates")
        if not isinstance(source_candidates, list):
            source_candidates = []
        rerun_inputs: list[dict[str, Any]] = []
        for candidate in source_candidates:
            if not isinstance(candidate, dict):
                continue
            run_id = str(candidate.get("run_id") or "")
            candidate_provenance = ocr_provenance_by_run_id.get(run_id, {})
            if not isinstance(candidate_provenance, dict):
                candidate_provenance = {}
            source_message = candidate_provenance.get("source_message")
            if not isinstance(source_message, dict):
                source_message = _source_message_reference(
                    message_id=str(candidate.get("source_message_id") or ""),
                    message_lookup={},
                )
            result_message = candidate_provenance.get("result_message")
            if not isinstance(result_message, dict):
                result_message = _source_message_reference(
                    message_id=str(candidate.get("result_message_id") or ""),
                    message_lookup={},
                )
            image_asset = candidate.get("image_asset")
            if not isinstance(image_asset, dict):
                image_asset = {}
            rerun_inputs.append(
                {
                    "run_id": run_id,
                    "source_image_name": str(candidate.get("source_image_name") or ""),
                    "source_name": str(candidate.get("source_name") or ""),
                    "status": str(candidate.get("status") or ""),
                    "created_at": _int_value(candidate.get("created_at")),
                    "extracted_text_chars": _int_value(
                        candidate.get("extracted_text_chars")
                    ),
                    "extracted_text_preview": str(
                        candidate.get("extracted_text_preview") or ""
                    ),
                    "source_message_id": str(candidate.get("source_message_id") or ""),
                    "result_message_id": str(candidate.get("result_message_id") or ""),
                    "exact_feedback_result_link": bool(
                        candidate_provenance.get("exact_feedback_result_link")
                    ),
                    "source_message": source_message,
                    "result_message": result_message,
                    "image_asset": image_asset,
                }
            )

        exact_links = _int_value(provenance_counts.get("exact_feedback_result_links"))
        source_message_ids_present = _int_value(
            provenance_counts.get("ocr_source_message_ids_present")
        )
        result_message_ids_present = _int_value(
            provenance_counts.get("ocr_result_message_ids_present")
        )
        resolved_inputs = sum(
            1
            for row in rerun_inputs
            if isinstance(row.get("image_asset"), dict)
            and row["image_asset"].get("resolved")
        )
        confirmation = item.get("confirmation")
        if not isinstance(confirmation, dict):
            confirmation = {}
        feedback_sources_found = sum(
            1 for row in feedback_inputs if row["source_message"].get("present")
        )
        blocker_state = _ocr_retry_input_blocker_state(
            confirmation=confirmation,
            exact_feedback_result_links=exact_links,
            source_message_ids_present=source_message_ids_present,
            result_message_ids_present=result_message_ids_present,
        )
        input_items.append(
            {
                "group_id": group_id,
                "source_label": str(item.get("source_label") or ""),
                "source_history": source_history,
                "source_session_id": str(item.get("source_session_id") or ""),
                "session_id": str(item.get("session_id") or ""),
                "title": str(item.get("title") or ""),
                "feedback_ids": item.get("feedback_ids")
                if isinstance(item.get("feedback_ids"), list)
                else [],
                "readiness": item.get("readiness")
                if isinstance(item.get("readiness"), dict)
                else {},
                "confirmation": confirmation,
                "blocker_state": blocker_state,
                "feedback_inputs": feedback_inputs,
                "rerun_inputs": rerun_inputs,
                "counts": {
                    "feedback_inputs": len(feedback_inputs),
                    "feedback_sources_found": feedback_sources_found,
                    "rerun_inputs": len(rerun_inputs),
                    "resolved_rerun_inputs": resolved_inputs,
                    "unresolved_rerun_inputs": len(rerun_inputs) - resolved_inputs,
                    "ocr_source_message_ids_present": source_message_ids_present,
                    "ocr_result_message_ids_present": result_message_ids_present,
                    "exact_feedback_result_links": exact_links,
                },
            }
        )
    return input_items


def build_ocr_retry_input_packet_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    verification_report = build_ocr_retry_source_verification_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    verification_items = verification_report.get("verification_items")
    if not isinstance(verification_items, list):
        verification_items = []
    verification_items = [item for item in verification_items if isinstance(item, dict)]
    provenance_items = _build_ocr_retry_source_provenance_items(verification_items)
    input_items = _build_ocr_retry_input_items(
        verification_items=verification_items,
        provenance_items=provenance_items,
    )
    verification_counts = verification_report.get("counts")
    if not isinstance(verification_counts, dict):
        verification_counts = {}
    verification_filters = verification_report.get("filters")
    if not isinstance(verification_filters, dict):
        verification_filters = {}
    item_counts = [item.get("counts") for item in input_items]

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION,
        "verification_schema_version": verification_report.get("schema_version", ""),
        "provenance_schema_version": OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION,
        "state": verification_report.get("state", "unknown"),
        "manual_evals_db": verification_report.get("manual_evals_db", {}),
        "filters": {
            "status": verification_filters.get("status") or "open",
            "outcome": verification_filters.get("outcome") or "",
            "cohort": verification_filters.get("cohort") or "",
            "limit": _int_value(verification_filters.get("limit")),
            "packet_basis": "verified_source_candidates_and_source_history_provenance",
        },
        "counts": {
            "total_feedback_rows": _int_value(
                verification_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                verification_counts.get("returned_feedback_rows")
            ),
            "input_items": len(input_items),
            "blocked_input_items": sum(
                1
                for item in input_items
                if isinstance(item.get("blocker_state"), dict)
                and item["blocker_state"].get("state") == "blocked"
            ),
            "feedback_inputs": sum(
                _int_value(counts.get("feedback_inputs"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "feedback_sources_found": sum(
                _int_value(counts.get("feedback_sources_found"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "rerun_inputs": sum(
                _int_value(counts.get("rerun_inputs"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "resolved_rerun_inputs": sum(
                _int_value(counts.get("resolved_rerun_inputs"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "unresolved_rerun_inputs": sum(
                _int_value(counts.get("unresolved_rerun_inputs"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_source_message_ids_present": sum(
                _int_value(counts.get("ocr_source_message_ids_present"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_result_message_ids_present": sum(
                _int_value(counts.get("ocr_result_message_ids_present"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "exact_feedback_result_links": sum(
                _int_value(counts.get("exact_feedback_result_links"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "limit_applied": bool(verification_counts.get("limit_applied")),
        },
        "input_items": input_items,
    }
    warnings = verification_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _ocr_retry_manifest_selection_gate(
    *,
    resolved_source_artifacts: int,
    closure_state: dict[str, Any],
) -> dict[str, Any]:
    if resolved_source_artifacts <= 0:
        return {
            "state": "blocked",
            "reason_code": "no_resolved_source_artifacts",
            "reason": "no resolved source artifact is available for rerun selection",
            "next_action": "resolve_or_curate_source_artifact",
        }
    if closure_state.get("state") == "ready":
        return {
            "state": "ready_for_review",
            "reason_code": "exact_feedback_result_link_available",
            "reason": (
                "source artifact is available, but an exact feedback-result "
                "link already exists"
            ),
            "next_action": "review_exact_link_before_feedback_closure",
        }
    return {
        "state": "ready_for_selection",
        "reason_code": str(closure_state.get("reason_code") or ""),
        "reason": str(closure_state.get("reason") or ""),
        "next_action": "select_source_artifacts_for_rerun_or_case_curation",
    }


def _ocr_retry_manifest_source_artifact(
    *,
    source_item: dict[str, Any],
) -> dict[str, Any]:
    image_asset = source_item.get("image_asset")
    if not isinstance(image_asset, dict):
        image_asset = {}
    thumbnail = image_asset.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    return {
        "run_id": str(source_item.get("run_id") or ""),
        "source_image_name": str(source_item.get("source_image_name") or ""),
        "source_name": str(source_item.get("source_name") or ""),
        "status": str(source_item.get("status") or ""),
        "created_at": _int_value(source_item.get("created_at")),
        "ocr_text_chars": _int_value(source_item.get("extracted_text_chars")),
        "ocr_text_preview": str(source_item.get("extracted_text_preview") or ""),
        "source_message_id": str(source_item.get("source_message_id") or ""),
        "result_message_id": str(source_item.get("result_message_id") or ""),
        "exact_feedback_result_link": bool(
            source_item.get("exact_feedback_result_link")
        ),
        "image": {
            "resolved": bool(image_asset.get("resolved")),
            "status": str(image_asset.get("status") or "unknown"),
            "source_filename": str(image_asset.get("source_filename") or ""),
            "resolved_path": str(image_asset.get("resolved_path") or ""),
            "mime_type": str(image_asset.get("mime_type") or ""),
            "source_size_bytes": _int_value(image_asset.get("source_size_bytes")),
            "thumbnail": {
                "available": bool(thumbnail.get("available")),
                "width": _int_value(thumbnail.get("width")),
                "height": _int_value(thumbnail.get("height")),
            },
        },
    }


def _build_ocr_retry_rerun_manifest_items(
    input_items: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    manifest_items: list[dict[str, Any]] = []
    for input_item in input_items:
        feedback_inputs = input_item.get("feedback_inputs")
        if not isinstance(feedback_inputs, list):
            feedback_inputs = []
        rerun_inputs = input_item.get("rerun_inputs")
        if not isinstance(rerun_inputs, list):
            rerun_inputs = []
        clean_feedback_inputs = [
            feedback_input
            for feedback_input in feedback_inputs
            if isinstance(feedback_input, dict)
        ]
        feedback_source_previews: list[dict[str, Any]] = []
        for feedback_input in clean_feedback_inputs:
            source_message = feedback_input.get("source_message")
            if not isinstance(source_message, dict):
                source_message = {}
            feedback_source_previews.append(
                {
                    "feedback_id": _int_value(feedback_input.get("feedback_id")),
                    "message_id": str(feedback_input.get("message_id") or ""),
                    "source_state": str(source_message.get("state") or "unknown"),
                    "source_role": str(source_message.get("role") or ""),
                    "source_preview": str(source_message.get("content_preview") or ""),
                }
            )
        source_artifacts = [
            _ocr_retry_manifest_source_artifact(
                source_item=row,
            )
            for row in rerun_inputs
            if isinstance(row, dict)
        ]
        resolved_source_artifacts = sum(
            1
            for artifact in source_artifacts
            if isinstance(artifact.get("image"), dict)
            and artifact["image"].get("resolved")
        )
        artifacts_with_thumbnail = sum(
            1
            for artifact in source_artifacts
            if isinstance(artifact.get("image"), dict)
            and isinstance(artifact["image"].get("thumbnail"), dict)
            and artifact["image"]["thumbnail"].get("available")
        )
        closure_state = input_item.get("blocker_state")
        if not isinstance(closure_state, dict):
            closure_state = {}
        selection_gate = _ocr_retry_manifest_selection_gate(
            resolved_source_artifacts=resolved_source_artifacts,
            closure_state=closure_state,
        )
        manifest_items.append(
            {
                "group_id": str(input_item.get("group_id") or ""),
                "source_label": str(input_item.get("source_label") or ""),
                "source_history": input_item.get("source_history")
                if isinstance(input_item.get("source_history"), dict)
                else {},
                "source_session_id": str(input_item.get("source_session_id") or ""),
                "session_id": str(input_item.get("session_id") or ""),
                "title": str(input_item.get("title") or ""),
                "feedback_ids": input_item.get("feedback_ids")
                if isinstance(input_item.get("feedback_ids"), list)
                else [],
                "readiness": input_item.get("readiness")
                if isinstance(input_item.get("readiness"), dict)
                else {},
                "feedback_closure_state": closure_state,
                "selection_gate": selection_gate,
                "feedback_source_previews": feedback_source_previews,
                "source_artifacts": source_artifacts,
                "counts": {
                    "feedback_inputs": len(clean_feedback_inputs),
                    "source_artifacts": len(source_artifacts),
                    "resolved_source_artifacts": resolved_source_artifacts,
                    "unresolved_source_artifacts": (
                        len(source_artifacts) - resolved_source_artifacts
                    ),
                    "artifacts_with_thumbnail": artifacts_with_thumbnail,
                },
            }
        )
    return manifest_items


def build_ocr_retry_rerun_manifest_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    input_report = build_ocr_retry_input_packet_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    input_items = input_report.get("input_items")
    if not isinstance(input_items, list):
        input_items = []
    input_items = [item for item in input_items if isinstance(item, dict)]
    manifest_items = _build_ocr_retry_rerun_manifest_items(input_items)
    input_counts = input_report.get("counts")
    if not isinstance(input_counts, dict):
        input_counts = {}
    input_filters = input_report.get("filters")
    if not isinstance(input_filters, dict):
        input_filters = {}
    item_counts = [item.get("counts") for item in manifest_items]

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION,
        "input_packet_schema_version": input_report.get("schema_version", ""),
        "state": input_report.get("state", "unknown"),
        "manual_evals_db": input_report.get("manual_evals_db", {}),
        "filters": {
            "status": input_filters.get("status") or "open",
            "outcome": input_filters.get("outcome") or "",
            "cohort": input_filters.get("cohort") or "",
            "limit": _int_value(input_filters.get("limit")),
            "packet_basis": "resolved_source_artifact_selection_gate",
        },
        "counts": {
            "total_feedback_rows": _int_value(input_counts.get("total_feedback_rows")),
            "returned_feedback_rows": _int_value(
                input_counts.get("returned_feedback_rows")
            ),
            "manifest_items": len(manifest_items),
            "selection_ready_items": sum(
                1
                for item in manifest_items
                if isinstance(item.get("selection_gate"), dict)
                and item["selection_gate"].get("state")
                in {"ready_for_selection", "ready_for_review"}
            ),
            "feedback_closure_blocked_items": sum(
                1
                for item in manifest_items
                if isinstance(item.get("feedback_closure_state"), dict)
                and item["feedback_closure_state"].get("state") == "blocked"
            ),
            "feedback_inputs": _int_value(input_counts.get("feedback_inputs")),
            "source_artifacts": sum(
                _int_value(counts.get("source_artifacts"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "resolved_source_artifacts": sum(
                _int_value(counts.get("resolved_source_artifacts"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "unresolved_source_artifacts": sum(
                _int_value(counts.get("unresolved_source_artifacts"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "artifacts_with_thumbnail": sum(
                _int_value(counts.get("artifacts_with_thumbnail"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_source_message_ids_present": _int_value(
                input_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                input_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                input_counts.get("exact_feedback_result_links")
            ),
            "limit_applied": bool(input_counts.get("limit_applied")),
        },
        "manifest_items": manifest_items,
    }
    warnings = input_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _split_artifact_ids(artifact_ids: Sequence[str] | None) -> list[str]:
    if not artifact_ids:
        return []
    clean_ids: list[str] = []
    seen: set[str] = set()
    for value in artifact_ids:
        for item in str(value).split(","):
            artifact_id = item.strip()
            if artifact_id and artifact_id not in seen:
                seen.add(artifact_id)
                clean_ids.append(artifact_id)
    return clean_ids


def _ocr_retry_plan_artifact_id(
    *,
    manifest_item: dict[str, Any],
    artifact: dict[str, Any],
) -> str:
    group_id = str(manifest_item.get("group_id") or "")
    run_id = str(artifact.get("run_id") or "")
    source_image_name = str(artifact.get("source_image_name") or "")
    artifact_key = run_id or source_image_name or "unknown-source-artifact"
    return f"{group_id}::{artifact_key}"


def _ocr_retry_plan_artifact_action(selection_gate: dict[str, Any]) -> str:
    if selection_gate.get("state") == "ready_for_review":
        return "review_exact_link_before_rerun"
    return "rerun_or_curate_source_artifact"


def _ocr_retry_plan_payload_inputs(
    *,
    artifact_id: str,
    manifest_item: dict[str, Any],
    artifact: dict[str, Any],
) -> dict[str, Any]:
    image = artifact.get("image")
    if not isinstance(image, dict):
        image = {}
    thumbnail = image.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    return {
        "artifact_id": artifact_id,
        "operation": "ocr_retry_rerun_or_case_curation",
        "preview_only": True,
        "feedback_ids": manifest_item.get("feedback_ids")
        if isinstance(manifest_item.get("feedback_ids"), list)
        else [],
        "source_session_id": str(manifest_item.get("source_session_id") or ""),
        "session_id": str(manifest_item.get("session_id") or ""),
        "ocr_run_id": str(artifact.get("run_id") or ""),
        "source_image_name": str(artifact.get("source_image_name") or ""),
        "resolved_path": str(image.get("resolved_path") or ""),
        "mime_type": str(image.get("mime_type") or ""),
        "source_size_bytes": _int_value(image.get("source_size_bytes")),
        "thumbnail": {
            "available": bool(thumbnail.get("available")),
            "width": _int_value(thumbnail.get("width")),
            "height": _int_value(thumbnail.get("height")),
        },
    }


def _ocr_retry_plan_source_preview(
    feedback_source_previews: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    for preview in feedback_source_previews:
        if not isinstance(preview, dict):
            continue
        if str(preview.get("source_preview") or ""):
            return {
                "feedback_id": _int_value(preview.get("feedback_id")),
                "message_id": str(preview.get("message_id") or ""),
                "source_state": str(preview.get("source_state") or "unknown"),
                "source_role": str(preview.get("source_role") or ""),
                "source_preview": str(preview.get("source_preview") or ""),
            }
    return {
        "feedback_id": 0,
        "message_id": "",
        "source_state": "unknown",
        "source_role": "",
        "source_preview": "",
    }


def _build_ocr_retry_rerun_plan_items(
    *,
    manifest_items: Sequence[dict[str, Any]],
    selected_artifact_ids: Sequence[str],
) -> tuple[list[dict[str, Any]], set[str]]:
    requested_artifact_ids = set(selected_artifact_ids)
    found_artifact_ids: set[str] = set()
    plan_items: list[dict[str, Any]] = []
    for manifest_item in manifest_items:
        selection_gate = manifest_item.get("selection_gate")
        if not isinstance(selection_gate, dict):
            selection_gate = {}
        if selection_gate.get("state") not in {
            "ready_for_selection",
            "ready_for_review",
        }:
            continue

        feedback_source_previews = manifest_item.get("feedback_source_previews")
        if not isinstance(feedback_source_previews, list):
            feedback_source_previews = []
        clean_feedback_previews = [
            preview for preview in feedback_source_previews if isinstance(preview, dict)
        ]
        source_preview = _ocr_retry_plan_source_preview(clean_feedback_previews)
        closure_state = manifest_item.get("feedback_closure_state")
        if not isinstance(closure_state, dict):
            closure_state = {}
        artifacts = manifest_item.get("source_artifacts")
        if not isinstance(artifacts, list):
            artifacts = []

        plan_artifacts: list[dict[str, Any]] = []
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            image = artifact.get("image")
            if not isinstance(image, dict) or not image.get("resolved"):
                continue
            artifact_id = _ocr_retry_plan_artifact_id(
                manifest_item=manifest_item,
                artifact=artifact,
            )
            found_artifact_ids.add(artifact_id)
            if requested_artifact_ids and artifact_id not in requested_artifact_ids:
                continue
            payload_inputs = _ocr_retry_plan_payload_inputs(
                artifact_id=artifact_id,
                manifest_item=manifest_item,
                artifact=artifact,
            )
            plan_artifacts.append(
                {
                    "artifact_id": artifact_id,
                    "action": _ocr_retry_plan_artifact_action(selection_gate),
                    "preview_only": True,
                    "selection_gate": selection_gate,
                    "feedback_closure_state": closure_state,
                    "feedback_ids": payload_inputs["feedback_ids"],
                    "source_session_id": payload_inputs["source_session_id"],
                    "session_id": payload_inputs["session_id"],
                    "ocr_run_id": payload_inputs["ocr_run_id"],
                    "source_image_name": payload_inputs["source_image_name"],
                    "source_name": str(artifact.get("source_name") or ""),
                    "resolved_path": payload_inputs["resolved_path"],
                    "thumbnail": payload_inputs["thumbnail"],
                    "ocr_text_preview": str(artifact.get("ocr_text_preview") or ""),
                    "feedback_source_preview": source_preview,
                    "payload_inputs": payload_inputs,
                    "command_preview": {
                        "mode": "payload_only",
                        "label": "manual_eval_ocr_retry_rerun_preview",
                        "payload_schema": "source_artifact_selection",
                    },
                }
            )
        if not plan_artifacts:
            continue
        plan_items.append(
            {
                "group_id": str(manifest_item.get("group_id") or ""),
                "source_label": str(manifest_item.get("source_label") or ""),
                "source_history": manifest_item.get("source_history")
                if isinstance(manifest_item.get("source_history"), dict)
                else {},
                "source_session_id": str(manifest_item.get("source_session_id") or ""),
                "session_id": str(manifest_item.get("session_id") or ""),
                "title": str(manifest_item.get("title") or ""),
                "feedback_ids": manifest_item.get("feedback_ids")
                if isinstance(manifest_item.get("feedback_ids"), list)
                else [],
                "readiness": manifest_item.get("readiness")
                if isinstance(manifest_item.get("readiness"), dict)
                else {},
                "selection_gate": selection_gate,
                "feedback_closure_state": closure_state,
                "feedback_source_previews": clean_feedback_previews,
                "plan_artifacts": plan_artifacts,
                "counts": {
                    "plan_artifacts": len(plan_artifacts),
                    "feedback_inputs": len(clean_feedback_previews),
                },
            }
        )
    return plan_items, found_artifact_ids


def build_ocr_retry_rerun_plan_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    manifest_report = build_ocr_retry_rerun_manifest_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    manifest_items = manifest_report.get("manifest_items")
    if not isinstance(manifest_items, list):
        manifest_items = []
    manifest_items = [item for item in manifest_items if isinstance(item, dict)]
    selected_artifact_ids = _split_artifact_ids(artifact_ids)
    plan_items, found_artifact_ids = _build_ocr_retry_rerun_plan_items(
        manifest_items=manifest_items,
        selected_artifact_ids=selected_artifact_ids,
    )
    manifest_counts = manifest_report.get("counts")
    if not isinstance(manifest_counts, dict):
        manifest_counts = {}
    manifest_filters = manifest_report.get("filters")
    if not isinstance(manifest_filters, dict):
        manifest_filters = {}
    item_counts = [item.get("counts") for item in plan_items]
    unmatched_artifact_ids = [
        artifact_id
        for artifact_id in selected_artifact_ids
        if artifact_id not in found_artifact_ids
    ]

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION,
        "manifest_schema_version": manifest_report.get("schema_version", ""),
        "state": manifest_report.get("state", "unknown"),
        "manual_evals_db": manifest_report.get("manual_evals_db", {}),
        "filters": {
            "status": manifest_filters.get("status") or "open",
            "outcome": manifest_filters.get("outcome") or "",
            "cohort": manifest_filters.get("cohort") or "",
            "limit": _int_value(manifest_filters.get("limit")),
            "packet_basis": "rerun_manifest_resolved_artifact_command_preview",
            "selection_mode": (
                "requested_artifact_ids"
                if selected_artifact_ids
                else "all_ready_resolved_source_artifacts"
            ),
            "artifact_ids": selected_artifact_ids,
        },
        "counts": {
            "total_feedback_rows": _int_value(
                manifest_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                manifest_counts.get("returned_feedback_rows")
            ),
            "manifest_items": _int_value(manifest_counts.get("manifest_items")),
            "plan_items": len(plan_items),
            "source_artifacts": _int_value(manifest_counts.get("source_artifacts")),
            "resolved_source_artifacts": _int_value(
                manifest_counts.get("resolved_source_artifacts")
            ),
            "planned_source_artifacts": sum(
                _int_value(counts.get("plan_artifacts"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "feedback_closure_blocked_items": _int_value(
                manifest_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                manifest_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                manifest_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                manifest_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": len(selected_artifact_ids),
            "unmatched_artifact_ids": len(unmatched_artifact_ids),
            "preview_only": True,
            "limit_applied": bool(manifest_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": unmatched_artifact_ids,
        "plan_items": plan_items,
    }
    warnings = manifest_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    if unmatched_artifact_ids:
        report.setdefault("warnings", []).append(
            "one or more requested artifact ids were not found in resolved "
            "source artifacts"
        )
    return report


OCR_RETRY_SELECTION_ALLOWED_ACTIONS = ("rerun_input", "curated_case", "context_only")


def _ocr_retry_selection_source_key(artifact: dict[str, Any]) -> str:
    for key in ("resolved_path", "source_image_name", "artifact_id"):
        value = str(artifact.get(key) or "").strip()
        if value:
            return value
    return "unknown-source-artifact"


def _ocr_retry_selection_shortlist_id(
    *,
    source_session_id: str,
    source_key: str,
    artifact: dict[str, Any],
) -> str:
    source_name = str(artifact.get("source_image_name") or "").strip()
    if not source_name:
        source_name = Path(source_key).name.strip()
    if not source_name:
        source_name = str(artifact.get("artifact_id") or "").strip()
    return (
        f"{source_session_id or 'unknown-session'}::{source_name or 'source-artifact'}"
    )


def _extend_unique_ints(target: list[int], values: object) -> None:
    if not isinstance(values, list):
        return
    seen = set(target)
    for value in values:
        item = _int_value(value)
        if item and item not in seen:
            seen.add(item)
            target.append(item)


def _append_unique_preview(
    target: list[dict[str, Any]],
    preview: dict[str, Any],
    seen: set[tuple[int, str, str]],
) -> None:
    key = (
        _int_value(preview.get("feedback_id")),
        str(preview.get("message_id") or ""),
        str(preview.get("source_preview") or ""),
    )
    if key in seen:
        return
    seen.add(key)
    target.append(preview)


def _ocr_retry_selection_decision(candidate_count: int) -> dict[str, Any]:
    reason_code = (
        "duplicate_source_artifacts_collapsed"
        if candidate_count > 1
        else "source_artifact_needs_review"
    )
    return {
        "state": "needs_human_selection",
        "allowed_actions": list(OCR_RETRY_SELECTION_ALLOWED_ACTIONS),
        "default_action": "undecided",
        "reason_code": reason_code,
        "next_action": "choose_source_artifact_disposition",
    }


def _build_ocr_retry_selection_review_items(
    plan_items: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped_items: dict[tuple[str, str], dict[str, Any]] = {}
    order: list[tuple[str, str]] = []
    preview_seen: dict[tuple[str, str], set[tuple[int, str, str]]] = {}

    for plan_item in plan_items:
        plan_artifacts = plan_item.get("plan_artifacts")
        if not isinstance(plan_artifacts, list):
            continue
        feedback_previews = plan_item.get("feedback_source_previews")
        if not isinstance(feedback_previews, list):
            feedback_previews = []
        clean_feedback_previews = [
            preview for preview in feedback_previews if isinstance(preview, dict)
        ]
        for artifact in plan_artifacts:
            if not isinstance(artifact, dict):
                continue
            source_session_id = str(
                artifact.get("source_session_id")
                or plan_item.get("source_session_id")
                or ""
            )
            source_key = _ocr_retry_selection_source_key(artifact)
            group_key = (source_session_id, source_key)
            if group_key not in grouped_items:
                order.append(group_key)
                preview_seen[group_key] = set()
                thumbnail = artifact.get("thumbnail")
                if not isinstance(thumbnail, dict):
                    thumbnail = {}
                grouped_items[group_key] = {
                    "shortlist_id": _ocr_retry_selection_shortlist_id(
                        source_session_id=source_session_id,
                        source_key=source_key,
                        artifact=artifact,
                    ),
                    "source_key": source_key,
                    "session_id": str(
                        artifact.get("session_id") or plan_item.get("session_id") or ""
                    ),
                    "source_session_id": source_session_id,
                    "title": str(plan_item.get("title") or ""),
                    "source_label": str(plan_item.get("source_label") or ""),
                    "source_history": plan_item.get("source_history")
                    if isinstance(plan_item.get("source_history"), dict)
                    else {},
                    "feedback_ids": [],
                    "source_image_name": str(artifact.get("source_image_name") or ""),
                    "source_name": str(artifact.get("source_name") or ""),
                    "resolved_path": str(artifact.get("resolved_path") or ""),
                    "thumbnail": thumbnail,
                    "source_image": {
                        "source_image_name": str(
                            artifact.get("source_image_name") or ""
                        ),
                        "source_name": str(artifact.get("source_name") or ""),
                        "resolved_path": str(artifact.get("resolved_path") or ""),
                        "thumbnail": thumbnail,
                    },
                    "selection_gate": plan_item.get("selection_gate")
                    if isinstance(plan_item.get("selection_gate"), dict)
                    else {},
                    "feedback_closure_state": plan_item.get("feedback_closure_state")
                    if isinstance(plan_item.get("feedback_closure_state"), dict)
                    else {},
                    "readiness": plan_item.get("readiness")
                    if isinstance(plan_item.get("readiness"), dict)
                    else {},
                    "feedback_source_previews": [],
                    "source_preview": _ocr_retry_plan_source_preview(
                        clean_feedback_previews
                    ),
                    "candidate_ocr_runs": [],
                }

            item = grouped_items[group_key]
            _extend_unique_ints(item["feedback_ids"], artifact.get("feedback_ids"))
            for preview in clean_feedback_previews:
                _append_unique_preview(
                    item["feedback_source_previews"],
                    preview,
                    preview_seen[group_key],
                )
            candidate: dict[str, Any] = {
                "artifact_id": str(artifact.get("artifact_id") or ""),
                "ocr_run_id": str(artifact.get("ocr_run_id") or ""),
                "action": str(artifact.get("action") or ""),
                "preview_only": bool(artifact.get("preview_only")),
                "feedback_ids": artifact.get("feedback_ids")
                if isinstance(artifact.get("feedback_ids"), list)
                else [],
                "source_session_id": str(artifact.get("source_session_id") or ""),
                "session_id": str(artifact.get("session_id") or ""),
                "source_image_name": str(artifact.get("source_image_name") or ""),
                "source_name": str(artifact.get("source_name") or ""),
                "resolved_path": str(artifact.get("resolved_path") or ""),
                "thumbnail": artifact.get("thumbnail")
                if isinstance(artifact.get("thumbnail"), dict)
                else {},
                "ocr_text_preview": str(artifact.get("ocr_text_preview") or ""),
                "feedback_source_preview": artifact.get("feedback_source_preview")
                if isinstance(artifact.get("feedback_source_preview"), dict)
                else {},
                "payload_inputs": artifact.get("payload_inputs")
                if isinstance(artifact.get("payload_inputs"), dict)
                else {},
                "command_preview": artifact.get("command_preview")
                if isinstance(artifact.get("command_preview"), dict)
                else {},
            }
            item["candidate_ocr_runs"].append(candidate)

    shortlist_items: list[dict[str, Any]] = []
    for group_key in order:
        item = grouped_items[group_key]
        candidate_count = len(item["candidate_ocr_runs"])
        item["selection_decision"] = _ocr_retry_selection_decision(candidate_count)
        item["counts"] = {
            "candidate_ocr_runs": candidate_count,
            "duplicate_source_artifacts": max(0, candidate_count - 1),
            "feedback_inputs": len(item["feedback_source_previews"]),
        }
        shortlist_items.append(item)
    return shortlist_items


def build_ocr_retry_selection_review_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    plan_report = build_ocr_retry_rerun_plan_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    plan_items = plan_report.get("plan_items")
    if not isinstance(plan_items, list):
        plan_items = []
    plan_items = [item for item in plan_items if isinstance(item, dict)]
    selection_review_items = _build_ocr_retry_selection_review_items(plan_items)

    plan_counts = plan_report.get("counts")
    if not isinstance(plan_counts, dict):
        plan_counts = {}
    plan_filters = plan_report.get("filters")
    if not isinstance(plan_filters, dict):
        plan_filters = {}
    planned_source_artifacts = _int_value(plan_counts.get("planned_source_artifacts"))
    duplicate_count = sum(
        _int_value(item.get("counts", {}).get("duplicate_source_artifacts"))
        for item in selection_review_items
        if isinstance(item.get("counts"), dict)
    )

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION,
        "rerun_plan_schema_version": plan_report.get("schema_version", ""),
        "state": plan_report.get("state", "unknown"),
        "manual_evals_db": plan_report.get("manual_evals_db", {}),
        "filters": {
            "status": plan_filters.get("status") or "open",
            "outcome": plan_filters.get("outcome") or "",
            "cohort": plan_filters.get("cohort") or "",
            "limit": _int_value(plan_filters.get("limit")),
            "packet_basis": "rerun_plan_source_artifact_selection_review",
            "selection_mode": plan_filters.get("selection_mode") or "",
            "artifact_ids": plan_filters.get("artifact_ids")
            if isinstance(plan_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(plan_counts.get("total_feedback_rows")),
            "returned_feedback_rows": _int_value(
                plan_counts.get("returned_feedback_rows")
            ),
            "plan_items": _int_value(plan_counts.get("plan_items")),
            "planned_source_artifacts": planned_source_artifacts,
            "shortlist_items": len(selection_review_items),
            "collapsed_duplicate_source_artifacts": duplicate_count,
            "candidate_ocr_runs": sum(
                _int_value(item.get("counts", {}).get("candidate_ocr_runs"))
                for item in selection_review_items
                if isinstance(item.get("counts"), dict)
            ),
            "decision_pending_items": len(selection_review_items),
            "feedback_closure_blocked_items": _int_value(
                plan_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                plan_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                plan_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                plan_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": _int_value(
                plan_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                plan_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(plan_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": plan_report.get("unmatched_artifact_ids", []),
        "selection_review_items": selection_review_items,
    }
    warnings = plan_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _ocr_retry_selection_template_item(
    item: dict[str, Any],
) -> dict[str, Any]:
    decision = item.get("selection_decision")
    if not isinstance(decision, dict):
        decision = {}
    allowed_actions = decision.get("allowed_actions")
    if not isinstance(allowed_actions, list):
        allowed_actions = list(OCR_RETRY_SELECTION_ALLOWED_ACTIONS)
    candidate_rows = item.get("candidate_ocr_runs")
    if not isinstance(candidate_rows, list):
        candidate_rows = []
    candidate_artifacts: list[dict[str, Any]] = []
    for candidate in candidate_rows:
        if not isinstance(candidate, dict):
            continue
        candidate_artifacts.append(
            {
                "artifact_id": str(candidate.get("artifact_id") or ""),
                "ocr_run_id": str(candidate.get("ocr_run_id") or ""),
                "action": str(candidate.get("action") or ""),
                "preview_only": bool(candidate.get("preview_only")),
                "feedback_ids": candidate.get("feedback_ids")
                if isinstance(candidate.get("feedback_ids"), list)
                else [],
                "source_image_name": str(candidate.get("source_image_name") or ""),
                "source_name": str(candidate.get("source_name") or ""),
                "resolved_path": str(candidate.get("resolved_path") or ""),
                "thumbnail": candidate.get("thumbnail")
                if isinstance(candidate.get("thumbnail"), dict)
                else {},
                "ocr_text_preview": str(candidate.get("ocr_text_preview") or ""),
                "payload_inputs": candidate.get("payload_inputs")
                if isinstance(candidate.get("payload_inputs"), dict)
                else {},
                "command_preview": candidate.get("command_preview")
                if isinstance(candidate.get("command_preview"), dict)
                else {},
            }
        )
    item_counts = item.get("counts")
    if not isinstance(item_counts, dict):
        item_counts = {}
    return {
        "shortlist_id": str(item.get("shortlist_id") or ""),
        "source_key": str(item.get("source_key") or ""),
        "session_id": str(item.get("session_id") or ""),
        "source_session_id": str(item.get("source_session_id") or ""),
        "title": str(item.get("title") or ""),
        "feedback_ids": item.get("feedback_ids")
        if isinstance(item.get("feedback_ids"), list)
        else [],
        "source_image_name": str(item.get("source_image_name") or ""),
        "source_name": str(item.get("source_name") or ""),
        "resolved_path": str(item.get("resolved_path") or ""),
        "thumbnail": item.get("thumbnail")
        if isinstance(item.get("thumbnail"), dict)
        else {},
        "source_preview": item.get("source_preview")
        if isinstance(item.get("source_preview"), dict)
        else {},
        "readiness": item.get("readiness")
        if isinstance(item.get("readiness"), dict)
        else {},
        "feedback_closure_state": item.get("feedback_closure_state")
        if isinstance(item.get("feedback_closure_state"), dict)
        else {},
        "decision_input": {
            "selected_action": "undecided",
            "allowed_actions": [str(action) for action in allowed_actions],
            "selected_artifact_ids": [],
            "rationale": "",
            "notes": "",
            "requires_human_selection": True,
        },
        "candidate_artifacts": candidate_artifacts,
        "counts": {
            "candidate_artifacts": len(candidate_artifacts),
            "duplicate_source_artifacts": _int_value(
                item_counts.get("duplicate_source_artifacts")
            ),
            "feedback_inputs": _int_value(item_counts.get("feedback_inputs")),
        },
    }


def build_ocr_retry_selection_template_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    selection_review = build_ocr_retry_selection_review_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    selection_items = selection_review.get("selection_review_items")
    if not isinstance(selection_items, list):
        selection_items = []
    template_items = [
        _ocr_retry_selection_template_item(item)
        for item in selection_items
        if isinstance(item, dict)
    ]
    review_counts = selection_review.get("counts")
    if not isinstance(review_counts, dict):
        review_counts = {}
    review_filters = selection_review.get("filters")
    if not isinstance(review_filters, dict):
        review_filters = {}
    duplicate_count = sum(
        _int_value(item.get("counts", {}).get("duplicate_source_artifacts"))
        for item in template_items
        if isinstance(item.get("counts"), dict)
    )

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION,
        "selection_review_schema_version": selection_review.get("schema_version", ""),
        "state": selection_review.get("state", "unknown"),
        "manual_evals_db": selection_review.get("manual_evals_db", {}),
        "filters": {
            "status": review_filters.get("status") or "open",
            "outcome": review_filters.get("outcome") or "",
            "cohort": review_filters.get("cohort") or "",
            "limit": _int_value(review_filters.get("limit")),
            "packet_basis": "selection_review_human_decision_template",
            "selection_mode": review_filters.get("selection_mode") or "",
            "artifact_ids": review_filters.get("artifact_ids")
            if isinstance(review_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(review_counts.get("total_feedback_rows")),
            "returned_feedback_rows": _int_value(
                review_counts.get("returned_feedback_rows")
            ),
            "shortlist_items": _int_value(review_counts.get("shortlist_items")),
            "template_items": len(template_items),
            "candidate_artifacts": sum(
                _int_value(item.get("counts", {}).get("candidate_artifacts"))
                for item in template_items
                if isinstance(item.get("counts"), dict)
            ),
            "collapsed_duplicate_source_artifacts": duplicate_count,
            "default_undecided_items": len(template_items),
            "feedback_closure_blocked_items": _int_value(
                review_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                review_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                review_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                review_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": _int_value(
                review_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                review_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(review_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": selection_review.get("unmatched_artifact_ids", []),
        "selection_template": {
            "template_version": "manual_ocr_retry_selection.v1",
            "default_action": "undecided",
            "allowed_actions": list(OCR_RETRY_SELECTION_ALLOWED_ACTIONS),
            "mutation": "none",
            "items": template_items,
        },
    }
    warnings = selection_review.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _json_fingerprint(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def _json_safe_copy(payload: object) -> object:
    return json.loads(json.dumps(payload, ensure_ascii=True, sort_keys=True))


def _ocr_retry_selection_draft_template(
    template_report: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    raw_template = template_report.get("selection_template")
    if not isinstance(raw_template, dict):
        raw_template = {}
    template = _json_safe_copy(raw_template)
    if not isinstance(template, dict):
        template = {}
    items = template.get("items")
    if not isinstance(items, list):
        items = []
        template["items"] = items
    for item in items:
        if isinstance(item, dict):
            item["template_item_fingerprint"] = _json_fingerprint(
                {
                    "selection_template_schema_version": template_report.get(
                        "schema_version", ""
                    ),
                    "item": item,
                }
            )
    template_fingerprint = _json_fingerprint(
        {
            "selection_template_schema_version": template_report.get(
                "schema_version", ""
            ),
            "filters": template_report.get("filters", {}),
            "selection_template": template,
        }
    )
    template["template_fingerprint"] = template_fingerprint
    return template, template_fingerprint


def build_ocr_retry_selection_decision_draft_payload(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    template_report = build_ocr_retry_selection_template_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    template, template_fingerprint = _ocr_retry_selection_draft_template(
        template_report
    )
    template_counts = template_report.get("counts")
    if not isinstance(template_counts, dict):
        template_counts = {}
    template_filters = template_report.get("filters")
    if not isinstance(template_filters, dict):
        template_filters = {}
    draft_items = template.get("items")
    if not isinstance(draft_items, list):
        draft_items = []
    payload: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION,
        "selection_template_schema_version": template_report.get("schema_version", ""),
        "state": template_report.get("state", "unknown"),
        "manual_evals_db": template_report.get("manual_evals_db", {}),
        "filters": {
            "status": template_filters.get("status") or "open",
            "outcome": template_filters.get("outcome") or "",
            "cohort": template_filters.get("cohort") or "",
            "limit": _int_value(template_filters.get("limit")),
            "packet_basis": "selection_template_local_decision_draft",
            "selection_mode": template_filters.get("selection_mode") or "",
            "artifact_ids": template_filters.get("artifact_ids")
            if isinstance(template_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(
                template_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                template_counts.get("returned_feedback_rows")
            ),
            "shortlist_items": _int_value(template_counts.get("shortlist_items")),
            "draft_items": len(draft_items),
            "candidate_artifacts": _int_value(
                template_counts.get("candidate_artifacts")
            ),
            "collapsed_duplicate_source_artifacts": _int_value(
                template_counts.get("collapsed_duplicate_source_artifacts")
            ),
            "default_undecided_items": _int_value(
                template_counts.get("default_undecided_items")
            ),
            "feedback_closure_blocked_items": _int_value(
                template_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                template_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                template_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                template_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": _int_value(
                template_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                template_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(template_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": template_report.get("unmatched_artifact_ids", []),
        "template_fingerprint": template_fingerprint,
        "draft_contract": {
            "mutation": "none",
            "execution": "none",
            "local_only": True,
            "requires_validation": True,
            "next_validation_schema_version": (
                OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION
            ),
            "next_apply_preview_schema_version": (
                OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION
            ),
            "allowed_actions": list(OCR_RETRY_SELECTION_ALLOWED_ACTIONS),
        },
        "selection_template": template,
    }
    warnings = template_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        payload["warnings"] = warnings
    return payload


def write_ocr_retry_selection_decision_draft(
    *,
    db_path: Path,
    output_path: Path | None = None,
    force: bool = False,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    payload = build_ocr_retry_selection_decision_draft_payload(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    resolved_path = (output_path or DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH).expanduser()
    quoted_output_path = shlex.quote(str(resolved_path))
    counts = payload.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION,
        "selection_template_schema_version": payload.get(
            "selection_template_schema_version", ""
        ),
        "state": "pending",
        "manual_evals_db": payload.get("manual_evals_db", {}),
        "filters": payload.get("filters", {}),
        "counts": counts,
        "template_fingerprint": payload.get("template_fingerprint", ""),
        "output": {
            "path": str(resolved_path),
            "force": force,
            "overwritten": False,
            "local_only": True,
        },
        "next_commands": {
            "validate": (
                "make manual-evals-ocr-retry-selection-validate "
                f"SELECTION_PATH={quoted_output_path}"
            ),
            "apply_preview": (
                "make manual-evals-ocr-retry-selection-apply-preview "
                f"SELECTION_PATH={quoted_output_path}"
            ),
        },
    }
    if resolved_path.exists() and resolved_path.is_dir():
        report["state"] = "blocked"
        report.setdefault("warnings", []).append(
            f"OCR retry selection draft output path is a directory: {resolved_path}"
        )
        return report
    if resolved_path.exists() and not force:
        report["state"] = "blocked"
        report.setdefault("warnings", []).append(
            "OCR retry selection draft already exists; pass --force to overwrite: "
            f"{resolved_path}"
        )
        return report

    existed = resolved_path.exists()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report["state"] = "written"
    output = report["output"]
    if isinstance(output, dict):
        output["overwritten"] = existed
    return report


def _load_ocr_retry_selection_decision_payload(
    selection_path: Path | None,
) -> tuple[object | None, dict[str, Any], list[str]]:
    if selection_path is None:
        return (
            None,
            {
                "state": "missing",
                "path": "",
                "schema_version": "",
            },
            ["no OCR retry selection decision file was provided"],
        )
    resolved_path = selection_path.expanduser()
    source = {
        "state": "loaded",
        "path": str(resolved_path),
        "schema_version": "",
    }
    if not resolved_path.exists():
        source["state"] = "error"
        return (
            None,
            source,
            [f"OCR retry selection decision file was not found: {resolved_path}"],
        )
    if not resolved_path.is_file():
        source["state"] = "error"
        return (
            None,
            source,
            [f"OCR retry selection decision path is not a file: {resolved_path}"],
        )
    try:
        payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        source["state"] = "error"
        return (
            None,
            source,
            [
                "OCR retry selection decision file is not valid JSON: "
                f"line {exc.lineno} column {exc.colno}"
            ],
        )
    if isinstance(payload, dict):
        source["schema_version"] = str(payload.get("schema_version") or "")
    return payload, source, []


def _clean_selected_artifact_ids(value: object) -> list[str]:
    if isinstance(value, str):
        raw_values: Sequence[object] = value.split(",")
    elif isinstance(value, list):
        raw_values = value
    else:
        return []
    selected: list[str] = []
    seen: set[str] = set()
    for raw_value in raw_values:
        artifact_id = str(raw_value).strip()
        if artifact_id and artifact_id not in seen:
            seen.add(artifact_id)
            selected.append(artifact_id)
    return selected


def _selection_decision_items_from_payload(
    payload: object,
) -> tuple[list[dict[str, Any]], list[str]]:
    if payload is None:
        return [], []

    raw_items: list[object]
    if isinstance(payload, list):
        raw_items = payload
    elif isinstance(payload, dict):
        decision_payload = payload.get("decisions")
        if isinstance(decision_payload, list):
            raw_items = decision_payload
        else:
            template = payload.get("selection_template")
            if isinstance(template, dict) and isinstance(template.get("items"), list):
                raw_items = template["items"]
            elif isinstance(payload.get("items"), list):
                raw_items = payload["items"]
            elif payload.get("shortlist_id"):
                raw_items = [payload]
            else:
                return [], [
                    "OCR retry selection decision JSON does not contain a "
                    "`decisions` list or `selection_template.items` list"
                ]
    else:
        return [], ["OCR retry selection decision JSON must be an object or list"]

    extracted_decisions: list[dict[str, Any]] = []
    warnings: list[str] = []
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            warnings.append(f"decision item {index} is not an object")
            continue
        decision_input = raw_item.get("decision_input")
        if isinstance(decision_input, dict):
            source = decision_input
        else:
            source = raw_item
        extracted_decisions.append(
            {
                "index": index,
                "shortlist_id": str(raw_item.get("shortlist_id") or "").strip(),
                "selected_action": str(source.get("selected_action") or "").strip(),
                "selected_artifact_ids": _clean_selected_artifact_ids(
                    source.get("selected_artifact_ids")
                ),
                "rationale": str(source.get("rationale") or "").strip(),
                "notes": str(source.get("notes") or "").strip(),
            }
        )
    return extracted_decisions, warnings


def _selection_template_items_by_shortlist_id(
    template_report: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    template = template_report.get("selection_template")
    if not isinstance(template, dict):
        return {}
    items = template.get("items")
    if not isinstance(items, list):
        return {}
    by_shortlist_id: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        shortlist_id = str(item.get("shortlist_id") or "").strip()
        if shortlist_id:
            by_shortlist_id[shortlist_id] = item
    return by_shortlist_id


def _candidate_artifact_ids(item: dict[str, Any]) -> set[str]:
    candidates = item.get("candidate_artifacts")
    if not isinstance(candidates, list):
        return set()
    return {
        str(candidate.get("artifact_id") or "").strip()
        for candidate in candidates
        if isinstance(candidate, dict)
        and str(candidate.get("artifact_id") or "").strip()
    }


def _feedback_closure_blocked(item: dict[str, Any]) -> bool:
    closure_state = item.get("feedback_closure_state")
    return isinstance(closure_state, dict) and closure_state.get("state") == "blocked"


def _validate_ocr_retry_selection_decision(
    *,
    item: dict[str, Any],
    decision: dict[str, Any] | None,
    duplicate_count: int,
) -> dict[str, Any]:
    shortlist_id = str(item.get("shortlist_id") or "")
    candidate_ids = _candidate_artifact_ids(item)
    selected_action = ""
    selected_artifact_ids: list[str] = []
    rationale = ""
    notes = ""
    issues: list[str] = []
    if decision is None:
        issues.append("missing_decision")
    else:
        selected_action = str(decision.get("selected_action") or "").strip()
        selected_artifact_ids = _clean_selected_artifact_ids(
            decision.get("selected_artifact_ids")
        )
        rationale = str(decision.get("rationale") or "").strip()
        notes = str(decision.get("notes") or "").strip()
        if duplicate_count:
            issues.append("duplicate_decision")
        if not selected_action or selected_action == "undecided":
            issues.append("pending_selected_action")
        elif selected_action not in OCR_RETRY_SELECTION_ALLOWED_ACTIONS:
            issues.append("invalid_selected_action")
        elif selected_action in {"rerun_input", "curated_case"}:
            if not selected_artifact_ids:
                issues.append("missing_selected_artifact")
        elif selected_action == "context_only" and selected_artifact_ids:
            issues.append("context_only_must_not_select_artifacts")
        missing_artifact_ids = [
            artifact_id
            for artifact_id in selected_artifact_ids
            if artifact_id not in candidate_ids
        ]
        if missing_artifact_ids:
            issues.append("selected_artifact_not_in_shortlist")

    invalid_issue_codes = {
        "duplicate_decision",
        "invalid_selected_action",
        "missing_selected_artifact",
        "context_only_must_not_select_artifacts",
        "selected_artifact_not_in_shortlist",
    }
    pending_issue_codes = {"missing_decision", "pending_selected_action"}
    if any(issue in invalid_issue_codes for issue in issues):
        state = "invalid"
    elif any(issue in pending_issue_codes for issue in issues):
        state = "pending"
    else:
        state = "valid"

    return {
        "shortlist_id": shortlist_id,
        "state": state,
        "issues": issues,
        "selected_action": selected_action or "undecided",
        "allowed_actions": list(OCR_RETRY_SELECTION_ALLOWED_ACTIONS),
        "selected_artifact_ids": selected_artifact_ids,
        "candidate_artifact_ids": sorted(candidate_ids),
        "invalid_selected_artifact_ids": [
            artifact_id
            for artifact_id in selected_artifact_ids
            if artifact_id not in candidate_ids
        ],
        "rationale": rationale,
        "notes": notes,
        "feedback_ids": item.get("feedback_ids")
        if isinstance(item.get("feedback_ids"), list)
        else [],
        "feedback_closure_state": item.get("feedback_closure_state")
        if isinstance(item.get("feedback_closure_state"), dict)
        else {},
        "feedback_closure_blocked": _feedback_closure_blocked(item),
        "source_image_name": str(item.get("source_image_name") or ""),
        "resolved_path": str(item.get("resolved_path") or ""),
        "preview_only": True,
    }


def build_ocr_retry_selection_validation_report(
    *,
    db_path: Path,
    selection_path: Path | None = None,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    template_report = build_ocr_retry_selection_template_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    payload, decision_source, decision_warnings = (
        _load_ocr_retry_selection_decision_payload(selection_path)
    )
    submitted_decisions, extraction_warnings = _selection_decision_items_from_payload(
        payload
    )
    template_items = _selection_template_items_by_shortlist_id(template_report)
    decisions_by_shortlist_id: dict[str, dict[str, Any]] = {}
    duplicate_counts: dict[str, int] = {}
    stale_decisions: list[dict[str, Any]] = []

    for decision in submitted_decisions:
        shortlist_id = str(decision.get("shortlist_id") or "").strip()
        if not shortlist_id:
            stale_decisions.append(
                {
                    "shortlist_id": "",
                    "state": "invalid",
                    "issues": ["missing_shortlist_id"],
                    "selected_action": decision.get("selected_action") or "undecided",
                    "selected_artifact_ids": decision.get("selected_artifact_ids")
                    if isinstance(decision.get("selected_artifact_ids"), list)
                    else [],
                    "candidate_artifact_ids": [],
                    "invalid_selected_artifact_ids": decision.get(
                        "selected_artifact_ids"
                    )
                    if isinstance(decision.get("selected_artifact_ids"), list)
                    else [],
                    "preview_only": True,
                }
            )
            continue
        if shortlist_id not in template_items:
            stale_decisions.append(
                {
                    "shortlist_id": shortlist_id,
                    "state": "invalid",
                    "issues": ["stale_shortlist_id"],
                    "selected_action": decision.get("selected_action") or "undecided",
                    "selected_artifact_ids": decision.get("selected_artifact_ids")
                    if isinstance(decision.get("selected_artifact_ids"), list)
                    else [],
                    "candidate_artifact_ids": [],
                    "invalid_selected_artifact_ids": decision.get(
                        "selected_artifact_ids"
                    )
                    if isinstance(decision.get("selected_artifact_ids"), list)
                    else [],
                    "preview_only": True,
                }
            )
            continue
        if shortlist_id in decisions_by_shortlist_id:
            duplicate_counts[shortlist_id] = duplicate_counts.get(shortlist_id, 0) + 1
            continue
        decisions_by_shortlist_id[shortlist_id] = decision

    validation_items = [
        _validate_ocr_retry_selection_decision(
            item=item,
            decision=decisions_by_shortlist_id.get(shortlist_id),
            duplicate_count=duplicate_counts.get(shortlist_id, 0),
        )
        for shortlist_id, item in template_items.items()
    ]
    validation_items.extend(stale_decisions)

    invalid_decisions = sum(
        1 for item in validation_items if item.get("state") == "invalid"
    )
    pending_decisions = sum(
        1 for item in validation_items if item.get("state") == "pending"
    )
    valid_decisions = sum(
        1 for item in validation_items if item.get("state") == "valid"
    )
    missing_decisions = sum(
        1
        for item in validation_items
        if isinstance(item.get("issues"), list) and "missing_decision" in item["issues"]
    )
    invalid_selected_artifacts = sum(
        len(item.get("invalid_selected_artifact_ids", []))
        for item in validation_items
        if isinstance(item.get("invalid_selected_artifact_ids"), list)
    )
    selected_artifacts = sum(
        len(item.get("selected_artifact_ids", []))
        for item in validation_items
        if isinstance(item.get("selected_artifact_ids"), list)
    )
    duplicate_decisions = sum(duplicate_counts.values())
    source_state = str(decision_source.get("state") or "unknown")
    if source_state == "error" or invalid_decisions or duplicate_decisions:
        state = "error"
    elif pending_decisions or source_state == "missing":
        state = "attention"
    else:
        state = "ok"

    template_counts = template_report.get("counts")
    if not isinstance(template_counts, dict):
        template_counts = {}
    template_filters = template_report.get("filters")
    if not isinstance(template_filters, dict):
        template_filters = {}

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION,
        "selection_template_schema_version": template_report.get("schema_version", ""),
        "state": state,
        "manual_evals_db": template_report.get("manual_evals_db", {}),
        "decision_source": decision_source,
        "filters": {
            "status": template_filters.get("status") or "open",
            "outcome": template_filters.get("outcome") or "",
            "cohort": template_filters.get("cohort") or "",
            "limit": _int_value(template_filters.get("limit")),
            "packet_basis": "selection_template_human_decision_validation",
            "selection_mode": template_filters.get("selection_mode") or "",
            "artifact_ids": template_filters.get("artifact_ids")
            if isinstance(template_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(
                template_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                template_counts.get("returned_feedback_rows")
            ),
            "shortlist_items": len(template_items),
            "candidate_artifacts": _int_value(
                template_counts.get("candidate_artifacts")
            ),
            "submitted_decisions": len(submitted_decisions),
            "valid_decisions": valid_decisions,
            "pending_decisions": pending_decisions,
            "invalid_decisions": invalid_decisions,
            "missing_decisions": missing_decisions,
            "stale_decisions": len(stale_decisions),
            "duplicate_decisions": duplicate_decisions,
            "selected_artifacts": selected_artifacts,
            "invalid_selected_artifacts": invalid_selected_artifacts,
            "feedback_closure_blocked_items": _int_value(
                template_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                template_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                template_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                template_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": _int_value(
                template_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                template_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(template_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": template_report.get("unmatched_artifact_ids", []),
        "selection_validation_items": validation_items,
    }
    warnings = template_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = list(warnings)
    for warning in [*decision_warnings, *extraction_warnings]:
        report.setdefault("warnings", []).append(warning)
    return report


def _empty_selection_apply_actions() -> dict[str, list[dict[str, Any]]]:
    return {action: [] for action in OCR_RETRY_SELECTION_ALLOWED_ACTIONS}


def _selection_apply_selected_artifacts(
    *,
    template_item: dict[str, Any],
    selected_artifact_ids: Sequence[str],
) -> list[dict[str, Any]]:
    candidates = template_item.get("candidate_artifacts")
    if not isinstance(candidates, list):
        return []
    by_artifact_id = {
        str(candidate.get("artifact_id") or ""): candidate
        for candidate in candidates
        if isinstance(candidate, dict) and str(candidate.get("artifact_id") or "")
    }
    selected_artifacts: list[dict[str, Any]] = []
    for artifact_id in selected_artifact_ids:
        candidate = by_artifact_id.get(str(artifact_id))
        if not isinstance(candidate, dict):
            continue
        payload_inputs = candidate.get("payload_inputs")
        if not isinstance(payload_inputs, dict):
            payload_inputs = {}
        command_preview = candidate.get("command_preview")
        if not isinstance(command_preview, dict):
            command_preview = {}
        selected_artifacts.append(
            {
                "artifact_id": str(candidate.get("artifact_id") or ""),
                "ocr_run_id": str(candidate.get("ocr_run_id") or ""),
                "preview_only": bool(candidate.get("preview_only")),
                "source_session_id": str(
                    payload_inputs.get("source_session_id")
                    or template_item.get("source_session_id")
                    or ""
                ),
                "session_id": str(
                    payload_inputs.get("session_id")
                    or template_item.get("session_id")
                    or ""
                ),
                "feedback_ids": candidate.get("feedback_ids")
                if isinstance(candidate.get("feedback_ids"), list)
                else [],
                "source_image_name": str(candidate.get("source_image_name") or ""),
                "source_name": str(candidate.get("source_name") or ""),
                "resolved_path": str(candidate.get("resolved_path") or ""),
                "thumbnail": candidate.get("thumbnail")
                if isinstance(candidate.get("thumbnail"), dict)
                else {},
                "ocr_text_preview": str(candidate.get("ocr_text_preview") or ""),
                "payload_inputs": payload_inputs,
                "command_preview": {
                    "mode": str(command_preview.get("mode") or "payload_only"),
                    "label": str(command_preview.get("label") or ""),
                    "payload_schema": str(command_preview.get("payload_schema") or ""),
                },
            }
        )
    return selected_artifacts


def _selection_apply_item(
    *,
    validation_item: dict[str, Any],
    template_item: dict[str, Any],
) -> dict[str, Any]:
    selected_action = str(validation_item.get("selected_action") or "")
    selected_artifact_ids = validation_item.get("selected_artifact_ids")
    if not isinstance(selected_artifact_ids, list):
        selected_artifact_ids = []
    selected_artifacts = _selection_apply_selected_artifacts(
        template_item=template_item,
        selected_artifact_ids=[str(item) for item in selected_artifact_ids],
    )
    closure_state = validation_item.get("feedback_closure_state")
    if not isinstance(closure_state, dict):
        closure_state = {}
    return {
        "shortlist_id": str(validation_item.get("shortlist_id") or ""),
        "selected_action": selected_action,
        "application_mode": "preview_only",
        "mutation": "none",
        "execution": "none",
        "feedback_ids": validation_item.get("feedback_ids")
        if isinstance(validation_item.get("feedback_ids"), list)
        else [],
        "source_session_id": str(template_item.get("source_session_id") or ""),
        "session_id": str(template_item.get("session_id") or ""),
        "source_image_name": str(template_item.get("source_image_name") or ""),
        "resolved_path": str(template_item.get("resolved_path") or ""),
        "selected_artifact_ids": [str(item) for item in selected_artifact_ids],
        "selected_artifacts": selected_artifacts,
        "rationale": str(validation_item.get("rationale") or ""),
        "notes": str(validation_item.get("notes") or ""),
        "feedback_closure_state": closure_state,
        "feedback_closure_blocked": _feedback_closure_blocked(template_item),
        "preview_only": True,
    }


def _selection_apply_validation_blockers(
    validation_report: dict[str, Any],
) -> list[dict[str, Any]]:
    validation_items = validation_report.get("selection_validation_items")
    if not isinstance(validation_items, list):
        return []
    blockers: list[dict[str, Any]] = []
    for item in validation_items:
        if not isinstance(item, dict) or item.get("state") == "valid":
            continue
        blockers.append(
            {
                "shortlist_id": str(item.get("shortlist_id") or ""),
                "state": str(item.get("state") or "unknown"),
                "selected_action": str(item.get("selected_action") or "undecided"),
                "issues": item.get("issues")
                if isinstance(item.get("issues"), list)
                else [],
                "selected_artifact_ids": item.get("selected_artifact_ids")
                if isinstance(item.get("selected_artifact_ids"), list)
                else [],
                "invalid_selected_artifact_ids": item.get(
                    "invalid_selected_artifact_ids"
                )
                if isinstance(item.get("invalid_selected_artifact_ids"), list)
                else [],
                "feedback_ids": item.get("feedback_ids")
                if isinstance(item.get("feedback_ids"), list)
                else [],
                "preview_only": True,
            }
        )
    return blockers


def build_ocr_retry_selection_apply_preview_report(
    *,
    db_path: Path,
    selection_path: Path | None = None,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    validation_report = build_ocr_retry_selection_validation_report(
        db_path=db_path,
        selection_path=selection_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    validation_counts = validation_report.get("counts")
    if not isinstance(validation_counts, dict):
        validation_counts = {}
    validation_filters = validation_report.get("filters")
    if not isinstance(validation_filters, dict):
        validation_filters = {}
    decision_source = validation_report.get("decision_source")
    if not isinstance(decision_source, dict):
        decision_source = {}

    validation_state = str(validation_report.get("state") or "unknown")
    blocked = validation_state != "ok"
    apply_actions = _empty_selection_apply_actions()
    apply_items: list[dict[str, Any]] = []
    blockers = (
        _selection_apply_validation_blockers(validation_report) if blocked else []
    )

    if not blocked:
        template_report = build_ocr_retry_selection_template_report(
            db_path=db_path,
            outcome=outcome,
            cohort=cohort,
            limit=limit,
            artifact_ids=artifact_ids,
        )
        template_items = _selection_template_items_by_shortlist_id(template_report)
        validation_items = validation_report.get("selection_validation_items")
        if not isinstance(validation_items, list):
            validation_items = []
        for validation_item in validation_items:
            if not isinstance(validation_item, dict):
                continue
            shortlist_id = str(validation_item.get("shortlist_id") or "")
            template_item = template_items.get(shortlist_id)
            if not isinstance(template_item, dict):
                continue
            apply_item = _selection_apply_item(
                validation_item=validation_item,
                template_item=template_item,
            )
            selected_action = str(apply_item.get("selected_action") or "")
            if selected_action in apply_actions:
                apply_actions[selected_action].append(apply_item)
            apply_items.append(apply_item)

    selected_artifacts = sum(
        len(item.get("selected_artifacts", []))
        for item in apply_items
        if isinstance(item.get("selected_artifacts"), list)
    )
    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION,
        "selection_validation_schema_version": validation_report.get(
            "schema_version", ""
        ),
        "state": "blocked" if blocked else "ok",
        "validation_state": validation_state,
        "manual_evals_db": validation_report.get("manual_evals_db", {}),
        "decision_source": decision_source,
        "filters": {
            "status": validation_filters.get("status") or "open",
            "outcome": validation_filters.get("outcome") or "",
            "cohort": validation_filters.get("cohort") or "",
            "limit": _int_value(validation_filters.get("limit")),
            "packet_basis": "selection_validation_application_preview",
            "selection_mode": validation_filters.get("selection_mode") or "",
            "artifact_ids": validation_filters.get("artifact_ids")
            if isinstance(validation_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(
                validation_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                validation_counts.get("returned_feedback_rows")
            ),
            "shortlist_items": _int_value(validation_counts.get("shortlist_items")),
            "candidate_artifacts": _int_value(
                validation_counts.get("candidate_artifacts")
            ),
            "submitted_decisions": _int_value(
                validation_counts.get("submitted_decisions")
            ),
            "valid_decisions": _int_value(validation_counts.get("valid_decisions")),
            "pending_decisions": _int_value(validation_counts.get("pending_decisions")),
            "invalid_decisions": _int_value(validation_counts.get("invalid_decisions")),
            "missing_decisions": _int_value(validation_counts.get("missing_decisions")),
            "stale_decisions": _int_value(validation_counts.get("stale_decisions")),
            "duplicate_decisions": _int_value(
                validation_counts.get("duplicate_decisions")
            ),
            "blocked_by_validation": len(blockers),
            "preview_items": len(apply_items),
            "rerun_input_items": len(apply_actions["rerun_input"]),
            "curated_case_items": len(apply_actions["curated_case"]),
            "context_only_items": len(apply_actions["context_only"]),
            "selected_artifacts": selected_artifacts,
            "feedback_closure_blocked_items": _int_value(
                validation_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                validation_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                validation_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                validation_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": _int_value(
                validation_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                validation_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(validation_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": validation_report.get("unmatched_artifact_ids", []),
        "validation_blockers": blockers,
        "application_preview": {
            "mutation": "none",
            "execution": "none",
            "requires_validation_state": "ok",
            "actions": apply_actions,
            "items": apply_items,
        },
    }
    warnings = validation_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    if blocked:
        report.setdefault("warnings", []).append(
            "selection application preview is blocked until validation state is ok"
        )
    return report


def _execution_readiness_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    payload_inputs = artifact.get("payload_inputs")
    if not isinstance(payload_inputs, dict):
        payload_inputs = {}
    command_preview = artifact.get("command_preview")
    if not isinstance(command_preview, dict):
        command_preview = {}
    resolved_path = str(artifact.get("resolved_path") or "").strip()
    artifact_id = str(artifact.get("artifact_id") or "").strip()
    issues: list[str] = []
    if not artifact_id:
        issues.append("missing_artifact_id")
    if not resolved_path:
        issues.append("missing_resolved_path")
        source_file_exists = False
    else:
        source_file_exists = Path(resolved_path).is_file()
        if not source_file_exists:
            issues.append("source_file_missing")
    if str(payload_inputs.get("operation") or "") != "ocr_retry_rerun_or_case_curation":
        issues.append("unexpected_payload_operation")
    if str(command_preview.get("mode") or "payload_only") != "payload_only":
        issues.append("unexpected_command_preview_mode")
    return {
        "artifact_id": artifact_id,
        "state": "blocked" if issues else "ready",
        "issues": issues,
        "source_file_exists": source_file_exists,
        "resolved_path": resolved_path,
        "source_image_name": str(artifact.get("source_image_name") or ""),
        "ocr_run_id": str(artifact.get("ocr_run_id") or ""),
        "source_session_id": str(artifact.get("source_session_id") or ""),
        "session_id": str(artifact.get("session_id") or ""),
        "payload_inputs": payload_inputs,
        "command_preview": {
            "mode": str(command_preview.get("mode") or "payload_only"),
            "label": str(command_preview.get("label") or ""),
            "payload_schema": str(command_preview.get("payload_schema") or ""),
        },
        "preview_only": True,
    }


def _execution_readiness_item(item: dict[str, Any]) -> dict[str, Any]:
    action = str(item.get("selected_action") or "")
    selected_artifacts = item.get("selected_artifacts")
    if not isinstance(selected_artifacts, list):
        selected_artifacts = []
    readiness_artifacts = [
        _execution_readiness_artifact(artifact)
        for artifact in selected_artifacts
        if isinstance(artifact, dict)
    ]
    issues: list[str] = []
    if action not in OCR_RETRY_SELECTION_ALLOWED_ACTIONS:
        issues.append("invalid_selected_action")
    elif action in {"rerun_input", "curated_case"} and not readiness_artifacts:
        issues.append("missing_selected_artifact")
    elif action == "context_only" and readiness_artifacts:
        issues.append("context_only_must_not_select_artifacts")
    if any(artifact["state"] != "ready" for artifact in readiness_artifacts):
        issues.append("selected_artifact_not_executable")
    state = "blocked" if issues else "ready"
    return {
        "shortlist_id": str(item.get("shortlist_id") or ""),
        "state": state,
        "issues": issues,
        "selected_action": action,
        "executable": state == "ready" and action in {"rerun_input", "curated_case"},
        "execution_gate": "explicit_follow_up_required",
        "mutation": "none",
        "execution": "none",
        "feedback_ids": item.get("feedback_ids")
        if isinstance(item.get("feedback_ids"), list)
        else [],
        "source_session_id": str(item.get("source_session_id") or ""),
        "session_id": str(item.get("session_id") or ""),
        "source_image_name": str(item.get("source_image_name") or ""),
        "resolved_path": str(item.get("resolved_path") or ""),
        "selected_artifact_ids": item.get("selected_artifact_ids")
        if isinstance(item.get("selected_artifact_ids"), list)
        else [],
        "selected_artifacts": readiness_artifacts,
        "feedback_closure_state": item.get("feedback_closure_state")
        if isinstance(item.get("feedback_closure_state"), dict)
        else {},
        "feedback_closure_blocked": bool(item.get("feedback_closure_blocked")),
        "preview_only": True,
    }


def build_ocr_retry_execution_readiness_report(
    *,
    db_path: Path,
    selection_path: Path | None = None,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    apply_report = build_ocr_retry_selection_apply_preview_report(
        db_path=db_path,
        selection_path=selection_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    apply_counts = apply_report.get("counts")
    if not isinstance(apply_counts, dict):
        apply_counts = {}
    apply_filters = apply_report.get("filters")
    if not isinstance(apply_filters, dict):
        apply_filters = {}
    decision_source = apply_report.get("decision_source")
    if not isinstance(decision_source, dict):
        decision_source = {}
    preview = apply_report.get("application_preview")
    if not isinstance(preview, dict):
        preview = {}
    apply_items = preview.get("items")
    if not isinstance(apply_items, list):
        apply_items = []

    apply_state = str(apply_report.get("state") or "unknown")
    readiness_items = (
        [
            _execution_readiness_item(item)
            for item in apply_items
            if isinstance(item, dict)
        ]
        if apply_state == "ok"
        else []
    )
    item_blockers = [item for item in readiness_items if item.get("state") != "ready"]
    validation_blockers = apply_report.get("validation_blockers")
    if not isinstance(validation_blockers, list):
        validation_blockers = []
    state = "ready" if apply_state == "ok" and not item_blockers else "blocked"
    source_files_ready = sum(
        1
        for item in readiness_items
        for artifact in item.get("selected_artifacts", [])
        if isinstance(artifact, dict) and artifact.get("source_file_exists")
    )
    source_files_missing = sum(
        1
        for item in readiness_items
        for artifact in item.get("selected_artifacts", [])
        if isinstance(artifact, dict) and not artifact.get("source_file_exists")
    )
    selected_artifacts = sum(
        len(item.get("selected_artifacts", []))
        for item in readiness_items
        if isinstance(item.get("selected_artifacts"), list)
    )

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION,
        "selection_apply_preview_schema_version": apply_report.get(
            "schema_version", ""
        ),
        "state": state,
        "apply_preview_state": apply_state,
        "validation_state": str(apply_report.get("validation_state") or "unknown"),
        "manual_evals_db": apply_report.get("manual_evals_db", {}),
        "decision_source": decision_source,
        "filters": {
            "status": apply_filters.get("status") or "open",
            "outcome": apply_filters.get("outcome") or "",
            "cohort": apply_filters.get("cohort") or "",
            "limit": _int_value(apply_filters.get("limit")),
            "packet_basis": "selection_apply_preview_execution_readiness",
            "selection_mode": apply_filters.get("selection_mode") or "",
            "artifact_ids": apply_filters.get("artifact_ids")
            if isinstance(apply_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(apply_counts.get("total_feedback_rows")),
            "returned_feedback_rows": _int_value(
                apply_counts.get("returned_feedback_rows")
            ),
            "shortlist_items": _int_value(apply_counts.get("shortlist_items")),
            "candidate_artifacts": _int_value(apply_counts.get("candidate_artifacts")),
            "submitted_decisions": _int_value(apply_counts.get("submitted_decisions")),
            "valid_decisions": _int_value(apply_counts.get("valid_decisions")),
            "pending_decisions": _int_value(apply_counts.get("pending_decisions")),
            "invalid_decisions": _int_value(apply_counts.get("invalid_decisions")),
            "blocked_by_validation": _int_value(
                apply_counts.get("blocked_by_validation")
            ),
            "apply_preview_items": _int_value(apply_counts.get("preview_items")),
            "readiness_items": len(readiness_items),
            "ready_items": sum(
                1 for item in readiness_items if item.get("state") == "ready"
            ),
            "blocked_items": len(item_blockers),
            "executable_items": sum(
                1 for item in readiness_items if item.get("executable")
            ),
            "rerun_input_items": _int_value(apply_counts.get("rerun_input_items")),
            "curated_case_items": _int_value(apply_counts.get("curated_case_items")),
            "context_only_items": _int_value(apply_counts.get("context_only_items")),
            "selected_artifacts": selected_artifacts,
            "source_files_ready": source_files_ready,
            "source_files_missing": source_files_missing,
            "feedback_closure_blocked_items": _int_value(
                apply_counts.get("feedback_closure_blocked_items")
            ),
            "requested_artifact_ids": _int_value(
                apply_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                apply_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(apply_counts.get("limit_applied")),
        },
        "readiness_contract": {
            "mutation": "none",
            "execution": "none",
            "readiness_only": True,
            "requires_validation_state": "ok",
            "requires_apply_preview_state": "ok",
            "requires_explicit_follow_up_gate": True,
        },
        "validation_blockers": validation_blockers,
        "readiness_blockers": item_blockers,
        "execution_readiness_items": readiness_items,
    }
    warnings = apply_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = list(warnings)
    if apply_state != "ok":
        report.setdefault("warnings", []).append(
            "execution readiness is blocked until selection apply-preview state is ok"
        )
    elif item_blockers:
        report.setdefault("warnings", []).append(
            "one or more selected OCR retry artifacts are not executable yet"
        )
    return report


class OcrRetryExecutionProviderError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status: str = "provider_error",
        retry_after: str = "",
    ) -> None:
        super().__init__(message)
        self.status = status
        self.retry_after = retry_after


OcrRetryRunner = Callable[[dict[str, Any]], dict[str, Any]]


def _utc_run_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _short_text_preview(value: object, *, limit: int = 240) -> str:
    normalized = _normalize_text(value)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def _selection_file_fingerprint(selection_path: Path | None) -> str:
    if selection_path is None or not selection_path.is_file():
        return ""
    return hashlib.sha256(selection_path.read_bytes()).hexdigest()


def _ocr_retry_execution_mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "read_only",
        "feedback_closure": "none",
        "live_eval_rows": "none",
        "manual_eval_warehouse": "none",
    }


def _ocr_retry_execution_blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _blocked_ocr_retry_execution_report(
    *,
    readiness_report: dict[str, Any] | None,
    selection_path: Path | None,
    confirm_token: str,
    execution_blockers: Sequence[dict[str, str]],
    ocr_provider: str,
    ocr_model: str,
    execution_dir: Path | None,
) -> dict[str, Any]:
    readiness_counts: dict[str, Any] = {}
    if isinstance(readiness_report, dict):
        counts = readiness_report.get("counts")
        if isinstance(counts, dict):
            readiness_counts = counts
    return {
        "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
        "state": "blocked",
        "execution_mode": "local_bundle",
        "selection_path": str(selection_path or ""),
        "selection_fingerprint": _selection_file_fingerprint(selection_path),
        "readiness_schema_version": readiness_report.get("schema_version", "")
        if isinstance(readiness_report, dict)
        else "",
        "readiness_state": readiness_report.get("state", "not_checked")
        if isinstance(readiness_report, dict)
        else "not_checked",
        "confirmation": {
            "required": OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
            "provided": bool(confirm_token),
            "state": "ok"
            if confirm_token == OCR_RETRY_EXECUTION_CONFIRM_TOKEN
            else "blocked",
        },
        "ocr_provider": ocr_provider,
        "ocr_model": ocr_model,
        "counts": {
            "readiness_items": _int_value(readiness_counts.get("readiness_items")),
            "executable_items": _int_value(readiness_counts.get("executable_items")),
            "requests": 0,
            "responses": 0,
            "succeeded": 0,
            "failed": 0,
            "context_only_skipped": _int_value(
                readiness_counts.get("context_only_items")
            ),
        },
        "mutation_boundary": _ocr_retry_execution_mutation_boundary(),
        "output": {
            "written": False,
            "root": str(execution_dir or ""),
            "run_dir": "",
        },
        "execution_blockers": list(execution_blockers),
        "warnings": [blocker["detail"] for blocker in execution_blockers],
    }


def _response_retry_after_from_openai_error(exc: Exception) -> str:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if headers is None:
        return ""
    retry_after = headers.get("retry-after") or headers.get("Retry-After")
    return str(retry_after or "").strip()


def _ocr_retry_request_source(request: dict[str, Any]) -> dict[str, Any]:
    source = request.get("source")
    if isinstance(source, dict):
        return source
    return {}


def _run_scaffold_ocr_retry_request(request: dict[str, Any]) -> dict[str, Any]:
    source = _ocr_retry_request_source(request)
    resolved_path = Path(str(source.get("resolved_path") or "")).expanduser()
    raw_bytes = resolved_path.read_bytes()
    extracted_text = raw_bytes.decode("utf-8", errors="ignore").strip()
    status = "ok" if extracted_text else "stub"
    if not extracted_text:
        extracted_text = (
            "[OCR scaffold] Binary payload received. Configure "
            "POLINKO_OCR_PROVIDER=openai for text extraction."
        )
    return {
        "status": status,
        "provider": "scaffold",
        "model": "scaffold",
        "extracted_text": extracted_text,
        "extracted_text_preview": _short_text_preview(extracted_text),
        "chars": len(extracted_text),
    }


def _run_openai_ocr_retry_request(
    request: dict[str, Any],
    *,
    ocr_model: str,
    ocr_prompt: str,
) -> dict[str, Any]:
    try:
        from openai import (
            APIConnectionError,
            APIStatusError,
            AuthenticationError,
            OpenAI,
            RateLimitError,
        )
    except ImportError as exc:  # pragma: no cover - package is present in repo env
        raise OcrRetryExecutionProviderError(
            "openai package is not installed",
            status="provider_not_configured",
        ) from exc

    api_key = str(os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise OcrRetryExecutionProviderError(
            "OPENAI_API_KEY is not set",
            status="provider_not_configured",
        )

    source = _ocr_retry_request_source(request)
    resolved_path = Path(str(source.get("resolved_path") or "")).expanduser()
    mime_type = str(
        source.get("mime_type")
        or mimetypes.guess_type(str(resolved_path))[0]
        or "application/octet-stream"
    )
    if not mime_type.startswith("image/"):
        raise OcrRetryExecutionProviderError(
            f"OpenAI OCR expects image input, got {mime_type}",
            status="invalid_request",
        )
    data_url = (
        f"data:{mime_type};base64,"
        f"{base64.b64encode(resolved_path.read_bytes()).decode('ascii')}"
    )
    client = OpenAI(api_key=api_key)
    ocr_input = cast(
        Any,
        [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": ocr_prompt},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
    )
    try:
        response = client.responses.create(
            model=ocr_model,
            input=ocr_input,
            temperature=0,
        )
    except AuthenticationError as exc:
        raise OcrRetryExecutionProviderError(
            "OpenAI authentication failed",
            status="authentication_error",
        ) from exc
    except RateLimitError as exc:
        raise OcrRetryExecutionProviderError(
            "OpenAI OCR rate limit reached",
            status="rate_limited",
            retry_after=_response_retry_after_from_openai_error(exc),
        ) from exc
    except APIConnectionError as exc:
        raise OcrRetryExecutionProviderError(
            "Connection error reaching OpenAI OCR provider",
            status="provider_unavailable",
        ) from exc
    except APIStatusError as exc:
        status = "provider_unavailable" if exc.status_code >= 500 else "provider_error"
        if exc.status_code == 429:
            status = "rate_limited"
        if exc.status_code in {400, 413, 415, 422}:
            status = "invalid_request"
        if exc.status_code in {401, 403}:
            status = "authentication_error"
        raise OcrRetryExecutionProviderError(
            f"OpenAI OCR error ({exc.status_code})",
            status=status,
            retry_after=_response_retry_after_from_openai_error(exc),
        ) from exc

    output_text = getattr(response, "output_text", None)
    extracted_text = (
        str(output_text).strip()
        if isinstance(output_text, str) and output_text.strip()
        else "[OCR] No text detected."
    )
    return {
        "status": "ok",
        "provider": "openai",
        "model": ocr_model,
        "extracted_text": extracted_text,
        "extracted_text_preview": _short_text_preview(extracted_text),
        "chars": len(extracted_text),
    }


def _run_default_ocr_retry_request(
    request: dict[str, Any],
    *,
    ocr_provider: str,
    ocr_model: str,
    ocr_prompt: str,
) -> dict[str, Any]:
    provider = (ocr_provider or "scaffold").strip().lower()
    if provider == "openai":
        return _run_openai_ocr_retry_request(
            request,
            ocr_model=ocr_model,
            ocr_prompt=ocr_prompt,
        )
    if provider == "scaffold":
        return _run_scaffold_ocr_retry_request(request)
    raise OcrRetryExecutionProviderError(
        f"unsupported OCR retry provider: {provider}",
        status="provider_not_configured",
    )


def _ocr_retry_execution_requests(
    *,
    run_id: str,
    readiness_report: dict[str, Any],
    ocr_provider: str,
    ocr_model: str,
) -> list[dict[str, Any]]:
    readiness_items = readiness_report.get("execution_readiness_items")
    if not isinstance(readiness_items, list):
        return []
    requests: list[dict[str, Any]] = []
    for item in readiness_items:
        if not isinstance(item, dict) or not item.get("executable"):
            continue
        artifacts = item.get("selected_artifacts")
        if not isinstance(artifacts, list):
            continue
        for artifact in artifacts:
            if not isinstance(artifact, dict) or artifact.get("state") != "ready":
                continue
            payload_inputs = artifact.get("payload_inputs")
            if not isinstance(payload_inputs, dict):
                payload_inputs = {}
            resolved_path = str(artifact.get("resolved_path") or "").strip()
            mime_type = str(
                payload_inputs.get("mime_type")
                or mimetypes.guess_type(resolved_path)[0]
                or "application/octet-stream"
            )
            request_index = len(requests) + 1
            requests.append(
                {
                    "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
                    "run_id": run_id,
                    "request_id": f"{run_id}::{request_index:04d}",
                    "sequence": request_index,
                    "operation": "ocr_retry_rerun_or_case_curation",
                    "selected_action": str(item.get("selected_action") or ""),
                    "shortlist_id": str(item.get("shortlist_id") or ""),
                    "artifact_id": str(artifact.get("artifact_id") or ""),
                    "feedback_ids": item.get("feedback_ids")
                    if isinstance(item.get("feedback_ids"), list)
                    else [],
                    "source_session_id": str(artifact.get("source_session_id") or ""),
                    "session_id": str(artifact.get("session_id") or ""),
                    "ocr_run_id": str(artifact.get("ocr_run_id") or ""),
                    "source": {
                        "resolved_path": resolved_path,
                        "source_image_name": str(
                            artifact.get("source_image_name") or ""
                        ),
                        "mime_type": mime_type,
                        "source_file_exists": bool(artifact.get("source_file_exists")),
                    },
                    "provider": {
                        "name": ocr_provider,
                        "model": ocr_model,
                    },
                    "payload_inputs": payload_inputs,
                    "command_preview": artifact.get("command_preview")
                    if isinstance(artifact.get("command_preview"), dict)
                    else {},
                    "warehouse_mutation": "none",
                }
            )
    return requests


def _normalize_ocr_retry_response(
    *,
    request: dict[str, Any],
    raw_response: dict[str, Any],
) -> dict[str, Any]:
    status = str(raw_response.get("status") or "ok")
    extracted_text = str(raw_response.get("extracted_text") or "")
    return {
        "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
        "run_id": request.get("run_id", ""),
        "request_id": request.get("request_id", ""),
        "artifact_id": request.get("artifact_id", ""),
        "shortlist_id": request.get("shortlist_id", ""),
        "status": status,
        "provider": str(raw_response.get("provider") or ""),
        "model": str(raw_response.get("model") or ""),
        "extracted_text_preview": str(
            raw_response.get("extracted_text_preview")
            or _short_text_preview(extracted_text)
        ),
        "extracted_text_chars": _int_value(
            raw_response.get("chars")
            if "chars" in raw_response
            else len(extracted_text)
        ),
        "retry_after": str(raw_response.get("retry_after") or ""),
        "error": str(raw_response.get("error") or ""),
        "warehouse_mutation": "none",
    }


def _error_ocr_retry_response(
    *,
    request: dict[str, Any],
    exc: Exception,
) -> dict[str, Any]:
    status = "provider_error"
    retry_after = ""
    if isinstance(exc, OcrRetryExecutionProviderError):
        status = exc.status
        retry_after = exc.retry_after
    return {
        "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
        "run_id": request.get("run_id", ""),
        "request_id": request.get("request_id", ""),
        "artifact_id": request.get("artifact_id", ""),
        "shortlist_id": request.get("shortlist_id", ""),
        "status": status,
        "provider": "",
        "model": "",
        "extracted_text_preview": "",
        "extracted_text_chars": 0,
        "retry_after": retry_after,
        "error": str(exc),
        "warehouse_mutation": "none",
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _write_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_ocr_retry_execution_bundle(
    *,
    db_path: Path,
    selection_path: Path | None,
    confirm_token: str,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
    execution_dir: Path | None = None,
    ocr_provider: str = "scaffold",
    ocr_model: str = DEFAULT_OCR_RETRY_MODEL,
    ocr_prompt: str = DEFAULT_OCR_RETRY_PROMPT,
    run_id: str | None = None,
    ocr_runner: OcrRetryRunner | None = None,
) -> dict[str, Any]:
    resolved_selection_path = selection_path.expanduser() if selection_path else None
    resolved_execution_root = (
        execution_dir.expanduser() if execution_dir else DEFAULT_OCR_RETRY_EXECUTION_DIR
    )
    normalized_provider = (ocr_provider or "scaffold").strip().lower()
    normalized_model = (ocr_model or DEFAULT_OCR_RETRY_MODEL).strip()
    normalized_prompt = (ocr_prompt or DEFAULT_OCR_RETRY_PROMPT).strip()

    readiness_report = (
        build_ocr_retry_execution_readiness_report(
            db_path=db_path,
            selection_path=resolved_selection_path,
            outcome=outcome,
            cohort=cohort,
            limit=limit,
            artifact_ids=artifact_ids,
        )
        if resolved_selection_path is not None
        else None
    )

    blockers: list[dict[str, str]] = []
    if resolved_selection_path is None:
        blockers.append(
            _ocr_retry_execution_blocker(
                "missing_selection_path",
                "SELECTION_PATH is required before OCR retry execution.",
            )
        )
    elif not resolved_selection_path.is_file():
        blockers.append(
            _ocr_retry_execution_blocker(
                "selection_path_not_found",
                f"OCR retry selection decision file was not found: {resolved_selection_path}",
            )
        )
    if confirm_token != OCR_RETRY_EXECUTION_CONFIRM_TOKEN:
        blockers.append(
            _ocr_retry_execution_blocker(
                "missing_confirmation",
                "CONFIRM=ocr-retry-execute is required before OCR retry execution.",
            )
        )
    readiness_state = (
        str(readiness_report.get("state") or "unknown")
        if isinstance(readiness_report, dict)
        else "not_checked"
    )
    readiness_counts = (
        readiness_report.get("counts") if isinstance(readiness_report, dict) else {}
    )
    if not isinstance(readiness_counts, dict):
        readiness_counts = {}
    if isinstance(readiness_report, dict) and readiness_state != "ready":
        blockers.append(
            _ocr_retry_execution_blocker(
                "readiness_not_ready",
                f"OCR retry execution readiness is {readiness_state}.",
            )
        )
    if (
        isinstance(readiness_report, dict)
        and readiness_state == "ready"
        and _int_value(readiness_counts.get("executable_items")) < 1
    ):
        blockers.append(
            _ocr_retry_execution_blocker(
                "no_executable_items",
                "No executable OCR retry items were selected.",
            )
        )
    if resolved_execution_root.exists() and not resolved_execution_root.is_dir():
        blockers.append(
            _ocr_retry_execution_blocker(
                "execution_dir_not_directory",
                f"OCR retry execution output path is not a directory: {resolved_execution_root}",
            )
        )
    if blockers:
        return _blocked_ocr_retry_execution_report(
            readiness_report=readiness_report,
            selection_path=resolved_selection_path,
            confirm_token=confirm_token,
            execution_blockers=blockers,
            ocr_provider=normalized_provider,
            ocr_model=normalized_model,
            execution_dir=resolved_execution_root,
        )

    assert readiness_report is not None
    actual_run_id = run_id or (
        f"ocr-retry-{_utc_run_timestamp()}-"
        f"{_selection_file_fingerprint(resolved_selection_path)[:10]}-"
        f"{uuid.uuid4().hex[:8]}"
    )
    run_dir = resolved_execution_root / actual_run_id
    if run_dir.exists():
        return _blocked_ocr_retry_execution_report(
            readiness_report=readiness_report,
            selection_path=resolved_selection_path,
            confirm_token=confirm_token,
            execution_blockers=[
                _ocr_retry_execution_blocker(
                    "execution_run_dir_exists",
                    f"OCR retry execution run directory already exists: {run_dir}",
                )
            ],
            ocr_provider=normalized_provider,
            ocr_model=normalized_model,
            execution_dir=resolved_execution_root,
        )

    requests = _ocr_retry_execution_requests(
        run_id=actual_run_id,
        readiness_report=readiness_report,
        ocr_provider=normalized_provider,
        ocr_model=normalized_model,
    )
    if not requests:
        return _blocked_ocr_retry_execution_report(
            readiness_report=readiness_report,
            selection_path=resolved_selection_path,
            confirm_token=confirm_token,
            execution_blockers=[
                _ocr_retry_execution_blocker(
                    "no_execution_requests",
                    "No OCR retry execution requests could be built.",
                )
            ],
            ocr_provider=normalized_provider,
            ocr_model=normalized_model,
            execution_dir=resolved_execution_root,
        )

    run_dir.mkdir(parents=True)
    files = {
        "manifest": str(run_dir / "manifest.json"),
        "requests": str(run_dir / "requests.jsonl"),
        "responses": str(run_dir / "responses.jsonl"),
        "summary": str(run_dir / "summary.json"),
    }
    manifest = {
        "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
        "run_id": actual_run_id,
        "created_at": datetime.now(UTC).isoformat(),
        "execution_mode": "local_bundle",
        "selection_path": str(resolved_selection_path),
        "selection_fingerprint": _selection_file_fingerprint(resolved_selection_path),
        "readiness_schema_version": readiness_report.get("schema_version", ""),
        "readiness_state": readiness_report.get("state", "unknown"),
        "readiness_counts": readiness_counts,
        "filters": readiness_report.get("filters")
        if isinstance(readiness_report.get("filters"), dict)
        else {},
        "decision_source": readiness_report.get("decision_source")
        if isinstance(readiness_report.get("decision_source"), dict)
        else {},
        "ocr_provider": normalized_provider,
        "ocr_model": normalized_model,
        "request_count": len(requests),
        "mutation_boundary": _ocr_retry_execution_mutation_boundary(),
        "files": files,
    }
    _write_json(run_dir / "manifest.json", manifest)
    _write_jsonl(run_dir / "requests.jsonl", requests)

    runner = ocr_runner or (
        lambda request: _run_default_ocr_retry_request(
            request,
            ocr_provider=normalized_provider,
            ocr_model=normalized_model,
            ocr_prompt=normalized_prompt,
        )
    )
    responses: list[dict[str, Any]] = []
    stop_reason = ""
    for request in requests:
        try:
            responses.append(
                _normalize_ocr_retry_response(
                    request=request,
                    raw_response=runner(request),
                )
            )
        except Exception as exc:  # noqa: BLE001 - provider errors must be recorded
            response = _error_ocr_retry_response(request=request, exc=exc)
            responses.append(response)
            if response["status"] in {"rate_limited", "provider_unavailable"}:
                stop_reason = str(response["status"])
                break

    _write_jsonl(run_dir / "responses.jsonl", responses)
    succeeded = sum(1 for response in responses if response.get("status") == "ok")
    failed = len(responses) - succeeded
    skipped = len(requests) - len(responses)
    state = "completed"
    if failed and succeeded:
        state = "partial_failure"
    elif failed:
        state = "failed"
    summary = {
        "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
        "run_id": actual_run_id,
        "state": state,
        "execution_mode": "local_bundle",
        "selection_path": str(resolved_selection_path),
        "selection_fingerprint": manifest["selection_fingerprint"],
        "readiness_schema_version": manifest["readiness_schema_version"],
        "readiness_state": readiness_report.get("state", "unknown"),
        "ocr_provider": normalized_provider,
        "ocr_model": normalized_model,
        "counts": {
            "readiness_items": _int_value(readiness_counts.get("readiness_items")),
            "executable_items": _int_value(readiness_counts.get("executable_items")),
            "requests": len(requests),
            "responses": len(responses),
            "succeeded": succeeded,
            "failed": failed,
            "skipped_after_stop": skipped,
            "context_only_skipped": _int_value(
                readiness_counts.get("context_only_items")
            ),
        },
        "stop_reason": stop_reason,
        "mutation_boundary": _ocr_retry_execution_mutation_boundary(),
        "output": {
            "written": True,
            "root": str(resolved_execution_root),
            "run_dir": str(run_dir),
            "files": files,
        },
    }
    _write_json(run_dir / "summary.json", summary)
    return summary


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


def _format_confirmation_reasons(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    reason_parts: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        code = str(item.get("code") or "unknown")
        reason = _display_text(item.get("reason"))
        reason_parts.append(f"{code}: {reason}")
    return " | ".join(reason_parts) if reason_parts else "none"


def _format_source_candidate_line(candidate: dict[str, Any]) -> str:
    image_asset = candidate.get("image_asset")
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
    preview = _truncate_text(candidate.get("extracted_text_preview"), max_chars=80)
    return (
        f"ocr={candidate.get('run_id') or 'none'} "
        f"source_image={candidate.get('source_image_name') or 'none'} "
        f"source_message={candidate.get('source_message_id') or 'none'} "
        f"result_message={candidate.get('result_message_id') or 'none'} "
        f"status={candidate.get('status') or 'none'} "
        f"image_status={image_asset.get('status') or 'unknown'} "
        f"resolved={'yes' if image_asset.get('resolved') else 'no'} "
        f"thumbnail={thumbnail_text} "
        f"preview={preview or 'none'}"
    )


def format_ocr_retry_source_verification_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry source verification: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('verification_items'))} "
        "needs_review="
        f"{_int_value(counts.get('needs_review_verification_items'))} "
        f"source_candidates={_int_value(counts.get('source_candidates'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    verification_items = report.get("verification_items")
    if not isinstance(verification_items, list) or not verification_items:
        lines.append("verification_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in verification_items:
        if not isinstance(item, dict):
            continue
        readiness = item.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        confirmation = item.get("confirmation")
        if not isinstance(confirmation, dict):
            confirmation = {}
        source_candidates = item.get("source_candidates")
        if not isinstance(source_candidates, list):
            source_candidates = []
        reasons = confirmation.get("reasons")
        lines.extend(
            [
                "- "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                f"confirmation={confirmation.get('state') or 'unknown'} "
                f"ocr_runs={_int_value(item.get('same_session_ocr_runs'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)} "
                "explicit_links="
                f"{_int_value(readiness.get('explicit_feedback_to_result_links'))} "
                "unlinked_feedback="
                f"{_int_value(readiness.get('unlinked_feedback_rows'))}",
                f"  reasons={_format_confirmation_reasons(reasons)}",
            ]
        )
        feedback_rows = item.get("feedback_rows")
        if not isinstance(feedback_rows, list):
            feedback_rows = []
        if feedback_rows:
            lines.append("  feedback_rows:")
        for row in feedback_rows:
            if not isinstance(row, dict):
                continue
            lines.extend(
                [
                    "  - "
                    f"feedback={_int_value(row.get('feedback_id'))} "
                    f"message={row.get('message_id') or 'unknown'} "
                    f"outcome={row.get('outcome') or 'unknown'}",
                    f"    note={_display_text(row.get('note'))}",
                    "    recommended_action="
                    f"{_display_text(row.get('recommended_action'))}",
                    f"    action_taken={_display_text(row.get('action_taken'))}",
                ]
            )
        context_rows = [
            candidate
            for candidate in source_candidates[:OCR_RETRY_TERMINAL_CONTEXT_LIMIT]
            if isinstance(candidate, dict)
        ]
        if context_rows:
            lines.append("  source_candidates:")
            for candidate in context_rows:
                lines.append(f"  - {_format_source_candidate_line(candidate)}")
            hidden_rows = len(source_candidates) - len(context_rows)
            if hidden_rows > 0:
                lines.append(f"  source_candidates_more={hidden_rows}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)


def _format_source_message_ref(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    state = str(value.get("state") or "unknown")
    if state == "empty":
        return "none"
    if state != "found":
        return state
    preview = _truncate_text(value.get("content_preview"), max_chars=80)
    return (
        f"found role={value.get('role') or 'unknown'} "
        f"chars={_int_value(value.get('content_chars'))} "
        f"preview={preview or 'none'}"
    )


def _format_ocr_message_provenance_line(item: dict[str, Any]) -> str:
    return (
        f"ocr={item.get('run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"source_message={item.get('source_message_id') or 'none'} "
        f"source_state={_format_source_message_ref(item.get('source_message'))} "
        f"result_message={item.get('result_message_id') or 'none'} "
        f"result_state={_format_source_message_ref(item.get('result_message'))} "
        "exact_feedback_link="
        f"{'yes' if item.get('exact_feedback_result_link') else 'no'}"
    )


def format_ocr_retry_source_provenance_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry source provenance: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('provenance_items'))} "
        "source_history="
        f"{_int_value(counts.get('source_history_available'))}/"
        f"{_int_value(counts.get('provenance_items'))} "
        "feedback_sources="
        f"{_int_value(counts.get('feedback_messages_found'))}/"
        f"{_int_value(counts.get('feedback_messages'))} "
        f"ocr_runs={_int_value(counts.get('ocr_runs'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    provenance_items = report.get("provenance_items")
    if not isinstance(provenance_items, list) or not provenance_items:
        lines.append("provenance_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in provenance_items:
        if not isinstance(item, dict):
            continue
        source_history = item.get("source_history")
        if not isinstance(source_history, dict):
            source_history = {}
        item_counts = item.get("counts")
        if not isinstance(item_counts, dict):
            item_counts = {}
        lines.extend(
            [
                "- "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                f"source_history={source_history.get('state') or 'unknown'} "
                "feedback_sources="
                f"{_int_value(item_counts.get('feedback_messages_found'))}/"
                f"{_int_value(item_counts.get('feedback_messages'))} "
                f"ocr_runs={_int_value(item_counts.get('ocr_runs'))} "
                "exact_links="
                f"{_int_value(item_counts.get('exact_feedback_result_links'))}",
                f"  title={_display_text(item.get('title'))}",
                f"  source_history_db={source_history.get('path') or 'unknown'}",
            ]
        )
        feedback_messages = item.get("feedback_messages")
        if not isinstance(feedback_messages, list):
            feedback_messages = []
        if feedback_messages:
            lines.append("  feedback_messages:")
        for row in feedback_messages:
            if not isinstance(row, dict):
                continue
            lines.append(
                "  - "
                f"feedback={_int_value(row.get('feedback_id'))} "
                f"message={row.get('message_id') or 'unknown'} "
                f"source_state={_format_source_message_ref(row.get('source_message'))}"
            )
        ocr_rows = item.get("ocr_message_provenance")
        if not isinstance(ocr_rows, list):
            ocr_rows = []
        context_rows = [
            row
            for row in ocr_rows[:OCR_RETRY_TERMINAL_CONTEXT_LIMIT]
            if isinstance(row, dict)
        ]
        if context_rows:
            lines.append("  ocr_message_provenance:")
            for row in context_rows:
                lines.append(f"  - {_format_ocr_message_provenance_line(row)}")
            hidden_rows = len(ocr_rows) - len(context_rows)
            if hidden_rows > 0:
                lines.append(f"  ocr_message_provenance_more={hidden_rows}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)


def _format_input_blocker_state(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    state = str(value.get("state") or "unknown")
    reason_code = str(value.get("reason_code") or "")
    next_action = str(value.get("next_action") or "")
    if not reason_code and not next_action:
        return state
    parts = [state]
    if reason_code:
        parts.append(f"reason={reason_code}")
    if next_action:
        parts.append(f"next={next_action}")
    return " ".join(parts)


def _format_ocr_retry_input_line(item: dict[str, Any]) -> str:
    image_asset = item.get("image_asset")
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
    preview = _truncate_text(item.get("extracted_text_preview"), max_chars=80)
    return (
        f"ocr={item.get('run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"image_status={image_asset.get('status') or 'unknown'} "
        f"resolved={'yes' if image_asset.get('resolved') else 'no'} "
        f"thumbnail={thumbnail_text} "
        f"source_message={item.get('source_message_id') or 'none'} "
        f"result_message={item.get('result_message_id') or 'none'} "
        "exact_feedback_link="
        f"{'yes' if item.get('exact_feedback_result_link') else 'no'} "
        f"preview={preview or 'none'}"
    )


def format_ocr_retry_input_packet_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry input packet: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('input_items'))} "
        f"blocked={_int_value(counts.get('blocked_input_items'))} "
        "feedback_inputs="
        f"{_int_value(counts.get('feedback_sources_found'))}/"
        f"{_int_value(counts.get('feedback_inputs'))} "
        f"rerun_inputs={_int_value(counts.get('rerun_inputs'))} "
        "resolved="
        f"{_int_value(counts.get('resolved_rerun_inputs'))}/"
        f"{_int_value(counts.get('rerun_inputs'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    input_items = report.get("input_items")
    if not isinstance(input_items, list) or not input_items:
        lines.append("input_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in input_items:
        if not isinstance(item, dict):
            continue
        readiness = item.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        item_counts = item.get("counts")
        if not isinstance(item_counts, dict):
            item_counts = {}
        lines.extend(
            [
                "- "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                f"blocker={_format_input_blocker_state(item.get('blocker_state'))} "
                f"rerun_inputs={_int_value(item_counts.get('rerun_inputs'))} "
                "exact_links="
                f"{_int_value(item_counts.get('exact_feedback_result_links'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)} "
                "explicit_links="
                f"{_int_value(readiness.get('explicit_feedback_to_result_links'))} "
                "unlinked_feedback="
                f"{_int_value(readiness.get('unlinked_feedback_rows'))}",
            ]
        )
        feedback_inputs = item.get("feedback_inputs")
        if not isinstance(feedback_inputs, list):
            feedback_inputs = []
        if feedback_inputs:
            lines.append("  feedback_inputs:")
        for row in feedback_inputs:
            if not isinstance(row, dict):
                continue
            lines.extend(
                [
                    "  - "
                    f"feedback={_int_value(row.get('feedback_id'))} "
                    f"message={row.get('message_id') or 'unknown'} "
                    "source_state="
                    f"{_format_source_message_ref(row.get('source_message'))}",
                    f"    note={_display_text(row.get('note'))}",
                    "    recommended_action="
                    f"{_display_text(row.get('recommended_action'))}",
                ]
            )
        rerun_inputs = item.get("rerun_inputs")
        if not isinstance(rerun_inputs, list):
            rerun_inputs = []
        context_rows = [
            row
            for row in rerun_inputs[:OCR_RETRY_TERMINAL_CONTEXT_LIMIT]
            if isinstance(row, dict)
        ]
        if context_rows:
            lines.append("  rerun_inputs:")
            for row in context_rows:
                lines.append(f"  - {_format_ocr_retry_input_line(row)}")
            hidden_rows = len(rerun_inputs) - len(context_rows)
            if hidden_rows > 0:
                lines.append(f"  rerun_inputs_more={hidden_rows}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)


def _format_manifest_selection_gate(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    state = str(value.get("state") or "unknown")
    reason_code = str(value.get("reason_code") or "")
    next_action = str(value.get("next_action") or "")
    parts = [state]
    if reason_code:
        parts.append(f"reason={reason_code}")
    if next_action:
        parts.append(f"next={next_action}")
    return " ".join(parts)


def _format_manifest_feedback_preview(item: dict[str, Any]) -> str:
    return (
        f"feedback={_int_value(item.get('feedback_id'))} "
        f"message={item.get('message_id') or 'unknown'} "
        f"source_state={item.get('source_state') or 'unknown'} "
        f"role={item.get('source_role') or 'unknown'} "
        "preview="
        f"{_truncate_text(item.get('source_preview'), max_chars=100) or 'none'}"
    )


def _format_manifest_source_artifact_line(item: dict[str, Any]) -> str:
    image = item.get("image")
    if not isinstance(image, dict):
        image = {}
    thumbnail = image.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    thumbnail_text = "none"
    if thumbnail.get("available"):
        thumbnail_text = (
            f"{_int_value(thumbnail.get('width'))}x"
            f"{_int_value(thumbnail.get('height'))}"
        )
    preview = _truncate_text(item.get("ocr_text_preview"), max_chars=80)
    return (
        f"ocr={item.get('run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"image_status={image.get('status') or 'unknown'} "
        f"resolved={'yes' if image.get('resolved') else 'no'} "
        f"thumbnail={thumbnail_text} "
        f"source_message={item.get('source_message_id') or 'none'} "
        f"result_message={item.get('result_message_id') or 'none'} "
        "exact_feedback_link="
        f"{'yes' if item.get('exact_feedback_result_link') else 'no'} "
        f"preview={preview or 'none'}"
    )


def format_ocr_retry_rerun_manifest_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    source_artifacts = _int_value(counts.get("source_artifacts"))
    resolved_source_artifacts = _int_value(counts.get("resolved_source_artifacts"))
    lines = [
        "manual eval OCR retry rerun manifest: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('manifest_items'))} "
        f"selection_ready={_int_value(counts.get('selection_ready_items'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        f"feedback_inputs={_int_value(counts.get('feedback_inputs'))} "
        f"source_artifacts={source_artifacts} "
        f"resolved={resolved_source_artifacts}/{source_artifacts} "
        f"thumbnails={_int_value(counts.get('artifacts_with_thumbnail'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    manifest_items = report.get("manifest_items")
    if not isinstance(manifest_items, list) or not manifest_items:
        lines.append("manifest_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in manifest_items:
        if not isinstance(item, dict):
            continue
        item_counts = item.get("counts")
        if not isinstance(item_counts, dict):
            item_counts = {}
        readiness = item.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        lines.extend(
            [
                "- "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                "selection="
                f"{_format_manifest_selection_gate(item.get('selection_gate'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                "source_artifacts="
                f"{_int_value(item_counts.get('source_artifacts'))} "
                "resolved="
                f"{_int_value(item_counts.get('resolved_source_artifacts'))}/"
                f"{_int_value(item_counts.get('source_artifacts'))} "
                "thumbnails="
                f"{_int_value(item_counts.get('artifacts_with_thumbnail'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)}",
            ]
        )

        feedback_previews = item.get("feedback_source_previews")
        if not isinstance(feedback_previews, list):
            feedback_previews = []
        artifacts = item.get("source_artifacts")
        if not isinstance(artifacts, list):
            artifacts = []
        preview_by_feedback = {
            _int_value(preview.get("feedback_id")): preview
            for preview in feedback_previews
            if isinstance(preview, dict)
        }
        if preview_by_feedback:
            lines.append("  source_previews:")
            for preview in preview_by_feedback.values():
                lines.append(f"  - {_format_manifest_feedback_preview(preview)}")

        context_rows = [row for row in artifacts[:OCR_RETRY_TERMINAL_CONTEXT_LIMIT]]
        if context_rows:
            lines.append("  source_artifacts:")
            for row in context_rows:
                if isinstance(row, dict):
                    lines.append(f"  - {_format_manifest_source_artifact_line(row)}")
            hidden_rows = len(artifacts) - len(context_rows)
            if hidden_rows > 0:
                lines.append(f"  source_artifacts_more={hidden_rows}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)


def _format_plan_thumbnail(value: object) -> str:
    if not isinstance(value, dict) or not value.get("available"):
        return "none"
    return f"{_int_value(value.get('width'))}x{_int_value(value.get('height'))}"


def _format_plan_artifact_line(item: dict[str, Any]) -> str:
    preview = _truncate_text(item.get("ocr_text_preview"), max_chars=80)
    return (
        f"artifact={item.get('artifact_id') or 'none'} "
        f"action={item.get('action') or 'unknown'} "
        f"preview_only={'yes' if item.get('preview_only') else 'no'} "
        f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
        f"ocr={item.get('ocr_run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
        f"source_path={item.get('resolved_path') or 'none'} "
        f"ocr_preview={preview or 'none'}"
    )


def _format_plan_source_preview(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    preview = _truncate_text(value.get("source_preview"), max_chars=100)
    return (
        f"feedback={_int_value(value.get('feedback_id'))} "
        f"message={value.get('message_id') or 'unknown'} "
        f"source_state={value.get('source_state') or 'unknown'} "
        f"role={value.get('source_role') or 'unknown'} "
        f"preview={preview or 'none'}"
    )


def format_ocr_retry_rerun_plan_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry rerun plan: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('plan_items'))} "
        f"planned_artifacts={_int_value(counts.get('planned_source_artifacts'))} "
        "resolved="
        f"{_int_value(counts.get('resolved_source_artifacts'))}/"
        f"{_int_value(counts.get('source_artifacts'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"selection={filters.get('selection_mode') or 'unknown'} "
        f"requested_artifacts={_int_value(counts.get('requested_artifact_ids'))} "
        f"unmatched={_int_value(counts.get('unmatched_artifact_ids'))} "
        f"preview_only={'yes' if counts.get('preview_only') else 'no'} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    unmatched_artifact_ids = report.get("unmatched_artifact_ids")
    if isinstance(unmatched_artifact_ids, list) and unmatched_artifact_ids:
        lines.append(
            "unmatched_artifact_ids: "
            + ",".join(str(item) for item in unmatched_artifact_ids)
        )

    plan_items = report.get("plan_items")
    if not isinstance(plan_items, list) or not plan_items:
        lines.append("plan_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in plan_items:
        if not isinstance(item, dict):
            continue
        item_counts = item.get("counts")
        if not isinstance(item_counts, dict):
            item_counts = {}
        readiness = item.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        lines.extend(
            [
                "- "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                "selection="
                f"{_format_manifest_selection_gate(item.get('selection_gate'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                f"plan_artifacts={_int_value(item_counts.get('plan_artifacts'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)}",
            ]
        )
        plan_artifacts = item.get("plan_artifacts")
        if not isinstance(plan_artifacts, list):
            plan_artifacts = []
        for artifact in plan_artifacts:
            if not isinstance(artifact, dict):
                continue
            lines.append(f"  - {_format_plan_artifact_line(artifact)}")
            lines.append(
                "    source_preview="
                f"{_format_plan_source_preview(artifact.get('feedback_source_preview'))}"
            )
            payload = artifact.get("payload_inputs")
            if isinstance(payload, dict):
                lines.append(
                    "    payload="
                    f"artifact_id={payload.get('artifact_id') or 'none'} "
                    f"operation={payload.get('operation') or 'unknown'} "
                    f"source_path={payload.get('resolved_path') or 'none'}"
                )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)


def _format_selection_decision(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    allowed_actions = value.get("allowed_actions")
    if isinstance(allowed_actions, list):
        actions_text = ",".join(str(item) for item in allowed_actions)
    else:
        actions_text = "none"
    parts = [str(value.get("state") or "unknown")]
    if actions_text:
        parts.append(f"actions={actions_text}")
    reason_code = str(value.get("reason_code") or "")
    next_action = str(value.get("next_action") or "")
    if reason_code:
        parts.append(f"reason={reason_code}")
    if next_action:
        parts.append(f"next={next_action}")
    return " ".join(parts)


def _format_selection_candidate_line(item: dict[str, Any]) -> str:
    preview = _truncate_text(item.get("ocr_text_preview"), max_chars=80)
    return (
        f"artifact={item.get('artifact_id') or 'none'} "
        f"action={item.get('action') or 'unknown'} "
        f"preview_only={'yes' if item.get('preview_only') else 'no'} "
        f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
        f"ocr={item.get('ocr_run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
        f"source_path={item.get('resolved_path') or 'none'} "
        f"ocr_preview={preview or 'none'}"
    )


def format_ocr_retry_selection_review_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry selection review: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('shortlist_items'))} "
        f"planned_artifacts={_int_value(counts.get('planned_source_artifacts'))} "
        "collapsed_duplicates="
        f"{_int_value(counts.get('collapsed_duplicate_source_artifacts'))} "
        f"candidate_runs={_int_value(counts.get('candidate_ocr_runs'))} "
        f"decision_pending={_int_value(counts.get('decision_pending_items'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"selection={filters.get('selection_mode') or 'unknown'} "
        f"requested_artifacts={_int_value(counts.get('requested_artifact_ids'))} "
        f"unmatched={_int_value(counts.get('unmatched_artifact_ids'))} "
        f"preview_only={'yes' if counts.get('preview_only') else 'no'} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    unmatched_artifact_ids = report.get("unmatched_artifact_ids")
    if isinstance(unmatched_artifact_ids, list) and unmatched_artifact_ids:
        lines.append(
            "unmatched_artifact_ids: "
            + ",".join(str(item) for item in unmatched_artifact_ids)
        )

    selection_items = report.get("selection_review_items")
    if not isinstance(selection_items, list) or not selection_items:
        lines.append("selection_review_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in selection_items:
        if not isinstance(item, dict):
            continue
        item_counts = item.get("counts")
        if not isinstance(item_counts, dict):
            item_counts = {}
        readiness = item.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        lines.extend(
            [
                "- "
                f"shortlist={item.get('shortlist_id') or 'unknown'} "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                "decision="
                f"{_format_selection_decision(item.get('selection_decision'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                f"source_image={item.get('source_image_name') or 'none'} "
                f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
                "candidate_runs="
                f"{_int_value(item_counts.get('candidate_ocr_runs'))} "
                "duplicate_artifacts="
                f"{_int_value(item_counts.get('duplicate_source_artifacts'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)}",
                f"  source_path={item.get('resolved_path') or 'none'}",
                "  source_preview="
                f"{_format_plan_source_preview(item.get('source_preview'))}",
            ]
        )
        candidate_rows = item.get("candidate_ocr_runs")
        if not isinstance(candidate_rows, list):
            candidate_rows = []
        if candidate_rows:
            lines.append("  candidate_ocr_runs:")
            for candidate in candidate_rows:
                if isinstance(candidate, dict):
                    lines.append(f"  - {_format_selection_candidate_line(candidate)}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)


def _format_template_decision_input(value: object) -> str:
    if not isinstance(value, dict):
        return "selected_action=unknown allowed=none"
    allowed_actions = value.get("allowed_actions")
    if isinstance(allowed_actions, list):
        allowed_text = ",".join(str(item) for item in allowed_actions)
    else:
        allowed_text = "none"
    selected_ids = value.get("selected_artifact_ids")
    if isinstance(selected_ids, list) and selected_ids:
        selected_text = ",".join(str(item) for item in selected_ids)
    else:
        selected_text = "none"
    return (
        f"selected_action={value.get('selected_action') or 'unknown'} "
        f"allowed={allowed_text or 'none'} "
        f"selected_artifacts={selected_text}"
    )


def _format_template_candidate_line(item: dict[str, Any]) -> str:
    preview = _truncate_text(item.get("ocr_text_preview"), max_chars=80)
    return (
        f"artifact={item.get('artifact_id') or 'none'} "
        f"ocr={item.get('ocr_run_id') or 'none'} "
        f"action={item.get('action') or 'unknown'} "
        f"preview_only={'yes' if item.get('preview_only') else 'no'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
        f"source_path={item.get('resolved_path') or 'none'} "
        f"ocr_preview={preview or 'none'}"
    )


def format_ocr_retry_selection_template_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry selection template: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('template_items'))} "
        f"shortlist={_int_value(counts.get('shortlist_items'))} "
        f"candidate_artifacts={_int_value(counts.get('candidate_artifacts'))} "
        "collapsed_duplicates="
        f"{_int_value(counts.get('collapsed_duplicate_source_artifacts'))} "
        f"undecided={_int_value(counts.get('default_undecided_items'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"selection={filters.get('selection_mode') or 'unknown'} "
        f"requested_artifacts={_int_value(counts.get('requested_artifact_ids'))} "
        f"unmatched={_int_value(counts.get('unmatched_artifact_ids'))} "
        f"preview_only={'yes' if counts.get('preview_only') else 'no'} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    unmatched_artifact_ids = report.get("unmatched_artifact_ids")
    if isinstance(unmatched_artifact_ids, list) and unmatched_artifact_ids:
        lines.append(
            "unmatched_artifact_ids: "
            + ",".join(str(item) for item in unmatched_artifact_ids)
        )

    template = report.get("selection_template")
    if not isinstance(template, dict):
        template = {}
    template_items = template.get("items")
    if not isinstance(template_items, list) or not template_items:
        lines.append("selection_template_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in template_items:
        if not isinstance(item, dict):
            continue
        item_counts = item.get("counts")
        if not isinstance(item_counts, dict):
            item_counts = {}
        readiness = item.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        lines.extend(
            [
                "- "
                f"shortlist={item.get('shortlist_id') or 'unknown'} "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                f"{_format_template_decision_input(item.get('decision_input'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                f"source_image={item.get('source_image_name') or 'none'} "
                f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
                "candidate_artifacts="
                f"{_int_value(item_counts.get('candidate_artifacts'))} "
                "duplicate_artifacts="
                f"{_int_value(item_counts.get('duplicate_source_artifacts'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)}",
                f"  source_path={item.get('resolved_path') or 'none'}",
                "  source_preview="
                f"{_format_plan_source_preview(item.get('source_preview'))}",
                "  fill_template="
                "selected_action=<rerun_input|curated_case|context_only> "
                "selected_artifact_ids=<artifact_id,...> rationale=<text>",
            ]
        )
        candidate_rows = item.get("candidate_artifacts")
        if not isinstance(candidate_rows, list):
            candidate_rows = []
        if candidate_rows:
            lines.append("  candidate_artifacts:")
            for candidate in candidate_rows:
                if isinstance(candidate, dict):
                    lines.append(f"  - {_format_template_candidate_line(candidate)}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)


def format_ocr_retry_selection_decision_draft_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}
    output = report.get("output")
    if not isinstance(output, dict):
        output = {}
    next_commands = report.get("next_commands")
    if not isinstance(next_commands, dict):
        next_commands = {}

    lines = [
        "manual eval OCR retry selection decision draft: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('draft_items'))} "
        f"shortlist={_int_value(counts.get('shortlist_items'))} "
        f"candidate_artifacts={_int_value(counts.get('candidate_artifacts'))} "
        "collapsed_duplicates="
        f"{_int_value(counts.get('collapsed_duplicate_source_artifacts'))} "
        f"undecided={_int_value(counts.get('default_undecided_items'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"selection={filters.get('selection_mode') or 'unknown'} "
        f"requested_artifacts={_int_value(counts.get('requested_artifact_ids'))} "
        f"unmatched={_int_value(counts.get('unmatched_artifact_ids'))} "
        f"preview_only={'yes' if counts.get('preview_only') else 'no'} "
        f"force={'yes' if output.get('force') else 'no'} "
        f"overwritten={'yes' if output.get('overwritten') else 'no'} "
        f"local_only={'yes' if output.get('local_only') else 'no'} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')} "
        f"output={output.get('path') or 'none'} "
        f"fingerprint={report.get('template_fingerprint') or 'none'}",
    ]
    validate_command = str(next_commands.get("validate") or "")
    apply_preview_command = str(next_commands.get("apply_preview") or "")
    if validate_command:
        lines.append(f"next_validate={validate_command}")
    if apply_preview_command:
        lines.append(f"next_apply_preview={apply_preview_command}")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def _format_validation_issues(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    return ",".join(str(item) for item in value)


def _format_validation_artifact_ids(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    return ",".join(str(item) for item in value)


def format_ocr_retry_selection_validation_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    decision_source = report.get("decision_source")
    if not isinstance(decision_source, dict):
        decision_source = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    lines = [
        "manual eval OCR retry selection validation: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('shortlist_items'))} "
        f"candidate_artifacts={_int_value(counts.get('candidate_artifacts'))} "
        f"submitted={_int_value(counts.get('submitted_decisions'))} "
        f"valid={_int_value(counts.get('valid_decisions'))} "
        f"pending={_int_value(counts.get('pending_decisions'))} "
        f"invalid={_int_value(counts.get('invalid_decisions'))} "
        f"missing={_int_value(counts.get('missing_decisions'))} "
        f"stale={_int_value(counts.get('stale_decisions'))} "
        f"duplicates={_int_value(counts.get('duplicate_decisions'))} "
        f"selected_artifacts={_int_value(counts.get('selected_artifacts'))} "
        "invalid_artifacts="
        f"{_int_value(counts.get('invalid_selected_artifacts'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"selection={filters.get('selection_mode') or 'unknown'} "
        f"requested_artifacts={_int_value(counts.get('requested_artifact_ids'))} "
        f"unmatched={_int_value(counts.get('unmatched_artifact_ids'))} "
        f"preview_only={'yes' if counts.get('preview_only') else 'no'} "
        f"decision_source={decision_source.get('state') or 'unknown'} "
        f"decision_path={decision_source.get('path') or 'none'} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    unmatched_artifact_ids = report.get("unmatched_artifact_ids")
    if isinstance(unmatched_artifact_ids, list) and unmatched_artifact_ids:
        lines.append(
            "unmatched_artifact_ids: "
            + ",".join(str(item) for item in unmatched_artifact_ids)
        )

    validation_items = report.get("selection_validation_items")
    if not isinstance(validation_items, list) or not validation_items:
        lines.append("selection_validation_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in validation_items:
        if not isinstance(item, dict):
            continue
        lines.append(
            "- "
            f"shortlist={item.get('shortlist_id') or 'none'} "
            f"state={item.get('state') or 'unknown'} "
            f"action={item.get('selected_action') or 'undecided'} "
            f"issues={_format_validation_issues(item.get('issues'))} "
            "feedback="
            f"{_format_feedback_ids(item.get('feedback_ids'))} "
            "closure="
            f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
            "selected_artifacts="
            f"{_format_validation_artifact_ids(item.get('selected_artifact_ids'))} "
            "invalid_artifacts="
            f"{_format_validation_artifact_ids(item.get('invalid_selected_artifact_ids'))} "
            "candidate_artifacts="
            f"{_format_validation_artifact_ids(item.get('candidate_artifact_ids'))} "
            f"source_image={item.get('source_image_name') or 'none'} "
            f"source_path={item.get('resolved_path') or 'none'} "
            f"preview_only={'yes' if item.get('preview_only') else 'no'}"
        )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def _format_apply_selected_artifact_line(item: dict[str, Any]) -> str:
    preview = _truncate_text(item.get("ocr_text_preview"), max_chars=80)
    command = item.get("command_preview")
    if not isinstance(command, dict):
        command = {}
    return (
        f"artifact={item.get('artifact_id') or 'none'} "
        f"ocr={item.get('ocr_run_id') or 'none'} "
        f"session={item.get('session_id') or 'none'} "
        f"source_session={item.get('source_session_id') or 'none'} "
        f"preview_only={'yes' if item.get('preview_only') else 'no'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
        f"source_path={item.get('resolved_path') or 'none'} "
        f"command={command.get('mode') or 'payload_only'} "
        f"ocr_preview={preview or 'none'}"
    )


def format_ocr_retry_selection_apply_preview_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    decision_source = report.get("decision_source")
    if not isinstance(decision_source, dict):
        decision_source = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    lines = [
        "manual eval OCR retry selection apply preview: "
        f"state={report.get('state', 'unknown')} "
        f"validation={report.get('validation_state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('shortlist_items'))} "
        f"candidate_artifacts={_int_value(counts.get('candidate_artifacts'))} "
        f"submitted={_int_value(counts.get('submitted_decisions'))} "
        f"valid={_int_value(counts.get('valid_decisions'))} "
        f"pending={_int_value(counts.get('pending_decisions'))} "
        f"invalid={_int_value(counts.get('invalid_decisions'))} "
        f"missing={_int_value(counts.get('missing_decisions'))} "
        f"stale={_int_value(counts.get('stale_decisions'))} "
        f"duplicates={_int_value(counts.get('duplicate_decisions'))} "
        f"blocked={_int_value(counts.get('blocked_by_validation'))} "
        f"preview_items={_int_value(counts.get('preview_items'))} "
        f"rerun_input={_int_value(counts.get('rerun_input_items'))} "
        f"curated_case={_int_value(counts.get('curated_case_items'))} "
        f"context_only={_int_value(counts.get('context_only_items'))} "
        f"selected_artifacts={_int_value(counts.get('selected_artifacts'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"selection={filters.get('selection_mode') or 'unknown'} "
        f"requested_artifacts={_int_value(counts.get('requested_artifact_ids'))} "
        f"unmatched={_int_value(counts.get('unmatched_artifact_ids'))} "
        f"preview_only={'yes' if counts.get('preview_only') else 'no'} "
        f"decision_source={decision_source.get('state') or 'unknown'} "
        f"decision_path={decision_source.get('path') or 'none'} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    blockers = report.get("validation_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("validation_blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"shortlist={blocker.get('shortlist_id') or 'none'} "
                f"state={blocker.get('state') or 'unknown'} "
                f"action={blocker.get('selected_action') or 'undecided'} "
                f"issues={_format_validation_issues(blocker.get('issues'))} "
                f"feedback={_format_feedback_ids(blocker.get('feedback_ids'))} "
                "selected_artifacts="
                f"{_format_validation_artifact_ids(blocker.get('selected_artifact_ids'))} "
                "invalid_artifacts="
                f"{_format_validation_artifact_ids(blocker.get('invalid_selected_artifact_ids'))}"
            )
    preview = report.get("application_preview")
    if not isinstance(preview, dict):
        preview = {}
    items = preview.get("items")
    if not isinstance(items, list) or not items:
        lines.append("application_preview_items: none")
    else:
        for item in items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"action={item.get('selected_action') or 'unknown'} "
                f"shortlist={item.get('shortlist_id') or 'none'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                "selected_artifacts="
                f"{_format_validation_artifact_ids(item.get('selected_artifact_ids'))} "
                f"source_image={item.get('source_image_name') or 'none'} "
                f"source_path={item.get('resolved_path') or 'none'} "
                f"mutation={item.get('mutation') or 'none'} "
                f"execution={item.get('execution') or 'none'} "
                f"preview_only={'yes' if item.get('preview_only') else 'no'}"
            )
            selected_artifacts = item.get("selected_artifacts")
            if isinstance(selected_artifacts, list) and selected_artifacts:
                lines.append("  selected_artifacts:")
                for artifact in selected_artifacts:
                    if isinstance(artifact, dict):
                        lines.append(
                            f"  - {_format_apply_selected_artifact_line(artifact)}"
                        )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def _format_execution_readiness_artifact(item: dict[str, Any]) -> str:
    command = item.get("command_preview")
    if not isinstance(command, dict):
        command = {}
    payload = item.get("payload_inputs")
    if not isinstance(payload, dict):
        payload = {}
    return (
        f"artifact={item.get('artifact_id') or 'none'} "
        f"state={item.get('state') or 'unknown'} "
        f"issues={_format_validation_issues(item.get('issues'))} "
        f"source_exists={'yes' if item.get('source_file_exists') else 'no'} "
        f"ocr={item.get('ocr_run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"source_path={item.get('resolved_path') or 'none'} "
        f"operation={payload.get('operation') or 'none'} "
        f"command={command.get('mode') or 'payload_only'}"
    )


def format_ocr_retry_execution_readiness_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    decision_source = report.get("decision_source")
    if not isinstance(decision_source, dict):
        decision_source = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    lines = [
        "manual eval OCR retry execution readiness: "
        f"state={report.get('state', 'unknown')} "
        f"validation={report.get('validation_state', 'unknown')} "
        f"apply_preview={report.get('apply_preview_state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('shortlist_items'))} "
        f"candidate_artifacts={_int_value(counts.get('candidate_artifacts'))} "
        f"submitted={_int_value(counts.get('submitted_decisions'))} "
        f"valid={_int_value(counts.get('valid_decisions'))} "
        f"pending={_int_value(counts.get('pending_decisions'))} "
        f"invalid={_int_value(counts.get('invalid_decisions'))} "
        f"validation_blocked={_int_value(counts.get('blocked_by_validation'))} "
        f"apply_items={_int_value(counts.get('apply_preview_items'))} "
        f"ready={_int_value(counts.get('ready_items'))} "
        f"executable={_int_value(counts.get('executable_items'))} "
        f"blocked={_int_value(counts.get('blocked_items'))} "
        f"rerun_input={_int_value(counts.get('rerun_input_items'))} "
        f"curated_case={_int_value(counts.get('curated_case_items'))} "
        f"context_only={_int_value(counts.get('context_only_items'))} "
        f"selected_artifacts={_int_value(counts.get('selected_artifacts'))} "
        f"source_files_ready={_int_value(counts.get('source_files_ready'))} "
        f"source_files_missing={_int_value(counts.get('source_files_missing'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        f"selection={filters.get('selection_mode') or 'unknown'} "
        f"requested_artifacts={_int_value(counts.get('requested_artifact_ids'))} "
        f"unmatched={_int_value(counts.get('unmatched_artifact_ids'))} "
        f"preview_only={'yes' if counts.get('preview_only') else 'no'} "
        f"decision_source={decision_source.get('state') or 'unknown'} "
        f"decision_path={decision_source.get('path') or 'none'} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    validation_blockers = report.get("validation_blockers")
    if isinstance(validation_blockers, list) and validation_blockers:
        lines.append("validation_blockers:")
        for blocker in validation_blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"shortlist={blocker.get('shortlist_id') or 'none'} "
                f"state={blocker.get('state') or 'unknown'} "
                f"issues={_format_validation_issues(blocker.get('issues'))} "
                f"feedback={_format_feedback_ids(blocker.get('feedback_ids'))}"
            )

    readiness_items = report.get("execution_readiness_items")
    if not isinstance(readiness_items, list) or not readiness_items:
        lines.append("execution_readiness_items: none")
    else:
        for item in readiness_items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"action={item.get('selected_action') or 'unknown'} "
                f"shortlist={item.get('shortlist_id') or 'none'} "
                f"readiness={item.get('state') or 'unknown'} "
                f"executable={'yes' if item.get('executable') else 'no'} "
                f"issues={_format_validation_issues(item.get('issues'))} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                "selected_artifacts="
                f"{_format_validation_artifact_ids(item.get('selected_artifact_ids'))} "
                f"source_image={item.get('source_image_name') or 'none'} "
                f"source_path={item.get('resolved_path') or 'none'} "
                f"gate={item.get('execution_gate') or 'none'} "
                f"mutation={item.get('mutation') or 'none'} "
                f"execution={item.get('execution') or 'none'} "
                f"preview_only={'yes' if item.get('preview_only') else 'no'}"
            )
            selected_artifacts = item.get("selected_artifacts")
            if isinstance(selected_artifacts, list) and selected_artifacts:
                lines.append("  selected_artifacts:")
                for artifact in selected_artifacts:
                    if isinstance(artifact, dict):
                        lines.append(
                            f"  - {_format_execution_readiness_artifact(artifact)}"
                        )

    readiness_blockers = report.get("readiness_blockers")
    if isinstance(readiness_blockers, list) and readiness_blockers:
        lines.append("readiness_blockers:")
        for blocker in readiness_blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"shortlist={blocker.get('shortlist_id') or 'none'} "
                f"action={blocker.get('selected_action') or 'unknown'} "
                f"issues={_format_validation_issues(blocker.get('issues'))}"
            )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def format_ocr_retry_execution_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    output = report.get("output")
    if not isinstance(output, dict):
        output = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}

    lines = [
        "manual eval OCR retry execution: "
        f"state={report.get('state', 'unknown')} "
        f"readiness={report.get('readiness_state', 'unknown')} "
        f"provider={report.get('ocr_provider') or 'unknown'} "
        f"model={report.get('ocr_model') or 'unknown'} "
        f"readiness_items={_int_value(counts.get('readiness_items'))} "
        f"executable={_int_value(counts.get('executable_items'))} "
        f"requests={_int_value(counts.get('requests'))} "
        f"responses={_int_value(counts.get('responses'))} "
        f"succeeded={_int_value(counts.get('succeeded'))} "
        f"failed={_int_value(counts.get('failed'))} "
        f"context_only_skipped={_int_value(counts.get('context_only_skipped'))} "
        f"warehouse_mutation={mutation.get('manual_eval_warehouse') or 'none'} "
        f"output={output.get('run_dir') or 'none'}",
    ]
    stop_reason = str(report.get("stop_reason") or "")
    if stop_reason:
        lines.append(f"stop_reason: {stop_reason}")
    blockers = report.get("execution_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("execution_blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"code={blocker.get('code') or 'unknown'} "
                f"detail={blocker.get('detail') or ''}"
            )
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
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
        "--ocr-retry-source-verification",
        action="store_true",
        help="Print read-only OCR retry source-verification packets.",
    )
    parser.add_argument(
        "--ocr-retry-source-provenance",
        action="store_true",
        help="Print read-only OCR retry source-history provenance packets.",
    )
    parser.add_argument(
        "--ocr-retry-input-packet",
        action="store_true",
        help="Print read-only OCR retry rerun input packets.",
    )
    parser.add_argument(
        "--ocr-retry-rerun-manifest",
        action="store_true",
        help="Print read-only OCR retry rerun source-artifact manifests.",
    )
    parser.add_argument(
        "--ocr-retry-rerun-plan",
        action="store_true",
        help="Print read-only OCR retry rerun plan and payload previews.",
    )
    parser.add_argument(
        "--ocr-retry-selection-review",
        action="store_true",
        help="Print read-only OCR retry source-artifact selection review packets.",
    )
    parser.add_argument(
        "--ocr-retry-selection-template",
        action="store_true",
        help="Print read-only OCR retry human-selection decision templates.",
    )
    parser.add_argument(
        "--ocr-retry-selection-draft",
        action="store_true",
        help="Write a local fillable OCR retry human-selection draft JSON file.",
    )
    parser.add_argument(
        "--ocr-retry-selection-validate",
        action="store_true",
        help="Validate a local OCR retry human-selection JSON against the shortlist.",
    )
    parser.add_argument(
        "--ocr-retry-selection-apply-preview",
        action="store_true",
        help="Print a read-only would-apply preview for valid OCR retry selections.",
    )
    parser.add_argument(
        "--ocr-retry-execution-readiness",
        action="store_true",
        help="Print read-only OCR retry execution readiness for selected decisions.",
    )
    parser.add_argument(
        "--ocr-retry-execute",
        action="store_true",
        help="Run guarded OCR retry execution into a local ignored bundle.",
    )
    parser.add_argument(
        "--selection-path",
        default="",
        help="Path to a local OCR retry human-selection decision JSON file.",
    )
    parser.add_argument(
        "--confirm",
        default="",
        help="Required confirmation token for OCR retry execution.",
    )
    parser.add_argument(
        "--execution-dir",
        default="",
        help="Root directory for local OCR retry execution run bundles.",
    )
    parser.add_argument(
        "--ocr-provider",
        choices=("scaffold", "openai"),
        default=os.getenv("POLINKO_OCR_PROVIDER", "scaffold"),
        help="OCR provider for guarded retry execution.",
    )
    parser.add_argument(
        "--ocr-model",
        default=os.getenv("POLINKO_OCR_MODEL", DEFAULT_OCR_RETRY_MODEL),
        help="OCR model for guarded retry execution.",
    )
    parser.add_argument(
        "--ocr-prompt",
        default=os.getenv("POLINKO_OCR_PROMPT", DEFAULT_OCR_RETRY_PROMPT),
        help="OCR prompt for guarded retry execution.",
    )
    parser.add_argument(
        "--output-path",
        default="",
        help="Path for generated local output such as a selection decision draft.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing generated local output file.",
    )
    parser.add_argument(
        "--artifact-id",
        action="append",
        default=[],
        help=(
            "Limit OCR retry rerun plans to one artifact id. May be repeated "
            "or comma-separated."
        ),
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
    if args.ocr_retry_selection_draft:
        report = write_ocr_retry_selection_decision_draft(
            db_path=db_path,
            output_path=Path(args.output_path)
            if str(args.output_path).strip()
            else None,
            force=bool(args.force),
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
            artifact_ids=args.artifact_id,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_selection_decision_draft_report(report))
        return 0 if report.get("state") == "written" else 2

    if args.ocr_retry_selection_apply_preview:
        report = build_ocr_retry_selection_apply_preview_report(
            db_path=db_path,
            selection_path=Path(args.selection_path)
            if str(args.selection_path).strip()
            else None,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
            artifact_ids=args.artifact_id,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_selection_apply_preview_report(report))
        return 0

    if args.ocr_retry_execution_readiness:
        report = build_ocr_retry_execution_readiness_report(
            db_path=db_path,
            selection_path=Path(args.selection_path)
            if str(args.selection_path).strip()
            else None,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
            artifact_ids=args.artifact_id,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_execution_readiness_report(report))
        return 0

    if args.ocr_retry_execute:
        report = write_ocr_retry_execution_bundle(
            db_path=db_path,
            selection_path=Path(args.selection_path)
            if str(args.selection_path).strip()
            else None,
            confirm_token=str(args.confirm or ""),
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
            artifact_ids=args.artifact_id,
            execution_dir=Path(args.execution_dir)
            if str(args.execution_dir).strip()
            else None,
            ocr_provider=str(args.ocr_provider or "scaffold"),
            ocr_model=str(args.ocr_model or DEFAULT_OCR_RETRY_MODEL),
            ocr_prompt=str(args.ocr_prompt or DEFAULT_OCR_RETRY_PROMPT),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_execution_report(report))
        if report.get("state") == "completed":
            return 0
        if report.get("state") in {"partial_failure", "failed"}:
            return 1
        return 2

    if args.ocr_retry_selection_validate:
        report = build_ocr_retry_selection_validation_report(
            db_path=db_path,
            selection_path=Path(args.selection_path)
            if str(args.selection_path).strip()
            else None,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
            artifact_ids=args.artifact_id,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_selection_validation_report(report))
        return 0

    if args.ocr_retry_selection_template:
        report = build_ocr_retry_selection_template_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
            artifact_ids=args.artifact_id,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_selection_template_report(report))
        return 0

    if args.ocr_retry_selection_review:
        report = build_ocr_retry_selection_review_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
            artifact_ids=args.artifact_id,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_selection_review_report(report))
        return 0

    if args.ocr_retry_rerun_plan:
        report = build_ocr_retry_rerun_plan_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
            artifact_ids=args.artifact_id,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_rerun_plan_report(report))
        return 0

    if args.ocr_retry_rerun_manifest:
        report = build_ocr_retry_rerun_manifest_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_rerun_manifest_report(report))
        return 0

    if args.ocr_retry_input_packet:
        report = build_ocr_retry_input_packet_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_input_packet_report(report))
        return 0

    if args.ocr_retry_source_provenance:
        report = build_ocr_retry_source_provenance_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_source_provenance_report(report))
        return 0

    if args.ocr_retry_source_verification:
        report = build_ocr_retry_source_verification_report(
            db_path=db_path,
            outcome=args.outcome or "partial",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_source_verification_report(report))
        return 0

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
