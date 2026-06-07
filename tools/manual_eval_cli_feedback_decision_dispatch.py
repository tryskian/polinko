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


def handle_feedback_decision_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
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

    return None
