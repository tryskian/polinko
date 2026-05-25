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

from tools import manual_eval_feedback_decisions as feedback_decisions
from tools import manual_eval_open_feedback as open_feedback
from tools import manual_eval_ocr_retry_candidates as ocr_retry_candidates
from tools import manual_eval_ocr_retry_rerun_manifest as ocr_retry_rerun_manifest
from tools import manual_eval_ocr_retry_rerun_plan as ocr_retry_rerun_plan
from tools import manual_eval_ocr_retry_selection_review as ocr_retry_selection_review
from tools import (
    manual_eval_ocr_retry_selection_decision_draft as ocr_retry_selection_decision_draft,
)
from tools import (
    manual_eval_ocr_retry_selection_apply_preview as ocr_retry_selection_apply_preview,
)
from tools import (
    manual_eval_ocr_retry_execution_readiness as ocr_retry_execution_readiness,
)
from tools import (
    manual_eval_ocr_retry_selection_template as ocr_retry_selection_template,
)
from tools import (
    manual_eval_ocr_retry_selection_validation as ocr_retry_selection_validation,
)
from tools import (
    manual_eval_ocr_retry_source_verification as ocr_retry_source_verification,
)
from tools import manual_eval_ocr_retry_input_packet as ocr_retry_input_packet
from tools import manual_eval_ocr_retry_source_provenance as ocr_retry_source_provenance
from tools import manual_eval_overlay_readiness as overlay_readiness_reports
from tools import manual_eval_overlay_source_index as overlay_source_index
from tools import manual_eval_source_context as source_context_reports
from tools.manual_eval_feedback_decisions import (
    build_feedback_decision_draft_payload as _build_feedback_decision_draft_payload,
    build_feedback_decision_preview_report as _build_feedback_decision_preview_report,
    format_feedback_decision_draft_report,
    format_feedback_decision_preview_report,
    write_feedback_decision_draft as _write_feedback_decision_draft,
)
from tools.manual_eval_ocr_retry_candidates import (
    build_ocr_retry_candidates_report,
    format_ocr_retry_candidates_report,
)
from tools.manual_eval_ocr_retry_source_verification import (
    build_ocr_retry_source_verification_report,
    format_ocr_retry_source_verification_report,
)
from tools.manual_eval_ocr_retry_input_packet import (
    build_ocr_retry_input_packet_report,
    format_ocr_retry_input_packet_report,
)
from tools.manual_eval_ocr_retry_rerun_manifest import (
    build_ocr_retry_rerun_manifest_report,
    format_ocr_retry_rerun_manifest_report,
)
from tools.manual_eval_ocr_retry_rerun_plan import (
    build_ocr_retry_rerun_plan_report,
    format_ocr_retry_rerun_plan_report,
)
from tools.manual_eval_ocr_retry_selection_review import (
    build_ocr_retry_selection_review_report,
    format_ocr_retry_selection_review_report,
)
from tools.manual_eval_ocr_retry_selection_decision_draft import (
    format_ocr_retry_selection_decision_draft_report,
    write_ocr_retry_selection_decision_draft,
)
from tools.manual_eval_ocr_retry_selection_apply_preview import (
    build_ocr_retry_selection_apply_preview_report,
    format_ocr_retry_selection_apply_preview_report,
)
from tools.manual_eval_ocr_retry_execution_readiness import (
    build_ocr_retry_execution_readiness_report,
    format_ocr_retry_execution_readiness_report,
)
from tools.manual_eval_ocr_retry_selection_template import (
    build_ocr_retry_selection_template_report,
    format_ocr_retry_selection_template_report,
)
from tools.manual_eval_ocr_retry_selection_validation import (
    build_ocr_retry_selection_validation_report,
    format_ocr_retry_selection_validation_report,
)
from tools.manual_eval_ocr_retry_source_provenance import (
    build_ocr_retry_source_provenance_report,
    format_ocr_retry_source_provenance_report,
)
from tools.manual_evals_db_status import data_freshness_status
from tools.manual_eval_open_feedback import (
    build_filtered_open_feedback_actionable_rows as _build_filtered_open_feedback_actionable_rows,
    build_open_feedback_actionables_report,
    build_open_feedback_cohorts_report,
    feedback_action_cohort as _feedback_action_cohort,
    format_open_feedback_actionables_report,
    format_open_feedback_cohorts_report,
    normalize_cohort_filter as _normalize_cohort_filter,
    normalize_outcome_filter as _normalize_outcome_filter,
)
from tools.manual_eval_overlay_source_index import (
    build_overlay_source_context_index_draft_payload as _build_overlay_source_context_index_draft_payload,
    build_overlay_source_context_index_validation_report as _build_overlay_source_context_index_validation_report,
    format_overlay_source_context_index_draft_report,
    format_overlay_source_context_index_validation_report,
    write_overlay_source_context_index_draft as _write_overlay_source_context_index_draft,
)
from tools.manual_eval_overlay_readiness import (
    build_overlay_ocr_comparison_readiness_report,
    format_overlay_ocr_comparison_readiness_report,
)
from tools.manual_eval_source_context import (
    build_feedback_source_context_report,
    format_feedback_source_context_report,
)


DEFAULT_OVERLAY_SOURCE_CONTEXT_INDEX_PATH = (
    overlay_source_index.DEFAULT_OVERLAY_SOURCE_CONTEXT_INDEX_PATH
)
OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION = (
    overlay_source_index.OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION
)
OVERLAY_SOURCE_CONTEXT_INDEX_DRAFT_SCHEMA_VERSION = (
    overlay_source_index.OVERLAY_SOURCE_CONTEXT_INDEX_DRAFT_SCHEMA_VERSION
)
OVERLAY_SOURCE_CONTEXT_INDEX_VALIDATION_SCHEMA_VERSION = (
    overlay_source_index.OVERLAY_SOURCE_CONTEXT_INDEX_VALIDATION_SCHEMA_VERSION
)
DEFAULT_FEEDBACK_DECISION_PATH = feedback_decisions.DEFAULT_FEEDBACK_DECISION_PATH
FEEDBACK_DECISION_PREVIEW_SCHEMA_VERSION = (
    feedback_decisions.FEEDBACK_DECISION_PREVIEW_SCHEMA_VERSION
)
FEEDBACK_DECISION_DRAFT_SCHEMA_VERSION = (
    feedback_decisions.FEEDBACK_DECISION_DRAFT_SCHEMA_VERSION
)
FEEDBACK_DECISION_ACTION_DESCRIPTIONS = (
    feedback_decisions.FEEDBACK_DECISION_ACTION_DESCRIPTIONS
)
FEEDBACK_DECISION_ACTIONS = feedback_decisions.FEEDBACK_DECISION_ACTIONS
ACTIONABLES_SCHEMA_VERSION = open_feedback.ACTIONABLES_SCHEMA_VERSION
COHORTS_SCHEMA_VERSION = open_feedback.COHORTS_SCHEMA_VERSION
COHORT_DESCRIPTIONS = open_feedback.COHORT_DESCRIPTIONS
COHORT_IDS = open_feedback.COHORT_IDS
COHORT_FILTER_CHOICES = open_feedback.COHORT_FILTER_CHOICES
DEFAULT_DB_PATH = Path(".local/runtime_dbs/active/manual_evals.db")
FEEDBACK_SOURCE_CONTEXT_SCHEMA_VERSION = (
    source_context_reports.FEEDBACK_SOURCE_CONTEXT_SCHEMA_VERSION
)
OVERLAY_OCR_COMPARISON_READINESS_SCHEMA_VERSION = (
    overlay_readiness_reports.OVERLAY_OCR_COMPARISON_READINESS_SCHEMA_VERSION
)
FEEDBACK_RECLASSIFY_SCHEMA_VERSION = "polinko.manual_eval_feedback_reclassify.v1"
OCR_RETRY_CANDIDATES_SCHEMA_VERSION = (
    ocr_retry_candidates.OCR_RETRY_CANDIDATES_SCHEMA_VERSION
)
OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION = (
    ocr_retry_source_verification.OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION
)
OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION = (
    ocr_retry_source_provenance.OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION
)
OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION = (
    ocr_retry_input_packet.OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION
)
OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION = (
    ocr_retry_rerun_manifest.OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION
)
OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION = (
    ocr_retry_rerun_plan.OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION
)
OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION = (
    ocr_retry_selection_review.OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION
)
OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION = (
    ocr_retry_selection_template.OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION
)
OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION = (
    ocr_retry_selection_decision_draft.OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION
)
OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION = (
    ocr_retry_selection_validation.OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION
)
OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION = (
    ocr_retry_selection_apply_preview.OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION
)
OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION = (
    ocr_retry_execution_readiness.OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION
)
OCR_RETRY_EXECUTION_SCHEMA_VERSION = "polinko.manual_eval_ocr_retry_execution.v1"
OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_execution_report.v1"
)
OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_feedback_closure_preview.v1"
)
OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_feedback_closure_apply.v1"
)
OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1"
)
OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_feedback_closure_restore.v1"
)
NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION = (
    "polinko.manual_eval_no_context_feedback_reclassify.v1"
)
OCR_RETRY_EXECUTION_CONFIRM_TOKEN = "ocr-retry-execute"
OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN = "ocr-retry-feedback-closure-apply"
OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN = "ocr-retry-feedback-closure-restore"
NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN = "manual-evals-no-context-reclassify"
FEEDBACK_RECLASSIFY_CONFIRM_TOKEN = "manual-evals-feedback-reclassify"
DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH = (
    ocr_retry_selection_decision_draft.DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH
)
build_ocr_retry_selection_decision_draft_payload = (
    ocr_retry_selection_decision_draft.build_ocr_retry_selection_decision_draft_payload
)
DEFAULT_OCR_RETRY_EXECUTION_DIR = Path(".local/manual_eval_runs/ocr_retry")
DEFAULT_FEEDBACK_CLOSURE_APPLY_BACKUP_ROOT = Path(".local_archive")
DEFAULT_FEEDBACK_CLOSURE_RESTORE_BACKUP_ROOT = Path(".local_archive")
DEFAULT_NO_CONTEXT_RECLASSIFY_BACKUP_ROOT = Path(".local_archive")
DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT = Path(".local_archive")
DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH = Path(
    ".local/manual_eval_decisions/feedback_reclassify.json"
)
DEFAULT_OCR_RETRY_MODEL = "gpt-4.1-mini"
DEFAULT_OCR_RETRY_PROMPT = (
    "Extract all readable text from this image. Preserve line breaks and symbols "
    "exactly. Do not invent letters or words; if uncertain, output [?]."
)
OCR_RETRY_TERMINAL_CONTEXT_LIMIT = 3


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
    if isinstance(parsed, dict):
        all_tags = parsed.get("all")
        if isinstance(all_tags, list):
            return [str(item) for item in all_tags if str(item).strip()]
        tags: list[str] = []
        for key in ("positive", "negative"):
            value = parsed.get(key)
            if isinstance(value, list):
                tags.extend(str(item) for item in value if str(item).strip())
        return list(dict.fromkeys(tags))
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if str(item).strip()]


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


def build_overlay_source_context_index_draft_payload(
    *,
    db_path: Path,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_overlay_hypothesis",
    limit: int = 100,
) -> dict[str, Any]:
    return _build_overlay_source_context_index_draft_payload(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        readiness_builder=build_overlay_ocr_comparison_readiness_report,
    )


def write_overlay_source_context_index_draft(
    *,
    db_path: Path,
    output_path: Path | None = None,
    force: bool = False,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_overlay_hypothesis",
    limit: int = 100,
) -> dict[str, Any]:
    return _write_overlay_source_context_index_draft(
        db_path=db_path,
        output_path=output_path,
        force=force,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        readiness_builder=build_overlay_ocr_comparison_readiness_report,
    )


def build_overlay_source_context_index_validation_report(
    *,
    db_path: Path,
    overlay_source_index_path: Path | None = None,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_overlay_hypothesis",
    limit: int = 100,
) -> dict[str, Any]:
    return _build_overlay_source_context_index_validation_report(
        db_path=db_path,
        overlay_source_index_path=overlay_source_index_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        readiness_builder=build_overlay_ocr_comparison_readiness_report,
    )


def build_feedback_decision_draft_payload(
    *,
    db_path: Path,
    outcome: str | None = "fail",
    cohort: str | None = "grounding_source_verification",
    limit: int = 1,
) -> dict[str, Any]:
    return _build_feedback_decision_draft_payload(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        source_context_builder=build_feedback_source_context_report,
    )


def write_feedback_decision_draft(
    *,
    db_path: Path,
    output_path: Path | None = None,
    force: bool = False,
    outcome: str | None = "fail",
    cohort: str | None = "grounding_source_verification",
    limit: int = 1,
) -> dict[str, Any]:
    return _write_feedback_decision_draft(
        db_path=db_path,
        output_path=output_path,
        force=force,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        source_context_builder=build_feedback_source_context_report,
    )


def build_feedback_decision_preview_report(
    *,
    db_path: Path,
    decision_path: Path | None = None,
    outcome: str | None = "fail",
    cohort: str | None = "grounding_source_verification",
    limit: int = 1,
) -> dict[str, Any]:
    return _build_feedback_decision_preview_report(
        db_path=db_path,
        decision_path=decision_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        source_context_builder=build_feedback_source_context_report,
        feedback_status_is_open=_feedback_status_is_open,
        feedback_action_cohort=_feedback_action_cohort,
    )


def _truncate_text(value: object, *, max_chars: int = 180) -> str:
    text = _normalize_text(value)
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "..."


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


