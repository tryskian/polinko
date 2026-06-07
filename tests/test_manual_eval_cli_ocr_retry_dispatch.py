import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from tools import manual_eval_cli_ocr_retry_dispatch as dispatch


class ManualEvalCliOcrRetryDispatchTests(unittest.TestCase):
    def test_pre_feedback_dispatch_preserves_group_order(self) -> None:
        calls: list[str] = []

        def handler(name: str, status: int | None):
            def _handle(**_kwargs: Any) -> int | None:
                calls.append(name)
                return status

            return _handle

        with (
            patch.object(
                dispatch,
                "handle_ocr_retry_selection_pre_feedback_commands",
                handler("selection", None),
            ),
            patch.object(
                dispatch,
                "handle_ocr_retry_execution_pre_feedback_commands",
                handler("execution", None),
            ),
            patch.object(
                dispatch,
                "handle_ocr_retry_feedback_closure_commands",
                handler("feedback_closure", 7),
            ),
        ):
            status = dispatch.handle_ocr_retry_pre_feedback_commands(
                args=object(),
                db_path=Path("manual_evals.db"),
                finish=lambda *_args, **_kwargs: 0,
            )

        self.assertEqual(status, 7)
        self.assertEqual(calls, ["selection", "execution", "feedback_closure"])

    def test_pre_feedback_dispatch_short_circuits_on_first_match(self) -> None:
        calls: list[str] = []

        def selection_handler(**_kwargs: Any) -> int:
            calls.append("selection")
            return 3

        def execution_handler(**_kwargs: Any) -> None:
            calls.append("execution")

        with (
            patch.object(
                dispatch,
                "handle_ocr_retry_selection_pre_feedback_commands",
                selection_handler,
            ),
            patch.object(
                dispatch,
                "handle_ocr_retry_execution_pre_feedback_commands",
                execution_handler,
            ),
        ):
            status = dispatch.handle_ocr_retry_pre_feedback_commands(
                args=object(),
                db_path=Path("manual_evals.db"),
                finish=lambda *_args, **_kwargs: 0,
            )

        self.assertEqual(status, 3)
        self.assertEqual(calls, ["selection"])

    def test_post_feedback_dispatch_preserves_group_order(self) -> None:
        calls: list[str] = []

        def handler(name: str, status: int | None):
            def _handle(**_kwargs: Any) -> int | None:
                calls.append(name)
                return status

            return _handle

        with (
            patch.object(
                dispatch,
                "handle_ocr_retry_execution_post_feedback_commands",
                handler("execution", None),
            ),
            patch.object(
                dispatch,
                "handle_ocr_retry_selection_post_feedback_commands",
                handler("selection", 9),
            ),
        ):
            status = dispatch.handle_ocr_retry_post_feedback_commands(
                args=object(),
                db_path=Path("manual_evals.db"),
                finish=lambda *_args, **_kwargs: 0,
            )

        self.assertEqual(status, 9)
        self.assertEqual(calls, ["execution", "selection"])


if __name__ == "__main__":
    unittest.main()
