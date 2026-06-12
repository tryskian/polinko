from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    default_filters,
    optional_path,
    positive_limit,
)
from tools.manual_eval_overlay_readiness import (
    build_overlay_ocr_comparison_readiness_report,
    format_overlay_ocr_comparison_readiness_report,
)
from tools.manual_eval_overlay_source_index import (
    build_overlay_source_context_index_validation_report,
    format_overlay_source_context_index_draft_report,
    format_overlay_source_context_index_validation_report,
    write_overlay_source_context_index_draft,
)


def handle_feedback_overlay_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    if args.overlay_ocr_comparison_readiness:
        filters = default_filters(args, outcome="fail", cohort="ocr_overlay_hypothesis")
        report = build_overlay_ocr_comparison_readiness_report(
            db_path=db_path,
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
            overlay_source_index_path=optional_path(args.overlay_source_index),
        )
        return finish(
            report,
            format_overlay_ocr_comparison_readiness_report,
            status_by_state={"error": 2},
        )

    if args.overlay_source_index_draft:
        filters = default_filters(args, outcome="fail", cohort="ocr_overlay_hypothesis")
        report = write_overlay_source_context_index_draft(
            db_path=db_path,
            output_path=optional_path(args.output_path),
            force=bool(args.force),
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_overlay_source_context_index_draft_report,
            status_by_state={"written": 0},
            default_status=2,
        )

    if args.overlay_source_index_validate:
        filters = default_filters(args, outcome="fail", cohort="ocr_overlay_hypothesis")
        report = build_overlay_source_context_index_validation_report(
            db_path=db_path,
            overlay_source_index_path=optional_path(args.overlay_source_index),
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_overlay_source_context_index_validation_report,
            status_by_state={"ready": 0},
            default_status=2,
        )

    return None
