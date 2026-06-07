from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import FinishReport
from tools.manual_eval_cli_feedback_decision_dispatch import (
    handle_feedback_decision_commands,
)
from tools.manual_eval_cli_feedback_open_dispatch import handle_open_feedback_commands
from tools.manual_eval_cli_feedback_overlay_dispatch import (
    handle_feedback_overlay_commands,
)
from tools.manual_eval_cli_feedback_reclassify_dispatch import (
    handle_feedback_reclassify_command_group,
)
from tools.manual_eval_cli_feedback_source_context_dispatch import (
    handle_feedback_source_context_commands,
)


def handle_feedback_reclassify_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    return handle_feedback_reclassify_command_group(
        args=args,
        db_path=db_path,
        finish=finish,
    )


def handle_feedback_context_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    for handler in (
        handle_feedback_source_context_commands,
        handle_feedback_overlay_commands,
        handle_feedback_decision_commands,
        handle_open_feedback_commands,
    ):
        status = handler(args=args, db_path=db_path, finish=finish)
        if status is not None:
            return status
    return None
