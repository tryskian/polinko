import json
import tempfile
import unittest
from pathlib import Path

from api.eval_viz import build_pass_fail_viz_payload, render_pass_fail_viz_html


class EvalVizTests(unittest.TestCase):
    def test_payload_uses_latest_report_and_builds_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            stability_dir = root / "ocr_stability_runs"
            growth_dir = root / "ocr_growth_stability_runs"
            stability_dir.mkdir(parents=True, exist_ok=True)
            growth_dir.mkdir(parents=True, exist_ok=True)

            first = {
                "run_id": "1711000000-r1",
                "summary": {"passed": 2, "failed": 1, "errors": 0, "attempted": 3},
                "cases": [],
            }
            second = {
                "run_id": "1711003600-r1",
                "summary": {"passed": 4, "failed": 2, "errors": 0, "attempted": 6},
                "cases": [
                    {
                        "id": "case-a",
                        "status": "pass",
                        "must_contain": ["alpha"],
                        "must_contain_any": ["beta", "gamma"],
                        "must_appear_in_order": ["one", "two"],
                        "must_match_regex": [r"\\d+"],
                        "extracted_text": "alpha and beta",
                        "source_name": "sample-a.png",
                        "image_path": "/tmp/sample-a.png",
                    }
                ],
            }

            (stability_dir / "1711000000-r1.json").write_text(json.dumps(first), encoding="utf-8")
            (growth_dir / "1711003600-r1.json").write_text(json.dumps(second), encoding="utf-8")

            payload = build_pass_fail_viz_payload(report_root=root, max_evals=10)
            self.assertEqual(payload["runs_total"], 2)
            self.assertEqual(payload["summary"]["run_id"], "1711003600-r1")
            self.assertEqual(payload["summary"]["pass"], 4)
            self.assertEqual(payload["summary"]["fail"], 2)
            self.assertEqual(len(payload["evals"]), 1)
            row = payload["evals"][0]
            self.assertEqual(row["item"], "case-a")
            self.assertEqual(row["outcome"], "PASS")
            self.assertIn("contain: alpha", row["expected"])
            self.assertIn("contain any: beta | gamma", row["expected"])
            self.assertIn("ordered: one -> two", row["expected"])
            self.assertIn("regex: \\\\d+", row["expected"])
            self.assertEqual(row["observed"], "alpha and beta")
            self.assertTrue(row["row_key"].startswith("case-a::"))

    def test_payload_without_reports_has_safe_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload = build_pass_fail_viz_payload(report_root=Path(tmp_dir))
            self.assertEqual(payload["runs_total"], 0)
            self.assertEqual(payload["summary"]["pass"], 0)
            self.assertEqual(payload["summary"]["fail"], 0)
            self.assertEqual(payload["evals"], [])

    def test_html_contains_separate_table_panel_and_detail_pane(self) -> None:
        html = render_pass_fail_viz_html(refresh_ms=2500, chart_max_points=20)
        self.assertIn('class="chart-wrap"', html)
        self.assertIn('class="table-wrap-panel"', html)
        self.assertIn('id="evalRows"', html)
        self.assertIn('id="detailCard"', html)
        self.assertIn('id="chartPoints"', html)
        self.assertIn('id="chartPointSelect"', html)
        self.assertIn("click persists", html)
        self.assertIn("const REFRESH_MS = 2500;", html)
        self.assertIn("const DEFAULT_MAX_CHART_POINTS = 20;", html)


if __name__ == "__main__":
    unittest.main()
