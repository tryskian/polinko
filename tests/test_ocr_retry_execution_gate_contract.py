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
            *sorted((REPO_ROOT / "makefiles").glob("*.mk")),
            *sorted((REPO_ROOT / "makefiles" / "config").glob("*.mk")),
            *sorted((REPO_ROOT / "makefiles" / "evals").glob("*.mk")),
        ]
    )


class OcrRetryExecutionGateContractTests(unittest.TestCase):
    def test_execution_gate_design_is_documented_but_not_runnable(self) -> None:
        design = _read("docs/runtime/OCR_RETRY_EXECUTION_GATE.md")
        normalized_design = " ".join(design.split())

        for expected in (
            "Status: `designed-only`",
            "No OCR retry execution Make target exists yet.",
            "`make manual-evals-ocr-retry-execute`",
            "`SELECTION_PATH=<path>`",
            "`CONFIRM=ocr-retry-execute`",
            "The command must recompute readiness inside the same process.",
            "selection validation reports `state=ok`",
            "selection apply-preview reports `state=ok`",
            "execution readiness reports `state=ready`",
            "`context_only` decisions stay non-executing.",
            ".local/manual_eval_runs/ocr_retry/",
            "manual_evals.db",
            "Rollback Story",
            "Failure Handling",
            "Until those tests and the command exist, OCR retry execution remains designed but not runnable.",
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
                "designed-only OCR retry execution gate shape",
            ),
            "docs/runtime/LOCAL_TOOLING.md": (
                "docs/runtime/OCR_RETRY_EXECUTION_GATE.md",
                "It is not runnable yet.",
            ),
            "docs/runtime/OCR_REFERENCE.md": (
                "docs/runtime/OCR_RETRY_EXECUTION_GATE.md",
                "no runnable retry execution target exists yet",
            ),
            "docs/runtime/RUNBOOK.md": (
                "OCR retry execution gate design",
                "no runnable OCR retry execution target exists yet",
            ),
            "docs/governance/STATE.md": (
                "docs/runtime/OCR_RETRY_EXECUTION_GATE.md",
                "no runnable retry execution target exists yet",
            ),
            "docs/governance/DECISIONS.md": (
                "## D-101: Design OCR retry execution before implementation",
                "The human lead confirmed the next kernel should still not run evals",
            ),
        }

        for path, expected_items in expectations.items():
            text = " ".join(_read(path).split())
            for expected in expected_items:
                self.assertIn(expected, text, path)

    def test_no_ocr_retry_execution_target_or_parser_flag_exists_yet(self) -> None:
        makefile_text = _makefile_contract_text()
        health_tool = _read("tools/manual_evals_db_health.py")

        self.assertIsNone(
            re.search(
                r"(?m)^manual-evals-ocr-retry-execute\s+manualdb-ocr-retry-execute:",
                makefile_text,
            )
        )
        self.assertNotIn("--ocr-retry-execute", health_tool)
        self.assertNotIn("ocr_retry_execute", health_tool)


if __name__ == "__main__":
    unittest.main()
