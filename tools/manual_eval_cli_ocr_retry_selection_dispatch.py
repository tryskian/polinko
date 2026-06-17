from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    STATUS_WRITTEN_OK,
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
    paths = local_artifact_paths(args)

    if args.ocr_retry_selection_validate:
        report = build_ocr_retry_selection_validation_report(
            db_path=db_path,
            selection_path=paths.selection_path,
            **ocr_retry_report_kwargs(args, include_artifact_ids=True),
        )
        return finish(report, format_ocr_retry_selection_validation_report)

    if args.ocr_retry_selection_template:
        report = build_ocr_retry_selection_template_report(
            db_path=db_path,
            **ocr_retry_report_kwargs(args, include_artifact_ids=True),
        )
        return finish(report, format_ocr_retry_selection_template_report)

    if args.ocr_retry_selection_review:
        report = build_ocr_retry_selection_review_report(
            db_path=db_path,
            **ocr_retry_report_kwargs(args, include_artifact_ids=True),
        )
        return finish(report, format_ocr_retry_selection_review_report)

    if args.ocr_retry_rerun_plan:
        report = build_ocr_retry_rerun_plan_report(
            db_path=db_path,
            **ocr_retry_report_kwargs(args, include_artifact_ids=True),
        )
        return finish(report, format_ocr_retry_rerun_plan_report)

    if args.ocr_retry_rerun_manifest:
        report = build_ocr_retry_rerun_manifest_report(
            db_path=db_path,
            **ocr_retry_report_kwargs(args),
        )
        return finish(report, format_ocr_retry_rerun_manifest_report)

    if args.ocr_retry_input_packet:
        report = build_ocr_retry_input_packet_report(
            db_path=db_path,
            **ocr_retry_report_kwargs(args),
        )
        return finish(report, format_ocr_retry_input_packet_report)

    if args.ocr_retry_source_provenance:
        report = build_ocr_retry_source_provenance_report(
            db_path=db_path,
            **ocr_retry_report_kwargs(args),
        )
        return finish(report, format_ocr_retry_source_provenance_report)

    if args.ocr_retry_source_verification:
        report = build_ocr_retry_source_verification_report(
            db_path=db_path,
            **ocr_retry_report_kwargs(args),
        )
        return finish(report, format_ocr_retry_source_verification_report)

    if args.ocr_retry_candidates:
        report = build_ocr_retry_candidates_report(
            db_path=db_path,
            **ocr_retry_report_kwargs(args),
        )
        return finish(report, format_ocr_retry_candidates_report)

    return None
