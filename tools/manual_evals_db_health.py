from __future__ import annotations

import argparse
import json
import os
import sqlite3
from collections.abc import Sequence
from contextlib import closing
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
from tools.manual_eval_feedback_reclassify import (
    DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT as DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT,
    DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH as DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH,
    FEEDBACK_RECLASSIFY_CONFIRM_TOKEN as FEEDBACK_RECLASSIFY_CONFIRM_TOKEN,
    FEEDBACK_RECLASSIFY_SCHEMA_VERSION as FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
    build_feedback_reclassify_report,
    write_feedback_reclassify,
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
DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH = (
    ocr_retry_selection_decision_draft.DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH
)
build_ocr_retry_selection_decision_draft_payload = (
    ocr_retry_selection_decision_draft.build_ocr_retry_selection_decision_draft_payload
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


def _feedback_status_normalized(status: object) -> str:
    return str(status or "").strip().casefold()


def _feedback_status_is_open(status: object) -> bool:
    return _feedback_status_normalized(status) == "open"


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
