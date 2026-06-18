import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from tools import manual_eval_cli_feedback_dispatch as dispatch
from tools import manual_eval_cli_feedback_overlay_dispatch as overlay_dispatch
from tools import manual_eval_cli_feedback_reclassify_dispatch as reclassify_dispatch


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

    def test_feedback_overlay_group_preserves_report_command_order(self) -> None:
        calls: list[tuple[str, dict[str, Any]]] = []

        def formatter(_report: dict[str, Any]) -> str:
            return "report"

        def builder(name: str):
            def _build(**kwargs: Any) -> dict[str, Any]:
                calls.append((name, kwargs))
                return {"state": "ok", "name": name}

            return _build

        commands = (
            overlay_dispatch.FeedbackOverlayCommand(
                flag="first_command",
                builder=builder("first"),
                formatter=formatter,
                status_by_state={"ok": 0},
            ),
            overlay_dispatch.FeedbackOverlayCommand(
                flag="second_command",
                builder=builder("second"),
                formatter=formatter,
                status_by_state={"ok": 0},
            ),
        )
        args = SimpleNamespace(
            first_command=False,
            second_command=True,
            outcome="",
            cohort=None,
            limit=0,
        )

        with patch.object(
            overlay_dispatch,
            "FEEDBACK_OVERLAY_COMMANDS",
            commands,
        ):
            status = overlay_dispatch.handle_feedback_overlay_commands(
                args=args,
                db_path=Path("manual_evals.db"),
                finish=lambda _report, _formatter, **_kwargs: 17,
            )

        self.assertEqual(status, 17)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "second")
        self.assertEqual(
            calls[0][1],
            {
                "db_path": Path("manual_evals.db"),
                "outcome": "fail",
                "cohort": "ocr_overlay_hypothesis",
                "limit": 1,
            },
        )

    def test_overlay_readiness_keeps_index_defaults_and_direct_finish(self) -> None:
        calls: list[dict[str, Any]] = []
        finish_calls: list[dict[str, Any]] = []

        def formatter(_report: dict[str, Any]) -> str:
            return "report"

        def builder(**kwargs: Any) -> dict[str, Any]:
            calls.append(kwargs)
            return {"state": "error"}

        def finish(*args: Any, **kwargs: Any) -> int:
            finish_calls.append({"args": args, "kwargs": kwargs})
            return 19

        commands = (
            overlay_dispatch.FeedbackOverlayCommand(
                flag="overlay_ocr_comparison_readiness",
                builder=builder,
                formatter=formatter,
                status_by_state={"error": 2},
                include_overlay_source_index_path=True,
                use_error_default=False,
            ),
        )
        args = SimpleNamespace(
            overlay_ocr_comparison_readiness=True,
            overlay_source_index="context-index.json",
            outcome="",
            cohort=None,
            limit=0,
        )

        with patch.object(
            overlay_dispatch,
            "FEEDBACK_OVERLAY_COMMANDS",
            commands,
        ):
            status = overlay_dispatch.handle_feedback_overlay_commands(
                args=args,
                db_path=Path("manual_evals.db"),
                finish=finish,
            )

        self.assertEqual(status, 19)
        self.assertEqual(
            calls,
            [
                {
                    "db_path": Path("manual_evals.db"),
                    "outcome": "fail",
                    "cohort": "ocr_overlay_hypothesis",
                    "limit": 1,
                    "overlay_source_index_path": Path("context-index.json"),
                }
            ],
        )
        self.assertEqual(finish_calls[0]["args"], ({"state": "error"}, formatter))
        self.assertEqual(finish_calls[0]["kwargs"], {"status_by_state": {"error": 2}})

    def test_overlay_source_index_draft_keeps_output_force_and_guarded_finish(
        self,
    ) -> None:
        calls: list[dict[str, Any]] = []
        finish_calls: list[dict[str, Any]] = []

        def formatter(_report: dict[str, Any]) -> str:
            return "report"

        def builder(**kwargs: Any) -> dict[str, Any]:
            calls.append(kwargs)
            return {"state": "written"}

        def finish(*args: Any, **kwargs: Any) -> int:
            finish_calls.append({"args": args, "kwargs": kwargs})
            return 23

        commands = (
            overlay_dispatch.FeedbackOverlayCommand(
                flag="overlay_source_index_draft",
                builder=builder,
                formatter=formatter,
                status_by_state={"written": 0},
                include_output_path=True,
                include_force=True,
            ),
        )
        args = SimpleNamespace(
            overlay_source_index_draft=True,
            output_path="source-index-draft.json",
            force=True,
            outcome="custom-outcome",
            cohort="custom-cohort",
            limit=5,
        )

        with patch.object(
            overlay_dispatch,
            "FEEDBACK_OVERLAY_COMMANDS",
            commands,
        ):
            status = overlay_dispatch.handle_feedback_overlay_commands(
                args=args,
                db_path=Path("manual_evals.db"),
                finish=finish,
            )

        self.assertEqual(status, 23)
        self.assertEqual(
            calls,
            [
                {
                    "db_path": Path("manual_evals.db"),
                    "outcome": "custom-outcome",
                    "cohort": "custom-cohort",
                    "limit": 5,
                    "output_path": Path("source-index-draft.json"),
                    "force": True,
                }
            ],
        )
        self.assertEqual(finish_calls[0]["args"], ({"state": "written"}, formatter))
        self.assertEqual(
            finish_calls[0]["kwargs"],
            {"status_by_state": {"written": 0}, "default_status": 2},
        )

    def test_overlay_source_index_validate_keeps_index_and_guarded_status(
        self,
    ) -> None:
        calls: list[dict[str, Any]] = []
        finish_calls: list[dict[str, Any]] = []

        def formatter(_report: dict[str, Any]) -> str:
            return "report"

        def builder(**kwargs: Any) -> dict[str, Any]:
            calls.append(kwargs)
            return {"state": "ready"}

        def finish(*args: Any, **kwargs: Any) -> int:
            finish_calls.append({"args": args, "kwargs": kwargs})
            return 29

        commands = (
            overlay_dispatch.FeedbackOverlayCommand(
                flag="overlay_source_index_validate",
                builder=builder,
                formatter=formatter,
                status_by_state={"ready": 0},
                include_overlay_source_index_path=True,
            ),
        )
        args = SimpleNamespace(
            overlay_source_index_validate=True,
            overlay_source_index="context-index.json",
            outcome="",
            cohort=None,
            limit=3,
        )

        with patch.object(
            overlay_dispatch,
            "FEEDBACK_OVERLAY_COMMANDS",
            commands,
        ):
            status = overlay_dispatch.handle_feedback_overlay_commands(
                args=args,
                db_path=Path("manual_evals.db"),
                finish=finish,
            )

        self.assertEqual(status, 29)
        self.assertEqual(
            calls,
            [
                {
                    "db_path": Path("manual_evals.db"),
                    "outcome": "fail",
                    "cohort": "ocr_overlay_hypothesis",
                    "limit": 3,
                    "overlay_source_index_path": Path("context-index.json"),
                }
            ],
        )
        self.assertEqual(finish_calls[0]["args"], ({"state": "ready"}, formatter))
        self.assertEqual(
            finish_calls[0]["kwargs"],
            {"status_by_state": {"ready": 0}, "default_status": 2},
        )

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

    def test_feedback_reclassify_group_preserves_report_command_order(self) -> None:
        calls: list[tuple[str, dict[str, Any]]] = []

        def formatter(_report: dict[str, Any]) -> str:
            return "report"

        def builder(name: str):
            def _build(**kwargs: Any) -> dict[str, Any]:
                calls.append((name, kwargs))
                return {"state": "ok", "name": name}

            return _build

        commands = (
            reclassify_dispatch.FeedbackReclassifyCommand(
                flag="first_command",
                builder=builder("first"),
                formatter=formatter,
                status_by_state={"ok": 0},
            ),
            reclassify_dispatch.FeedbackReclassifyCommand(
                flag="second_command",
                builder=builder("second"),
                formatter=formatter,
                status_by_state={"ok": 0},
            ),
        )
        args = SimpleNamespace(first_command=False, second_command=True)

        with patch.object(
            reclassify_dispatch,
            "FEEDBACK_RECLASSIFY_COMMANDS",
            commands,
        ):
            status = reclassify_dispatch.handle_feedback_reclassify_command_group(
                args=args,
                db_path=Path("manual_evals.db"),
                finish=lambda _report, _formatter, **_kwargs: 17,
            )

        self.assertEqual(status, 17)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "second")
        self.assertEqual(calls[0][1], {"db_path": Path("manual_evals.db")})

    def test_no_context_reclassify_command_keeps_default_filters(self) -> None:
        calls: list[dict[str, Any]] = []
        finish_calls: list[dict[str, Any]] = []

        def formatter(_report: dict[str, Any]) -> str:
            return "report"

        def builder(**kwargs: Any) -> dict[str, Any]:
            calls.append(kwargs)
            return {"state": "ok"}

        def finish(*args: Any, **kwargs: Any) -> int:
            finish_calls.append({"args": args, "kwargs": kwargs})
            return 19

        commands = (
            reclassify_dispatch.FeedbackReclassifyCommand(
                flag="no_context_feedback_reclassify_preview",
                builder=builder,
                formatter=formatter,
                status_by_state={"ok": 0},
                use_no_context_filters=True,
            ),
        )
        args = SimpleNamespace(
            no_context_feedback_reclassify_preview=True,
            outcome="",
            cohort=None,
            limit=0,
        )

        with patch.object(
            reclassify_dispatch,
            "FEEDBACK_RECLASSIFY_COMMANDS",
            commands,
        ):
            status = reclassify_dispatch.handle_feedback_reclassify_command_group(
                args=args,
                db_path=Path("manual_evals.db"),
                finish=finish,
            )

        self.assertEqual(status, 19)
        self.assertEqual(
            calls,
            [
                {
                    "db_path": Path("manual_evals.db"),
                    "outcome": "fail",
                    "cohort": "ocr_retry_evidence",
                    "limit": 1,
                }
            ],
        )
        self.assertEqual(finish_calls[0]["args"], ({"state": "ok"}, formatter))
        self.assertEqual(
            finish_calls[0]["kwargs"],
            {"status_by_state": {"ok": 0}, "default_status": 2},
        )

    def test_feedback_reclassify_apply_keeps_plan_confirm_and_backup(self) -> None:
        calls: list[dict[str, Any]] = []
        finish_calls: list[dict[str, Any]] = []

        def formatter(_report: dict[str, Any]) -> str:
            return "report"

        def builder(**kwargs: Any) -> dict[str, Any]:
            calls.append(kwargs)
            return {"state": "applied"}

        def finish(*args: Any, **kwargs: Any) -> int:
            finish_calls.append({"args": args, "kwargs": kwargs})
            return 23

        commands = (
            reclassify_dispatch.FeedbackReclassifyCommand(
                flag="feedback_reclassify_apply",
                builder=builder,
                formatter=formatter,
                status_by_state={"applied": 0},
                include_plan_path=True,
                include_confirm_token=True,
                include_backup_root=True,
            ),
        )
        args = SimpleNamespace(
            feedback_reclassify_apply=True,
            confirm="manual-evals-feedback-reclassify",
            plan_path="plans/reclassify.json",
            backup_root="backups",
        )

        with patch.object(
            reclassify_dispatch,
            "FEEDBACK_RECLASSIFY_COMMANDS",
            commands,
        ):
            status = reclassify_dispatch.handle_feedback_reclassify_command_group(
                args=args,
                db_path=Path("manual_evals.db"),
                finish=finish,
            )

        self.assertEqual(status, 23)
        self.assertEqual(
            calls,
            [
                {
                    "db_path": Path("manual_evals.db"),
                    "plan_path": Path("plans/reclassify.json"),
                    "confirm_token": "manual-evals-feedback-reclassify",
                    "backup_root": Path("backups"),
                }
            ],
        )
        self.assertEqual(finish_calls[0]["args"], ({"state": "applied"}, formatter))
        self.assertEqual(
            finish_calls[0]["kwargs"],
            {"status_by_state": {"applied": 0}, "default_status": 2},
        )


if __name__ == "__main__":
    unittest.main()
