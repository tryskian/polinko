import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class LocalToolingContractTests(unittest.TestCase):
    def test_local_tooling_contract_names_safe_operator_pattern(self) -> None:
        contract = _read("docs/runtime/LOCAL_TOOLING.md")
        normalized_contract = " ".join(contract.split())

        for expected in (
            "Local Tooling Contract",
            "Generate ignored local input.",
            "Validate that local input against current source truth.",
            "Preview the application without mutation.",
            "Execute only through a separate explicit follow-up gate.",
            "ignored default output path under `.local/`",
            "DRAFT_PATH=<path>",
            "SELECTION_PATH=<path>",
            "no-overwrite behavior by default",
            "`FORCE=1`",
            "deterministic `schema_version`",
            "source provenance or fingerprints",
            "validation command",
            "apply-preview command",
            "launch a browser",
            "run OCR",
            "close feedback",
            "write live eval rows",
            "mutate the manual eval warehouse",
        ):
            self.assertIn(expected, contract)

        self.assertIn(
            "repo-local contract for Polinko's future operator tools. It is not a shared package.",
            normalized_contract,
        )

    def test_local_tooling_contract_keeps_ocr_flow_as_instance_only(self) -> None:
        contract = _read("docs/runtime/LOCAL_TOOLING.md")
        normalized_contract = " ".join(contract.split())

        for expected in (
            "`make manual-evals-ocr-retry-selection-draft`",
            ".local/manual_eval_decisions/ocr_retry_selection_draft.json",
            "`schema_version=polinko.manual_eval_ocr_retry_selection_decision_draft.v1`",
            "`make manual-evals-ocr-retry-selection-validate`",
            "`make manual-evals-ocr-retry-selection-apply-preview`",
            "`make manual-evals-ocr-retry-execution-readiness`",
            "`schema_version=polinko.manual_eval_ocr_retry_execution_readiness.v1`",
            "`make manual-evals-ocr-retry-execute`",
            "`CONFIRM=ocr-retry-execute`",
            ".local/manual_eval_runs/ocr_retry/",
            "`make manual-evals-ocr-retry-execution-report`",
            "`RUN_DIR=<path>`",
            "`schema_version=polinko.manual_eval_ocr_retry_execution_report.v1`",
            "`make manual-evals-ocr-retry-feedback-closure-preview`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_preview.v1`",
            "Future Polinko tooling should adopt the contract, not the OCR-specific",
        ):
            self.assertIn(expected, contract)

        self.assertIn(
            "Extract shared code only after repeated Polinko behavior proves",
            normalized_contract,
        )

    def test_runtime_and_governance_surfaces_link_contract(self) -> None:
        expectations = {
            "docs/runtime/ARCHITECTURE.md": "docs/runtime/LOCAL_TOOLING.md",
            "docs/runtime/RUNBOOK.md": "docs/runtime/LOCAL_TOOLING.md",
            "docs/governance/STATE.md": "docs/runtime/LOCAL_TOOLING.md",
            "docs/governance/DECISIONS.md": (
                "## D-098: Name the reusable local tooling contract"
            ),
        }

        for path, expected in expectations.items():
            self.assertIn(expected, _read(path), path)

        decisions = _read("docs/governance/DECISIONS.md")
        normalized_decisions = " ".join(decisions.split())
        self.assertIn("Polinko-first tooling", normalized_decisions)
        self.assertIn("source-first manual eval workflows", decisions)

    def test_markdownlintignore_ignores_full_private_peanut_lane(self) -> None:
        markdownlintignore = _read(".markdownlintignore")

        self.assertIn("docs/peanut/**", markdownlintignore)
        self.assertNotIn("docs/peanut/transcripts/**", markdownlintignore)


if __name__ == "__main__":
    unittest.main()
