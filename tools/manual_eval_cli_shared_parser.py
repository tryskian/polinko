from __future__ import annotations

import argparse
from typing import NamedTuple

from tools.manual_eval_cli_contracts import COHORT_FILTER_CHOICES, DEFAULT_DB_PATH


class BooleanFlagArg(NamedTuple):
    flag: str
    help: str


def add_boolean_flag_args(
    parser: argparse.ArgumentParser, flags: tuple[BooleanFlagArg, ...]
) -> None:
    for flag in flags:
        parser.add_argument(
            flag.flag,
            action="store_true",
            help=flag.help,
        )


def add_common_report_args(parser: argparse.ArgumentParser) -> None:
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


def add_local_artifact_args(parser: argparse.ArgumentParser) -> None:
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


def add_output_filter_args(parser: argparse.ArgumentParser) -> None:
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
