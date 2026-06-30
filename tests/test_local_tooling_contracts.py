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
            "Preview the application as a read-only would-apply step.",
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
            "browser state",
            "OCR execution state",
            "feedback status",
            "live eval rows",
            "manual eval warehouse state",
        ):
            self.assertIn(expected, contract)

        self.assertIn(
            "repo-local contract for Polinko's future operator tools. It stays inside this repo.",
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
            "`make manual-evals-ocr-retry-feedback-closure-apply`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`",
            "`CONFIRM=ocr-retry-feedback-closure-apply`",
            "`make manual-evals-ocr-retry-feedback-closure-apply-report`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1`",
            "backup-first warehouse copy",
            "`make manual-evals-feedback-decision-draft`",
            ".local/manual_eval_decisions/feedback_decision.json",
            "`schema_version=polinko.manual_eval_feedback_decision_draft.v1`",
            "`make manual-evals-feedback-decision-preview`",
            "`schema_version=polinko.manual_eval_feedback_decision_preview.v1`",
            "Manual Feedback Decision Packets",
            "`make manual-evals-overlay-comparison-readiness`",
            "`schema_version=polinko.manual_eval_overlay_ocr_comparison_readiness.v1`",
            "payload-only previews for a future overlay/OCR comparison lane",
            "`make manual-evals-overlay-source-index-draft`",
            "`schema_version=polinko.manual_eval_overlay_source_context_index_draft.v1`",
            "`make manual-evals-overlay-source-index-validate`",
            "`schema_version=polinko.manual_eval_overlay_source_context_index_validation.v1`",
            "`make manual-evals-ocr-retry-feedback-closure-restore-preview`",
            "`make manual-evals-ocr-retry-feedback-closure-restore`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_restore.v1`",
            "`CONFIRM=ocr-retry-feedback-closure-restore`",
            ".local_archive/manual-evals-feedback-closure-restore-<timestamp>/",
            "Future Polinko tooling should adopt the contract, not the OCR-specific",
        ):
            self.assertIn(expected, contract)

        self.assertIn(
            "Extract shared code only after repeated Polinko behavior proves",
            normalized_contract,
        )
        self.assertIn(
            "`keep_open` is the default evidence posture",
            normalized_contract,
        )
        self.assertIn(
            "until there is a real OCR comparison lane",
            normalized_contract,
        )

    def test_overlay_feedback_decision_pressure_is_documented(self) -> None:
        expectations = {
            "docs/runtime/LOCAL_TOOLING.md": (
                "overlay-assisted OCR hypothesis rows",
                "real OCR comparison lane",
            ),
            "docs/runtime/RUNBOOK.md": (
                "overlay-assisted OCR hypothesis rows",
                "exact OCR retry execution target",
            ),
            "docs/governance/STATE.md": (
                "overlay-assisted OCR hypothesis rows",
                "hypothesis pressure",
            ),
            "docs/governance/DECISIONS.md": (
                "## D-116: Treat overlay feedback decisions as evidence pressure",
                "Human-led: The human lead clarified",
            ),
        }

        for path, required_snippets in expectations.items():
            text = _read(path)
            normalized_text = " ".join(text.split())
            for snippet in required_snippets:
                self.assertIn(snippet, normalized_text, path)

    def test_overlay_comparison_readiness_is_documented(self) -> None:
        expectations = {
            "docs/eval/README.md": (
                "make manual-evals-overlay-comparison-readiness",
                "polinko.manual_eval_overlay_ocr_comparison_readiness.v1",
                "polinko.manual_eval_overlay_source_context_index.v1",
                "make manual-evals-overlay-source-index-draft",
                "polinko.manual_eval_overlay_source_context_index_validation.v1",
            ),
            "docs/runtime/LOCAL_TOOLING.md": (
                "`make manual-evals-overlay-comparison-readiness`",
                "OVERLAY_SOURCE_INDEX_PATH=<path>",
                "payload-only previews for a future overlay/OCR comparison lane",
                "`make manual-evals-overlay-source-index-draft`",
                "`make manual-evals-overlay-source-index-validate`",
            ),
            "docs/runtime/RUNBOOK.md": (
                "`make manual-evals-overlay-comparison-readiness`",
                "OVERLAY_SOURCE_INDEX_PATH=<path>",
                "before any OCR run, feedback closure, eval write, or warehouse mutation",
                "`make manual-evals-overlay-source-index-draft`",
                "`make manual-evals-overlay-source-index-validate`",
            ),
            "docs/governance/STATE.md": (
                "`make manual-evals-overlay-comparison-readiness`",
                "polinko.manual_eval_overlay_source_context_index.v1",
                "source-image candidates, exact blockers, and payload-only previews",
                "`make manual-evals-overlay-source-index-draft`",
                "polinko.manual_eval_overlay_source_context_index_validation.v1",
            ),
            "docs/governance/DECISIONS.md": (
                "## D-117: Add read-only overlay/OCR comparison readiness",
                "Human-led: The human lead carried forward the overlay experiment",
                "## D-118: Index overlay source context through local human input",
                "## D-119: Draft and validate overlay source indexes locally",
            ),
        }

        for path, required_snippets in expectations.items():
            text = _read(path)
            normalized_text = " ".join(text.split())
            for snippet in required_snippets:
                self.assertIn(snippet, normalized_text, path)

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
