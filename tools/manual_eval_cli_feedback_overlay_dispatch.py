from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    STATUS_ERROR,
    STATUS_READY_OK,
    STATUS_WRITTEN_OK,
    filtered_report_kwargs,
    finish_report_with_error_default,
    local_artifact_paths,
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
    paths = local_artifact_paths(args)

    if args.overlay_ocr_comparison_readiness:
        report = build_overlay_ocr_comparison_readiness_report(
            db_path=db_path,
            overlay_source_index_path=paths.overlay_source_index_path,
            **filtered_report_kwargs(
                args,
                outcome="fail",
                cohort="ocr_overlay_hypothesis",
            ),
        )
        return finish(
            report,
            format_overlay_ocr_comparison_readiness_report,
            status_by_state=STATUS_ERROR,
        )

    if args.overlay_source_index_draft:
        report = write_overlay_source_context_index_draft(
            db_path=db_path,
            output_path=paths.output_path,
            force=bool(args.force),
            **filtered_report_kwargs(
                args,
                outcome="fail",
                cohort="ocr_overlay_hypothesis",
            ),
        )
        return finish_report_with_error_default(
            finish=finish,
            report=report,
            formatter=format_overlay_source_context_index_draft_report,
            status_by_state=STATUS_WRITTEN_OK,
        )

    if args.overlay_source_index_validate:
        report = build_overlay_source_context_index_validation_report(
            db_path=db_path,
            overlay_source_index_path=paths.overlay_source_index_path,
            **filtered_report_kwargs(
                args,
                outcome="fail",
                cohort="ocr_overlay_hypothesis",
            ),
        )
        return finish_report_with_error_default(
            finish=finish,
            report=report,
            formatter=format_overlay_source_context_index_validation_report,
            status_by_state=STATUS_READY_OK,
        )

    return None
