from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    FinishReport,
    STATUS_ERROR,
    filtered_report_kwargs,
)
from tools.manual_eval_source_context import (
    build_feedback_source_context_report,
    format_feedback_source_context_report,
)


def handle_feedback_source_context_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    if args.feedback_source_context:
        report = build_feedback_source_context_report(
            db_path=db_path,
            **filtered_report_kwargs(
                args,
                outcome="fail",
                cohort="grounding_source_verification",
            ),
        )
        return finish(
            report,
            format_feedback_source_context_report,
            status_by_state=STATUS_ERROR,
        )

    return None
