import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from tools.manual_eval_cli_dispatch_support import default_filters, dispatch_first_match


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


if __name__ == "__main__":
    unittest.main()
