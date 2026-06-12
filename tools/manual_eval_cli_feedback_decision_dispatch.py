from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    DEFAULT_ERROR_STATUS,
    FinishReport,
    STATUS_OK,
    STATUS_WRITTEN_OK,
    default_filters,
    optional_path,
    positive_limit,
)
from tools.manual_eval_feedback_decisions import (
    build_feedback_decision_preview_report,
    format_feedback_decision_draft_report,
    format_feedback_decision_preview_report,
    write_feedback_decision_draft,
)


def handle_feedback_decision_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    if args.feedback_decision_draft:
        filters = default_filters(
            args,
            outcome="fail",
            cohort="grounding_source_verification",
        )
        report = write_feedback_decision_draft(
            db_path=db_path,
            output_path=optional_path(args.output_path),
            force=bool(args.force),
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_feedback_decision_draft_report,
            status_by_state=STATUS_WRITTEN_OK,
            default_status=DEFAULT_ERROR_STATUS,
        )

    if args.feedback_decision_preview:
        filters = default_filters(
            args,
            outcome="fail",
            cohort="grounding_source_verification",
        )
        report = build_feedback_decision_preview_report(
            db_path=db_path,
            decision_path=optional_path(args.decision_path),
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_feedback_decision_preview_report,
            status_by_state=STATUS_OK,
            default_status=DEFAULT_ERROR_STATUS,
        )

    return None
