import unittest

import tools.manual_eval_cli_contracts as contracts


class ManualEvalCliContractsTests(unittest.TestCase):
    def test_public_export_order_preserves_manual_eval_contract(self) -> None:
        self.assertEqual(
            contracts.__all__,
            [
                "ACTIONABLES_SCHEMA_VERSION",
                "COHORTS_SCHEMA_VERSION",
                "COHORT_DESCRIPTIONS",
                "COHORT_FILTER_CHOICES",
                "COHORT_IDS",
                "DEFAULT_DB_PATH",
                "DEFAULT_FEEDBACK_DECISION_PATH",
                "DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH",
                "DEFAULT_OVERLAY_SOURCE_CONTEXT_INDEX_PATH",
                "FEEDBACK_DECISION_ACTION_DESCRIPTIONS",
                "FEEDBACK_DECISION_ACTIONS",
                "FEEDBACK_DECISION_DRAFT_SCHEMA_VERSION",
                "FEEDBACK_DECISION_PREVIEW_SCHEMA_VERSION",
                "FEEDBACK_SOURCE_CONTEXT_SCHEMA_VERSION",
                "OCR_RETRY_CANDIDATES_SCHEMA_VERSION",
                "OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION",
                "OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION",
                "OCR_RETRY_EXECUTION_SCHEMA_VERSION",
                "OCR_RETRY_FEEDBACK_CLOSURE_WAREHOUSE_MUTATION_FIELD",
                "OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION",
                "OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION",
                "OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION",
                "OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION",
                "OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION",
                "OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION",
                "OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION",
                "OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION",
                "OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION",
                "OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION",
                "OCR_RETRY_TERMINAL_CONTEXT_LIMIT",
                "OVERLAY_OCR_COMPARISON_READINESS_SCHEMA_VERSION",
                "OVERLAY_SOURCE_CONTEXT_INDEX_DRAFT_SCHEMA_VERSION",
                "OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION",
                "OVERLAY_SOURCE_CONTEXT_INDEX_VALIDATION_SCHEMA_VERSION",
                "build_ocr_retry_selection_decision_draft_payload",
            ],
        )

    def test_public_exports_resolve_to_contract_values(self) -> None:
        for name in contracts.__all__:
            with self.subTest(name=name):
                self.assertTrue(hasattr(contracts, name))

    def test_shared_contract_values_preserve_manual_eval_defaults(self) -> None:
        self.assertEqual(
            str(contracts.DEFAULT_DB_PATH),
            ".local/runtime_dbs/active/manual_evals.db",
        )
        self.assertEqual(
            contracts.OCR_RETRY_FEEDBACK_CLOSURE_WAREHOUSE_MUTATION_FIELD,
            "manual_eval_warehouse",
        )


if __name__ == "__main__":
    unittest.main()
