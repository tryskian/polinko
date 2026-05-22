import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
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
            local_reports_dir = root / ".local" / "eval_reports"
            notebook_dir = root / ".local" / "notebooks"
            tracked_dir.mkdir(parents=True)
            local_cases_dir.mkdir(parents=True)
            local_reports_dir.mkdir(parents=True)
            notebook_dir.mkdir(parents=True)
            (tracked_dir / "ocr_eval_cases.json").write_text(
                json.dumps({"cases": [{"id": "base-1"}, {"id": "base-2"}]}),
                encoding="utf-8",
            )
            (local_cases_dir / "ocr_transcript_cases_all.json").write_text(
                json.dumps([{"id": "local-1"}]),
                encoding="utf-8",
            )
            (local_cases_dir / "ocr_generalization_review.json").write_text(
                json.dumps(
                    {
                        "schema_version": "polinko.test_review.v1",
                        "generated_at": "2026-05-21T20:00:00Z",
                        "selected_candidates": [
                            {"id": "candidate-1"},
                            {"id": "candidate-2"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (local_cases_dir / "ocr_typed_from_transcripts.json").write_bytes(
                b"\x8dnot-json"
            )
            (local_reports_dir / "ocr_growth_metrics.json").write_text(
                json.dumps(
                    {
                        "generated_at": "2026-05-01T20:00:00Z",
                        "cases": [{"id": "old-1"}],
                    }
                ),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                inventory = build_inventory(
                    root=root,
                    now=datetime(2026, 5, 22, 20, 0, tzinfo=timezone.utc),
                    freshness_days=7,
                )

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
        self.assertEqual(local_cases["generalization_review"]["json_shape"], "object")
        self.assertEqual(
            local_cases["generalization_review"]["source_schema_version"],
            "polinko.test_review.v1",
        )
        self.assertEqual(local_cases["generalization_review"]["rows"], 2)
        self.assertEqual(
            local_cases["generalization_review"]["row_source"],
            "selected_candidates",
        )
        self.assertEqual(
            local_cases["generalization_review"]["list_counts"],
            {"selected_candidates": 2},
        )
        self.assertEqual(
            local_cases["generalization_review"]["freshness_state"],
            "current",
        )
        self.assertEqual(local_cases["generalization_review"]["age_days"], 1.0)

        local_reports = _by_name(inventory["local_reports"])
        self.assertEqual(local_reports["growth_metrics"]["freshness_state"], "stale")
        self.assertEqual(local_reports["growth_metrics"]["age_days"], 21.0)
        self.assertEqual(
            local_reports["growth_metrics"]["freshness_reason"],
            "generated_at_older_than_threshold",
        )

        freshness = inventory["freshness"]
        stale_names = {item["name"] for item in freshness["stale_items"]}
        current_names = {item["name"] for item in freshness["current_items"]}
        unknown_names = {item["name"] for item in freshness["unknown_items"]}

        self.assertEqual(freshness["threshold_days"], 7)
        self.assertIn("growth_metrics", stale_names)
        self.assertIn("generalization_review", current_names)
        self.assertIn("transcript_all", unknown_names)

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
        self.assertIn("freshness", output)
        self.assertIn("stale=1", output)
        self.assertIn("stale: local_reports/growth_metrics", output)
        self.assertIn(".local/notebooks", output)
        self.assertIn("row_source=selected_candidates", output)
        self.assertIn("freshness=current", output)

    def test_local_notebook_lane_is_ignored(self) -> None:
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn(".local/notebooks/", gitignore)
        self.assertIn(".local/manual_eval_decisions/", gitignore)
        self.assertIn(".local/manual_eval_runs/", gitignore)


if __name__ == "__main__":
    unittest.main()
