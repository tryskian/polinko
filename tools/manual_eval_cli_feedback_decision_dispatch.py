from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, NamedTuple

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    LocalArtifactPaths,
    ReportFormatter,
    STATUS_OK,
    STATUS_WRITTEN_OK,
    filtered_report_kwargs,
    finish_report_with_error_default,
    local_artifact_paths,
)
from tools.manual_eval_feedback_decisions import (
    build_feedback_decision_preview_report,
    format_feedback_decision_draft_report,
    format_feedback_decision_preview_report,
    write_feedback_decision_draft,
)

ReportBuilder = Callable[..., dict[str, Any]]
FEEDBACK_DECISION_OUTCOME = "fail"
FEEDBACK_DECISION_COHORT = "grounding_source_verification"


class FeedbackDecisionCommand(NamedTuple):
    flag: str
    builder: ReportBuilder
    formatter: ReportFormatter
    status_by_state: Mapping[str, int]
    include_output_path: bool = False
    include_force: bool = False
    include_decision_path: bool = False


FEEDBACK_DECISION_COMMANDS = (
    FeedbackDecisionCommand(
        flag="feedback_decision_draft",
        builder=write_feedback_decision_draft,
        formatter=format_feedback_decision_draft_report,
        status_by_state=STATUS_WRITTEN_OK,
        include_output_path=True,
        include_force=True,
    ),
    FeedbackDecisionCommand(
        flag="feedback_decision_preview",
        builder=build_feedback_decision_preview_report,
        formatter=format_feedback_decision_preview_report,
        status_by_state=STATUS_OK,
        include_decision_path=True,
    ),
)


def _feedback_decision_report_kwargs(
    *,
    command: FeedbackDecisionCommand,
    args: Any,
    paths: LocalArtifactPaths,
) -> dict[str, Any]:
    kwargs = filtered_report_kwargs(
        args,
        outcome=FEEDBACK_DECISION_OUTCOME,
        cohort=FEEDBACK_DECISION_COHORT,
    )
    if command.include_output_path:
        kwargs["output_path"] = paths.output_path
    if command.include_force:
        kwargs["force"] = bool(args.force)
    if command.include_decision_path:
        kwargs["decision_path"] = paths.decision_path
    return kwargs


def handle_feedback_decision_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    paths = local_artifact_paths(args)

    for command in FEEDBACK_DECISION_COMMANDS:
        if getattr(args, command.flag):
            report = command.builder(
                db_path=db_path,
                **_feedback_decision_report_kwargs(
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
