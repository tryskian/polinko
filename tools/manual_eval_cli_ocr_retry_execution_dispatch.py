from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    DEFAULT_ERROR_STATUS,
    FinishReport,
    STATUS_ERROR,
    STATUS_OCR_EXECUTION,
    local_artifact_paths,
    ocr_retry_command_args,
)
from tools.manual_eval_ocr_retry_execution_bundle_report import (
    build_ocr_retry_execution_bundle_report,
)
from tools.manual_eval_ocr_retry_execution_readiness import (
    build_ocr_retry_execution_readiness_report,
    format_ocr_retry_execution_readiness_report,
)
from tools.manual_eval_ocr_retry_execution_report import (
    format_ocr_retry_execution_bundle_report,
    format_ocr_retry_execution_report,
)
from tools.manual_eval_ocr_retry_execution_writer import (
    DEFAULT_OCR_RETRY_MODEL,
    DEFAULT_OCR_RETRY_PROMPT,
    write_ocr_retry_execution_bundle,
)


def handle_ocr_retry_execution_pre_feedback_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    paths = local_artifact_paths(args)

    if args.ocr_retry_execution_readiness:
        command_args = ocr_retry_command_args(args)
        report = build_ocr_retry_execution_readiness_report(
            db_path=db_path,
            selection_path=paths.selection_path,
            outcome=command_args.outcome,
            cohort=command_args.cohort,
            limit=command_args.limit,
            artifact_ids=command_args.artifact_ids,
        )
        return finish(report, format_ocr_retry_execution_readiness_report)

    if args.ocr_retry_execution_report:
        report = build_ocr_retry_execution_bundle_report(
            run_dir=paths.run_dir,
        )
        return finish(
            report,
            format_ocr_retry_execution_bundle_report,
            status_by_state=STATUS_ERROR,
        )

    return None


def handle_ocr_retry_execution_post_feedback_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    paths = local_artifact_paths(args)

    if args.ocr_retry_execute:
        command_args = ocr_retry_command_args(args)
        report = write_ocr_retry_execution_bundle(
            db_path=db_path,
            selection_path=paths.selection_path,
            confirm_token=str(args.confirm or ""),
            outcome=command_args.outcome,
            cohort=command_args.cohort,
            limit=command_args.limit,
            artifact_ids=command_args.artifact_ids,
            execution_dir=paths.execution_dir,
            ocr_provider=str(args.ocr_provider or "scaffold"),
            ocr_model=str(args.ocr_model or DEFAULT_OCR_RETRY_MODEL),
            ocr_prompt=str(args.ocr_prompt or DEFAULT_OCR_RETRY_PROMPT),
        )
        return finish(
            report,
            format_ocr_retry_execution_report,
            status_by_state=STATUS_OCR_EXECUTION,
            default_status=DEFAULT_ERROR_STATUS,
        )

    return None
