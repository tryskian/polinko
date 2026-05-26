from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    optional_path,
    positive_limit,
)
from tools.manual_eval_feedback_decisions import (
    build_feedback_decision_preview_report,
    format_feedback_decision_draft_report,
    format_feedback_decision_preview_report,
    write_feedback_decision_draft,
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
from tools.manual_eval_open_feedback import (
    build_open_feedback_actionables_report,
    build_open_feedback_cohorts_report,
    format_open_feedback_actionables_report,
    format_open_feedback_cohorts_report,
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
from tools.manual_eval_source_context import (
    build_feedback_source_context_report,
    format_feedback_source_context_report,
)


def handle_feedback_reclassify_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    if args.no_context_feedback_reclassify_preview:
        report = build_no_context_feedback_reclassify_report(
            db_path=db_path,
            outcome=args.outcome or "fail",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_no_context_feedback_reclassify_report,
            status_by_state={"ok": 0},
            default_status=2,
        )

    if args.no_context_feedback_reclassify_apply:
        report = write_no_context_feedback_reclassify(
            db_path=db_path,
            confirm_token=str(args.confirm or ""),
            backup_root=optional_path(args.backup_root),
            outcome=args.outcome or "fail",
            cohort=args.cohort or "ocr_retry_evidence",
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_no_context_feedback_reclassify_report,
            status_by_state={"applied": 0},
            default_status=2,
        )

    if args.feedback_reclassify_preview:
        report = build_feedback_reclassify_report(
            db_path=db_path,
            plan_path=optional_path(args.plan_path),
        )
        return finish(
            report,
            format_feedback_reclassify_report,
            status_by_state={"ok": 0},
            default_status=2,
        )

    if args.feedback_reclassify_apply:
        report = write_feedback_reclassify(
            db_path=db_path,
            plan_path=optional_path(args.plan_path),
            confirm_token=str(args.confirm or ""),
            backup_root=optional_path(args.backup_root),
        )
        return finish(
            report,
            format_feedback_reclassify_report,
            status_by_state={"applied": 0},
            default_status=2,
        )

    return None


def handle_feedback_context_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    if args.feedback_source_context:
        report = build_feedback_source_context_report(
            db_path=db_path,
            outcome=args.outcome or "fail",
            cohort=args.cohort or "grounding_source_verification",
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_feedback_source_context_report,
            status_by_state={"error": 2},
        )

    if args.overlay_ocr_comparison_readiness:
        report = build_overlay_ocr_comparison_readiness_report(
            db_path=db_path,
            outcome=args.outcome or "fail",
            cohort=args.cohort or "ocr_overlay_hypothesis",
            limit=positive_limit(args.limit),
            overlay_source_index_path=optional_path(args.overlay_source_index),
        )
        return finish(
            report,
            format_overlay_ocr_comparison_readiness_report,
            status_by_state={"error": 2},
        )

    if args.overlay_source_index_draft:
        report = write_overlay_source_context_index_draft(
            db_path=db_path,
            output_path=optional_path(args.output_path),
            force=bool(args.force),
            outcome=args.outcome or "fail",
            cohort=args.cohort or "ocr_overlay_hypothesis",
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_overlay_source_context_index_draft_report,
            status_by_state={"written": 0},
            default_status=2,
        )

    if args.overlay_source_index_validate:
        report = build_overlay_source_context_index_validation_report(
            db_path=db_path,
            overlay_source_index_path=optional_path(args.overlay_source_index),
            outcome=args.outcome or "fail",
            cohort=args.cohort or "ocr_overlay_hypothesis",
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_overlay_source_context_index_validation_report,
            status_by_state={"ready": 0},
            default_status=2,
        )

    if args.feedback_decision_draft:
        report = write_feedback_decision_draft(
            db_path=db_path,
            output_path=optional_path(args.output_path),
            force=bool(args.force),
            outcome=args.outcome or "fail",
            cohort=args.cohort or "grounding_source_verification",
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_feedback_decision_draft_report,
            status_by_state={"written": 0},
            default_status=2,
        )

    if args.feedback_decision_preview:
        report = build_feedback_decision_preview_report(
            db_path=db_path,
            decision_path=optional_path(args.decision_path),
            outcome=args.outcome or "fail",
            cohort=args.cohort or "grounding_source_verification",
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_feedback_decision_preview_report,
            status_by_state={"ok": 0},
            default_status=2,
        )

    if args.open_feedback_cohorts:
        report = build_open_feedback_cohorts_report(
            db_path=db_path,
            outcome=args.outcome,
            cohort=args.cohort,
        )
        return finish(report, format_open_feedback_cohorts_report)

    if args.open_feedback_actionables:
        report = build_open_feedback_actionables_report(
            db_path=db_path,
            outcome=args.outcome,
            cohort=args.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(report, format_open_feedback_actionables_report)

    return None
