from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, NamedTuple

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    LocalArtifactPaths,
    ReportFormatter,
    STATUS_APPLIED_OK,
    STATUS_BLOCKED_ERROR,
    STATUS_OK,
    STATUS_RESTORED_OK,
    first_enabled_command,
    finish_report_with_error_default,
    local_artifact_paths,
)
from tools.manual_eval_ocr_retry_feedback_closure_apply import (
    write_ocr_retry_feedback_closure_apply,
)
from tools.manual_eval_ocr_retry_feedback_closure_apply_report import (
    build_ocr_retry_feedback_closure_apply_report,
)
from tools.manual_eval_ocr_retry_feedback_closure_formatters import (
    format_ocr_retry_feedback_closure_apply_report,
    format_ocr_retry_feedback_closure_apply_verification_report,
    format_ocr_retry_feedback_closure_preview_report,
    format_ocr_retry_feedback_closure_restore_report,
)
from tools.manual_eval_ocr_retry_feedback_closure_preview import (
    build_ocr_retry_feedback_closure_preview_report,
)
from tools.manual_eval_ocr_retry_feedback_closure_restore import (
    build_ocr_retry_feedback_closure_restore_preview_report,
    write_ocr_retry_feedback_closure_restore,
)


ReportBuilder = Callable[..., dict[str, Any]]


class OcrRetryFeedbackClosureCommand(NamedTuple):
    flag: str
    builder: ReportBuilder
    formatter: ReportFormatter
    status_by_state: Mapping[str, int]
    guarded_finish: bool = True
    include_db_path: bool = False
    include_run_dir: bool = False
    include_backup_dir: bool = False
    include_confirm_token: bool = False
    include_backup_root: bool = False
    include_restore_root: bool = False


OCR_RETRY_FEEDBACK_CLOSURE_COMMANDS = (
    OcrRetryFeedbackClosureCommand(
        flag="ocr_retry_feedback_closure_preview",
        builder=build_ocr_retry_feedback_closure_preview_report,
        formatter=format_ocr_retry_feedback_closure_preview_report,
        status_by_state=STATUS_BLOCKED_ERROR,
        guarded_finish=False,
        include_run_dir=True,
    ),
    OcrRetryFeedbackClosureCommand(
        flag="ocr_retry_feedback_closure_apply",
        builder=write_ocr_retry_feedback_closure_apply,
        formatter=format_ocr_retry_feedback_closure_apply_report,
        status_by_state=STATUS_APPLIED_OK,
        include_db_path=True,
        include_run_dir=True,
        include_confirm_token=True,
        include_backup_root=True,
    ),
    OcrRetryFeedbackClosureCommand(
        flag="ocr_retry_feedback_closure_apply_report",
        builder=build_ocr_retry_feedback_closure_apply_report,
        formatter=format_ocr_retry_feedback_closure_apply_verification_report,
        status_by_state=STATUS_OK,
        include_db_path=True,
        include_run_dir=True,
    ),
    OcrRetryFeedbackClosureCommand(
        flag="ocr_retry_feedback_closure_restore_preview",
        builder=build_ocr_retry_feedback_closure_restore_preview_report,
        formatter=format_ocr_retry_feedback_closure_restore_report,
        status_by_state=STATUS_OK,
        include_db_path=True,
        include_backup_dir=True,
    ),
    OcrRetryFeedbackClosureCommand(
        flag="ocr_retry_feedback_closure_restore",
        builder=write_ocr_retry_feedback_closure_restore,
        formatter=format_ocr_retry_feedback_closure_restore_report,
        status_by_state=STATUS_RESTORED_OK,
        include_db_path=True,
        include_backup_dir=True,
        include_confirm_token=True,
        include_restore_root=True,
    ),
)


def _feedback_closure_report_kwargs(
    *,
    command: OcrRetryFeedbackClosureCommand,
    db_path: Path,
    paths: LocalArtifactPaths,
    confirm_token: str,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if command.include_db_path:
        kwargs["db_path"] = db_path
    if command.include_run_dir:
        kwargs["run_dir"] = paths.run_dir
    if command.include_backup_dir:
        kwargs["backup_dir"] = paths.backup_dir
    if command.include_confirm_token:
        kwargs["confirm_token"] = confirm_token
    if command.include_backup_root:
        kwargs["backup_root"] = paths.backup_root
    if command.include_restore_root:
        kwargs["restore_root"] = paths.restore_root
    return kwargs


def handle_ocr_retry_feedback_closure_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    paths = local_artifact_paths(args)

    command = first_enabled_command(
        args=args,
        commands=OCR_RETRY_FEEDBACK_CLOSURE_COMMANDS,
    )
    if command is None:
        return None

    report = command.builder(
        **_feedback_closure_report_kwargs(
            command=command,
            db_path=db_path,
            paths=paths,
            confirm_token=str(args.confirm or ""),
        )
    )
    if command.guarded_finish:
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
