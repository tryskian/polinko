from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    ReportFormatter,
    STATUS_WRITTEN_OK,
    first_enabled_command,
    finish_report_with_error_default,
    local_artifact_paths,
    ocr_retry_report_kwargs,
)
from tools.manual_eval_ocr_retry_candidates import (
    build_ocr_retry_candidates_report,
    format_ocr_retry_candidates_report,
)
from tools.manual_eval_ocr_retry_input_packet import (
    build_ocr_retry_input_packet_report,
    format_ocr_retry_input_packet_report,
)
from tools.manual_eval_ocr_retry_rerun_manifest import (
    build_ocr_retry_rerun_manifest_report,
    format_ocr_retry_rerun_manifest_report,
)
from tools.manual_eval_ocr_retry_rerun_plan import (
    build_ocr_retry_rerun_plan_report,
    format_ocr_retry_rerun_plan_report,
)
from tools.manual_eval_ocr_retry_selection_apply_preview import (
    build_ocr_retry_selection_apply_preview_report,
    format_ocr_retry_selection_apply_preview_report,
)
from tools.manual_eval_ocr_retry_selection_decision_draft import (
    format_ocr_retry_selection_decision_draft_report,
    write_ocr_retry_selection_decision_draft,
)
from tools.manual_eval_ocr_retry_selection_review import (
    build_ocr_retry_selection_review_report,
    format_ocr_retry_selection_review_report,
)
from tools.manual_eval_ocr_retry_selection_template import (
    build_ocr_retry_selection_template_report,
    format_ocr_retry_selection_template_report,
)
from tools.manual_eval_ocr_retry_selection_validation import (
    build_ocr_retry_selection_validation_report,
    format_ocr_retry_selection_validation_report,
)
from tools.manual_eval_ocr_retry_source_provenance import (
    build_ocr_retry_source_provenance_report,
    format_ocr_retry_source_provenance_report,
)
from tools.manual_eval_ocr_retry_source_verification import (
    build_ocr_retry_source_verification_report,
    format_ocr_retry_source_verification_report,
)


ReportBuilder = Callable[..., dict[str, Any]]


class OcrRetrySelectionReportCommand(NamedTuple):
    flag: str
    builder: ReportBuilder
    formatter: ReportFormatter
    include_artifact_ids: bool = False
    include_selection_path: bool = False


OCR_RETRY_SELECTION_REPORT_COMMANDS = (
    OcrRetrySelectionReportCommand(
        flag="ocr_retry_selection_validate",
        builder=build_ocr_retry_selection_validation_report,
        formatter=format_ocr_retry_selection_validation_report,
        include_artifact_ids=True,
        include_selection_path=True,
    ),
    OcrRetrySelectionReportCommand(
        flag="ocr_retry_selection_template",
        builder=build_ocr_retry_selection_template_report,
        formatter=format_ocr_retry_selection_template_report,
        include_artifact_ids=True,
    ),
    OcrRetrySelectionReportCommand(
        flag="ocr_retry_selection_review",
        builder=build_ocr_retry_selection_review_report,
        formatter=format_ocr_retry_selection_review_report,
        include_artifact_ids=True,
    ),
    OcrRetrySelectionReportCommand(
        flag="ocr_retry_rerun_plan",
        builder=build_ocr_retry_rerun_plan_report,
        formatter=format_ocr_retry_rerun_plan_report,
        include_artifact_ids=True,
    ),
    OcrRetrySelectionReportCommand(
        flag="ocr_retry_rerun_manifest",
        builder=build_ocr_retry_rerun_manifest_report,
        formatter=format_ocr_retry_rerun_manifest_report,
    ),
    OcrRetrySelectionReportCommand(
        flag="ocr_retry_input_packet",
        builder=build_ocr_retry_input_packet_report,
        formatter=format_ocr_retry_input_packet_report,
    ),
    OcrRetrySelectionReportCommand(
        flag="ocr_retry_source_provenance",
        builder=build_ocr_retry_source_provenance_report,
        formatter=format_ocr_retry_source_provenance_report,
    ),
    OcrRetrySelectionReportCommand(
        flag="ocr_retry_source_verification",
        builder=build_ocr_retry_source_verification_report,
        formatter=format_ocr_retry_source_verification_report,
    ),
    OcrRetrySelectionReportCommand(
        flag="ocr_retry_candidates",
        builder=build_ocr_retry_candidates_report,
        formatter=format_ocr_retry_candidates_report,
    ),
)


def handle_ocr_retry_selection_pre_feedback_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    paths = local_artifact_paths(args)

    if args.ocr_retry_selection_draft:
        report = write_ocr_retry_selection_decision_draft(
            db_path=db_path,
            output_path=paths.output_path,
            force=bool(args.force),
            **ocr_retry_report_kwargs(args, include_artifact_ids=True),
        )
        return finish_report_with_error_default(
            finish=finish,
            report=report,
            formatter=format_ocr_retry_selection_decision_draft_report,
            status_by_state=STATUS_WRITTEN_OK,
        )

    if args.ocr_retry_selection_apply_preview:
        report = build_ocr_retry_selection_apply_preview_report(
            db_path=db_path,
            selection_path=paths.selection_path,
            **ocr_retry_report_kwargs(args, include_artifact_ids=True),
        )
        return finish(report, format_ocr_retry_selection_apply_preview_report)

    return None


def handle_ocr_retry_selection_post_feedback_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    command = first_enabled_command(
        args=args,
        commands=OCR_RETRY_SELECTION_REPORT_COMMANDS,
    )
    if command is None:
        return None

    report_kwargs = ocr_retry_report_kwargs(
        args,
        include_artifact_ids=command.include_artifact_ids,
    )
    if command.include_selection_path:
        report_kwargs["selection_path"] = local_artifact_paths(args).selection_path

    report = command.builder(db_path=db_path, **report_kwargs)
    return finish(report, command.formatter)
