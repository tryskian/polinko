import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _makefile_contract_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            REPO_ROOT / "Makefile",
            *sorted((REPO_ROOT / "makefiles").glob("**/*.mk")),
        ]
    )


class OcrRetryExecutionGateContractTests(unittest.TestCase):
    def test_execution_gate_documents_local_bundle_executor_boundary(self) -> None:
        design = _read("docs/runtime/OCR_RETRY_EXECUTION_GATE.md")
        normalized_design = " ".join(design.split())

        for expected in (
            "Status: `implemented-local-bundle`",
            "The OCR retry execution Make target exists only as a guarded local-bundle writer.",
            "`make manual-evals-ocr-retry-execute`",
            "`SELECTION_PATH=<path>`",
            "`CONFIRM=ocr-retry-execute`",
            "The command must recompute readiness inside the same process.",
            "`manual-evals-ocr-retry-execute` writes only ignored local run bundles.",
            "`make manual-evals-ocr-retry-execution-report`",
            "`RUN_DIR=<path>`",
            "`schema_version=polinko.manual_eval_ocr_retry_execution_report.v1`",
            "The report target is read-only.",
            "`make manual-evals-ocr-retry-feedback-closure-preview`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_preview.v1`",
            "The feedback-closure preview target is read-only.",
            "The feedback-closure apply target is implemented as a backup-first local warehouse writer.",
            "`make manual-evals-ocr-retry-feedback-closure-apply`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`",
            "`CONFIRM=ocr-retry-feedback-closure-apply`",
            "`make manual-evals-ocr-retry-feedback-closure-apply-report`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1`",
            "`make manual-evals-ocr-retry-feedback-closure-restore-preview`",
            "`make manual-evals-ocr-retry-feedback-closure-restore`",
            "`schema_version=polinko.manual_eval_ocr_retry_feedback_closure_restore.v1`",
            "`CONFIRM=ocr-retry-feedback-closure-restore`",
            ".local_archive/manual-evals-feedback-closure-apply-<timestamp>/",
            ".local_archive/manual-evals-feedback-closure-restore-<timestamp>/",
            "It must not write live eval rows, run OCR, refresh `manual_evals.db`",
            "whole-database rollback",
            "selection validation reports `state=ok`",
            "selection apply-preview reports `state=ok`",
            "execution readiness reports `state=ready`",
            "`context_only` decisions stay non-executing.",
            ".local/manual_eval_runs/ocr_retry/",
            "manual_evals.db",
            "Rollback Story",
            "Failure Handling",
            "Feedback closure, live eval writes, and warehouse mutation remain separate follow-up gates.",
        ):
            self.assertIn(expected, normalized_design)

        for forbidden in (
            "run OCR now",
            "close feedback now",
            "write live eval rows now",
        ):
            self.assertNotIn(forbidden, normalized_design)

    def test_runtime_and_governance_surfaces_link_execution_gate_design(self) -> None:
        expectations = {
            "docs/runtime/ARCHITECTURE.md": (
                "docs/runtime/OCR_RETRY_EXECUTION_GATE.md",
                "local-bundle OCR retry execution gate shape",
            ),
            "docs/runtime/LOCAL_TOOLING.md": (
                "docs/runtime/OCR_RETRY_EXECUTION_GATE.md",
                "local ignored run bundles",
            ),
            "docs/runtime/OCR_REFERENCE.md": (
                "docs/runtime/OCR_RETRY_EXECUTION_GATE.md",
                "local-bundle retry execution target exists",
            ),
            "docs/runtime/RUNBOOK.md": (
                "OCR retry execution",
                "make manual-evals-ocr-retry-execute",
                "make manual-evals-ocr-retry-execution-report",
                "make manual-evals-ocr-retry-feedback-closure-preview",
                "make manual-evals-ocr-retry-feedback-closure-apply",
                "make manual-evals-ocr-retry-feedback-closure-restore",
                "backup-first",
            ),
            "docs/governance/STATE.md": (
                "docs/runtime/OCR_RETRY_EXECUTION_GATE.md",
                "local-bundle OCR retry executor",
            ),
            "docs/governance/DECISIONS.md": (
                "## D-102: Implement OCR retry execution as a local bundle first",
                "The human lead approved the next kernel after the execution-gate design",
            ),
        }

        for path, expected_items in expectations.items():
            text = " ".join(_read(path).split())
            for expected in expected_items:
                self.assertIn(expected, text, path)

    def test_ocr_retry_execution_target_and_parser_flag_are_guarded(self) -> None:
        makefile_text = _makefile_contract_text()
        health_tool = _read("tools/manual_evals_db_health.py")

        self.assertIsNotNone(
            re.search(
                r"(?m)^manual-evals-ocr-retry-execute\s+manualdb-ocr-retry-execute:",
                makefile_text,
            )
        )
        self.assertIn("--ocr-retry-execute", health_tool)
        self.assertIn("--ocr-retry-execution-report", health_tool)
        self.assertIn("--ocr-retry-feedback-closure-preview", health_tool)
        self.assertIn("--ocr-retry-feedback-closure-apply", health_tool)
        self.assertIn("--ocr-retry-feedback-closure-apply-report", health_tool)
        self.assertIn("--ocr-retry-feedback-closure-restore-preview", health_tool)
        self.assertIn("--ocr-retry-feedback-closure-restore", health_tool)
        self.assertIn("OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION", health_tool)
        self.assertIn("OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION", health_tool)
        self.assertIn("OCR_RETRY_FEEDBACK_CLOSURE_APPLY_SCHEMA_VERSION", health_tool)
        self.assertIn(
            "OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_SCHEMA_VERSION",
            health_tool,
        )
        self.assertIn("OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_SCHEMA_VERSION", health_tool)
        self.assertIn("--confirm", health_tool)
        self.assertIn("OCR_RETRY_EXECUTION_CONFIRM_TOKEN", health_tool)
        self.assertIn("OCR_RETRY_FEEDBACK_CLOSURE_APPLY_CONFIRM_TOKEN", health_tool)
        self.assertIn("OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_CONFIRM_TOKEN", health_tool)
        self.assertIn("CONFIRM=ocr-retry-execute", health_tool)
        self.assertIn("CONFIRM=ocr-retry-feedback-closure-apply", health_tool)
        self.assertIn("CONFIRM=ocr-retry-feedback-closure-restore", health_tool)
        self.assertIn("manual_eval_warehouse", health_tool)
        self.assertIn("build_ocr_retry_execution_readiness_report", health_tool)
        self.assertIn(
            "manual-evals-ocr-retry-feedback-closure-apply",
            makefile_text,
        )
        self.assertIn(
            "manual-evals-ocr-retry-feedback-closure-apply-report",
            makefile_text,
        )
        self.assertIn(
            "manual-evals-ocr-retry-feedback-closure-restore-preview",
            makefile_text,
        )
        self.assertIn(
            "manual-evals-ocr-retry-feedback-closure-restore",
            makefile_text,
        )


if __name__ == "__main__":
    unittest.main()
