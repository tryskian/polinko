from __future__ import annotations

import argparse


def add_feedback_context_args(parser: argparse.ArgumentParser) -> None:
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


def add_feedback_reclassify_args(parser: argparse.ArgumentParser) -> None:
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
