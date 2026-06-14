from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    DEFAULT_ERROR_STATUS,
    FinishReport,
    STATUS_WRITTEN_OK,
    ocr_retry_filters,
    optional_path,
    positive_limit,
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
    if args.ocr_retry_selection_draft:
        filters = ocr_retry_filters(args)
        report = write_ocr_retry_selection_decision_draft(
            db_path=db_path,
            output_path=optional_path(args.output_path),
            force=bool(args.force),
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(
            report,
            format_ocr_retry_selection_decision_draft_report,
            status_by_state=STATUS_WRITTEN_OK,
            default_status=DEFAULT_ERROR_STATUS,
        )

    if args.ocr_retry_selection_apply_preview:
        filters = ocr_retry_filters(args)
        report = build_ocr_retry_selection_apply_preview_report(
            db_path=db_path,
            selection_path=optional_path(args.selection_path),
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_selection_apply_preview_report)

    return None


def handle_ocr_retry_selection_post_feedback_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    if args.ocr_retry_selection_validate:
        filters = ocr_retry_filters(args)
        report = build_ocr_retry_selection_validation_report(
            db_path=db_path,
            selection_path=optional_path(args.selection_path),
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_selection_validation_report)

    if args.ocr_retry_selection_template:
        filters = ocr_retry_filters(args)
        report = build_ocr_retry_selection_template_report(
            db_path=db_path,
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_selection_template_report)

    if args.ocr_retry_selection_review:
        filters = ocr_retry_filters(args)
        report = build_ocr_retry_selection_review_report(
            db_path=db_path,
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_selection_review_report)

    if args.ocr_retry_rerun_plan:
        filters = ocr_retry_filters(args)
        report = build_ocr_retry_rerun_plan_report(
            db_path=db_path,
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
            artifact_ids=args.artifact_id,
        )
        return finish(report, format_ocr_retry_rerun_plan_report)

    if args.ocr_retry_rerun_manifest:
        filters = ocr_retry_filters(args)
        report = build_ocr_retry_rerun_manifest_report(
            db_path=db_path,
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(report, format_ocr_retry_rerun_manifest_report)

    if args.ocr_retry_input_packet:
        filters = ocr_retry_filters(args)
        report = build_ocr_retry_input_packet_report(
            db_path=db_path,
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(report, format_ocr_retry_input_packet_report)

    if args.ocr_retry_source_provenance:
        filters = ocr_retry_filters(args)
        report = build_ocr_retry_source_provenance_report(
            db_path=db_path,
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(report, format_ocr_retry_source_provenance_report)

    if args.ocr_retry_source_verification:
        filters = ocr_retry_filters(args)
        report = build_ocr_retry_source_verification_report(
            db_path=db_path,
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(report, format_ocr_retry_source_verification_report)

    if args.ocr_retry_candidates:
        filters = ocr_retry_filters(args)
        report = build_ocr_retry_candidates_report(
            db_path=db_path,
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(report, format_ocr_retry_candidates_report)

    return None
