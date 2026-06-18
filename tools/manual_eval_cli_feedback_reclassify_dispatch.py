from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, NamedTuple

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    LocalArtifactPaths,
    ReportFormatter,
    STATUS_APPLIED_OK,
    STATUS_OK,
    filtered_report_kwargs,
    finish_report_with_error_default,
    local_artifact_paths,
)
from tools.manual_eval_feedback_reclassify import (
    build_feedback_reclassify_report,
    format_feedback_reclassify_report,
    write_feedback_reclassify,
)
from tools.manual_eval_no_context_feedback_reclassify import (
    build_no_context_feedback_reclassify_report,
    format_no_context_feedback_reclassify_report,
    write_no_context_feedback_reclassify,
)

ReportBuilder = Callable[..., dict[str, Any]]
NO_CONTEXT_RECLASSIFY_OUTCOME = "fail"
NO_CONTEXT_RECLASSIFY_COHORT = "ocr_retry_evidence"


class FeedbackReclassifyCommand(NamedTuple):
    flag: str
    builder: ReportBuilder
    formatter: ReportFormatter
    status_by_state: Mapping[str, int]
    use_no_context_filters: bool = False
    include_plan_path: bool = False
    include_confirm_token: bool = False
    include_backup_root: bool = False


FEEDBACK_RECLASSIFY_COMMANDS = (
    FeedbackReclassifyCommand(
        flag="no_context_feedback_reclassify_preview",
        builder=build_no_context_feedback_reclassify_report,
        formatter=format_no_context_feedback_reclassify_report,
        status_by_state=STATUS_OK,
        use_no_context_filters=True,
    ),
    FeedbackReclassifyCommand(
        flag="no_context_feedback_reclassify_apply",
        builder=write_no_context_feedback_reclassify,
        formatter=format_no_context_feedback_reclassify_report,
        status_by_state=STATUS_APPLIED_OK,
        use_no_context_filters=True,
        include_confirm_token=True,
        include_backup_root=True,
    ),
    FeedbackReclassifyCommand(
        flag="feedback_reclassify_preview",
        builder=build_feedback_reclassify_report,
        formatter=format_feedback_reclassify_report,
        status_by_state=STATUS_OK,
        include_plan_path=True,
    ),
    FeedbackReclassifyCommand(
        flag="feedback_reclassify_apply",
        builder=write_feedback_reclassify,
        formatter=format_feedback_reclassify_report,
        status_by_state=STATUS_APPLIED_OK,
        include_plan_path=True,
        include_confirm_token=True,
        include_backup_root=True,
    ),
)


def _feedback_reclassify_report_kwargs(
    *,
    command: FeedbackReclassifyCommand,
    args: Any,
    paths: LocalArtifactPaths,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if command.use_no_context_filters:
        kwargs.update(
            filtered_report_kwargs(
                args,
                outcome=NO_CONTEXT_RECLASSIFY_OUTCOME,
                cohort=NO_CONTEXT_RECLASSIFY_COHORT,
            )
        )
    if command.include_plan_path:
        kwargs["plan_path"] = paths.plan_path
    if command.include_confirm_token:
        kwargs["confirm_token"] = str(args.confirm or "")
    if command.include_backup_root:
        kwargs["backup_root"] = paths.backup_root
    return kwargs


def handle_feedback_reclassify_command_group(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    paths = local_artifact_paths(args)

    for command in FEEDBACK_RECLASSIFY_COMMANDS:
        if getattr(args, command.flag):
            report = command.builder(
                db_path=db_path,
                **_feedback_reclassify_report_kwargs(
                    command=command,
                    args=args,
                    paths=paths,
                ),
            )
            return finish_report_with_error_default(
                finish=finish,
                report=report,
                formatter=command.formatter,
                status_by_state=command.status_by_state,
            )

    return None
