import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from tools.manual_eval_cli_dispatch_support import (
    default_filters,
    dispatch_first_match,
    filtered_command_args,
    ocr_retry_command_args,
    ocr_retry_filters,
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


if __name__ == "__main__":
    unittest.main()
