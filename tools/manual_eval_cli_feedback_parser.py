from __future__ import annotations

import argparse

from tools.manual_eval_cli_shared_parser import BooleanFlagArg, add_boolean_flag_args


FEEDBACK_CONTEXT_FLAGS = (
    BooleanFlagArg(
        "--open-feedback-actionables",
        "Print open feedback rows that need manual-eval triage.",
    ),
    BooleanFlagArg(
        "--open-feedback-cohorts",
        "Print read-only cohorts for open manual-eval feedback actionables.",
    ),
    BooleanFlagArg(
        "--feedback-source-context",
        "Print read-only source-history context for selected open feedback rows.",
    ),
    BooleanFlagArg(
        "--feedback-decision-preview",
        "Preview a local human-reviewed feedback decision without mutation.",
    ),
    BooleanFlagArg(
        "--feedback-decision-draft",
        "Write a local manual feedback decision draft without mutation.",
    ),
    BooleanFlagArg(
        "--overlay-ocr-comparison-readiness",
        "Print read-only overlay/OCR comparison readiness packets.",
    ),
    BooleanFlagArg(
        "--overlay-source-index-draft",
        "Write a local fillable overlay/source image context index draft.",
    ),
    BooleanFlagArg(
        "--overlay-source-index-validate",
        "Validate a local overlay/source image context index against readiness.",
    ),
)


FEEDBACK_RECLASSIFY_FLAGS = (
    BooleanFlagArg(
        "--no-context-feedback-reclassify-preview",
        "Preview reclassifying no-context OCR feedback into overlay-hypothesis evidence.",
    ),
    BooleanFlagArg(
        "--no-context-feedback-reclassify-apply",
        "Apply guarded overlay-hypothesis feedback reclassification after backup.",
    ),
    BooleanFlagArg(
        "--feedback-reclassify-preview",
        "Preview feedback reclassification from a local JSON decision plan.",
    ),
    BooleanFlagArg(
        "--feedback-reclassify-apply",
        "Apply guarded feedback reclassification from a local JSON decision plan.",
    ),
)


def add_feedback_context_args(parser: argparse.ArgumentParser) -> None:
    add_boolean_flag_args(parser, FEEDBACK_CONTEXT_FLAGS)
    parser.add_argument(
        "--overlay-source-index",
        default="",
        help="Path to a local overlay/source image context index JSON file.",
    )


def add_feedback_reclassify_args(parser: argparse.ArgumentParser) -> None:
    add_boolean_flag_args(parser, FEEDBACK_RECLASSIFY_FLAGS)
