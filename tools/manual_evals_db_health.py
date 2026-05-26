from __future__ import annotations

from pathlib import Path

from tools.manual_eval_cli_feedback_dispatch import (
    handle_feedback_context_commands,
    handle_feedback_reclassify_commands,
)
from tools.manual_eval_cli_ocr_retry_dispatch import (
    handle_ocr_retry_post_feedback_commands,
    handle_ocr_retry_pre_feedback_commands,
)
from tools.manual_eval_cli_contracts import (
    ACTIONABLES_SCHEMA_VERSION as ACTIONABLES_SCHEMA_VERSION,
    COHORTS_SCHEMA_VERSION as COHORTS_SCHEMA_VERSION,
    COHORT_DESCRIPTIONS as COHORT_DESCRIPTIONS,
    COHORT_FILTER_CHOICES as COHORT_FILTER_CHOICES,
    COHORT_IDS as COHORT_IDS,
    DEFAULT_DB_PATH as DEFAULT_DB_PATH,
    DEFAULT_FEEDBACK_DECISION_PATH as DEFAULT_FEEDBACK_DECISION_PATH,
    DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH as DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH,
    DEFAULT_OVERLAY_SOURCE_CONTEXT_INDEX_PATH as DEFAULT_OVERLAY_SOURCE_CONTEXT_INDEX_PATH,
    FEEDBACK_DECISION_ACTION_DESCRIPTIONS as FEEDBACK_DECISION_ACTION_DESCRIPTIONS,
    FEEDBACK_DECISION_ACTIONS as FEEDBACK_DECISION_ACTIONS,
    FEEDBACK_DECISION_DRAFT_SCHEMA_VERSION as FEEDBACK_DECISION_DRAFT_SCHEMA_VERSION,
    FEEDBACK_DECISION_PREVIEW_SCHEMA_VERSION as FEEDBACK_DECISION_PREVIEW_SCHEMA_VERSION,
    FEEDBACK_SOURCE_CONTEXT_SCHEMA_VERSION as FEEDBACK_SOURCE_CONTEXT_SCHEMA_VERSION,
    OCR_RETRY_CANDIDATES_SCHEMA_VERSION as OCR_RETRY_CANDIDATES_SCHEMA_VERSION,
    OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION as OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION,
    OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION as OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION,
    OCR_RETRY_EXECUTION_SCHEMA_VERSION as OCR_RETRY_EXECUTION_SCHEMA_VERSION,
    OCR_RETRY_FEEDBACK_CLOSURE_WAREHOUSE_MUTATION_FIELD as OCR_RETRY_FEEDBACK_CLOSURE_WAREHOUSE_MUTATION_FIELD,
    OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION as OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION,
    OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION as OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION,
    OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION as OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION,
    OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION as OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION,
    OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION as OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION,
    OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION as OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION,
    OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION as OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION,
    OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION as OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION,
    OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION as OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION,
    OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION as OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION,
    OCR_RETRY_TERMINAL_CONTEXT_LIMIT as OCR_RETRY_TERMINAL_CONTEXT_LIMIT,
    OVERLAY_OCR_COMPARISON_READINESS_SCHEMA_VERSION as OVERLAY_OCR_COMPARISON_READINESS_SCHEMA_VERSION,
    OVERLAY_SOURCE_CONTEXT_INDEX_DRAFT_SCHEMA_VERSION as OVERLAY_SOURCE_CONTEXT_INDEX_DRAFT_SCHEMA_VERSION,
    OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION as OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION,
    OVERLAY_SOURCE_CONTEXT_INDEX_VALIDATION_SCHEMA_VERSION as OVERLAY_SOURCE_CONTEXT_INDEX_VALIDATION_SCHEMA_VERSION,
    build_ocr_retry_selection_decision_draft_payload as build_ocr_retry_selection_decision_draft_payload,
)
from tools.manual_eval_cli_output import finish_manual_eval_report as _finish_report
from tools.manual_eval_cli_parser import build_manual_evals_db_health_parser
from tools.manual_eval_feedback_decisions import (
    build_feedback_decision_draft_payload as build_feedback_decision_draft_payload,
    build_feedback_decision_preview_report as build_feedback_decision_preview_report,
    format_feedback_decision_draft_report as format_feedback_decision_draft_report,
    format_feedback_decision_preview_report as format_feedback_decision_preview_report,
    write_feedback_decision_draft as write_feedback_decision_draft,
)
from tools.manual_eval_feedback_reclassify import (
    DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT as DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT,
    DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH as DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH,
    FEEDBACK_RECLASSIFY_CONFIRM_TOKEN as FEEDBACK_RECLASSIFY_CONFIRM_TOKEN,
    FEEDBACK_RECLASSIFY_SCHEMA_VERSION as FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
    build_feedback_reclassify_report as build_feedback_reclassify_report,
    format_feedback_reclassify_report as format_feedback_reclassify_report,
    write_feedback_reclassify as write_feedback_reclassify,
)
from tools.manual_eval_health_report import (
    build_manual_evals_health_report,
    format_manual_evals_health_report,
)
from tools.manual_eval_no_context_feedback_reclassify import (
    DEFAULT_NO_CONTEXT_RECLASSIFY_BACKUP_ROOT as DEFAULT_NO_CONTEXT_RECLASSIFY_BACKUP_ROOT,
    NO_CONTEXT_RECLASSIFIED_RECOMMENDED_ACTION as NO_CONTEXT_RECLASSIFIED_RECOMMENDED_ACTION,
    NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN as NO_CONTEXT_RECLASSIFY_CONFIRM_TOKEN,
    NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION as NO_CONTEXT_RECLASSIFY_SCHEMA_VERSION,
    build_no_context_feedback_reclassify_report as build_no_context_feedback_reclassify_report,
    format_no_context_feedback_reclassify_report as format_no_context_feedback_reclassify_report,
    write_no_context_feedback_reclassify as write_no_context_feedback_reclassify,
)
from tools.manual_eval_ocr_retry_candidates import (
    build_ocr_retry_candidates_report as build_ocr_retry_candidates_report,
    format_ocr_retry_candidates_report as format_ocr_retry_candidates_report,
)
from tools.manual_eval_ocr_retry_source_verification import (
    build_ocr_retry_source_verification_report as build_ocr_retry_source_verification_report,
    format_ocr_retry_source_verification_report as format_ocr_retry_source_verification_report,
)
from tools.manual_eval_ocr_retry_input_packet import (
    build_ocr_retry_input_packet_report as build_ocr_retry_input_packet_report,
    format_ocr_retry_input_packet_report as format_ocr_retry_input_packet_report,
)
from tools.manual_eval_ocr_retry_rerun_manifest import (
    build_ocr_retry_rerun_manifest_report as build_ocr_retry_rerun_manifest_report,
    format_ocr_retry_rerun_manifest_report as format_ocr_retry_rerun_manifest_report,
)
from tools.manual_eval_ocr_retry_rerun_plan import (
    build_ocr_retry_rerun_plan_report as build_ocr_retry_rerun_plan_report,
    format_ocr_retry_rerun_plan_report as format_ocr_retry_rerun_plan_report,
)
from tools.manual_eval_ocr_retry_selection_review import (
    build_ocr_retry_selection_review_report as build_ocr_retry_selection_review_report,
    format_ocr_retry_selection_review_report as format_ocr_retry_selection_review_report,
)
from tools.manual_eval_ocr_retry_selection_decision_draft import (
    format_ocr_retry_selection_decision_draft_report as format_ocr_retry_selection_decision_draft_report,
    write_ocr_retry_selection_decision_draft as write_ocr_retry_selection_decision_draft,
)
from tools.manual_eval_ocr_retry_selection_apply_preview import (
    build_ocr_retry_selection_apply_preview_report as build_ocr_retry_selection_apply_preview_report,
    format_ocr_retry_selection_apply_preview_report as format_ocr_retry_selection_apply_preview_report,
)
from tools.manual_eval_ocr_retry_execution_readiness import (
    build_ocr_retry_execution_readiness_report as build_ocr_retry_execution_readiness_report,
    format_ocr_retry_execution_readiness_report as format_ocr_retry_execution_readiness_report,
)
from tools.manual_eval_ocr_retry_execution_report import (
    format_ocr_retry_execution_bundle_report as format_ocr_retry_execution_bundle_report,
    format_ocr_retry_execution_report as format_ocr_retry_execution_report,
)
from tools.manual_eval_ocr_retry_execution_bundle_report import (
    build_ocr_retry_execution_bundle_report as build_ocr_retry_execution_bundle_report,
)
from tools.manual_eval_ocr_retry_execution_requests import (
    OcrRetryExecutionProviderError as OcrRetryExecutionProviderError,
)
from tools.manual_eval_ocr_retry_execution_writer import (
    DEFAULT_OCR_RETRY_EXECUTION_DIR as DEFAULT_OCR_RETRY_EXECUTION_DIR,
    DEFAULT_OCR_RETRY_MODEL as DEFAULT_OCR_RETRY_MODEL,
    DEFAULT_OCR_RETRY_PROMPT as DEFAULT_OCR_RETRY_PROMPT,
    OCR_RETRY_EXECUTION_CONFIRM_TOKEN as OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
    write_ocr_retry_execution_bundle as write_ocr_retry_execution_bundle,
)
from tools.manual_eval_ocr_retry_feedback_closure_preview import (
    OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION as OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
    build_ocr_retry_feedback_closure_preview_report as build_ocr_retry_feedback_closure_preview_report,
)
from tools.manual_eval_ocr_retry_feedback_closure_apply import (
    DEFAULT_FEEDBACK_CLOSURE_APPLY_BACKUP_ROOT as DEFAULT_FEEDBACK_CLOSURE_APPLY_BACKUP_ROOT,
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN as OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN,
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION as OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION,
    write_ocr_retry_feedback_closure_apply as write_ocr_retry_feedback_closure_apply,
)
from tools.manual_eval_ocr_retry_feedback_closure_apply_report import (
    OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION as OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION,
    build_ocr_retry_feedback_closure_apply_report as build_ocr_retry_feedback_closure_apply_report,
)
from tools.manual_eval_ocr_retry_feedback_closure_restore import (
    DEFAULT_FEEDBACK_CLOSURE_RESTORE_BACKUP_ROOT as DEFAULT_FEEDBACK_CLOSURE_RESTORE_BACKUP_ROOT,
    OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN as OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN,
    OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION as OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION,
    build_ocr_retry_feedback_closure_restore_preview_report as build_ocr_retry_feedback_closure_restore_preview_report,
    write_ocr_retry_feedback_closure_restore as write_ocr_retry_feedback_closure_restore,
)
from tools.manual_eval_ocr_retry_feedback_closure_formatters import (
    format_ocr_retry_feedback_closure_apply_report as format_ocr_retry_feedback_closure_apply_report,
    format_ocr_retry_feedback_closure_apply_verification_report as format_ocr_retry_feedback_closure_apply_verification_report,
    format_ocr_retry_feedback_closure_preview_report as format_ocr_retry_feedback_closure_preview_report,
    format_ocr_retry_feedback_closure_restore_report as format_ocr_retry_feedback_closure_restore_report,
)
from tools.manual_eval_ocr_retry_selection_template import (
    build_ocr_retry_selection_template_report as build_ocr_retry_selection_template_report,
    format_ocr_retry_selection_template_report as format_ocr_retry_selection_template_report,
)
from tools.manual_eval_ocr_retry_selection_validation import (
    build_ocr_retry_selection_validation_report as build_ocr_retry_selection_validation_report,
    format_ocr_retry_selection_validation_report as format_ocr_retry_selection_validation_report,
)
from tools.manual_eval_ocr_retry_source_provenance import (
    build_ocr_retry_source_provenance_report as build_ocr_retry_source_provenance_report,
    format_ocr_retry_source_provenance_report as format_ocr_retry_source_provenance_report,
)
from tools.manual_eval_open_feedback import (
    build_open_feedback_actionables_report as build_open_feedback_actionables_report,
    build_open_feedback_cohorts_report as build_open_feedback_cohorts_report,
    format_open_feedback_actionables_report as format_open_feedback_actionables_report,
    format_open_feedback_cohorts_report as format_open_feedback_cohorts_report,
)
from tools.manual_eval_overlay_source_index import (
    build_overlay_source_context_index_draft_payload as build_overlay_source_context_index_draft_payload,
    build_overlay_source_context_index_validation_report as build_overlay_source_context_index_validation_report,
    format_overlay_source_context_index_draft_report as format_overlay_source_context_index_draft_report,
    format_overlay_source_context_index_validation_report as format_overlay_source_context_index_validation_report,
    write_overlay_source_context_index_draft as write_overlay_source_context_index_draft,
)
from tools.manual_eval_overlay_readiness import (
    build_overlay_ocr_comparison_readiness_report as build_overlay_ocr_comparison_readiness_report,
    format_overlay_ocr_comparison_readiness_report as format_overlay_ocr_comparison_readiness_report,
)
from tools.manual_eval_source_context import (
    build_feedback_source_context_report as build_feedback_source_context_report,
    format_feedback_source_context_report as format_feedback_source_context_report,
)

