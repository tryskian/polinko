from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, NamedTuple

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    LocalArtifactPaths,
    ReportFormatter,
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

ReportBuilder = Callable[..., dict[str, Any]]
OVERLAY_FEEDBACK_OUTCOME = "fail"
OVERLAY_FEEDBACK_COHORT = "ocr_overlay_hypothesis"


class FeedbackOverlayCommand(NamedTuple):
    flag: str
    builder: ReportBuilder
    formatter: ReportFormatter
    status_by_state: Mapping[str, int]
    include_output_path: bool = False
    include_force: bool = False
    include_overlay_source_index_path: bool = False
    use_error_default: bool = True


FEEDBACK_OVERLAY_COMMANDS = (
    FeedbackOverlayCommand(
        flag="overlay_ocr_comparison_readiness",
        builder=build_overlay_ocr_comparison_readiness_report,
        formatter=format_overlay_ocr_comparison_readiness_report,
        status_by_state=STATUS_ERROR,
        include_overlay_source_index_path=True,
        use_error_default=False,
    ),
    FeedbackOverlayCommand(
        flag="overlay_source_index_draft",
        builder=write_overlay_source_context_index_draft,
        formatter=format_overlay_source_context_index_draft_report,
        status_by_state=STATUS_WRITTEN_OK,
        include_output_path=True,
        include_force=True,
    ),
    FeedbackOverlayCommand(
        flag="overlay_source_index_validate",
        builder=build_overlay_source_context_index_validation_report,
        formatter=format_overlay_source_context_index_validation_report,
        status_by_state=STATUS_READY_OK,
        include_overlay_source_index_path=True,
    ),
)


def _feedback_overlay_report_kwargs(
    *,
    command: FeedbackOverlayCommand,
    args: Any,
    paths: LocalArtifactPaths,
) -> dict[str, Any]:
    kwargs = filtered_report_kwargs(
        args,
        outcome=OVERLAY_FEEDBACK_OUTCOME,
        cohort=OVERLAY_FEEDBACK_COHORT,
    )
    if command.include_output_path:
        kwargs["output_path"] = paths.output_path
    if command.include_force:
        kwargs["force"] = bool(args.force)
    if command.include_overlay_source_index_path:
        kwargs["overlay_source_index_path"] = paths.overlay_source_index_path
    return kwargs


def handle_feedback_overlay_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    paths = local_artifact_paths(args)

    for command in FEEDBACK_OVERLAY_COMMANDS:
        if getattr(args, command.flag):
            report = command.builder(
                db_path=db_path,
                **_feedback_overlay_report_kwargs(
                    command=command,
                    args=args,
                    paths=paths,
                ),
            )
            if command.use_error_default:
                return finish_report_with_error_default(
                    finish=finish,
                    report=report,
                    formatter=command.formatter,
                    status_by_state=command.status_by_state,
                )
            return finish(
                report,
                command.formatter,
                status_by_state=command.status_by_state,
            )

    return None
