from __future__ import annotations

import argparse
import json
import os
import shlex
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
    manual_eval_ocr_retry_execution_bundle_report as ocr_retry_execution_bundle_report,
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
from tools.manual_eval_no_context_feedback_reclassify import (
    DEFAULT_NO_CONTEXT_RECLASSIFY_BACKUP_ROOT as DEFAULT_NO_CONTEXT_RECLASSIFY_BACKUP_ROOT,
    NO_CONTEXT_RECLASSIFIED_RECOMMENDED_ACTION as NO_CONTEXT_RECLASSIFIED_RECOMMENDED_ACTION,
    NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN as NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN,
    NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION as NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
    build_no_context_feedback_reclassify_report,
    write_no_context_feedback_reclassify,
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
from tools.manual_eval_ocr_retry_execution_report import (
    format_ocr_retry_execution_bundle_report,
    format_ocr_retry_execution_report,
)
from tools.manual_eval_ocr_retry_execution_bundle_report import (
    build_ocr_retry_execution_bundle_report,
)
from tools.manual_eval_ocr_retry_execution_requests import (
    OcrRetryExecutionProviderError as OcrRetryExecutionProviderError,
)
from tools.manual_eval_ocr_retry_execution_writer import (
    DEFAULT_OCR_RETRY_EXECUTION_DIR as DEFAULT_OCR_RETRY_EXECUTION_DIR,
    DEFAULT_OCR_RETRY_MODEL,
    DEFAULT_OCR_RETRY_PROMPT,
    OCR_RETRY_EXECUTION_CONFIRM_TOKEN as OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
    write_ocr_retry_execution_bundle,
)
from tools.manual_eval_ocr_retry_feedback_closure_preview import (
    OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION as OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
    build_ocr_retry_feedback_closure_preview_report,
)
from tools.manual_eval_ocr_retry_feedback_closure_apply import (
    DEFAULT_FEEDBACK_CLOSURE_APPLY_BACKUP_ROOT as DEFAULT_FEEDBACK_CLOSURE_APPLY_BACKUP_ROOT,
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN as OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION as OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
    write_ocr_retry_feedback_closure_apply,
)
from tools.manual_eval_ocr_retry_feedback_closure_apply_report import (
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION as OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION,
    build_ocr_retry_feedback_closure_apply_report,
)
from tools.manual_eval_ocr_retry_feedback_closure_restore import (
    DEFAULT_FEEDBACK_CLOSURE_RESTORE_BACKUP_ROOT as DEFAULT_FEEDBACK_CLOSURE_RESTORE_BACKUP_ROOT,
    OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN as OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN,
    OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION as OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION,
    build_ocr_retry_feedback_closure_restore_preview_report,
    write_ocr_retry_feedback_closure_restore,
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
    build_open_feedback_actionables_report,
    build_open_feedback_cohorts_report,
    feedback_action_cohort as _feedback_action_cohort,
    format_open_feedback_actionables_report,
    format_open_feedback_cohorts_report,
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
OCR_RETRY_EXECUTION_SCHEMA_VERSION = (
    ocr_retry_execution_bundle_report.OCR_RETRY_EXECUTION_SCHEMA_VERSION
)
OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION = (
    ocr_retry_execution_bundle_report.OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION
)
FEEDBACK_RECLASSIFY_CONFIRM_TOKEN = "manual-evals-feedback-reclassify"
DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH = (
    ocr_retry_selection_decision_draft.DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH
)
build_ocr_retry_selection_decision_draft_payload = (
    ocr_retry_selection_decision_draft.build_ocr_retry_selection_decision_draft_payload
)
DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT = Path(".local_archive")
DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH = Path(
    ".local/manual_eval_decisions/feedback_reclassify.json"
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


def _utc_run_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _feedback_status_normalized(status: object) -> str:
    return str(status or "").strip().casefold()


def _feedback_status_is_open(status: object) -> bool:
    return _feedback_status_normalized(status) == "open"


def _feedback_status_is_closed(status: object) -> bool:
    return _feedback_status_normalized(status) == "closed"


def _closed_feedback_status_for_open_status(status: object) -> str:
    raw_status = str(status or "").strip()
    return "CLOSED" if raw_status.isupper() else "closed"


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


def _status_count(rows_by_id: dict[int, dict[str, Any]], status: str) -> int:
    return sum(
        1
        for row in rows_by_id.values()
        if _feedback_status_normalized(row.get("status")) == status.casefold()
    )


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
        help=(
            "Required confirmation token for guarded actions "
            "(CONFIRM=ocr-retry-execute, "
            "CONFIRM=ocr-retry-feedback-closure-apply, "
            "CONFIRM=ocr-retry-feedback-closure-restore)."
        ),
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
