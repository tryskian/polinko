import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class PolToolingDocsPinTests(unittest.TestCase):
    def test_governance_records_read_only_ocr_inventory_pin(self) -> None:
        decisions = _read("docs/governance/DECISIONS.md")
        normalized_decisions = " ".join(decisions.split())
        state = _read("docs/governance/STATE.md")
        charter = _read("docs/governance/CHARTER.md")

        self.assertIn(
            "## D-099: Pin OCR evidence tooling to read-only inventory before eval refresh",
            decisions,
        )
        for expected in (
            "`make ocr-inventory` and `make ocr-inventory-json` are the current OCR tooling pin",
            "without running OCR, launching browsers, writing eval rows, or mutating local databases",
            "read-only freshness states from existing `generated_at` metadata",
        ):
            self.assertIn(expected, normalized_decisions)

        for expected in (
            "live eval execution is pinned until an explicit resume decision",
            "current OCR work surface is read-only inventory plus guarded local-bundle",
            "OCR inventory freshness flags local case/report files",
        ):
            self.assertIn(expected, state)

        self.assertIn(
            "Use read-only inventory/status tooling before high-impact eval refreshes.",
            charter,
        )

    def test_runtime_docs_align_on_read_only_tooling_pin(self) -> None:
        expectations = {
            "docs/runtime/LOCAL_TOOLING.md": (
                "Read-only inventory and status tools are also local tooling.",
                "`make ocr-inventory-json`",
                "must not execute evals, run OCR, launch browsers, or mutate local data",
            ),
            "docs/runtime/RUNBOOK.md": (
                "Use read-only inventory/status tools before eval refreshes",
                "`make ocr-inventory-json`",
                "`FRESHNESS_DAYS=<days>`",
            ),
            "docs/runtime/OCR_REFERENCE.md": (
                "live eval execution is paused until explicitly resumed",
                "use `make ocr-inventory` and `make ocr-inventory-json`",
                "before any eval refresh while eval execution is pinned",
            ),
            "docs/runtime/ARCHITECTURE.md": (
                "read-only inventory/status tools for local evidence inspection",
                "read-only OCR inventory",
                "reports local evidence shape and freshness without eval execution",
            ),
            "docs/runtime/START_END_REFERENCE.md": (
                "Read-only tooling pin:",
                "`make ocr-inventory-json`",
                "`FRESHNESS_DAYS=<days>`",
            ),
            "docs/runtime/SURFACE_IA.md": (
                "Read-only OCR inventory is a tooling companion to the workbench",
                "`make ocr-inventory-json`",
                "without moving chat-facing routes or executing eval lanes",
            ),
            "docs/runtime/PACKAGE_BOUNDARY.md": (
                "`tools/report_ocr_lane_inventory.py`",
                "Local evidence inventory and operator tooling stay repo-local",
            ),
        }

        for path, expected_items in expectations.items():
            text = _read(path)
            normalized_text = " ".join(text.split())
            for expected in expected_items:
                self.assertIn(expected, normalized_text, path)


if __name__ == "__main__":
    unittest.main()
