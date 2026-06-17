import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from tools import manual_eval_cli_ocr_retry_dispatch as dispatch
from tools import manual_eval_cli_ocr_retry_selection_dispatch as selection_dispatch


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

    def test_selection_post_feedback_report_dispatch_preserves_order(self) -> None:
        calls: list[tuple[str, dict[str, Any]]] = []

        def formatter(_report: dict[str, Any]) -> str:
            return "report"

        def builder(name: str):
            def _build(**kwargs: Any) -> dict[str, Any]:
                calls.append((name, kwargs))
                return {"state": "ok", "name": name}

            return _build

        commands = (
            selection_dispatch.OcrRetrySelectionReportCommand(
                flag="ocr_retry_selection_template",
                builder=builder("template"),
                formatter=formatter,
                include_artifact_ids=True,
            ),
            selection_dispatch.OcrRetrySelectionReportCommand(
                flag="ocr_retry_candidates",
                builder=builder("candidates"),
                formatter=formatter,
            ),
        )
        args = SimpleNamespace(
            ocr_retry_selection_template=False,
            ocr_retry_candidates=True,
            outcome="",
            cohort=None,
            limit=0,
            artifact_id=["source-a"],
        )

        with patch.object(
            selection_dispatch,
            "OCR_RETRY_SELECTION_REPORT_COMMANDS",
            commands,
        ):
            status = (
                selection_dispatch.handle_ocr_retry_selection_post_feedback_commands(
                    args=args,
                    db_path=Path("manual_evals.db"),
                    finish=lambda _report, _formatter: 17,
                )
            )

        self.assertEqual(status, 17)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "candidates")
        self.assertEqual(
            calls[0][1],
            {
                "db_path": Path("manual_evals.db"),
                "outcome": "partial",
                "cohort": "ocr_retry_evidence",
                "limit": 1,
            },
        )

    def test_selection_post_feedback_validate_keeps_selection_path(self) -> None:
        calls: list[dict[str, Any]] = []

        def formatter(_report: dict[str, Any]) -> str:
            return "report"

        def build_validate(**kwargs: Any) -> dict[str, Any]:
            calls.append(kwargs)
            return {"state": "ok"}

        commands = (
            selection_dispatch.OcrRetrySelectionReportCommand(
                flag="ocr_retry_selection_validate",
                builder=build_validate,
                formatter=formatter,
                include_artifact_ids=True,
                include_selection_path=True,
            ),
        )
        args = SimpleNamespace(
            ocr_retry_selection_validate=True,
            outcome="fail",
            cohort="custom_cohort",
            limit=3,
            artifact_id=["source-a"],
            selection_path="selection.json",
        )

        with patch.object(
            selection_dispatch,
            "OCR_RETRY_SELECTION_REPORT_COMMANDS",
            commands,
        ):
            status = (
                selection_dispatch.handle_ocr_retry_selection_post_feedback_commands(
                    args=args,
                    db_path=Path("manual_evals.db"),
                    finish=lambda _report, _formatter: 19,
                )
            )

        self.assertEqual(status, 19)
        self.assertEqual(
            calls,
            [
                {
                    "db_path": Path("manual_evals.db"),
                    "outcome": "fail",
                    "cohort": "custom_cohort",
                    "limit": 3,
                    "artifact_ids": ["source-a"],
                    "selection_path": Path("selection.json"),
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