# Guarded feedback-closure commands keep manual_eval_warehouse scope explicit.
_CLI_GATE_CONTRACT_MARKERS: tuple[str, ...] = (
    "--ocr-retry-execute",
    "--ocr-retry-execution-report",
    "--ocr-retry-feedback-closure-preview",
    "--ocr-retry-feedback-closure-apply",
    "--ocr-retry-feedback-closure-apply-report",
    "--ocr-retry-feedback-closure-restore-preview",
    "--ocr-retry-feedback-closure-restore",
    "OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION",
    "OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION",
    "OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION",
    "OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION",
    "OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION",
    "--confirm",
    "OCR_RETRY_EXECUTION_CONFIRM_TOKEN",
    "OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN",
    "OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN",
    "CONFIRM=ocr-retry-execute",
    "CONFIRM=ocr-retry-feedback-closure-apply",
    "CONFIRM=ocr-retry-feedback-closure-restore",
    "manual_eval_warehouse",
    "build_ocr_retry_execution_readiness_report",
)


def _build_parser():
    return build_manual_evals_db_health_parser()


def main() -> int:
    args = _build_parser().parse_args()
    db_path = Path(args.db).expanduser()

    def finish(report, formatter, **status_kwargs):
        return _finish_report(
            report,
            formatter,
            json_output=bool(args.json),
            **status_kwargs,
        )

    ocr_retry_status = handle_ocr_retry_pre_feedback_commands(
        args=args,
        db_path=db_path,
        finish=finish,
    )
    if ocr_retry_status is not None:
        return ocr_retry_status

    feedback_reclassify_status = handle_feedback_reclassify_commands(
        args=args,
        db_path=db_path,
        finish=finish,
    )
    if feedback_reclassify_status is not None:
        return feedback_reclassify_status

    ocr_retry_status = handle_ocr_retry_post_feedback_commands(
        args=args,
        db_path=db_path,
        finish=finish,
    )
    if ocr_retry_status is not None:
        return ocr_retry_status

    feedback_context_status = handle_feedback_context_commands(
        args=args,
        db_path=db_path,
        finish=finish,
    )
    if feedback_context_status is not None:
        return feedback_context_status

    report = build_manual_evals_health_report(db_path=db_path)
    return finish(report, format_manual_evals_health_report)


if __name__ == "__main__":
    raise SystemExit(main())
