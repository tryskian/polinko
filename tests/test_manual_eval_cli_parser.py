import unittest
from collections.abc import Callable

from tools import manual_eval_cli_parser


class ManualEvalCliParserTests(unittest.TestCase):
    def test_parser_option_order_preserves_manual_eval_surface_contract(self) -> None:
        parser = manual_eval_cli_parser.build_manual_evals_db_health_parser()

        option_order = [
            action.option_strings[0]
            for action in parser._actions  # noqa: SLF001 - argparse exposes no public ordered action list.
            if action.option_strings and action.option_strings[0] != "-h"
        ]

        self.assertEqual(
            option_order,
            [
                "--db",
                "--json",
                "--open-feedback-actionables",
                "--open-feedback-cohorts",
                "--feedback-source-context",
                "--feedback-decision-preview",
                "--feedback-decision-draft",
                "--overlay-ocr-comparison-readiness",
                "--overlay-source-index-draft",
                "--overlay-source-index-validate",
                "--overlay-source-index",
                "--ocr-retry-candidates",
                "--ocr-retry-source-verification",
                "--ocr-retry-source-provenance",
                "--ocr-retry-input-packet",
                "--ocr-retry-rerun-manifest",
                "--ocr-retry-rerun-plan",
                "--ocr-retry-selection-review",
                "--ocr-retry-selection-template",
                "--ocr-retry-selection-draft",
                "--ocr-retry-selection-validate",
                "--ocr-retry-selection-apply-preview",
                "--ocr-retry-execution-readiness",
                "--ocr-retry-execute",
                "--ocr-retry-execution-report",
                "--ocr-retry-feedback-closure-preview",
                "--ocr-retry-feedback-closure-apply",
                "--ocr-retry-feedback-closure-apply-report",
                "--ocr-retry-feedback-closure-restore-preview",
                "--ocr-retry-feedback-closure-restore",
                "--no-context-feedback-reclassify-preview",
                "--no-context-feedback-reclassify-apply",
                "--feedback-reclassify-preview",
                "--feedback-reclassify-apply",
                "--plan-path",
                "--decision-path",
                "--selection-path",
                "--confirm",
                "--execution-dir",
                "--run-dir",
                "--backup-root",
                "--backup-dir",
                "--restore-root",
                "--ocr-provider",
                "--ocr-model",
                "--ocr-prompt",
                "--output-path",
                "--force",
                "--artifact-id",
                "--outcome",
                "--cohort",
                "--limit",
            ],
        )

    def test_parser_build_uses_argument_family_builders_in_order(self) -> None:
        calls: list[str] = []

        def record(name: str) -> Callable[[object], None]:
            def _record(_parser: object) -> None:
                calls.append(name)

            return _record

        originals = {
            name: getattr(manual_eval_cli_parser, name)
            for name in (
                "add_common_report_args",
                "add_feedback_context_args",
                "add_ocr_retry_args",
                "add_feedback_reclassify_args",
                "add_local_artifact_args",
                "add_ocr_execution_args",
                "add_output_filter_args",
            )
        }
        try:
            for name in originals:
                setattr(manual_eval_cli_parser, name, record(name))

            manual_eval_cli_parser.build_manual_evals_db_health_parser()
        finally:
            for name, original in originals.items():
                setattr(manual_eval_cli_parser, name, original)

        self.assertEqual(
            calls,
            [
                "add_common_report_args",
                "add_feedback_context_args",
                "add_ocr_retry_args",
                "add_feedback_reclassify_args",
                "add_local_artifact_args",
                "add_ocr_execution_args",
                "add_output_filter_args",
            ],
        )


if __name__ == "__main__":
    unittest.main()
