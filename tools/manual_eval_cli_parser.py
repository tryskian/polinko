from __future__ import annotations

import argparse
import os

from tools.manual_eval_cli_contracts import (
    COHORT_FILTER_CHOICES,
    DEFAULT_DB_PATH,
)
from tools.manual_eval_ocr_retry_execution_writer import (
    DEFAULT_OCR_RETRY_MODEL,
    DEFAULT_OCR_RETRY_PROMPT,
)


def _add_common_report_args(parser: argparse.ArgumentParser) -> None:
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


def _add_feedback_context_args(parser: argparse.ArgumentParser) -> None:
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


def _add_ocr_retry_args(parser: argparse.ArgumentParser) -> None:
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


def _add_feedback_reclassify_args(parser: argparse.ArgumentParser) -> None:
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


def _add_local_artifact_args(parser: argparse.ArgumentParser) -> None:
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


def _add_ocr_execution_args(parser: argparse.ArgumentParser) -> None:
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


def _add_output_filter_args(parser: argparse.ArgumentParser) -> None:
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


def build_manual_evals_db_health_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print read-only manual eval warehouse health signals.",
    )
    _add_common_report_args(parser)
    _add_feedback_context_args(parser)
    _add_ocr_retry_args(parser)
    _add_feedback_reclassify_args(parser)
    _add_local_artifact_args(parser)
    _add_ocr_execution_args(parser)
    _add_output_filter_args(parser)
    return parser
