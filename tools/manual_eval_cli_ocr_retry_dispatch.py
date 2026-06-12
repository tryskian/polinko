from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.manual_eval_cli_dispatch_support import FinishReport, dispatch_first_match
from tools.manual_eval_cli_ocr_retry_execution_dispatch import (
    handle_ocr_retry_execution_post_feedback_commands,
    handle_ocr_retry_execution_pre_feedback_commands,
)
from tools.manual_eval_cli_ocr_retry_feedback_closure_dispatch import (
    handle_ocr_retry_feedback_closure_commands,
)
from tools.manual_eval_cli_ocr_retry_selection_dispatch import (
    handle_ocr_retry_selection_post_feedback_commands,
    handle_ocr_retry_selection_pre_feedback_commands,
)


def handle_ocr_retry_pre_feedback_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    return dispatch_first_match(
        handlers=(
            handle_ocr_retry_selection_pre_feedback_commands,
            handle_ocr_retry_execution_pre_feedback_commands,
            handle_ocr_retry_feedback_closure_commands,
        ),
        args=args,
        db_path=db_path,
        finish=finish,
    )


def handle_ocr_retry_post_feedback_commands(
    *,
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    return dispatch_first_match(
        handlers=(
            handle_ocr_retry_execution_post_feedback_commands,
            handle_ocr_retry_selection_post_feedback_commands,
        ),
        args=args,
        db_path=db_path,
        finish=finish,
    )
