import unittest

from tools.manual_eval_cli_parser import build_manual_evals_db_health_parser


class ManualEvalCliParserTests(unittest.TestCase):
    def test_parser_option_order_preserves_manual_eval_surface_contract(self) -> None:
        parser = build_manual_evals_db_health_parser()

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


if __name__ == "__main__":
    unittest.main()
