from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

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
    build_feedback_decision_draft_payload as build_feedback_decision_draft_payload,
    build_feedback_decision_preview_report,
    format_feedback_decision_draft_report,
    format_feedback_decision_preview_report,
    write_feedback_decision_draft,
)
from tools.manual_eval_feedback_reclassify import (
    DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT as DEFAULT_FEEDBACK_RECLASSIFY_BACKUP_ROOT,
    DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH as DEFAULT_FEEDBACK_RECLASSIFY_PLAN_PATH,
    FEEDBACK_RECLASSIFY_CONFIRM_TOKEN as FEEDBACK_RECLASSIFY_CONFIRM_TOKEN,
    FEEDBACK_RECLASSIFY_SCHEMA_VERSION as FEEDBACK_RECLASSIFY_SCHEMA_VERSION,
    build_feedback_reclassify_report,
    format_feedback_reclassify_report,
    write_feedback_reclassify,
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
    build_no_context_feedback_reclassify_report,
    format_no_context_feedback_reclassify_report,
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
from tools.manual_eval_ocr_retry_feedback_closure_formatters import (
    format_ocr_retry_feedback_closure_apply_report,
    format_ocr_retry_feedback_closure_apply_verification_report,
    format_ocr_retry_feedback_closure_preview_report,
    format_ocr_retry_feedback_closure_restore_report,
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
from tools.manual_eval_open_feedback import (
    build_open_feedback_actionables_report,
    build_open_feedback_cohorts_report,
    format_open_feedback_actionables_report,
    format_open_feedback_cohorts_report,
)
from tools.manual_eval_overlay_source_index import (
    build_overlay_source_context_index_draft_payload as build_overlay_source_context_index_draft_payload,
    build_overlay_source_context_index_validation_report,
    format_overlay_source_context_index_draft_report,
    format_overlay_source_context_index_validation_report,
    write_overlay_source_context_index_draft,
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
OCR_RETRY_TERMINAL_CONTEXT_LIMIT = 3


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
