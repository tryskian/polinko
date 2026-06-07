import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from tools import manual_eval_cli_feedback_dispatch as dispatch


class ManualEvalCliFeedbackDispatchTests(unittest.TestCase):
    def test_feedback_context_dispatch_preserves_group_order(self) -> None:
        calls: list[str] = []

        def handler(name: str, status: int | None):
            def _handle(**_kwargs: Any) -> int | None:
                calls.append(name)
                return status

            return _handle

        with (
            patch.object(
                dispatch,
                "handle_feedback_source_context_commands",
                handler("source_context", None),
            ),
            patch.object(
                dispatch,
                "handle_feedback_overlay_commands",
                handler("overlay", None),
            ),
            patch.object(
                dispatch,
                "handle_feedback_decision_commands",
                handler("decision", None),
            ),
            patch.object(
                dispatch,
                "handle_open_feedback_commands",
                handler("open_feedback", 11),
            ),
        ):
            status = dispatch.handle_feedback_context_commands(
                args=object(),
                db_path=Path("manual_evals.db"),
                finish=lambda *_args, **_kwargs: 0,
            )

        self.assertEqual(status, 11)
        self.assertEqual(
            calls,
            ["source_context", "overlay", "decision", "open_feedback"],
        )

    def test_feedback_context_dispatch_short_circuits_on_first_match(self) -> None:
        calls: list[str] = []

        def source_context_handler(**_kwargs: Any) -> int:
            calls.append("source_context")
            return 5

        def overlay_handler(**_kwargs: Any) -> None:
            calls.append("overlay")

        with (
            patch.object(
                dispatch,
                "handle_feedback_source_context_commands",
                source_context_handler,
            ),
            patch.object(dispatch, "handle_feedback_overlay_commands", overlay_handler),
        ):
            status = dispatch.handle_feedback_context_commands(
                args=object(),
                db_path=Path("manual_evals.db"),
                finish=lambda *_args, **_kwargs: 0,
            )

        self.assertEqual(status, 5)
        self.assertEqual(calls, ["source_context"])

    def test_feedback_reclassify_dispatch_delegates_to_group(self) -> None:
        with patch.object(
            dispatch,
            "handle_feedback_reclassify_command_group",
            return_value=13,
        ) as reclassify_group:
            status = dispatch.handle_feedback_reclassify_commands(
                args=object(),
                db_path=Path("manual_evals.db"),
                finish=lambda *_args, **_kwargs: 0,
            )

        self.assertEqual(status, 13)
        reclassify_group.assert_called_once()


if __name__ == "__main__":
    unittest.main()
