import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from tools import manual_evals_db_health as router


class ManualEvalCliRouterTests(unittest.TestCase):
    def test_main_preserves_router_order_and_health_fallback(self) -> None:
        calls: list[str] = []
        args = SimpleNamespace(db="manual_evals.db", json=False)

        def handler(name: str):
            def _handle(**_kwargs: Any) -> None:
                calls.append(name)

            return _handle

        with (
            patch.object(
                router,
                "_build_parser",
                return_value=SimpleNamespace(parse_args=lambda: args),
            ),
            patch.object(
                router,
                "handle_ocr_retry_pre_feedback_commands",
                handler("ocr_retry_pre_feedback"),
            ),
            patch.object(
                router,
                "handle_feedback_reclassify_commands",
                handler("feedback_reclassify"),
            ),
            patch.object(
                router,
                "handle_ocr_retry_post_feedback_commands",
                handler("ocr_retry_post_feedback"),
            ),
            patch.object(
                router,
                "handle_feedback_context_commands",
                handler("feedback_context"),
            ),
            patch.object(
                router,
                "build_manual_evals_health_report",
                return_value={"state": "ok"},
            ) as health_report,
            patch.object(
                router,
                "format_manual_evals_health_report",
                return_value="manual eval health",
            ) as health_formatter,
            patch.object(router, "_finish_report", return_value=17) as finish_report,
        ):
            status = router.main()

        self.assertEqual(status, 17)
        self.assertEqual(
            calls,
            [
                "ocr_retry_pre_feedback",
                "feedback_reclassify",
                "ocr_retry_post_feedback",
                "feedback_context",
            ],
        )
        health_report.assert_called_once_with(db_path=Path("manual_evals.db"))
        finish_report.assert_called_once_with(
            {"state": "ok"},
            health_formatter,
            json_output=False,
        )

    def test_main_short_circuits_on_first_router_match(self) -> None:
        calls: list[str] = []
        args = SimpleNamespace(db="manual_evals.db", json=True)

        def ocr_retry_pre_feedback_handler(**_kwargs: Any) -> None:
            calls.append("ocr_retry_pre_feedback")

        def feedback_reclassify_handler(**_kwargs: Any) -> int:
            calls.append("feedback_reclassify")
            return 23

        def ocr_retry_post_feedback_handler(**_kwargs: Any) -> None:
            calls.append("ocr_retry_post_feedback")

        with (
            patch.object(
                router,
                "_build_parser",
                return_value=SimpleNamespace(parse_args=lambda: args),
            ),
            patch.object(
                router,
                "handle_ocr_retry_pre_feedback_commands",
                ocr_retry_pre_feedback_handler,
            ),
            patch.object(
                router,
                "handle_feedback_reclassify_commands",
                feedback_reclassify_handler,
            ),
            patch.object(
                router,
                "handle_ocr_retry_post_feedback_commands",
                ocr_retry_post_feedback_handler,
            ),
            patch.object(
                router, "handle_feedback_context_commands"
            ) as feedback_context,
            patch.object(router, "build_manual_evals_health_report") as health_report,
        ):
            status = router.main()

        self.assertEqual(status, 23)
        self.assertEqual(calls, ["ocr_retry_pre_feedback", "feedback_reclassify"])
        feedback_context.assert_not_called()
        health_report.assert_not_called()

    def test_router_gate_contract_markers_stay_explicit(self) -> None:
        self.assertEqual(
            router._CLI_GATE_CONTRACT_MARKERS,  # noqa: SLF001 - contract marker tuple.
            (
                "--ocr-retry-execute",
                "--ocr-retry-execution-report",
                "--ocr-retry-feedback-closure-preview",
                "--ocr-retry-feedback-closure-apply",
                "--ocr-retry-feedback-closure-apply-report",
                "--ocr-retry-feedback-closure-restore-preview",
                "--ocr-retry-feedback-closure-restore",
                "OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION",
                "OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION",
                "OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION",
                "OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION",
                "OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION",
                "--confirm",
                "OCR_RETRY_EXECUTION_CONFIRM_TOKEN",
                "OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN",
                "OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN",
                "CONFIRM=ocr-retry-execute",
                "CONFIRM=ocr-retry-feedback-closure-apply",
                "CONFIRM=ocr-retry-feedback-closure-restore",
                "manual_eval_warehouse",
                "build_ocr_retry_execution_readiness_report",
            ),
        )


if __name__ == "__main__":
    unittest.main()
