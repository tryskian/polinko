from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    default_filters,
    optional_path,
    positive_limit,
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
    if args.no_context_feedback_reclassify_preview:
        filters = default_filters(args, outcome="fail", cohort="ocr_retry_evidence")
        report = build_no_context_feedback_reclassify_report(
            db_path=db_path,
            outcome=filters.outcome,
            cohort=filters.cohort,
            limit=positive_limit(args.limit),
        )
        return finish(
            report,
            format_no_context_feedback_reclassify_report,
            status_by_state={"ok": 0},
            default_status=2,
        )

    if args.no_context_feedback_reclassify_apply:
        filters = default_filters(args, outcome="fail", cohort="ocr_retry_evidence")
        report = write_no_context_feedback_reclassify(
            db_path=db_path,
            confirm_token=str(args.confirm or ""),
            backup_root=optional_path(args.backup_root),
            outcome=filters.outcome,
            cohort=filters.cohort,
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
