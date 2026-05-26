from __future__ import annotations

from pathlib import Path

from tools import manual_eval_feedback_decisions as feedback_decisions
from tools import manual_eval_open_feedback as open_feedback
from tools import manual_eval_ocr_retry_candidates as ocr_retry_candidates
from tools import (
    manual_eval_ocr_retry_execution_bundle_report as ocr_retry_execution_bundle_report,
)
from tools import (
    manual_eval_ocr_retry_execution_readiness as ocr_retry_execution_readiness,
)
from tools import manual_eval_ocr_retry_input_packet as ocr_retry_input_packet
from tools import manual_eval_ocr_retry_rerun_manifest as ocr_retry_rerun_manifest
from tools import manual_eval_ocr_retry_rerun_plan as ocr_retry_rerun_plan
from tools import (
    manual_eval_ocr_retry_selection_apply_preview as ocr_retry_selection_apply_preview,
)
from tools import (
    manual_eval_ocr_retry_selection_decision_draft as ocr_retry_selection_decision_draft,
)
from tools import (
    manual_eval_ocr_retry_selection_review as ocr_retry_selection_review,
)
from tools import (
    manual_eval_ocr_retry_selection_template as ocr_retry_selection_template,
)
from tools import (
    manual_eval_ocr_retry_selection_validation as ocr_retry_selection_validation,
)
from tools import (
    manual_eval_ocr_retry_source_provenance as ocr_retry_source_provenance,
)
from tools import (
    manual_eval_ocr_retry_source_verification as ocr_retry_source_verification,
)
from tools import manual_eval_overlay_readiness as overlay_readiness_reports
from tools import manual_eval_overlay_source_index as overlay_source_index
from tools import manual_eval_source_context as source_context_reports


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
OCR_RETRY_FEEDBACK_CLOSURE_WAREHOUSE_MUTATION_FIELD = "manual_eval_warehouse"
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
OCR_RETRY_TERMINAL_CONTEXT_LIMIT = ocr_retry_candidates.OCR_RETRY_TERMINAL_CONTEXT_LIMIT

__all__ = [
    "ACTIONABLES_SCHEMA_VERSION",
    "COHORTS_SCHEMA_VERSION",
    "COHORT_DESCRIPTIONS",
    "COHORT_FILTER_CHOICES",
    "COHORT_IDS",
    "DEFAULT_DB_PATH",
    "DEFAULT_FEEDBACK_DECISION_PATH",
    "DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH",
    "DEFAULT_OVERLAY_SOURCE_CONTEXT_INDEX_PATH",
    "FEEDBACK_DECISION_ACTION_DESCRIPTIONS",
    "FEEDBACK_DECISION_ACTIONS",
    "FEEDBACK_DECISION_DRAFT_SCHEMA_VERSION",
    "FEEDBACK_DECISION_PREVIEW_SCHEMA_VERSION",
    "FEEDBACK_SOURCE_CONTEXT_SCHEMA_VERSION",
    "OCR_RETRY_CANDIDATES_SCHEMA_VERSION",
    "OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION",
    "OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION",
    "OCR_RETRY_EXECUTION_SCHEMA_VERSION",
    "OCR_RETRY_FEEDBACK_CLOSURE_WAREHOUSE_MUTATION_FIELD",
    "OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION",
    "OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION",
    "OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION",
    "OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION",
    "OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION",
    "OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION",
    "OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION",
    "OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION",
    "OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION",
    "OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION",
    "OCR_RETRY_TERMINAL_CONTEXT_LIMIT",
    "OVERLAY_OCR_COMPARISON_READINESS_SCHEMA_VERSION",
    "OVERLAY_SOURCE_CONTEXT_INDEX_DRAFT_SCHEMA_VERSION",
    "OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION",
    "OVERLAY_SOURCE_CONTEXT_INDEX_VALIDATION_SCHEMA_VERSION",
    "build_ocr_retry_selection_decision_draft_payload",
]