def _read_json_object(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [f"{path.name} could not be read: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"{path.name} is not valid JSON: {exc}"]
    if not isinstance(payload, dict):
        return None, [f"{path.name} must contain a JSON object"]
    return payload, []


def _read_jsonl_objects(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return rows, [f"{path.name} could not be read: {exc}"]
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{index} is not valid JSON: {exc}")
            continue
        if isinstance(payload, dict):
            rows.append(payload)
        else:
            errors.append(f"{path.name}:{index} must contain a JSON object")
    return rows, errors


def _bundle_path_under_run_dir(path: Path, run_dir: Path) -> bool:
    try:
        resolved_path = path.resolve()
        resolved_run_dir = run_dir.resolve()
    except OSError:
        return False
    return (
        resolved_path == resolved_run_dir or resolved_run_dir in resolved_path.parents
    )


def _bundle_file_path(value: object, *, run_dir: Path, fallback_name: str) -> Path:
    raw_path = str(value or "").strip()
    if not raw_path:
        return run_dir / fallback_name
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    if _bundle_path_under_run_dir(path, run_dir):
        return path
    return run_dir / path


def _bundle_mutation_boundary_ok(boundary: object) -> bool:
    return boundary == _ocr_retry_execution_mutation_boundary()


def _append_execution_bundle_blocker(
    blockers: list[dict[str, str]],
    *,
    code: str,
    detail: str,
) -> None:
    blockers.append({"code": code, "detail": detail})


def _check_execution_bundle_schema_versions(
    *,
    manifest: dict[str, Any] | None,
    summary: dict[str, Any] | None,
    requests: Sequence[dict[str, Any]],
    responses: Sequence[dict[str, Any]],
    blockers: list[dict[str, str]],
) -> None:
    payloads: list[tuple[str, dict[str, Any]]] = []
    if manifest is not None:
        payloads.append(("manifest.json", manifest))
    if summary is not None:
        payloads.append(("summary.json", summary))
    payloads.extend(
        (f"requests.jsonl:{index}", row) for index, row in enumerate(requests, start=1)
    )
    payloads.extend(
        (f"responses.jsonl:{index}", row)
        for index, row in enumerate(responses, start=1)
    )
    for label, payload in payloads:
        if payload.get("schema_version") != OCR_RETRY_EXECUTION_SCHEMA_VERSION:
            _append_execution_bundle_blocker(
                blockers,
                code="schema_version_mismatch",
                detail=(
                    f"{label} schema_version must be "
                    f"{OCR_RETRY_EXECUTION_SCHEMA_VERSION}"
                ),
            )


def _check_execution_bundle_run_ids(
    *,
    manifest: dict[str, Any] | None,
    summary: dict[str, Any] | None,
    requests: Sequence[dict[str, Any]],
    responses: Sequence[dict[str, Any]],
    blockers: list[dict[str, str]],
) -> str:
    run_ids = [
        str(payload.get("run_id") or "")
        for payload in (manifest, summary)
        if isinstance(payload, dict)
    ]
    run_ids.extend(str(row.get("run_id") or "") for row in requests)
    run_ids.extend(str(row.get("run_id") or "") for row in responses)
    non_empty_run_ids = [run_id for run_id in run_ids if run_id]
    unique_run_ids = sorted(set(non_empty_run_ids))
    if not non_empty_run_ids:
        _append_execution_bundle_blocker(
            blockers,
            code="missing_run_id",
            detail="execution bundle does not contain a run_id",
        )
        return ""
    if len(unique_run_ids) != 1 or len(non_empty_run_ids) != len(run_ids):
        _append_execution_bundle_blocker(
            blockers,
            code="run_id_mismatch",
            detail="manifest, summary, requests, and responses must share one run_id",
        )
    return unique_run_ids[0]


def _check_execution_bundle_mutation_boundary(
    *,
    manifest: dict[str, Any] | None,
    summary: dict[str, Any] | None,
    requests: Sequence[dict[str, Any]],
    responses: Sequence[dict[str, Any]],
    blockers: list[dict[str, str]],
) -> None:
    for label, payload in (("manifest.json", manifest), ("summary.json", summary)):
        if not isinstance(payload, dict):
            continue
        if not _bundle_mutation_boundary_ok(payload.get("mutation_boundary")):
            _append_execution_bundle_blocker(
                blockers,
                code="mutation_boundary_mismatch",
                detail=f"{label} mutation_boundary must match local-bundle no-mutation contract",
            )
    for label, rows in (("requests.jsonl", requests), ("responses.jsonl", responses)):
        for index, row in enumerate(rows, start=1):
            if str(row.get("warehouse_mutation") or "") != "none":
                _append_execution_bundle_blocker(
                    blockers,
                    code="warehouse_mutation_not_none",
                    detail=f"{label}:{index} warehouse_mutation must be none",
                )
            for field in (
                "feedback_closure",
                "live_eval_rows",
                "manual_eval_warehouse",
            ):
                if field in row and str(row.get(field) or "") != "none":
                    _append_execution_bundle_blocker(
                        blockers,
                        code="unexpected_mutation_field",
                        detail=f"{label}:{index} {field} must be none when present",
                    )


def _check_execution_bundle_counts(
    *,
    manifest: dict[str, Any] | None,
    summary: dict[str, Any] | None,
    requests: Sequence[dict[str, Any]],
    responses: Sequence[dict[str, Any]],
    blockers: list[dict[str, str]],
) -> dict[str, int]:
    succeeded = sum(1 for response in responses if response.get("status") == "ok")
    failed = len(responses) - succeeded
    skipped = len(requests) - len(responses)
    counts = {
        "requests": len(requests),
        "responses": len(responses),
        "succeeded": succeeded,
        "failed": failed,
        "skipped_after_stop": max(0, skipped),
    }
    if not requests:
        _append_execution_bundle_blocker(
            blockers,
            code="missing_requests",
            detail="requests.jsonl must contain at least one OCR retry request",
        )
    if manifest is not None and _int_value(manifest.get("request_count")) != len(
        requests
    ):
        _append_execution_bundle_blocker(
            blockers,
            code="manifest_request_count_mismatch",
            detail="manifest request_count must match requests.jsonl rows",
        )
    summary_counts = summary.get("counts") if isinstance(summary, dict) else None
    if isinstance(summary_counts, dict):
        for key, expected in counts.items():
            if _int_value(summary_counts.get(key)) != expected:
                _append_execution_bundle_blocker(
                    blockers,
                    code="summary_count_mismatch",
                    detail=f"summary counts.{key} must be {expected}",
                )
    if skipped < 0:
        _append_execution_bundle_blocker(
            blockers,
            code="response_count_exceeds_requests",
            detail="responses.jsonl has more rows than requests.jsonl",
        )
    if (
        skipped > 0
        and summary is not None
        and not str(summary.get("stop_reason") or "")
    ):
        _append_execution_bundle_blocker(
            blockers,
            code="missing_stop_reason",
            detail="summary stop_reason is required when responses stop before all requests",
        )
    expected_summary_state = "completed"
    if failed and succeeded:
        expected_summary_state = "partial_failure"
    elif failed:
        expected_summary_state = "failed"
    if (
        isinstance(summary, dict)
        and str(summary.get("state") or "") != expected_summary_state
    ):
        _append_execution_bundle_blocker(
            blockers,
            code="summary_state_mismatch",
            detail=f"summary state must be {expected_summary_state}",
        )
    return counts


def _check_execution_bundle_request_response_alignment(
    *,
    requests: Sequence[dict[str, Any]],
    responses: Sequence[dict[str, Any]],
    blockers: list[dict[str, str]],
) -> None:
    request_ids = [str(request.get("request_id") or "") for request in requests]
    response_ids = [str(response.get("request_id") or "") for response in responses]
    if len(set(request_ids)) != len(request_ids) or any(
        not item for item in request_ids
    ):
        _append_execution_bundle_blocker(
            blockers,
            code="request_id_invalid",
            detail="requests.jsonl request_id values must be non-empty and unique",
        )
    unknown_response_ids = sorted(set(response_ids) - set(request_ids))
    if unknown_response_ids:
        _append_execution_bundle_blocker(
            blockers,
            code="response_request_id_unmatched",
            detail="responses.jsonl contains request_id values not present in requests.jsonl",
        )
    duplicate_response_ids = [
        request_id
        for request_id in sorted(set(response_ids))
        if response_ids.count(request_id) > 1
    ]
    if duplicate_response_ids:
        _append_execution_bundle_blocker(
            blockers,
            code="response_request_id_duplicate",
            detail="responses.jsonl request_id values must be unique",
        )


def _bundle_payload_value(
    primary: dict[str, Any] | None,
    secondary: dict[str, Any] | None,
    key: str,
) -> object:
    if isinstance(primary, dict) and primary.get(key):
        return primary.get(key)
    if isinstance(secondary, dict) and secondary.get(key):
        return secondary.get(key)
    return ""


def build_ocr_retry_execution_bundle_report(
    *,
    run_dir: Path | None,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    warnings: list[str] = []
    if run_dir is None:
        _append_execution_bundle_blocker(
            blockers,
            code="missing_run_dir",
            detail="RUN_DIR is required before inspecting an OCR retry execution bundle.",
        )
        return {
            "schema_version": OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION,
            "state": "error",
            "run_dir": "",
            "run_id": "",
            "execution_state": "unknown",
            "readiness_state": "unknown",
            "counts": {
                "requests": 0,
                "responses": 0,
                "succeeded": 0,
                "failed": 0,
                "skipped_after_stop": 0,
                "files_available": 0,
                "files_expected": 4,
            },
            "mutation_boundary": _ocr_retry_execution_mutation_boundary(),
            "inspection_blockers": blockers,
            "warnings": [blocker["detail"] for blocker in blockers],
        }

    resolved_run_dir = run_dir.expanduser()
    if not resolved_run_dir.is_dir():
        _append_execution_bundle_blocker(
            blockers,
            code="run_dir_not_found",
            detail="OCR retry execution run directory was not found.",
        )
        return {
            "schema_version": OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION,
            "state": "error",
            "run_dir": str(resolved_run_dir),
            "run_id": resolved_run_dir.name,
            "execution_state": "unknown",
            "readiness_state": "unknown",
            "counts": {
                "requests": 0,
                "responses": 0,
                "succeeded": 0,
                "failed": 0,
                "skipped_after_stop": 0,
                "files_available": 0,
                "files_expected": 4,
            },
            "mutation_boundary": _ocr_retry_execution_mutation_boundary(),
            "inspection_blockers": blockers,
            "warnings": [blocker["detail"] for blocker in blockers],
        }

    expected_files = {
        "manifest": "manifest.json",
        "requests": "requests.jsonl",
        "responses": "responses.jsonl",
        "summary": "summary.json",
    }
    manifest_path = resolved_run_dir / expected_files["manifest"]
    manifest: dict[str, Any] | None = None
    if manifest_path.is_file():
        manifest, parse_errors = _read_json_object(manifest_path)
        for error in parse_errors:
            _append_execution_bundle_blocker(
                blockers, code="file_parse_error", detail=error
            )
    else:
        _append_execution_bundle_blocker(
            blockers,
            code="missing_bundle_file",
            detail="manifest.json is required in an OCR retry execution bundle.",
        )

    file_paths: dict[str, Path] = {
        key: resolved_run_dir / filename for key, filename in expected_files.items()
    }
    if isinstance(manifest, dict):
        manifest_files = manifest.get("files")
        if isinstance(manifest_files, dict):
            for key, filename in expected_files.items():
                file_paths[key] = _bundle_file_path(
                    manifest_files.get(key),
                    run_dir=resolved_run_dir,
                    fallback_name=filename,
                )

    file_reports: list[dict[str, Any]] = []
    files_under_run_dir: dict[str, bool] = {}
    for key, path in file_paths.items():
        exists = path.is_file()
        under_run_dir = _bundle_path_under_run_dir(path, resolved_run_dir)
        files_under_run_dir[key] = under_run_dir
        if not exists:
            _append_execution_bundle_blocker(
                blockers,
                code="missing_bundle_file",
                detail=f"{expected_files[key]} is required in an OCR retry execution bundle.",
            )
        if not under_run_dir:
            _append_execution_bundle_blocker(
                blockers,
                code="bundle_file_outside_run_dir",
                detail=f"{expected_files[key]} must be inside the run directory.",
            )
        file_reports.append(
            {
                "name": expected_files[key],
                "path": str(path),
                "exists": exists,
                "under_run_dir": under_run_dir,
            }
        )

    summary: dict[str, Any] | None = None
    requests: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    if file_paths["summary"].is_file() and files_under_run_dir.get("summary"):
        summary, parse_errors = _read_json_object(file_paths["summary"])
        for error in parse_errors:
            _append_execution_bundle_blocker(
                blockers, code="file_parse_error", detail=error
            )
    if file_paths["requests"].is_file() and files_under_run_dir.get("requests"):
        requests, parse_errors = _read_jsonl_objects(file_paths["requests"])
        for error in parse_errors:
            _append_execution_bundle_blocker(
                blockers, code="file_parse_error", detail=error
            )
    if file_paths["responses"].is_file() and files_under_run_dir.get("responses"):
        responses, parse_errors = _read_jsonl_objects(file_paths["responses"])
        for error in parse_errors:
            _append_execution_bundle_blocker(
                blockers, code="file_parse_error", detail=error
            )

    _check_execution_bundle_schema_versions(
        manifest=manifest,
        summary=summary,
        requests=requests,
        responses=responses,
        blockers=blockers,
    )
    run_id = _check_execution_bundle_run_ids(
        manifest=manifest,
        summary=summary,
        requests=requests,
        responses=responses,
        blockers=blockers,
    )
    _check_execution_bundle_mutation_boundary(
        manifest=manifest,
        summary=summary,
        requests=requests,
        responses=responses,
        blockers=blockers,
    )
    counts = _check_execution_bundle_counts(
        manifest=manifest,
        summary=summary,
        requests=requests,
        responses=responses,
        blockers=blockers,
    )
    _check_execution_bundle_request_response_alignment(
        requests=requests,
        responses=responses,
        blockers=blockers,
    )

    if counts["failed"] or counts["skipped_after_stop"]:
        warnings.append("bundle contains provider failures or skipped requests")
    state = "error" if blockers else "attention" if warnings else "ok"
    files_available = sum(1 for item in file_reports if item["exists"])
    execution_state = str(summary.get("state") or "unknown") if summary else "unknown"
    readiness_state = str(
        _bundle_payload_value(summary, manifest, "readiness_state") or "unknown"
    )
    ocr_provider = str(_bundle_payload_value(summary, manifest, "ocr_provider"))
    ocr_model = str(_bundle_payload_value(summary, manifest, "ocr_model"))
    mutation_boundary = (
        summary.get("mutation_boundary")
        if isinstance(summary, dict)
        and isinstance(summary.get("mutation_boundary"), dict)
        else _ocr_retry_execution_mutation_boundary()
    )
    return {
        "schema_version": OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION,
        "state": state,
        "run_dir": str(resolved_run_dir),
        "run_id": run_id or resolved_run_dir.name,
        "execution_state": execution_state,
        "readiness_state": readiness_state,
        "ocr_provider": ocr_provider,
        "ocr_model": ocr_model,
        "counts": {
            **counts,
            "files_available": files_available,
            "files_expected": len(expected_files),
        },
        "mutation_boundary": mutation_boundary,
        "files": file_reports,
        "source_paths": {
            "terminal": "hidden",
            "request_sources": sum(
                1
                for request in requests
                if isinstance(request.get("source"), dict)
                and str(
                    cast(dict[str, Any], request["source"]).get("resolved_path") or ""
                )
            ),
        },
        "inspection_blockers": blockers,
        "warnings": warnings,
    }


def _execution_bundle_report_file_path(
    report: dict[str, Any],
    filename: str,
) -> Path | None:
    files = report.get("files")
    if not isinstance(files, list):
        return None
    for item in files:
        if not isinstance(item, dict):
            continue
        if item.get("name") != filename:
            continue
        if not item.get("exists") or not item.get("under_run_dir"):
            return None
        return Path(str(item.get("path") or ""))
    return None


def _feedback_ids_from_request(request: dict[str, Any]) -> list[str]:
    feedback_ids = request.get("feedback_ids")
    if not isinstance(feedback_ids, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for value in feedback_ids:
        feedback_id = str(value or "").strip()
        if not feedback_id or feedback_id in seen:
            continue
        normalized.append(feedback_id)
        seen.add(feedback_id)
    return normalized


def _request_source_image_name(request: dict[str, Any]) -> str:
    source = request.get("source")
    if not isinstance(source, dict):
        return ""
    return str(source.get("source_image_name") or "").strip()


def _append_feedback_closure_evidence(
    item: dict[str, Any],
    *,
    request: dict[str, Any],
    response: dict[str, Any] | None,
) -> None:
    response_status = (
        str(response.get("status") or "unknown")
        if isinstance(response, dict)
        else "missing_response"
    )
    evidence = {
        "request_id": str(request.get("request_id") or ""),
        "artifact_id": str(request.get("artifact_id") or ""),
        "shortlist_id": str(request.get("shortlist_id") or ""),
        "source_image_name": _request_source_image_name(request),
        "response_status": response_status,
        "extracted_text_preview": str(response.get("extracted_text_preview") or "")
        if isinstance(response, dict)
        else "",
        "extracted_text_chars": _int_value(response.get("extracted_text_chars"))
        if isinstance(response, dict)
        else 0,
    }
    cast(list[dict[str, Any]], item["evidence"]).append(evidence)


def _finalize_feedback_closure_item(
    item: dict[str, Any],
    *,
    run_id: str,
) -> dict[str, Any]:
    evidence = item.get("evidence")
    if not isinstance(evidence, list):
        evidence = []
    statuses = [
        str(row.get("response_status") or "unknown")
        for row in evidence
        if isinstance(row, dict)
    ]
    ok_count = sum(1 for status in statuses if status == "ok")
    non_ok_count = len(statuses) - ok_count
    state = "blocked"
    reason = "no_successful_ocr_retry_response"
    proposed_status = "open"
    action_taken_preview = (
        "Preview only: no successful OCR retry response is available; keep "
        "feedback open."
    )
    if ok_count and not non_ok_count:
        state = "ready"
        reason = "successful_ocr_retry_response"
        proposed_status = "closed"
        action_taken_preview = (
            "Preview only: OCR retry bundle "
            f"{run_id} produced successful retry evidence for feedback "
            f"{item.get('feedback_id')}; inspect the local bundle before closure."
        )
    elif ok_count and non_ok_count:
        state = "attention"
        reason = "mixed_ocr_retry_response_status"
        action_taken_preview = (
            "Preview only: mixed OCR retry statuses are present; review the "
            "local bundle before deciding whether to close feedback."
        )

    return {
        **item,
        "state": state,
        "reason": reason,
        "response_statuses": statuses,
        "proposed_feedback_status": proposed_status,
        "action_taken_preview": action_taken_preview,
        "feedback_closure": "preview_only",
        "mutation": "none",
    }


def build_ocr_retry_feedback_closure_preview_report(
    *,
    run_dir: Path | None,
) -> dict[str, Any]:
    bundle_report = build_ocr_retry_execution_bundle_report(run_dir=run_dir)
    bundle_state = str(bundle_report.get("state") or "unknown")
    run_id = str(bundle_report.get("run_id") or "")
    mutation_boundary = _ocr_retry_execution_mutation_boundary()
    if bundle_state == "error":
        inspection_blockers = bundle_report.get("inspection_blockers")
        if not isinstance(inspection_blockers, list):
            inspection_blockers = []
        return {
            "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
            "state": "blocked",
            "run_dir": str(bundle_report.get("run_dir") or ""),
            "run_id": run_id,
            "bundle_state": bundle_state,
            "counts": {
                "bundle_requests": 0,
                "bundle_responses": 0,
                "feedback_items": 0,
                "ready_feedback": 0,
                "attention_feedback": 0,
                "blocked_feedback": 0,
                "requests_without_feedback_ids": 0,
            },
            "mutation_boundary": mutation_boundary,
            "closure_items": [],
            "preview_blockers": inspection_blockers,
            "warnings": [str(item) for item in bundle_report.get("warnings", [])],
        }

    requests_path = _execution_bundle_report_file_path(bundle_report, "requests.jsonl")
    responses_path = _execution_bundle_report_file_path(
        bundle_report, "responses.jsonl"
    )
    blockers: list[dict[str, str]] = []
    if requests_path is None or responses_path is None:
        blockers.append(
            {
                "code": "missing_bundle_rows",
                "detail": "requests.jsonl and responses.jsonl are required for closure preview.",
            }
        )
        return {
            "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
            "state": "blocked",
            "run_dir": str(bundle_report.get("run_dir") or ""),
            "run_id": run_id,
            "bundle_state": bundle_state,
            "counts": {
                "bundle_requests": 0,
                "bundle_responses": 0,
                "feedback_items": 0,
                "ready_feedback": 0,
                "attention_feedback": 0,
                "blocked_feedback": 0,
                "requests_without_feedback_ids": 0,
            },
            "mutation_boundary": mutation_boundary,
            "closure_items": [],
            "preview_blockers": blockers,
            "warnings": [blocker["detail"] for blocker in blockers],
        }

    requests, request_errors = _read_jsonl_objects(requests_path)
    responses, response_errors = _read_jsonl_objects(responses_path)
    for error in (*request_errors, *response_errors):
        blockers.append({"code": "bundle_parse_error", "detail": error})
    if blockers:
        return {
            "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
            "state": "blocked",
            "run_dir": str(bundle_report.get("run_dir") or ""),
            "run_id": run_id,
            "bundle_state": bundle_state,
            "counts": {
                "bundle_requests": len(requests),
                "bundle_responses": len(responses),
                "feedback_items": 0,
                "ready_feedback": 0,
                "attention_feedback": 0,
                "blocked_feedback": 0,
                "requests_without_feedback_ids": 0,
            },
            "mutation_boundary": mutation_boundary,
            "closure_items": [],
            "preview_blockers": blockers,
            "warnings": [blocker["detail"] for blocker in blockers],
        }

    response_by_request_id = {
        str(response.get("request_id") or ""): response for response in responses
    }
    closure_items_by_feedback: dict[str, dict[str, Any]] = {}
    requests_without_feedback_ids = 0
    for request in requests:
        feedback_ids = _feedback_ids_from_request(request)
        if not feedback_ids:
            requests_without_feedback_ids += 1
            continue
        response = response_by_request_id.get(str(request.get("request_id") or ""))
        for feedback_id in feedback_ids:
            item = closure_items_by_feedback.setdefault(
                feedback_id,
                {
                    "feedback_id": feedback_id,
                    "evidence": [],
                },
            )
            _append_feedback_closure_evidence(
                item,
                request=request,
                response=response,
            )

    closure_items = [
        _finalize_feedback_closure_item(item, run_id=run_id)
        for item in closure_items_by_feedback.values()
    ]
    ready_feedback = sum(1 for item in closure_items if item["state"] == "ready")
    attention_feedback = sum(
        1 for item in closure_items if item["state"] == "attention"
    )
    blocked_feedback = sum(1 for item in closure_items if item["state"] == "blocked")
    warnings = [str(item) for item in bundle_report.get("warnings", [])]
    if requests_without_feedback_ids:
        warnings.append("one or more requests do not carry feedback IDs")
    state = (
        "ok" if closure_items and ready_feedback == len(closure_items) else "attention"
    )
    return {
        "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
        "state": state,
        "run_dir": str(bundle_report.get("run_dir") or ""),
        "run_id": run_id,
        "bundle_state": bundle_state,
        "counts": {
            "bundle_requests": len(requests),
            "bundle_responses": len(responses),
            "feedback_items": len(closure_items),
            "ready_feedback": ready_feedback,
            "attention_feedback": attention_feedback,
            "blocked_feedback": blocked_feedback,
            "requests_without_feedback_ids": requests_without_feedback_ids,
        },
        "mutation_boundary": mutation_boundary,
        "closure_items": closure_items,
        "preview_blockers": [],
        "warnings": warnings,
    }


def _ocr_retry_feedback_closure_apply_mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "feedback_status_action_taken_updated_at_only",
        "feedback_closure": "applied",
        "live_eval_rows": "none",
        "manual_eval_warehouse": "feedback_rows_only",
        "ocr_run_rows": "none",
        "source_links": "none",
    }


def _ocr_retry_feedback_closure_apply_blocker(
    code: str,
    detail: str,
) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _feedback_status_normalized(status: object) -> str:
    return str(status or "").strip().casefold()


def _feedback_status_is_open(status: object) -> bool:
    return _feedback_status_normalized(status) == "open"


def _feedback_status_is_closed(status: object) -> bool:
    return _feedback_status_normalized(status) == "closed"


def _closed_feedback_status_for_open_status(status: object) -> str:
    raw_status = str(status or "").strip()
    return "CLOSED" if raw_status.isupper() else "closed"


def _feedback_closure_apply_counts(
    preview_report: dict[str, Any] | None,
    *,
    target_feedback_rows: int = 0,
    updated_feedback_rows: int = 0,
    skipped_feedback_rows: int = 0,
    backups_written: int = 0,
) -> dict[str, int]:
    preview_counts = (
        preview_report.get("counts") if isinstance(preview_report, dict) else {}
    )
    if not isinstance(preview_counts, dict):
        preview_counts = {}
    return {
        "bundle_requests": _int_value(preview_counts.get("bundle_requests")),
        "bundle_responses": _int_value(preview_counts.get("bundle_responses")),
        "preview_feedback_items": _int_value(preview_counts.get("feedback_items")),
        "ready_feedback": _int_value(preview_counts.get("ready_feedback")),
        "attention_feedback": _int_value(preview_counts.get("attention_feedback")),
        "blocked_feedback": _int_value(preview_counts.get("blocked_feedback")),
        "target_feedback_rows": target_feedback_rows,
        "updated_feedback_rows": updated_feedback_rows,
        "skipped_feedback_rows": skipped_feedback_rows,
        "backups_written": backups_written,
    }


def _blocked_ocr_retry_feedback_closure_apply_report(
    *,
    db_path: Path,
    run_dir: Path | None,
    backup_root: Path,
    confirm_token: str,
    preview_report: dict[str, Any] | None,
    blockers: Sequence[dict[str, str]],
    backup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if backup is None:
        backup = {
            "written": False,
            "root": str(backup_root),
            "dir": "",
            "db_path": "",
            "restore_command": "",
        }
    preview_counts = _feedback_closure_apply_counts(
        preview_report,
        backups_written=1 if backup.get("written") else 0,
    )
    return {
        "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
        "state": "blocked",
        "run_dir": str(run_dir or ""),
        "run_id": str(preview_report.get("run_id") or "")
        if isinstance(preview_report, dict)
        else "",
        "bundle_state": str(preview_report.get("bundle_state") or "not_checked")
        if isinstance(preview_report, dict)
        else "not_checked",
        "preview_state": str(preview_report.get("state") or "not_checked")
        if isinstance(preview_report, dict)
        else "not_checked",
        "confirmation": {
            "required": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
            "provided": bool(confirm_token),
            "state": "ok"
            if confirm_token == OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN
            else "blocked",
        },
        "manual_evals_db": {
            "path": str(db_path),
            "backup_required": True,
        },
        "counts": preview_counts,
        "mutation_boundary": _ocr_retry_feedback_closure_apply_mutation_boundary(),
        "backup": backup,
        "apply_items": [],
        "apply_blockers": list(blockers),
        "warnings": [blocker["detail"] for blocker in blockers],
    }


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


NO_CONTEXT_RECLASSIFIED_RECOMMENDED_ACTION = (
    "Preserve as overlay-assisted OCR hypothesis evidence; attach the "
    "overlay/source image context before rerunning OCR for comparison."
)
NO_CONTEXT_SOURCE_RESPONSE_MARKER = "no new image evidence in this turn"


def _no_context_reclassify_mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "feedback_recommended_action_action_taken_updated_at_only",
        "manual_eval_warehouse": "feedback_rows_only",
        "feedback_status": "unchanged",
        "ocr_runs": "unchanged",
        "image_assets": "unchanged",
        "eval_rows": "unchanged",
        "source_history_db": "unchanged",
        "pulse": "excluded",
    }


def _no_context_reclassify_blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _source_history_db_path(source_history_db: object) -> Path:
    path = Path(str(source_history_db or "")).expanduser()
    if path.is_absolute():
        return path
    return Path.cwd() / path


def _source_feedback_message(
    row: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    source_db_path = _source_history_db_path(row.get("source_history_db"))
    if not str(row.get("source_history_db") or "").strip():
        return None, [
            _no_context_reclassify_blocker(
                "missing_source_history_db",
                "feedback row does not name a source history DB.",
            )
        ]
    if not source_db_path.is_file():
        return None, [
            _no_context_reclassify_blocker(
                "source_history_db_not_found",
                "source history DB was not found.",
            )
        ]
    try:
        with closing(_connect_readonly(source_db_path)) as conn:
            source_row = conn.execute(
                """
                SELECT role, content, created_at
                FROM chat_messages
                WHERE session_id = ? AND message_id = ?
                LIMIT 1
                """,
                [
                    str(row.get("source_session_id") or ""),
                    str(row.get("message_id") or ""),
                ],
            ).fetchone()
    except sqlite3.Error as exc:
        return None, [
            _no_context_reclassify_blocker(
                "source_history_message_lookup_failed",
                f"source history message lookup failed: {exc}",
            )
        ]
    if source_row is None:
        return None, [
            _no_context_reclassify_blocker(
                "source_history_message_not_found",
                "source history DB does not contain the feedback message.",
            )
        ]
    return _row_dict(source_row), []


def _no_context_reclassify_preview_item(row: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    ocr_context = row.get("ocr_context")
    if not isinstance(ocr_context, dict):
        ocr_context = {}
    if _int_value(ocr_context.get("same_session_ocr_runs")) > 0:
        blockers.append(
            _no_context_reclassify_blocker(
                "same_session_ocr_exists",
                "feedback row already has same-session OCR context.",
            )
        )
    current_cohort = _feedback_action_cohort(row.get("recommended_action"))
    if current_cohort not in {"ocr_retry_evidence", "ocr_overlay_hypothesis"}:
        blockers.append(
            _no_context_reclassify_blocker(
                "feedback_not_ocr_retry_cohort",
                "feedback row is not in an OCR retry or overlay-hypothesis cohort.",
            )
        )

    source_message, source_blockers = _source_feedback_message(row)
    blockers.extend(source_blockers)
    source_role = ""
    source_content = ""
    source_created_at = 0
    if source_message is not None:
        source_role = str(source_message.get("role") or "")
        source_content = str(source_message.get("content") or "")
        source_created_at = _int_value(source_message.get("created_at"))
        if source_role != "assistant":
            blockers.append(
                _no_context_reclassify_blocker(
                    "source_message_not_assistant",
                    "feedback message is not an assistant response.",
                )
            )
        if NO_CONTEXT_SOURCE_RESPONSE_MARKER not in source_content.lower():
            blockers.append(
                _no_context_reclassify_blocker(
                    "source_message_not_no_image_response",
                    "feedback message is not the no-new-image-evidence response.",
                )
            )

    return {
        "feedback_id": _int_value(row.get("feedback_id")),
        "session_id": str(row.get("session_id") or ""),
        "source_session_id": str(row.get("source_session_id") or ""),
        "message_id": str(row.get("message_id") or ""),
        "outcome": str(row.get("outcome") or ""),
        "status": str(row.get("status") or ""),
        "title": str(row.get("title") or ""),
        "current_recommended_action": str(row.get("recommended_action") or ""),
        "new_recommended_action": NO_CONTEXT_RECLASSIFIED_RECOMMENDED_ACTION,
        "source_message": {
            "role": source_role,
            "created_at": source_created_at,
            "content_preview": _truncate_text(source_content),
        },
        "state": "ready" if not blockers else "blocked",
        "blockers": blockers,
    }


def build_no_context_feedback_reclassify_report(
    *,
    db_path: Path,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    outcome_filter = _normalize_outcome_filter(outcome)
    cohort_filter = _normalize_cohort_filter(cohort) or "ocr_retry_evidence"
    row_limit = max(1, limit)
    if not db_path.is_file():
        return {
            "schema_version": NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
            "state": "error",
            "mode": "preview",
            "manual_evals_db": {"path": str(db_path), "exists": False},
            "filters": {
                "status": "open",
                "outcome": outcome_filter or "",
                "cohort": cohort_filter,
                "limit": row_limit,
            },
            "counts": {
                "candidate_feedback": 0,
                "ready_feedback": 0,
                "blocked_feedback": 0,
            },
            "mutation_boundary": _no_context_reclassify_mutation_boundary(),
            "items": [],
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

    items = [_no_context_reclassify_preview_item(row) for row in rows]
    ready_feedback = sum(1 for item in items if item.get("state") == "ready")
    blocked_feedback = len(items) - ready_feedback
    return {
        "schema_version": NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
        "state": "ok" if integrity == "ok" else "error",
        "mode": "preview",
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
        },
        "counts": {
            "total_feedback_rows": len(all_rows),
            "candidate_feedback": len(items),
            "ready_feedback": ready_feedback,
            "blocked_feedback": blocked_feedback,
            "limit_applied": len(rows) < len(all_rows),
        },
        "mutation_boundary": _no_context_reclassify_mutation_boundary(),
        "items": items,
        "warnings": [],
    }


def _backup_manual_evals_db_for_no_context_reclassify(
    *,
    db_path: Path,
    backup_root: Path,
    applied_at: str,
    feedback_ids: Sequence[int],
) -> dict[str, Any]:
    backup_dir = backup_root / f"manual-evals-feedback-no-context-{applied_at}"
    backup_db_path = backup_dir / "manual_evals.db"
    if backup_dir.exists():
        raise FileExistsError(f"backup directory already exists: {backup_dir}")
    _sqlite_backup_copy(
        source_db_path=db_path,
        destination_db_path=backup_db_path,
    )
    backup_integrity = _sqlite_integrity_check(backup_db_path)
    manifest_path = backup_dir / "manifest.json"
    restore_command = (
        f"cp {shlex.quote(str(backup_db_path))} {shlex.quote(str(db_path))}"
    )
    _write_json(
        manifest_path,
        {
            "schema_version": NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
            "created_at": applied_at,
            "source_db_path": str(db_path),
            "backup_db_path": str(backup_db_path),
            "backup_integrity": backup_integrity,
            "feedback_ids": [int(feedback_id) for feedback_id in feedback_ids],
            "restore_command": restore_command,
        },
    )
    return {
        "written": True,
        "root": str(backup_root),
        "dir": str(backup_dir),
        "db_path": str(backup_db_path),
        "manifest_path": str(manifest_path),
        "integrity_check": backup_integrity,
        "restore_command": restore_command,
    }


def _no_context_reclassify_action_taken(
    *,
    feedback_id: int,
    backup_dir_name: str,
) -> str:
    return (
        "Reclassified by overlay-hypothesis feedback gate: feedback "
        f"{feedback_id} has no same-session OCR context and the source response "
        "requested new image evidence; preserved as overlay-assisted OCR "
        "hypothesis evidence. "
        f"Backup: {backup_dir_name}."
    )


def _blocked_no_context_reclassify_report(
    *,
    db_path: Path,
    preview_report: dict[str, Any],
    confirm_token: str,
    backup_root: Path,
    blockers: Sequence[dict[str, str]],
    backup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preview_counts = preview_report.get("counts")
    if not isinstance(preview_counts, dict):
        preview_counts = {}
    return {
        "schema_version": NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
        "state": "blocked",
        "mode": "apply",
        "manual_evals_db": {
            "path": str(db_path),
            "backup_required": True,
        },
        "confirmation": {
            "required": NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN,
            "provided": bool(confirm_token),
            "state": "ok"
            if confirm_token == NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN
            else "blocked",
        },
        "filters": preview_report.get("filters")
        if isinstance(preview_report, dict)
        else {},
        "counts": {
            "candidate_feedback": _int_value(preview_counts.get("candidate_feedback")),
            "ready_feedback": _int_value(preview_counts.get("ready_feedback")),
            "blocked_feedback": _int_value(preview_counts.get("blocked_feedback")),
            "updated_feedback_rows": 0,
            "backups_written": 1 if backup and backup.get("written") else 0,
            "apply_blockers": len(blockers),
        },
        "mutation_boundary": _no_context_reclassify_mutation_boundary(),
        "backup": backup
        or {
            "written": False,
            "root": str(backup_root),
            "dir": "",
            "db_path": "",
            "restore_command": "",
        },
        "apply_items": [],
        "apply_blockers": list(blockers),
        "warnings": [blocker["detail"] for blocker in blockers],
    }


def write_no_context_feedback_reclassify(
    *,
    db_path: Path,
    confirm_token: str,
    backup_root: Path | None = None,
    applied_at: str | None = None,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    resolved_db_path = db_path.expanduser()
    resolved_backup_root = (
        backup_root.expanduser()
        if backup_root is not None
        else DEFAULT_NO_CONTEXT_RECLASSIFY_BACKUP_ROOT
    )
    preview = build_no_context_feedback_reclassify_report(
        db_path=resolved_db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    blockers: list[dict[str, str]] = []
    if confirm_token != NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN:
        blockers.append(
            _no_context_reclassify_blocker(
                "missing_confirmation",
                "CONFIRM=manual-evals-no-context-reclassify is required before reclassification.",
            )
        )
    if not resolved_db_path.is_file():
        blockers.append(
            _no_context_reclassify_blocker(
                "manual_evals_db_not_found",
                f"manual eval warehouse was not found: {resolved_db_path}",
            )
        )
    if preview.get("state") != "ok":
        blockers.append(
            _no_context_reclassify_blocker(
                "preview_not_ok",
                f"overlay reclassification preview is {preview.get('state') or 'unknown'}.",
            )
        )
    items = preview.get("items")
    if not isinstance(items, list):
        items = []
    ready_items = [
        item
        for item in items
        if isinstance(item, dict) and item.get("state") == "ready"
    ]
    if not ready_items:
        blockers.append(
            _no_context_reclassify_blocker(
                "no_ready_feedback",
                "No ready overlay-hypothesis feedback rows are available to reclassify.",
            )
        )
    if len(ready_items) != len(items):
        blockers.append(
            _no_context_reclassify_blocker(
                "items_not_all_ready",
                "Every overlay reclassification preview item must be ready before apply.",
            )
        )

    feedback_ids, invalid_feedback_ids = _feedback_ids_from_closure_items(ready_items)
    if invalid_feedback_ids:
        blockers.append(
            _no_context_reclassify_blocker(
                "invalid_feedback_id",
                "No-context reclassification preview contains non-integer feedback IDs: "
                + ",".join(invalid_feedback_ids),
            )
        )

    rows_by_id: dict[int, dict[str, Any]] = {}
    if not blockers and feedback_ids:
        try:
            integrity = _sqlite_integrity_check(resolved_db_path)
        except sqlite3.Error as exc:
            blockers.append(
                _no_context_reclassify_blocker(
                    "manual_evals_db_integrity_check_failed",
                    f"manual eval warehouse integrity check failed: {exc}",
                )
            )
        else:
            if integrity != "ok":
                blockers.append(
                    _no_context_reclassify_blocker(
                        "manual_evals_db_integrity_not_ok",
                        f"manual eval warehouse integrity check returned {integrity}.",
                    )
                )
        if not blockers:
            rows_by_id = _feedback_rows_by_id(
                db_path=resolved_db_path,
                feedback_ids=feedback_ids,
            )
            missing_feedback_ids = [
                feedback_id
                for feedback_id in feedback_ids
                if feedback_id not in rows_by_id
            ]
            if missing_feedback_ids:
                blockers.append(
                    _no_context_reclassify_blocker(
                        "feedback_rows_missing",
                        "Feedback rows are missing from the current warehouse: "
                        + ",".join(
                            str(feedback_id) for feedback_id in missing_feedback_ids
                        ),
                    )
                )
            non_open_feedback = [
                f"{feedback_id}={rows_by_id[feedback_id].get('status') or 'unknown'}"
                for feedback_id in feedback_ids
                if not _feedback_status_is_open(
                    rows_by_id.get(feedback_id, {}).get("status")
                )
            ]
            if non_open_feedback:
                blockers.append(
                    _no_context_reclassify_blocker(
                        "feedback_rows_not_open",
                        "Feedback rows are no longer open: "
                        + ",".join(non_open_feedback),
                    )
                )

    if blockers:
        return _blocked_no_context_reclassify_report(
            db_path=resolved_db_path,
            preview_report=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=blockers,
        )

    actual_applied_at = applied_at or _utc_run_timestamp()
    try:
        backup = _backup_manual_evals_db_for_no_context_reclassify(
            db_path=resolved_db_path,
            backup_root=resolved_backup_root,
            applied_at=actual_applied_at,
            feedback_ids=feedback_ids,
        )
    except (OSError, sqlite3.Error) as exc:
        return _blocked_no_context_reclassify_report(
            db_path=resolved_db_path,
            preview_report=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=[
                _no_context_reclassify_blocker(
                    "backup_failed",
                    f"manual eval warehouse backup failed: {exc}",
                )
            ],
        )
    if backup.get("integrity_check") != "ok":
        return _blocked_no_context_reclassify_report(
            db_path=resolved_db_path,
            preview_report=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=[
                _no_context_reclassify_blocker(
                    "backup_integrity_not_ok",
                    "manual eval warehouse backup integrity check returned "
                    f"{backup.get('integrity_check') or 'missing'}.",
                )
            ],
            backup=backup,
        )

    item_by_feedback_id = {
        _int_value(item.get("feedback_id")): item for item in ready_items
    }
    backup_dir_name = Path(str(backup.get("dir") or "")).name
    updated_at = int(datetime.now(UTC).timestamp())
    apply_items: list[dict[str, Any]] = []
    with closing(sqlite3.connect(resolved_db_path)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("BEGIN IMMEDIATE")
        current_rows = conn.execute(
            "SELECT id, status FROM feedback WHERE id IN ("
            + ",".join("?" for _ in feedback_ids)
            + ")",
            feedback_ids,
        ).fetchall()
        current_statuses = {
            _int_value(row["id"]): str(row["status"] or "") for row in current_rows
        }
        no_longer_open = [
            f"{feedback_id}={current_statuses.get(feedback_id) or 'missing'}"
            for feedback_id in feedback_ids
            if not _feedback_status_is_open(current_statuses.get(feedback_id))
        ]
        if no_longer_open:
            conn.rollback()
            return _blocked_no_context_reclassify_report(
                db_path=resolved_db_path,
                preview_report=preview,
                confirm_token=confirm_token,
                backup_root=resolved_backup_root,
                blockers=[
                    _no_context_reclassify_blocker(
                        "feedback_rows_changed_after_backup",
                        "Feedback rows changed after backup and before apply: "
                        + ",".join(no_longer_open),
                    )
                ],
                backup=backup,
            )
        for feedback_id in feedback_ids:
            item = item_by_feedback_id[feedback_id]
            old_action = str(item.get("current_recommended_action") or "")
            new_action = str(item.get("new_recommended_action") or "")
            action_taken = _no_context_reclassify_action_taken(
                feedback_id=feedback_id,
                backup_dir_name=backup_dir_name,
            )
            conn.execute(
                """
                UPDATE feedback
                SET recommended_action = ?,
                    action_taken = ?,
                    updated_at = ?
                WHERE id = ? AND lower(status) = ?
                """,
                (new_action, action_taken, updated_at, feedback_id, "open"),
            )
            apply_items.append(
                {
                    "feedback_id": feedback_id,
                    "message_id": str(item.get("message_id") or ""),
                    "outcome": str(item.get("outcome") or ""),
                    "recommended_action_before": old_action,
                    "recommended_action_after": new_action,
                    "action_taken": action_taken,
                    "status": current_statuses.get(feedback_id) or "open",
                    "updated_at": updated_at,
                    "mutation": "recommended_action,action_taken,updated_at",
                }
            )
        conn.commit()

    return {
        "schema_version": NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
        "state": "applied",
        "mode": "apply",
        "applied_at": actual_applied_at,
        "manual_evals_db": {
            "path": str(resolved_db_path),
            "backup_required": True,
            "integrity_check": "ok",
        },
        "confirmation": {
            "required": NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN,
            "provided": True,
            "state": "ok",
        },
        "filters": preview.get("filters") if isinstance(preview, dict) else {},
        "counts": {
            "candidate_feedback": len(items),
            "ready_feedback": len(ready_items),
            "blocked_feedback": 0,
            "updated_feedback_rows": len(apply_items),
            "backups_written": 1,
            "apply_blockers": 0,
        },
        "mutation_boundary": _no_context_reclassify_mutation_boundary(),
        "backup": backup,
        "apply_items": apply_items,
        "updated_feedback_ids": feedback_ids,
        "apply_blockers": [],
        "warnings": [],
    }


def _feedback_reclassify_mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "feedback_recommended_action_action_taken_updated_at_only",
        "manual_eval_warehouse": "feedback_rows_only",
        "feedback_status": "unchanged",
        "ocr_runs": "unchanged",
        "image_assets": "unchanged",
        "eval_rows": "unchanged",
        "source_history_db": "unchanged",
        "pulse": "excluded",
    }


def _feedback_reclassify_blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load_feedback_reclassify_plan(
    plan_path: Path,
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    resolved_plan_path = plan_path.expanduser()
    if not resolved_plan_path.is_file():
        return None, [
            _feedback_reclassify_blocker(
                "plan_not_found",
                f"feedback reclassification plan was not found: {resolved_plan_path}",
            )
        ]
    try:
        payload = json.loads(resolved_plan_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [
            _feedback_reclassify_blocker(
                "plan_load_failed",
                f"feedback reclassification plan could not be loaded: {exc}",
            )
        ]
    except json.JSONDecodeError as exc:
        return None, [
            _feedback_reclassify_blocker(
                "plan_load_failed",
                "feedback reclassification plan is not valid JSON: "
                f"line {exc.lineno} column {exc.colno}",
            )
        ]
    if not isinstance(payload, dict):
        return None, [
            _feedback_reclassify_blocker(
                "plan_not_object",
                "feedback reclassification plan must be a JSON object.",
            )
        ]
    return payload, []


def _feedback_reclassify_decisions(
    plan_payload: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    if plan_payload is None:
        return [], []
    raw_items = plan_payload.get("decisions")
    if not isinstance(raw_items, list):
        return [], [
            _feedback_reclassify_blocker(
                "missing_decisions",
                "feedback reclassification plan must contain a decisions array.",
            )
        ]
    decisions: list[dict[str, Any]] = []
    blockers: list[dict[str, str]] = []
    seen: set[int] = set()
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            blockers.append(
                _feedback_reclassify_blocker(
                    "decision_not_object",
                    f"decision {index} must be a JSON object.",
                )
            )
            continue
        feedback_id = _int_value(raw_item.get("feedback_id"))
        if feedback_id <= 0:
            blockers.append(
                _feedback_reclassify_blocker(
                    "invalid_feedback_id",
                    f"decision {index} has an invalid feedback_id.",
                )
            )
            continue
        if feedback_id in seen:
            blockers.append(
                _feedback_reclassify_blocker(
                    "duplicate_feedback_id",
                    f"feedback {feedback_id} appears more than once in the plan.",
                )
            )
            continue
        recommended_action = _normalize_text(raw_item.get("recommended_action"))
        if not recommended_action:
            blockers.append(
                _feedback_reclassify_blocker(
                    "missing_recommended_action",
                    f"feedback {feedback_id} does not name a recommended_action.",
                )
            )
            continue
        rationale = _normalize_text(raw_item.get("rationale"))
        seen.add(feedback_id)
        decisions.append(
            {
                "feedback_id": feedback_id,
                "recommended_action": recommended_action,
                "rationale": rationale,
            }
        )
    return decisions, blockers


def _feedback_reclassify_preview_item(
    *,
    decision: dict[str, Any],
    row: dict[str, Any] | None,
) -> dict[str, Any]:
    feedback_id = _int_value(decision.get("feedback_id"))
    blockers: list[dict[str, str]] = []
    if row is None:
        blockers.append(
            _feedback_reclassify_blocker(
                "feedback_row_missing",
                f"feedback {feedback_id} was not found in the manual eval warehouse.",
            )
        )
        return {
            "feedback_id": feedback_id,
            "message_id": "",
            "outcome": "",
            "status": "",
            "current_recommended_action": "",
            "new_recommended_action": str(decision.get("recommended_action") or ""),
            "current_cohort": "",
            "new_cohort": _feedback_action_cohort(decision.get("recommended_action")),
            "rationale": str(decision.get("rationale") or ""),
            "state": "blocked",
            "blockers": blockers,
        }
    if not _feedback_status_is_open(row.get("status")):
        blockers.append(
            _feedback_reclassify_blocker(
                "feedback_row_not_open",
                f"feedback {feedback_id} is {row.get('status') or 'unknown'}, not open.",
            )
        )
    current_action = str(row.get("recommended_action") or "")
    new_action = str(decision.get("recommended_action") or "")
    current_cohort = _feedback_action_cohort(current_action)
    new_cohort = _feedback_action_cohort(new_action)
    if current_action == new_action:
        blockers.append(
            _feedback_reclassify_blocker(
                "recommended_action_unchanged",
                f"feedback {feedback_id} already has the requested recommended_action.",
            )
        )
    return {
        "feedback_id": feedback_id,
        "message_id": str(row.get("message_id") or ""),
        "outcome": str(row.get("outcome") or ""),
        "status": str(row.get("status") or ""),
        "current_recommended_action": current_action,
        "new_recommended_action": new_action,
        "current_cohort": current_cohort,
        "new_cohort": new_cohort,
        "rationale": str(decision.get("rationale") or ""),
        "state": "ready" if not blockers else "blocked",
        "blockers": blockers,
    }


def build_feedback_reclassify_report(
    *,
    db_path: Path,
    plan_path: Path | None = None,
) -> dict[str, Any]:
    resolved_plan_path = (
        plan_path.expanduser()
        if plan_path is not None
        else DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH
    )
    blockers: list[dict[str, str]] = []
    plan_payload, plan_blockers = _load_feedback_reclassify_plan(resolved_plan_path)
    blockers.extend(plan_blockers)
    decisions, decision_blockers = _feedback_reclassify_decisions(plan_payload)
    blockers.extend(decision_blockers)
    if not db_path.is_file():
        blockers.append(
            _feedback_reclassify_blocker(
                "manual_evals_db_not_found",
                f"manual eval warehouse was not found: {db_path}",
            )
        )

    integrity = "not_checked"
    rows_by_id: dict[int, dict[str, Any]] = {}
    if not blockers and decisions:
        with closing(_connect_readonly(db_path)) as conn:
            integrity = str(conn.execute("PRAGMA integrity_check").fetchone()[0])
        if integrity != "ok":
            blockers.append(
                _feedback_reclassify_blocker(
                    "manual_evals_db_integrity_not_ok",
                    f"manual eval warehouse integrity check returned {integrity}.",
                )
            )
        else:
            rows_by_id = _feedback_rows_by_id(
                db_path=db_path,
                feedback_ids=[
                    _int_value(item.get("feedback_id")) for item in decisions
                ],
            )

    items = [
        _feedback_reclassify_preview_item(
            decision=decision,
            row=rows_by_id.get(_int_value(decision.get("feedback_id"))),
        )
        for decision in decisions
    ]
    ready_feedback = sum(1 for item in items if item.get("state") == "ready")
    item_blockers = [
        blocker
        for item in items
        if isinstance(item.get("blockers"), list)
        for blocker in item["blockers"]
        if isinstance(blocker, dict)
    ]
    all_blockers = [*blockers, *item_blockers]
    return {
        "schema_version": FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
        "state": "ok" if not all_blockers else "blocked",
        "mode": "preview",
        "manual_evals_db": {
            "path": str(db_path),
            "exists": db_path.is_file(),
            "integrity": integrity,
        },
        "plan": {
            "path": str(resolved_plan_path),
            "exists": resolved_plan_path.is_file(),
        },
        "counts": {
            "planned_feedback": len(decisions),
            "ready_feedback": ready_feedback,
            "blocked_feedback": len(items) - ready_feedback,
            "plan_blockers": len(blockers),
            "item_blockers": len(item_blockers),
        },
        "mutation_boundary": _feedback_reclassify_mutation_boundary(),
        "items": items,
        "blockers": all_blockers,
        "warnings": [],
    }


def _backup_manual_evals_db_for_feedback_reclassify(
    *,
    db_path: Path,
    backup_root: Path,
    applied_at: str,
    feedback_ids: Sequence[int],
    plan_path: Path,
) -> dict[str, Any]:
    backup_dir = backup_root / f"manual-evals-feedback-reclassify-{applied_at}"
    backup_db_path = backup_dir / "manual_evals.db"
    if backup_dir.exists():
        raise FileExistsError(f"backup directory already exists: {backup_dir}")
    _sqlite_backup_copy(
        source_db_path=db_path,
        destination_db_path=backup_db_path,
    )
    backup_integrity = _sqlite_integrity_check(backup_db_path)
    manifest_path = backup_dir / "manifest.json"
    restore_command = (
        f"cp {shlex.quote(str(backup_db_path))} {shlex.quote(str(db_path))}"
    )
    _write_json(
        manifest_path,
        {
            "schema_version": FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
            "created_at": applied_at,
            "source_db_path": str(db_path),
            "backup_db_path": str(backup_db_path),
            "backup_integrity": backup_integrity,
            "plan_path": str(plan_path),
            "feedback_ids": [int(feedback_id) for feedback_id in feedback_ids],
            "restore_command": restore_command,
        },
    )
    return {
        "written": True,
        "root": str(backup_root),
        "dir": str(backup_dir),
        "db_path": str(backup_db_path),
        "manifest_path": str(manifest_path),
        "integrity_check": backup_integrity,
        "restore_command": restore_command,
    }


def _feedback_reclassify_action_taken(
    *,
    feedback_id: int,
    current_cohort: str,
    new_cohort: str,
    rationale: str,
    backup_dir_name: str,
) -> str:
    rationale_text = f" Rationale: {rationale}." if rationale else ""
    return (
        "Reclassified by manual feedback reclassification gate: feedback "
        f"{feedback_id} moved from {current_cohort or 'unknown'} to "
        f"{new_cohort or 'unknown'}.{rationale_text} Backup: {backup_dir_name}."
    )


def _blocked_feedback_reclassify_apply_report(
    *,
    db_path: Path,
    plan_path: Path,
    preview: dict[str, Any],
    confirm_token: str,
    backup_root: Path,
    blockers: Sequence[dict[str, str]],
    backup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preview_counts = preview.get("counts")
    if not isinstance(preview_counts, dict):
        preview_counts = {}
    return {
        "schema_version": FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
        "state": "blocked",
        "mode": "apply",
        "manual_evals_db": {"path": str(db_path), "backup_required": True},
        "plan": {"path": str(plan_path), "exists": plan_path.is_file()},
        "confirmation": {
            "required": FEEDBACK_RECLASSIFY_CONFIRM_TOKEN,
            "provided": bool(confirm_token),
            "state": "ok"
            if confirm_token == FEEDBACK_RECLASSIFY_CONFIRM_TOKEN
            else "blocked",
        },
        "counts": {
            "planned_feedback": _int_value(preview_counts.get("planned_feedback")),
            "ready_feedback": _int_value(preview_counts.get("ready_feedback")),
            "blocked_feedback": _int_value(preview_counts.get("blocked_feedback")),
            "updated_feedback_rows": 0,
            "backups_written": 1 if backup and backup.get("written") else 0,
            "apply_blockers": len(blockers),
        },
        "mutation_boundary": _feedback_reclassify_mutation_boundary(),
        "backup": backup
        or {
            "written": False,
            "root": str(backup_root),
            "dir": "",
            "db_path": "",
            "restore_command": "",
        },
        "apply_items": [],
        "apply_blockers": list(blockers),
        "warnings": [blocker["detail"] for blocker in blockers],
    }


def write_feedback_reclassify(
    *,
    db_path: Path,
    plan_path: Path | None,
    confirm_token: str,
    backup_root: Path | None = None,
    applied_at: str | None = None,
) -> dict[str, Any]:
    resolved_db_path = db_path.expanduser()
    resolved_plan_path = (
        plan_path.expanduser()
        if plan_path is not None
        else DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH
    )
    resolved_backup_root = (
        backup_root.expanduser()
        if backup_root is not None
        else DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT
    )
    preview = build_feedback_reclassify_report(
        db_path=resolved_db_path,
        plan_path=resolved_plan_path,
    )
    blockers: list[dict[str, str]] = []
    if confirm_token != FEEDBACK_RECLASSIFY_CONFIRM_TOKEN:
        blockers.append(
            _feedback_reclassify_blocker(
                "missing_confirmation",
                "CONFIRM=manual-evals-feedback-reclassify is required before feedback reclassification.",
            )
        )
    if preview.get("state") != "ok":
        blockers.append(
            _feedback_reclassify_blocker(
                "preview_not_ok",
                f"feedback reclassification preview is {preview.get('state') or 'unknown'}.",
            )
        )
    items = preview.get("items")
    if not isinstance(items, list):
        items = []
    ready_items = [
        item
        for item in items
        if isinstance(item, dict) and item.get("state") == "ready"
    ]
    if not ready_items:
        blockers.append(
            _feedback_reclassify_blocker(
                "no_ready_feedback",
                "No ready feedback rows are available to reclassify.",
            )
        )
    if len(ready_items) != len(items):
        blockers.append(
            _feedback_reclassify_blocker(
                "items_not_all_ready",
                "Every feedback reclassification preview item must be ready before apply.",
            )
        )
    feedback_ids, invalid_feedback_ids = _feedback_ids_from_closure_items(ready_items)
    if invalid_feedback_ids:
        blockers.append(
            _feedback_reclassify_blocker(
                "invalid_feedback_id",
                "Feedback reclassification preview contains non-integer feedback IDs: "
                + ",".join(invalid_feedback_ids),
            )
        )
    if blockers:
        return _blocked_feedback_reclassify_apply_report(
            db_path=resolved_db_path,
            plan_path=resolved_plan_path,
            preview=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=blockers,
        )

    actual_applied_at = applied_at or _utc_run_timestamp()
    try:
        backup = _backup_manual_evals_db_for_feedback_reclassify(
            db_path=resolved_db_path,
            backup_root=resolved_backup_root,
            applied_at=actual_applied_at,
            feedback_ids=feedback_ids,
            plan_path=resolved_plan_path,
        )
    except (OSError, sqlite3.Error) as exc:
        return _blocked_feedback_reclassify_apply_report(
            db_path=resolved_db_path,
            plan_path=resolved_plan_path,
            preview=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=[
                _feedback_reclassify_blocker(
                    "backup_failed",
                    f"manual eval warehouse backup failed: {exc}",
                )
            ],
        )
    if backup.get("integrity_check") != "ok":
        return _blocked_feedback_reclassify_apply_report(
            db_path=resolved_db_path,
            plan_path=resolved_plan_path,
            preview=preview,
            confirm_token=confirm_token,
            backup_root=resolved_backup_root,
            blockers=[
                _feedback_reclassify_blocker(
                    "backup_integrity_not_ok",
                    "manual eval warehouse backup integrity check returned "
                    f"{backup.get('integrity_check') or 'missing'}.",
                )
            ],
            backup=backup,
        )

    item_by_feedback_id = {
        _int_value(item.get("feedback_id")): item for item in ready_items
    }
    backup_dir_name = Path(str(backup.get("dir") or "")).name
    updated_at = int(datetime.now(UTC).timestamp())
    apply_items: list[dict[str, Any]] = []
    with closing(sqlite3.connect(resolved_db_path)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("BEGIN IMMEDIATE")
        current_rows = conn.execute(
            "SELECT id, status FROM feedback WHERE id IN ("
            + ",".join("?" for _ in feedback_ids)
            + ")",
            feedback_ids,
        ).fetchall()
        current_statuses = {
            _int_value(row["id"]): str(row["status"] or "") for row in current_rows
        }
        no_longer_open = [
            f"{feedback_id}={current_statuses.get(feedback_id) or 'missing'}"
            for feedback_id in feedback_ids
            if not _feedback_status_is_open(current_statuses.get(feedback_id))
        ]
        if no_longer_open:
            conn.rollback()
            return _blocked_feedback_reclassify_apply_report(
                db_path=resolved_db_path,
                plan_path=resolved_plan_path,
                preview=preview,
                confirm_token=confirm_token,
                backup_root=resolved_backup_root,
                blockers=[
                    _feedback_reclassify_blocker(
                        "feedback_rows_changed_after_backup",
                        "Feedback rows changed after backup and before apply: "
                        + ",".join(no_longer_open),
                    )
                ],
                backup=backup,
            )
        for feedback_id in feedback_ids:
            item = item_by_feedback_id[feedback_id]
            new_action = str(item.get("new_recommended_action") or "")
            action_taken = _feedback_reclassify_action_taken(
                feedback_id=feedback_id,
                current_cohort=str(item.get("current_cohort") or ""),
                new_cohort=str(item.get("new_cohort") or ""),
                rationale=str(item.get("rationale") or ""),
                backup_dir_name=backup_dir_name,
            )
            conn.execute(
                """
                UPDATE feedback
                SET recommended_action = ?,
                    action_taken = ?,
                    updated_at = ?
                WHERE id = ? AND lower(status) = ?
                """,
                (new_action, action_taken, updated_at, feedback_id, "open"),
            )
            apply_items.append(
                {
                    "feedback_id": feedback_id,
                    "message_id": str(item.get("message_id") or ""),
                    "outcome": str(item.get("outcome") or ""),
                    "recommended_action_before": str(
                        item.get("current_recommended_action") or ""
                    ),
                    "recommended_action_after": new_action,
                    "current_cohort": str(item.get("current_cohort") or ""),
                    "new_cohort": str(item.get("new_cohort") or ""),
                    "action_taken": action_taken,
                    "status": current_statuses.get(feedback_id) or "open",
                    "updated_at": updated_at,
                    "mutation": "recommended_action,action_taken,updated_at",
                }
            )
        conn.commit()

    return {
        "schema_version": FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
        "state": "applied",
        "mode": "apply",
        "applied_at": actual_applied_at,
        "manual_evals_db": {
            "path": str(resolved_db_path),
            "backup_required": True,
            "integrity_check": "ok",
        },
        "plan": {"path": str(resolved_plan_path), "exists": True},
        "confirmation": {
            "required": FEEDBACK_RECLASSIFY_CONFIRM_TOKEN,
            "provided": True,
            "state": "ok",
        },
        "counts": {
            "planned_feedback": len(items),
            "ready_feedback": len(ready_items),
            "blocked_feedback": 0,
            "updated_feedback_rows": len(apply_items),
            "backups_written": 1,
            "apply_blockers": 0,
        },
        "mutation_boundary": _feedback_reclassify_mutation_boundary(),
        "backup": backup,
        "apply_items": apply_items,
        "updated_feedback_ids": feedback_ids,
        "apply_blockers": [],
        "warnings": [],
    }


def _feedback_ids_from_closure_items(
    closure_items: Sequence[dict[str, Any]],
) -> tuple[list[int], list[str]]:
    feedback_ids: list[int] = []
    invalid_feedback_ids: list[str] = []
    seen: set[int] = set()
    for item in closure_items:
        raw_feedback_id = str(item.get("feedback_id") or "").strip()
        try:
            feedback_id = int(raw_feedback_id)
        except ValueError:
            invalid_feedback_ids.append(raw_feedback_id or "<empty>")
            continue
        if feedback_id < 1:
            invalid_feedback_ids.append(raw_feedback_id)
            continue
        if feedback_id in seen:
            continue
        seen.add(feedback_id)
        feedback_ids.append(feedback_id)
    return feedback_ids, invalid_feedback_ids


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


def _backup_manual_evals_db_for_feedback_closure(
    *,
    db_path: Path,
    backup_root: Path,
    applied_at: str,
    run_id: str,
    feedback_ids: Sequence[int],
) -> dict[str, Any]:
    backup_dir = backup_root / f"manual-evals-feedback-closure-apply-{applied_at}"
    backup_db_path = backup_dir / "manual_evals.db"
    if backup_dir.exists():
        raise FileExistsError(f"backup directory already exists: {backup_dir}")
    backup_dir.mkdir(parents=True)
    with closing(sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)) as source:
        with closing(sqlite3.connect(backup_db_path)) as destination:
            source.backup(destination)
    with closing(sqlite3.connect(backup_db_path)) as conn:
        row = conn.execute("PRAGMA integrity_check").fetchone()
    backup_integrity = str(row[0] or "") if row else "missing"
    manifest_path = backup_dir / "manifest.json"
    restore_command = (
        f"cp {shlex.quote(str(backup_db_path))} {shlex.quote(str(db_path))}"
    )
    _write_json(
        manifest_path,
        {
            "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
            "created_at": applied_at,
            "run_id": run_id,
            "source_db_path": str(db_path),
            "backup_db_path": str(backup_db_path),
            "backup_integrity": backup_integrity,
            "feedback_ids": [int(feedback_id) for feedback_id in feedback_ids],
            "restore_command": restore_command,
        },
    )
    return {
        "written": True,
        "root": str(backup_root),
        "dir": str(backup_dir),
        "db_path": str(backup_db_path),
        "manifest_path": str(manifest_path),
        "integrity_check": backup_integrity,
        "restore_command": restore_command,
    }


def _feedback_closure_action_taken(
    *,
    run_id: str,
    feedback_id: int,
    evidence_count: int,
    backup_dir_name: str,
) -> str:
    evidence_text = "request" if evidence_count == 1 else "requests"
    return (
        "Closed by OCR retry feedback-closure apply: "
        f"bundle {run_id} produced successful retry evidence for feedback "
        f"{feedback_id} from {evidence_count} {evidence_text}. "
        f"Backup: {backup_dir_name}."
    )


def write_ocr_retry_feedback_closure_apply(
    *,
    db_path: Path,
    run_dir: Path | None,
    confirm_token: str,
    backup_root: Path | None = None,
    applied_at: str | None = None,
) -> dict[str, Any]:
    resolved_db_path = db_path.expanduser()
    resolved_run_dir = run_dir.expanduser() if run_dir else None
    resolved_backup_root = (
        backup_root.expanduser()
        if backup_root is not None
        else DEFAULT_FEEDBACK_CLOSURE_APPLY_BACKUP_ROOT
    )
    preview_report = build_ocr_retry_feedback_closure_preview_report(
        run_dir=resolved_run_dir
    )
    blockers: list[dict[str, str]] = []

    if confirm_token != OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN:
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "missing_confirmation",
                "CONFIRM=ocr-retry-feedback-closure-apply is required before feedback closure apply.",
            )
        )
    if not resolved_db_path.is_file():
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "manual_evals_db_not_found",
                f"manual eval warehouse was not found: {resolved_db_path}",
            )
        )
    bundle_state = str(preview_report.get("bundle_state") or "unknown")
    preview_state = str(preview_report.get("state") or "unknown")
    if bundle_state != "ok":
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "bundle_report_not_ok",
                f"OCR retry execution bundle report is {bundle_state}.",
            )
        )
    if preview_state != "ok":
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "preview_not_ok",
                f"OCR retry feedback-closure preview is {preview_state}.",
            )
        )

    closure_items = preview_report.get("closure_items")
    if not isinstance(closure_items, list):
        closure_items = []
    ready_closure_items = [
        item
        for item in closure_items
        if isinstance(item, dict) and item.get("state") == "ready"
    ]
    if not ready_closure_items:
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "no_ready_feedback",
                "No ready feedback closure items are available to apply.",
            )
        )
    if len(ready_closure_items) != len(closure_items):
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "closure_items_not_all_ready",
                "Every feedback closure preview item must be ready before apply.",
            )
        )

    feedback_ids, invalid_feedback_ids = _feedback_ids_from_closure_items(
        ready_closure_items
    )
    if invalid_feedback_ids:
        blockers.append(
            _ocr_retry_feedback_closure_apply_blocker(
                "invalid_feedback_id",
                "Feedback closure preview contains non-integer feedback IDs: "
                + ",".join(invalid_feedback_ids),
            )
        )

    rows_by_id: dict[int, dict[str, Any]] = {}
    if not blockers and feedback_ids:
        try:
            integrity = _sqlite_integrity_check(resolved_db_path)
        except sqlite3.Error as exc:
            blockers.append(
                _ocr_retry_feedback_closure_apply_blocker(
                    "manual_evals_db_integrity_check_failed",
                    f"manual eval warehouse integrity check failed: {exc}",
                )
            )
        else:
            if integrity != "ok":
                blockers.append(
                    _ocr_retry_feedback_closure_apply_blocker(
                        "manual_evals_db_integrity_not_ok",
                        f"manual eval warehouse integrity check returned {integrity}.",
                    )
                )
        if not blockers:
            rows_by_id = _feedback_rows_by_id(
                db_path=resolved_db_path,
                feedback_ids=feedback_ids,
            )
            missing_feedback_ids = [
                feedback_id
                for feedback_id in feedback_ids
                if feedback_id not in rows_by_id
            ]
            if missing_feedback_ids:
                blockers.append(
                    _ocr_retry_feedback_closure_apply_blocker(
                        "feedback_rows_missing",
                        "Feedback rows are missing from the current warehouse: "
                        + ",".join(
                            str(feedback_id) for feedback_id in missing_feedback_ids
                        ),
                    )
                )
            non_open_feedback = [
                f"{feedback_id}={rows_by_id[feedback_id].get('status') or 'unknown'}"
                for feedback_id in feedback_ids
                if not _feedback_status_is_open(
                    rows_by_id.get(feedback_id, {}).get("status")
                )
            ]
            if non_open_feedback:
                blockers.append(
                    _ocr_retry_feedback_closure_apply_blocker(
                        "feedback_rows_not_open",
                        "Feedback rows are no longer open: "
                        + ",".join(non_open_feedback),
                    )
                )

    if blockers:
        return _blocked_ocr_retry_feedback_closure_apply_report(
            db_path=resolved_db_path,
            run_dir=resolved_run_dir,
            backup_root=resolved_backup_root,
            confirm_token=confirm_token,
            preview_report=preview_report,
            blockers=blockers,
        )

    run_id = str(preview_report.get("run_id") or "")
    actual_applied_at = applied_at or _utc_run_timestamp()
    try:
        backup = _backup_manual_evals_db_for_feedback_closure(
            db_path=resolved_db_path,
            backup_root=resolved_backup_root,
            applied_at=actual_applied_at,
            run_id=run_id,
            feedback_ids=feedback_ids,
        )
    except (OSError, sqlite3.Error) as exc:
        return _blocked_ocr_retry_feedback_closure_apply_report(
            db_path=resolved_db_path,
            run_dir=resolved_run_dir,
            backup_root=resolved_backup_root,
            confirm_token=confirm_token,
            preview_report=preview_report,
            blockers=[
                _ocr_retry_feedback_closure_apply_blocker(
                    "backup_failed",
                    f"manual eval warehouse backup failed: {exc}",
                )
            ],
        )
    if backup.get("integrity_check") != "ok":
        return _blocked_ocr_retry_feedback_closure_apply_report(
            db_path=resolved_db_path,
            run_dir=resolved_run_dir,
            backup_root=resolved_backup_root,
            confirm_token=confirm_token,
            preview_report=preview_report,
            blockers=[
                _ocr_retry_feedback_closure_apply_blocker(
                    "backup_integrity_not_ok",
                    "manual eval warehouse backup integrity check returned "
                    f"{backup.get('integrity_check') or 'missing'}.",
                )
            ],
            backup=backup,
        )

    backup_dir_name = Path(str(backup.get("dir") or "")).name
    updated_at = int(datetime.now(UTC).timestamp())
    apply_items: list[dict[str, Any]] = []
    item_by_feedback_id = {
        int(feedback_id): item
        for feedback_id, item in zip(feedback_ids, ready_closure_items, strict=True)
    }
    with closing(sqlite3.connect(resolved_db_path)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("BEGIN IMMEDIATE")
        current_rows = conn.execute(
            "SELECT id, status FROM feedback WHERE id IN ("
            + ",".join("?" for _ in feedback_ids)
            + ")",
            feedback_ids,
        ).fetchall()
        current_statuses = {
            _int_value(row["id"]): str(row["status"] or "") for row in current_rows
        }
        no_longer_open = [
            f"{feedback_id}={current_statuses.get(feedback_id) or 'missing'}"
            for feedback_id in feedback_ids
            if not _feedback_status_is_open(current_statuses.get(feedback_id))
        ]
        if no_longer_open:
            conn.rollback()
            return _blocked_ocr_retry_feedback_closure_apply_report(
                db_path=resolved_db_path,
                run_dir=resolved_run_dir,
                backup_root=resolved_backup_root,
                confirm_token=confirm_token,
                preview_report=preview_report,
                blockers=[
                    _ocr_retry_feedback_closure_apply_blocker(
                        "feedback_rows_changed_after_backup",
                        "Feedback rows changed after backup and before apply: "
                        + ",".join(no_longer_open),
                    )
                ],
                backup=backup,
            )
        for feedback_id in feedback_ids:
            preview_item = item_by_feedback_id[feedback_id]
            evidence = preview_item.get("evidence")
            evidence_count = len(evidence) if isinstance(evidence, list) else 0
            status_before = current_statuses.get(feedback_id) or "open"
            status_after = _closed_feedback_status_for_open_status(status_before)
            action_taken = _feedback_closure_action_taken(
                run_id=run_id,
                feedback_id=feedback_id,
                evidence_count=evidence_count,
                backup_dir_name=backup_dir_name,
            )
            conn.execute(
                """
                UPDATE feedback
                SET status = ?,
                    action_taken = ?,
                    updated_at = ?
                WHERE id = ? AND lower(status) = ?
                """,
                (status_after, action_taken, updated_at, feedback_id, "open"),
            )
            apply_items.append(
                {
                    "feedback_id": feedback_id,
                    "status_before": status_before,
                    "status_after": status_after,
                    "action_taken": action_taken,
                    "updated_at": updated_at,
                    "evidence_count": evidence_count,
                    "mutation": "status,action_taken,updated_at",
                }
            )
        conn.commit()

    report = {
        "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
        "state": "applied",
        "run_dir": str(resolved_run_dir or ""),
        "run_id": run_id,
        "bundle_state": bundle_state,
        "preview_state": preview_state,
        "applied_at": actual_applied_at,
        "confirmation": {
            "required": OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
            "provided": True,
            "state": "ok",
        },
        "manual_evals_db": {
            "path": str(resolved_db_path),
            "backup_required": True,
            "integrity_check": "ok",
        },
        "counts": _feedback_closure_apply_counts(
            preview_report,
            target_feedback_rows=len(feedback_ids),
            updated_feedback_rows=len(apply_items),
            skipped_feedback_rows=0,
            backups_written=1,
        ),
        "mutation_boundary": _ocr_retry_feedback_closure_apply_mutation_boundary(),
        "backup": backup,
        "apply_items": apply_items,
        "updated_feedback_ids": feedback_ids,
        "skipped_feedback_ids": [],
        "apply_blockers": [],
        "warnings": [],
    }
    if resolved_run_dir is not None and resolved_run_dir.is_dir():
        summary_path = resolved_run_dir / "feedback_closure_apply_summary.json"
        report["output"] = {
            "summary_path": str(summary_path),
            "written": True,
        }
        _write_json(summary_path, report)
    else:
        report["output"] = {
            "summary_path": "",
            "written": False,
        }
    return report


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
        summary, parse_errors = _read_json_object(summary_path)
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
    expected_boundary = _ocr_retry_feedback_closure_apply_mutation_boundary()
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


def _feedback_closure_restore_blocker(
    code: str,
    detail: str,
) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _ocr_retry_feedback_closure_restore_mutation_boundary() -> dict[str, str]:
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
            parsed_manifest, parse_errors = _read_json_object(manifest_path)
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
        "mutation_boundary": _ocr_retry_feedback_closure_restore_mutation_boundary(),
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
        "mutation_boundary": _ocr_retry_feedback_closure_restore_mutation_boundary(),
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


def format_ocr_retry_execution_bundle_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    files_available = _int_value(counts.get("files_available"))
    files_expected = _int_value(counts.get("files_expected"))
    run_dir_name = Path(str(report.get("run_dir") or "none")).name or "none"

    lines = [
        "manual eval OCR retry execution bundle: "
        f"state={report.get('state', 'unknown')} "
        f"run={report.get('run_id') or 'unknown'} "
        f"execution={report.get('execution_state') or 'unknown'} "
        f"readiness={report.get('readiness_state') or 'unknown'} "
        f"provider={report.get('ocr_provider') or 'unknown'} "
        f"model={report.get('ocr_model') or 'unknown'} "
        f"requests={_int_value(counts.get('requests'))} "
        f"responses={_int_value(counts.get('responses'))} "
        f"succeeded={_int_value(counts.get('succeeded'))} "
        f"failed={_int_value(counts.get('failed'))} "
        f"skipped={_int_value(counts.get('skipped_after_stop'))} "
        f"warehouse_mutation={mutation.get('manual_eval_warehouse') or 'none'} "
        f"files={files_available}/{files_expected} "
        f"dir={run_dir_name}",
    ]
    blockers = report.get("inspection_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("inspection_blockers:")
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


def format_ocr_retry_feedback_closure_preview_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    run_dir_name = Path(str(report.get("run_dir") or "none")).name or "none"

    lines = [
        "manual eval OCR retry feedback closure preview: "
        f"state={report.get('state', 'unknown')} "
        f"run={report.get('run_id') or 'unknown'} "
        f"bundle={report.get('bundle_state') or 'unknown'} "
        f"feedback={_int_value(counts.get('feedback_items'))} "
        f"ready={_int_value(counts.get('ready_feedback'))} "
        f"attention={_int_value(counts.get('attention_feedback'))} "
        f"blocked={_int_value(counts.get('blocked_feedback'))} "
        f"requests={_int_value(counts.get('bundle_requests'))} "
        f"responses={_int_value(counts.get('bundle_responses'))} "
        "requests_without_feedback_ids="
        f"{_int_value(counts.get('requests_without_feedback_ids'))} "
        f"feedback_closure={mutation.get('feedback_closure') or 'none'} "
        f"warehouse_mutation={mutation.get('manual_eval_warehouse') or 'none'} "
        f"dir={run_dir_name}",
    ]
    closure_items = report.get("closure_items")
    if isinstance(closure_items, list) and closure_items:
        lines.append("closure_items:")
        for item in closure_items:
            if not isinstance(item, dict):
                continue
            evidence = item.get("evidence")
            evidence_count = len(evidence) if isinstance(evidence, list) else 0
            lines.append(
                "- "
                f"feedback={item.get('feedback_id') or 'unknown'} "
                f"state={item.get('state') or 'unknown'} "
                f"reason={item.get('reason') or 'unknown'} "
                f"proposed_status={item.get('proposed_feedback_status') or 'open'} "
                f"evidence={evidence_count} "
                f"mutation={item.get('mutation') or 'none'}"
            )
    blockers = report.get("preview_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("preview_blockers:")
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


def format_ocr_retry_feedback_closure_apply_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    backup = report.get("backup")
    if not isinstance(backup, dict):
        backup = {}
    run_dir_name = Path(str(report.get("run_dir") or "none")).name or "none"
    backup_dir_name = Path(str(backup.get("dir") or "none")).name or "none"

    lines = [
        "manual eval OCR retry feedback closure apply: "
        f"state={report.get('state', 'unknown')} "
        f"run={report.get('run_id') or 'unknown'} "
        f"bundle={report.get('bundle_state') or 'unknown'} "
        f"preview={report.get('preview_state') or 'unknown'} "
        f"feedback={_int_value(counts.get('target_feedback_rows'))} "
        f"updated={_int_value(counts.get('updated_feedback_rows'))} "
        f"skipped={_int_value(counts.get('skipped_feedback_rows'))} "
        f"backups={_int_value(counts.get('backups_written'))} "
        f"feedback_closure={mutation.get('feedback_closure') or 'none'} "
        f"warehouse_mutation={mutation.get('manual_eval_warehouse') or 'none'} "
        f"dir={run_dir_name} "
        f"backup_dir={backup_dir_name}",
    ]
    apply_items = report.get("apply_items")
    if isinstance(apply_items, list) and apply_items:
        lines.append("apply_items:")
        for item in apply_items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"feedback={item.get('feedback_id') or 'unknown'} "
                f"status={item.get('status_before') or 'unknown'}"
                f"->{item.get('status_after') or 'unknown'} "
                f"evidence={_int_value(item.get('evidence_count'))} "
                f"mutation={item.get('mutation') or 'none'}"
            )
    blockers = report.get("apply_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("apply_blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"code={blocker.get('code') or 'unknown'} "
                f"detail={blocker.get('detail') or ''}"
            )
    if backup.get("restore_command"):
        lines.append("restore_hint=stop local server and restore from backup manifest")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def format_ocr_retry_feedback_closure_apply_verification_report(
    report: dict[str, Any],
) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    backup = report.get("backup")
    if not isinstance(backup, dict):
        backup = {}
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    run_dir_name = Path(str(report.get("run_dir") or "none")).name or "none"
    backup_dir_name = Path(str(backup.get("dir") or "none")).name or "none"

    lines = [
        "manual eval OCR retry feedback closure apply report: "
        f"state={report.get('state', 'unknown')} "
        f"run={report.get('run_id') or 'unknown'} "
        f"feedback={_int_value(counts.get('target_feedback_rows'))} "
        f"active_closed={_int_value(counts.get('active_closed_feedback'))} "
        f"backup_open={_int_value(counts.get('backup_open_feedback'))} "
        f"active_missing={_int_value(counts.get('active_missing_feedback'))} "
        f"backup_missing={_int_value(counts.get('backup_missing_feedback'))} "
        f"blockers={_int_value(counts.get('report_blockers'))} "
        f"active_integrity={manual_db.get('integrity_check') or 'unknown'} "
        f"backup_integrity={backup.get('integrity_check') or 'unknown'} "
        f"dir={run_dir_name} "
        f"backup_dir={backup_dir_name}",
    ]
    feedback_rows = report.get("feedback_rows")
    if isinstance(feedback_rows, list) and feedback_rows:
        lines.append("feedback_rows:")
        for row in feedback_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- "
                f"feedback={row.get('feedback_id') or 'unknown'} "
                f"active={row.get('active_status') or 'unknown'} "
                f"backup={row.get('backup_status') or 'unknown'} "
                "action_taken="
                f"{'yes' if row.get('active_action_taken_present') else 'no'}"
            )
    blockers = report.get("report_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("report_blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"code={blocker.get('code') or 'unknown'} "
                f"detail={blocker.get('detail') or ''}"
            )
    if backup.get("restore_command"):
        lines.append("restore_hint=stop local server and restore from backup manifest")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def format_ocr_retry_feedback_closure_restore_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    source_backup = report.get("source_backup")
    if not isinstance(source_backup, dict):
        source_backup = {}
    pre_restore_backup = report.get("pre_restore_backup")
    if not isinstance(pre_restore_backup, dict):
        pre_restore_backup = {}
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    backup_dir_name = Path(str(source_backup.get("dir") or "none")).name or "none"
    restore_dir_name = Path(str(pre_restore_backup.get("dir") or "none")).name or "none"

    lines = [
        "manual eval OCR retry feedback closure restore: "
        f"state={report.get('state', 'unknown')} "
        f"mode={report.get('mode') or 'unknown'} "
        f"run={report.get('run_id') or 'unknown'} "
        f"feedback={_int_value(counts.get('target_feedback_rows'))} "
        f"active_closed={_int_value(counts.get('active_closed_feedback'))} "
        f"backup_open={_int_value(counts.get('backup_open_feedback'))} "
        f"restored={_int_value(counts.get('restored_feedback_rows'))} "
        f"backups={_int_value(counts.get('backups_written'))} "
        f"blockers={_int_value(counts.get('restore_blockers'))} "
        f"active_integrity={manual_db.get('integrity_check') or 'unknown'} "
        f"backup_integrity={source_backup.get('integrity_check') or 'unknown'} "
        f"warehouse_mutation={mutation.get('manual_eval_warehouse') or 'none'} "
        f"backup_dir={backup_dir_name} "
        f"restore_dir={restore_dir_name}",
    ]
    feedback_rows = report.get("feedback_rows")
    if isinstance(feedback_rows, list) and feedback_rows:
        lines.append("feedback_rows:")
        for row in feedback_rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "- "
                f"feedback={row.get('feedback_id') or 'unknown'} "
                f"active={row.get('active_status') or 'unknown'} "
                f"backup={row.get('backup_status') or 'unknown'} "
                "action_taken="
                f"{'yes' if row.get('active_action_taken_present') else 'no'}"
            )
    restore_items = report.get("restore_items")
    if isinstance(restore_items, list) and restore_items:
        lines.append("restore_items:")
        for item in restore_items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"feedback={item.get('feedback_id') or 'unknown'} "
                f"status={item.get('status_before') or 'unknown'}"
                f"->{item.get('status_after') or 'unknown'} "
                f"mutation={item.get('mutation') or 'none'}"
            )
    blockers = report.get("restore_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("restore_blockers:")
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


def format_no_context_feedback_reclassify_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    backup = report.get("backup")
    if not isinstance(backup, dict):
        backup = {}
    lines = [
        "manual eval no-context feedback reclassify: "
        f"state={report.get('state') or 'unknown'} "
        f"mode={report.get('mode') or 'unknown'} "
        f"feedback={_int_value(counts.get('candidate_feedback'))} "
        f"ready={_int_value(counts.get('ready_feedback'))} "
        f"blocked={_int_value(counts.get('blocked_feedback'))} "
        f"updated={_int_value(counts.get('updated_feedback_rows'))} "
        f"mutation={mutation.get('manual_evals_db') or 'none'} "
        f"backup_dir={Path(str(backup.get('dir') or '')).name}",
    ]
    items = report.get("items")
    if not isinstance(items, list):
        items = report.get("apply_items")
    if isinstance(items, list) and items:
        lines.append("feedback_rows:")
        for item in items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"feedback={item.get('feedback_id') or 'unknown'} "
                f"state={item.get('state') or report.get('state') or 'unknown'} "
                f"outcome={item.get('outcome') or ''} "
                f"message={item.get('message_id') or ''} "
                f"mutation={item.get('mutation') or 'preview'}"
            )
            blockers = item.get("blockers")
            if isinstance(blockers, list) and blockers:
                for blocker in blockers:
                    if not isinstance(blocker, dict):
                        continue
                    lines.append(
                        "  blocker="
                        f"{blocker.get('code') or 'unknown'} "
                        f"detail={blocker.get('detail') or ''}"
                    )
    blockers = report.get("apply_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("apply_blockers:")
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


def format_feedback_reclassify_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    backup = report.get("backup")
    if not isinstance(backup, dict):
        backup = {}
    lines = [
        "manual eval feedback reclassify: "
        f"state={report.get('state') or 'unknown'} "
        f"mode={report.get('mode') or 'unknown'} "
        f"planned={_int_value(counts.get('planned_feedback'))} "
        f"ready={_int_value(counts.get('ready_feedback'))} "
        f"blocked={_int_value(counts.get('blocked_feedback'))} "
        f"updated={_int_value(counts.get('updated_feedback_rows'))} "
        f"mutation={mutation.get('manual_evals_db') or 'none'} "
        f"backup_dir={Path(str(backup.get('dir') or '')).name}",
    ]
    items = report.get("items")
    if not isinstance(items, list):
        items = report.get("apply_items")
    if isinstance(items, list) and items:
        lines.append("feedback_rows:")
        for item in items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"feedback={item.get('feedback_id') or 'unknown'} "
                f"state={item.get('state') or report.get('state') or 'unknown'} "
                f"from={item.get('current_cohort') or 'unknown'} "
                f"to={item.get('new_cohort') or 'unknown'} "
                f"outcome={item.get('outcome') or ''} "
                f"message={item.get('message_id') or ''} "
                f"mutation={item.get('mutation') or 'preview'}"
            )
            blockers = item.get("blockers")
            if isinstance(blockers, list) and blockers:
                for blocker in blockers:
                    if not isinstance(blocker, dict):
                        continue
                    lines.append(
                        "  blocker="
                        f"{blocker.get('code') or 'unknown'} "
                        f"detail={blocker.get('detail') or ''}"
                    )
    blockers = report.get("blockers")
    if not isinstance(blockers, list):
        blockers = report.get("apply_blockers")
    if isinstance(blockers, list) and blockers:
        label = "apply_blockers" if report.get("mode") == "apply" else "blockers"
        lines.append(f"{label}:")
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
        "--feedback-source-context",
        action="store_true",
        help="Print read-only source-history context for selected open feedback rows.",
    )
    parser.add_argument(
        "--feedback-decision-preview",
        action="store_true",
        help="Preview a local human-reviewed feedback decision without mutation.",
    )
    parser.add_argument(
        "--feedback-decision-draft",
        action="store_true",
        help="Write a local manual feedback decision draft without mutation.",
    )
    parser.add_argument(
        "--overlay-ocr-comparison-readiness",
        action="store_true",
        help="Print read-only overlay/OCR comparison readiness packets.",
    )
    parser.add_argument(
        "--overlay-source-index-draft",
        action="store_true",
        help="Write a local fillable overlay/source image context index draft.",
    )
    parser.add_argument(
        "--overlay-source-index-validate",
        action="store_true",
        help="Validate a local overlay/source image context index against readiness.",
    )
    parser.add_argument(
        "--overlay-source-index",
        default="",
        help="Path to a local overlay/source image context index JSON file.",
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
        "--ocr-retry-execution-report",
        action="store_true",
        help="Inspect a local OCR retry execution run bundle without mutation.",
    )
    parser.add_argument(
        "--ocr-retry-feedback-closure-preview",
        action="store_true",
        help="Preview feedback closure from a local OCR retry execution bundle.",
    )
    parser.add_argument(
        "--ocr-retry-feedback-closure-apply",
        action="store_true",
        help="Apply guarded OCR retry feedback closure after backup.",
    )
    parser.add_argument(
        "--ocr-retry-feedback-closure-apply-report",
        action="store_true",
        help="Inspect an OCR retry feedback-closure apply summary without mutation.",
    )
    parser.add_argument(
        "--ocr-retry-feedback-closure-restore-preview",
        action="store_true",
        help="Preview restoring manual_evals.db from a feedback-closure apply backup.",
    )
    parser.add_argument(
        "--ocr-retry-feedback-closure-restore",
        action="store_true",
        help="Restore manual_evals.db from a verified feedback-closure apply backup.",
    )
    parser.add_argument(
        "--no-context-feedback-reclassify-preview",
        action="store_true",
        help="Preview reclassifying no-context OCR feedback into overlay-hypothesis evidence.",
    )
    parser.add_argument(
        "--no-context-feedback-reclassify-apply",
        action="store_true",
        help="Apply guarded overlay-hypothesis feedback reclassification after backup.",
    )
    parser.add_argument(
        "--feedback-reclassify-preview",
        action="store_true",
        help="Preview feedback reclassification from a local JSON decision plan.",
    )
    parser.add_argument(
        "--feedback-reclassify-apply",
        action="store_true",
        help="Apply guarded feedback reclassification from a local JSON decision plan.",
    )
    parser.add_argument(
        "--plan-path",
        default="",
        help="Path to a local manual feedback reclassification decision plan.",
    )
    parser.add_argument(
        "--decision-path",
        default="",
        help="Path to a local human-reviewed manual feedback decision JSON file.",
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
        "--run-dir",
        default="",
        help="Path to one local OCR retry execution run bundle.",
    )
    parser.add_argument(
        "--backup-root",
        default="",
        help="Root directory for local feedback-closure apply backups.",
    )
    parser.add_argument(
        "--backup-dir",
        default="",
        help="Path to one local feedback-closure apply backup directory.",
    )
    parser.add_argument(
        "--restore-root",
        default="",
        help="Root directory for local feedback-closure restore backups.",
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

    if args.ocr_retry_execution_report:
        report = build_ocr_retry_execution_bundle_report(
            run_dir=Path(args.run_dir) if str(args.run_dir).strip() else None,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_execution_bundle_report(report))
        return 2 if report.get("state") == "error" else 0

    if args.ocr_retry_feedback_closure_preview:
        report = build_ocr_retry_feedback_closure_preview_report(
            run_dir=Path(args.run_dir) if str(args.run_dir).strip() else None,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_feedback_closure_preview_report(report))
        return 2 if report.get("state") == "blocked" else 0

    if args.ocr_retry_feedback_closure_apply:
        report = write_ocr_retry_feedback_closure_apply(
            db_path=db_path,
            run_dir=Path(args.run_dir) if str(args.run_dir).strip() else None,
            confirm_token=str(args.confirm or ""),
            backup_root=Path(args.backup_root)
            if str(args.backup_root).strip()
            else None,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_feedback_closure_apply_report(report))
        return 0 if report.get("state") == "applied" else 2

    if args.ocr_retry_feedback_closure_apply_report:
        report = build_ocr_retry_feedback_closure_apply_report(
            db_path=db_path,
            run_dir=Path(args.run_dir) if str(args.run_dir).strip() else None,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_feedback_closure_apply_verification_report(report))
        return 0 if report.get("state") == "ok" else 2

    if args.ocr_retry_feedback_closure_restore_preview:
        report = build_ocr_retry_feedback_closure_restore_preview_report(
            db_path=db_path,
            backup_dir=Path(args.backup_dir) if str(args.backup_dir).strip() else None,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_feedback_closure_restore_report(report))
        return 0 if report.get("state") == "ok" else 2

    if args.ocr_retry_feedback_closure_restore:
        report = write_ocr_retry_feedback_closure_restore(
            db_path=db_path,
            backup_dir=Path(args.backup_dir) if str(args.backup_dir).strip() else None,
            confirm_token=str(args.confirm or ""),
            restore_root=Path(args.restore_root)
            if str(args.restore_root).strip()
            else None,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_ocr_retry_feedback_closure_restore_report(report))
        return 0 if report.get("state") == "restored" else 2

    if args.no_context_feedback_reclassify_preview:
        report = build_no_context_feedback_reclassify_report(
            db_path=db_path,
            outcome=args.outcome or "fail",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_no_context_feedback_reclassify_report(report))
        return 0 if report.get("state") == "ok" else 2

    if args.no_context_feedback_reclassify_apply:
        report = write_no_context_feedback_reclassify(
            db_path=db_path,
            confirm_token=str(args.confirm or ""),
            backup_root=Path(args.backup_root)
            if str(args.backup_root).strip()
            else None,
            outcome=args.outcome or "fail",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_no_context_feedback_reclassify_report(report))
        return 0 if report.get("state") == "applied" else 2

    if args.feedback_reclassify_preview:
        report = build_feedback_reclassify_report(
            db_path=db_path,
            plan_path=Path(args.plan_path) if str(args.plan_path).strip() else None,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_feedback_reclassify_report(report))
        return 0 if report.get("state") == "ok" else 2

    if args.feedback_reclassify_apply:
        report = write_feedback_reclassify(
            db_path=db_path,
            plan_path=Path(args.plan_path) if str(args.plan_path).strip() else None,
            confirm_token=str(args.confirm or ""),
            backup_root=Path(args.backup_root)
            if str(args.backup_root).strip()
            else None,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_feedback_reclassify_report(report))
        return 0 if report.get("state") == "applied" else 2

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

    if args.feedback_source_context:
        report = build_feedback_source_context_report(
            db_path=db_path,
            outcome=args.outcome or "fail",
            cohort=args.cohort or "grounding_source_verification",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_feedback_source_context_report(report))
        return 2 if report.get("state") == "error" else 0

    if args.overlay_ocr_comparison_readiness:
        report = build_overlay_ocr_comparison_readiness_report(
            db_path=db_path,
            outcome=args.outcome or "fail",
            cohort=args.cohort or "ocr_overlay_hypothesis",
            limit=max(1, args.limit),
            overlay_source_index_path=Path(args.overlay_source_index)
            if str(args.overlay_source_index).strip()
            else None,
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_overlay_ocr_comparison_readiness_report(report))
        return 2 if report.get("state") == "error" else 0

    if args.overlay_source_index_draft:
        report = write_overlay_source_context_index_draft(
            db_path=db_path,
            output_path=Path(args.output_path)
            if str(args.output_path).strip()
            else None,
            force=bool(args.force),
            outcome=args.outcome or "fail",
            cohort=args.cohort or "ocr_overlay_hypothesis",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_overlay_source_context_index_draft_report(report))
        return 0 if report.get("state") == "written" else 2

    if args.overlay_source_index_validate:
        report = build_overlay_source_context_index_validation_report(
            db_path=db_path,
            overlay_source_index_path=Path(args.overlay_source_index)
            if str(args.overlay_source_index).strip()
            else None,
            outcome=args.outcome or "fail",
            cohort=args.cohort or "ocr_overlay_hypothesis",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_overlay_source_context_index_validation_report(report))
        return 0 if report.get("state") == "ready" else 2

    if args.feedback_decision_draft:
        report = write_feedback_decision_draft(
            db_path=db_path,
            output_path=Path(args.output_path)
            if str(args.output_path).strip()
            else None,
            force=bool(args.force),
            outcome=args.outcome or "fail",
            cohort=args.cohort or "grounding_source_verification",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_feedback_decision_draft_report(report))
        return 0 if report.get("state") == "written" else 2

    if args.feedback_decision_preview:
        report = build_feedback_decision_preview_report(
            db_path=db_path,
            decision_path=Path(args.decision_path)
            if str(args.decision_path).strip()
            else None,
            outcome=args.outcome or "fail",
            cohort=args.cohort or "grounding_source_verification",
            limit=max(1, args.limit),
        )
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(format_feedback_decision_preview_report(report))
        return 0 if report.get("state") == "ok" else 2

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
