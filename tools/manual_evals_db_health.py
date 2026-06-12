from __future__ import annotations

from pathlib import Path

from tools.manual_eval_cli_dispatch_support import dispatch_first_match
from tools.manual_eval_cli_feedback_dispatch import (
    handle_feedback_context_commands,
    handle_feedback_reclassify_commands,
)
from tools.manual_eval_cli_ocr_retry_dispatch import (
    handle_ocr_retry_post_feedback_commands,
    handle_ocr_retry_pre_feedback_commands,
)
from tools.manual_eval_cli_output import finish_manual_eval_report as _finish_report
from tools.manual_eval_cli_parser import build_manual_evals_db_health_parser
from tools.manual_eval_health_report import (
    build_manual_evals_health_report,
    format_manual_evals_health_report,
)

# Guarded feedback-closure commands keep manual_eval_warehouse scope explicit.
_CLI_GATE_CONTRACT_MARKERS: tuple[str, ...] = (
    "--ocr-retry-execute",
    "--ocr-retry-execution-report",
    "--ocr-retry-feedback-closure-preview",
    "--ocr-retry-feedback-closure-apply",
    "--ocr-retry-feedback-closure-apply-report",
    "--ocr-retry-feedback-closure-restore-preview",
    "--ocr-retry-feedback-closure-restore",
    "OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION",
    "OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION",
    "OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION",
    "OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION",
    "OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION",
    "--confirm",
    "OCR_RETRY_EXECUTION_CONFIRM_TOKEN",
    "OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN",
    "OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN",
    "CONFIRM=ocr-retry-execute",
    "CONFIRM=ocr-retry-feedback-closure-apply",
    "CONFIRM=ocr-retry-feedback-closure-restore",
    "manual_eval_warehouse",
    "build_ocr_retry_execution_readiness_report",
)


def _build_parser():
    return build_manual_evals_db_health_parser()


def main() -> int:
    args = _build_parser().parse_args()
    db_path = Path(args.db).expanduser()

    def finish(report, formatter, **status_kwargs):
        return _finish_report(
            report,
            formatter,
            json_output=bool(args.json),
            **status_kwargs,
        )

    command_status = dispatch_first_match(
        handlers=(
            handle_ocr_retry_pre_feedback_commands,
            handle_feedback_reclassify_commands,
            handle_ocr_retry_post_feedback_commands,
            handle_feedback_context_commands,
        ),
        args=args,
        db_path=db_path,
        finish=finish,
    )
    if command_status is not None:
        return command_status

    report = build_manual_evals_health_report(db_path=db_path)
    return finish(report, format_manual_evals_health_report)


if __name__ == "__main__":
    raise SystemExit(main())
