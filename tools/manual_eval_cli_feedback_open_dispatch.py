from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import FinishReport, positive_limit
from tools.manual_eval_open_feedback import (
    build_open_feedback_actionables_report,
    build_open_feedback_cohorts_report,
    format_open_feedback_actionables_report,
    format_open_feedback_cohorts_report,
)


def handle_open_feedback_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
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
