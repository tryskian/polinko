import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    default_filters,
    dispatch_first_match,
    filtered_command_args,
    filtered_report_kwargs,
    finish_report_with_error_default,
    first_enabled_command,
    local_artifact_paths,
    ocr_retry_command_args,
    ocr_retry_filters,
    ocr_retry_report_kwargs,
)


class ManualEvalCliDispatchSupportTests(unittest.TestCase):
    def test_dispatch_first_match_preserves_order_and_short_circuits(self) -> None:
        calls: list[str] = []

        def handler(name: str, status: int | None):
            def _handle(**_kwargs: Any) -> int | None:
                calls.append(name)
                return status

            return _handle

        status = dispatch_first_match(
            handlers=(
                handler("first", None),
                handler("second", 9),
                handler("third", 11),
            ),
            args=object(),
            db_path=Path("manual_evals.db"),
            finish=lambda *_args, **_kwargs: 0,
        )

        self.assertEqual(status, 9)
        self.assertEqual(calls, ["first", "second"])

    def test_dispatch_first_match_returns_none_when_no_handler_matches(self) -> None:
        calls: list[str] = []

        def handler(name: str):
            def _handle(**_kwargs: Any) -> None:
                calls.append(name)

            return _handle

        status = dispatch_first_match(
            handlers=(handler("first"), handler("second")),
            args=object(),
            db_path=Path("manual_evals.db"),
            finish=lambda *_args, **_kwargs: 0,
        )

        self.assertIsNone(status)
        self.assertEqual(calls, ["first", "second"])

    def test_first_enabled_command_preserves_order_and_short_circuits(self) -> None:
        commands = (
            SimpleNamespace(flag="first"),
            SimpleNamespace(flag="second"),
            SimpleNamespace(flag="third"),
        )

        command = first_enabled_command(
            args=SimpleNamespace(first=False, second=True, third=True),
            commands=commands,
        )

        self.assertIs(command, commands[1])

    def test_first_enabled_command_returns_none_when_no_flag_matches(self) -> None:
        command = first_enabled_command(
            args=SimpleNamespace(first=False, second=False),
            commands=(
                SimpleNamespace(flag="first"),
                SimpleNamespace(flag="second"),
            ),
        )

        self.assertIsNone(command)

    def test_first_enabled_command_keeps_missing_flag_errors_loud(self) -> None:
        with self.assertRaises(AttributeError):
            first_enabled_command(
                args=SimpleNamespace(first=False),
                commands=(
                    SimpleNamespace(flag="first"),
                    SimpleNamespace(flag="missing"),
                ),
            )

    def test_finish_report_with_error_default_uses_shared_default_status(self) -> None:
        calls: list[dict[str, Any]] = []
        report = {"state": "blocked"}

        def finish(*args: Any, **kwargs: Any) -> int:
            calls.append({"args": args, "kwargs": kwargs})
            return 2

        status = finish_report_with_error_default(
            finish=finish,
            report=report,
            formatter=str,
            status_by_state={"ok": 0},
        )

        self.assertEqual(status, 2)
        self.assertEqual(calls[0]["args"], (report, str))
        self.assertEqual(
            calls[0]["kwargs"],
            {"status_by_state": {"ok": 0}, "default_status": 2},
        )

    def test_default_filters_uses_command_family_defaults_for_blank_args(self) -> None:
        filters = default_filters(
            SimpleNamespace(outcome="", cohort=None),
            outcome="partial",
            cohort="ocr_retry_evidence",
        )

        self.assertEqual(filters.outcome, "partial")
        self.assertEqual(filters.cohort, "ocr_retry_evidence")

    def test_default_filters_preserves_explicit_args(self) -> None:
        filters = default_filters(
            SimpleNamespace(outcome="fail", cohort="ocr_overlay_hypothesis"),
            outcome="partial",
            cohort="ocr_retry_evidence",
        )

        self.assertEqual(filters.outcome, "fail")
        self.assertEqual(filters.cohort, "ocr_overlay_hypothesis")

    def test_ocr_retry_filters_use_retry_command_defaults(self) -> None:
        filters = ocr_retry_filters(SimpleNamespace(outcome="", cohort=None))

        self.assertEqual(filters.outcome, "partial")
        self.assertEqual(filters.cohort, "ocr_retry_evidence")

    def test_ocr_retry_filters_preserve_explicit_overrides(self) -> None:
        filters = ocr_retry_filters(
            SimpleNamespace(outcome="fail", cohort="grounding_source_verification"),
        )

        self.assertEqual(filters.outcome, "fail")
        self.assertEqual(filters.cohort, "grounding_source_verification")

    def test_filtered_command_args_use_family_defaults_and_positive_limit(self) -> None:
        command_args = filtered_command_args(
            SimpleNamespace(outcome="", cohort=None, limit=0),
            outcome="fail",
            cohort="grounding_source_verification",
        )

        self.assertEqual(command_args.outcome, "fail")
        self.assertEqual(command_args.cohort, "grounding_source_verification")
        self.assertEqual(command_args.limit, 1)

    def test_filtered_command_args_preserve_explicit_filters_and_limit(self) -> None:
        command_args = filtered_command_args(
            SimpleNamespace(
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=25,
            ),
            outcome="fail",
            cohort="grounding_source_verification",
        )

        self.assertEqual(command_args.outcome, "partial")
        self.assertEqual(command_args.cohort, "ocr_retry_evidence")
        self.assertEqual(command_args.limit, 25)

    def test_filtered_report_kwargs_use_family_defaults_and_positive_limit(
        self,
    ) -> None:
        kwargs = filtered_report_kwargs(
            SimpleNamespace(outcome="", cohort=None, limit=0),
            outcome="fail",
            cohort="grounding_source_verification",
        )

        self.assertEqual(
            kwargs,
            {
                "outcome": "fail",
                "cohort": "grounding_source_verification",
                "limit": 1,
            },
        )

    def test_filtered_report_kwargs_preserve_explicit_filters_and_limit(self) -> None:
        kwargs = filtered_report_kwargs(
            SimpleNamespace(
                outcome="partial",
                cohort="ocr_retry_evidence",
                limit=25,
            ),
            outcome="fail",
            cohort="grounding_source_verification",
        )

        self.assertEqual(
            kwargs,
            {
                "outcome": "partial",
                "cohort": "ocr_retry_evidence",
                "limit": 25,
            },
        )

    def test_local_artifact_paths_normalize_blank_and_missing_values(self) -> None:
        paths = local_artifact_paths(
            SimpleNamespace(
                backup_dir="",
                output_path="  ",
                run_dir=None,
                selection_path="selection.json",
            ),
        )

        self.assertIsNone(paths.backup_dir)
        self.assertIsNone(paths.backup_root)
        self.assertIsNone(paths.output_path)
        self.assertIsNone(paths.run_dir)
        self.assertEqual(paths.selection_path, Path("selection.json"))

    def test_local_artifact_paths_preserve_explicit_paths(self) -> None:
        paths = local_artifact_paths(
            SimpleNamespace(
                backup_dir="backups/apply",
                backup_root="backups",
                decision_path="decisions/feedback.json",
                execution_dir="runs",
                output_path="drafts/selection.json",
                overlay_source_index="overlay/index.json",
                plan_path="plans/reclassify.json",
                restore_root="restores",
                run_dir="runs/run-1",
                selection_path="selections/review.json",
            ),
        )

        self.assertEqual(paths.backup_dir, Path("backups/apply"))
        self.assertEqual(paths.backup_root, Path("backups"))
        self.assertEqual(paths.decision_path, Path("decisions/feedback.json"))
        self.assertEqual(paths.execution_dir, Path("runs"))
        self.assertEqual(paths.output_path, Path("drafts/selection.json"))
        self.assertEqual(paths.overlay_source_index_path, Path("overlay/index.json"))
        self.assertEqual(paths.plan_path, Path("plans/reclassify.json"))
        self.assertEqual(paths.restore_root, Path("restores"))
        self.assertEqual(paths.run_dir, Path("runs/run-1"))
        self.assertEqual(paths.selection_path, Path("selections/review.json"))

    def test_ocr_retry_command_args_use_retry_defaults(self) -> None:
        command_args = ocr_retry_command_args(
            SimpleNamespace(outcome="", cohort=None, limit=0, artifact_id=[]),
        )

        self.assertEqual(command_args.outcome, "partial")
        self.assertEqual(command_args.cohort, "ocr_retry_evidence")
        self.assertEqual(command_args.limit, 1)
        self.assertEqual(command_args.artifact_ids, [])

    def test_ocr_retry_command_args_preserve_explicit_args(self) -> None:
        command_args = ocr_retry_command_args(
            SimpleNamespace(
                outcome="fail",
                cohort="grounding_source_verification",
                limit=12,
                artifact_id=["artifact-a", "artifact-b"],
            ),
        )

        self.assertEqual(command_args.outcome, "fail")
        self.assertEqual(command_args.cohort, "grounding_source_verification")
        self.assertEqual(command_args.limit, 12)
        self.assertEqual(command_args.artifact_ids, ["artifact-a", "artifact-b"])

    def test_ocr_retry_report_kwargs_use_retry_defaults_without_artifacts(
        self,
    ) -> None:
        kwargs = ocr_retry_report_kwargs(
            SimpleNamespace(outcome="", cohort=None, limit=0, artifact_id=[]),
        )

        self.assertEqual(
            kwargs,
            {
                "outcome": "partial",
                "cohort": "ocr_retry_evidence",
                "limit": 1,
            },
        )

    def test_ocr_retry_report_kwargs_can_include_artifacts(self) -> None:
        kwargs = ocr_retry_report_kwargs(
            SimpleNamespace(
                outcome="fail",
                cohort="grounding_source_verification",
                limit=12,
                artifact_id=["artifact-a", "artifact-b"],
            ),
            include_artifact_ids=True,
        )

        self.assertEqual(
            kwargs,
            {
                "outcome": "fail",
                "cohort": "grounding_source_verification",
                "limit": 12,
                "artifact_ids": ["artifact-a", "artifact-b"],
            },
        )


if __name__ == "__main__":
    unittest.main()
