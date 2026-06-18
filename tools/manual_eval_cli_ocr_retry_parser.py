from __future__ import annotations

import argparse
import os

from tools.manual_eval_ocr_retry_execution_writer import (
    DEFAULT_OCR_RETRY_MODEL,
    DEFAULT_OCR_RETRY_PROMPT,
)
from tools.manual_eval_cli_shared_parser import BooleanFlagArg, add_boolean_flag_args


OCR_RETRY_FLAGS = (
    BooleanFlagArg(
        "--ocr-retry-candidates",
        "Print read-only OCR retry candidate packets for selected feedback.",
    ),
    BooleanFlagArg(
        "--ocr-retry-source-verification",
        "Print read-only OCR retry source-verification packets.",
    ),
    BooleanFlagArg(
        "--ocr-retry-source-provenance",
        "Print read-only OCR retry source-history provenance packets.",
    ),
    BooleanFlagArg(
        "--ocr-retry-input-packet",
        "Print read-only OCR retry rerun input packets.",
    ),
    BooleanFlagArg(
        "--ocr-retry-rerun-manifest",
        "Print read-only OCR retry rerun source-artifact manifests.",
    ),
    BooleanFlagArg(
        "--ocr-retry-rerun-plan",
        "Print read-only OCR retry rerun plan and payload previews.",
    ),
    BooleanFlagArg(
        "--ocr-retry-selection-review",
        "Print read-only OCR retry source-artifact selection review packets.",
    ),
    BooleanFlagArg(
        "--ocr-retry-selection-template",
        "Print read-only OCR retry human-selection decision templates.",
    ),
    BooleanFlagArg(
        "--ocr-retry-selection-draft",
        "Write a local fillable OCR retry human-selection draft JSON file.",
    ),
    BooleanFlagArg(
        "--ocr-retry-selection-validate",
        "Validate a local OCR retry human-selection JSON against the shortlist.",
    ),
    BooleanFlagArg(
        "--ocr-retry-selection-apply-preview",
        "Print a read-only would-apply preview for valid OCR retry selections.",
    ),
    BooleanFlagArg(
        "--ocr-retry-execution-readiness",
        "Print read-only OCR retry execution readiness for selected decisions.",
    ),
    BooleanFlagArg(
        "--ocr-retry-execute",
        "Run guarded OCR retry execution into a local ignored bundle.",
    ),
    BooleanFlagArg(
        "--ocr-retry-execution-report",
        "Inspect a local OCR retry execution run bundle without mutation.",
    ),
    BooleanFlagArg(
        "--ocr-retry-feedback-closure-preview",
        "Preview feedback closure from a local OCR retry execution bundle.",
    ),
    BooleanFlagArg(
        "--ocr-retry-feedback-closure-apply",
        "Apply guarded OCR retry feedback closure after backup.",
    ),
    BooleanFlagArg(
        "--ocr-retry-feedback-closure-apply-report",
        "Inspect an OCR retry feedback-closure apply summary without mutation.",
    ),
    BooleanFlagArg(
        "--ocr-retry-feedback-closure-restore-preview",
        "Preview restoring manual_evals.db from a feedback-closure apply backup.",
    ),
    BooleanFlagArg(
        "--ocr-retry-feedback-closure-restore",
        "Restore manual_evals.db from a verified feedback-closure apply backup.",
    ),
)


def add_ocr_retry_args(parser: argparse.ArgumentParser) -> None:
    add_boolean_flag_args(parser, OCR_RETRY_FLAGS)


def add_ocr_execution_args(parser: argparse.ArgumentParser) -> None:
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
