import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.report_ocr_lane_inventory import (
    SCHEMA_VERSION,
    build_inventory,
    format_inventory,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _by_name(items: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(item["name"]): item for item in items}


class OcrLaneInventoryTests(unittest.TestCase):
    def test_inventory_reports_tracked_and_local_ocr_paths_without_mutation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            tracked_dir = root / "docs" / "eval" / "beta_2_0"
            local_cases_dir = root / ".local" / "eval_cases"
            notebook_dir = root / ".local" / "notebooks"
            tracked_dir.mkdir(parents=True)
            local_cases_dir.mkdir(parents=True)
            notebook_dir.mkdir(parents=True)
            (tracked_dir / "ocr_eval_cases.json").write_text(
                json.dumps({"cases": [{"id": "base-1"}, {"id": "base-2"}]}),
                encoding="utf-8",
            )
            (local_cases_dir / "ocr_transcript_cases_all.json").write_text(
                json.dumps([{"id": "local-1"}]),
                encoding="utf-8",
            )
            (local_cases_dir / "ocr_typed_from_transcripts.json").write_bytes(
                b"\x8dnot-json"
            )

            with patch.dict(os.environ, {}, clear=True):
                inventory = build_inventory(root=root)

        self.assertEqual(inventory["schema_version"], SCHEMA_VERSION)

        tracked_cases = _by_name(inventory["tracked_cases"])
        self.assertEqual(
            tracked_cases["base_ocr_cases"]["path"],
            "docs/eval/beta_2_0/ocr_eval_cases.json",
        )
        self.assertEqual(tracked_cases["base_ocr_cases"]["kind"], "file")
        self.assertEqual(tracked_cases["base_ocr_cases"]["rows"], 2)

        local_cases = _by_name(inventory["local_cases"])
        self.assertEqual(
            local_cases["transcript_all"]["path"],
            ".local/eval_cases/ocr_transcript_cases_all.json",
        )
        self.assertEqual(local_cases["transcript_all"]["rows"], 1)
        self.assertEqual(local_cases["typed"]["kind"], "file")
        self.assertNotIn("rows", local_cases["typed"])

        notebooks = _by_name(inventory["notebooks"])
        self.assertEqual(notebooks["notebook_dir"]["path"], ".local/notebooks")
        self.assertEqual(
            notebooks["notebook_start"]["path"],
            ".local/notebooks/ocr-eval-live-filters-starter.ipynb",
        )

        output = format_inventory(inventory)
        self.assertIn("OCR lane inventory: polinko.ocr_lane_inventory.v1", output)
        self.assertIn("tracked cases", output)
        self.assertIn("manual eval sources", output)
        self.assertIn(".local/notebooks", output)

    def test_local_notebook_lane_is_ignored(self) -> None:
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn(".local/notebooks/", gitignore)


if __name__ == "__main__":
    unittest.main()
