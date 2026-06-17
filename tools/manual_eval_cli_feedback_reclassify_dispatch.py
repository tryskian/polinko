from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    STATUS_APPLIED_OK,
    STATUS_OK,
    filtered_command_args,
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


def handle_feedback_reclassify_command_group(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    paths = local_artifact_paths(args)

    if args.no_context_feedback_reclassify_preview:
        command_args = filtered_command_args(
            args,
            outcome="fail",
            cohort="ocr_retry_evidence",
        )
        report = build_no_context_feedback_reclassify_report(
            db_path=db_path,
            outcome=command_args.outcome,
            cohort=command_args.cohort,
            limit=command_args.limit,
        )
        return finish_report_with_error_default(
            finish=finish,
            report=report,
            formatter=format_no_context_feedback_reclassify_report,
            status_by_state=STATUS_OK,
        )

    if args.no_context_feedback_reclassify_apply:
        command_args = filtered_command_args(
            args,
            outcome="fail",
            cohort="ocr_retry_evidence",
        )
        report = write_no_context_feedback_reclassify(
            db_path=db_path,
            confirm_token=str(args.confirm or ""),
            backup_root=paths.backup_root,
            outcome=command_args.outcome,
            cohort=command_args.cohort,
            limit=command_args.limit,
        )
        return finish_report_with_error_default(
            finish=finish,
            report=report,
            formatter=format_no_context_feedback_reclassify_report,
            status_by_state=STATUS_APPLIED_OK,
        )

    if args.feedback_reclassify_preview:
        report = build_feedback_reclassify_report(
            db_path=db_path,
            plan_path=paths.plan_path,
        )
        return finish_report_with_error_default(
            finish=finish,
            report=report,
            formatter=format_feedback_reclassify_report,
            status_by_state=STATUS_OK,
        )

    if args.feedback_reclassify_apply:
        report = write_feedback_reclassify(
            db_path=db_path,
            plan_path=paths.plan_path,
            confirm_token=str(args.confirm or ""),
            backup_root=paths.backup_root,
        )
        return finish_report_with_error_default(
            finish=finish,
            report=report,
            formatter=format_feedback_reclassify_report,
            status_by_state=STATUS_APPLIED_OK,
        )

    return None
