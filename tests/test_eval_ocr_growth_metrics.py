import os
import tempfile
import unittest
from pathlib import Path

from tools.eval_ocr_growth_metrics import CaseMetadata
from tools.eval_ocr_growth_metrics import RunReport
from tools.eval_ocr_growth_metrics import _collect_run_reports
from tools.eval_ocr_growth_metrics import build_growth_report


class OcrGrowthMetricsTests(unittest.TestCase):
    def test_build_growth_report_computes_pass_from_fail_metrics(self) -> None:
        case_map = {
            "c1": CaseMetadata(case_id="c1", lane="handwriting", source_name="c1.png", image_path="/tmp/c1.png"),
            "c2": CaseMetadata(case_id="c2", lane="typed", source_name="c2.png", image_path="/tmp/c2.png"),
            "c3": CaseMetadata(case_id="c3", lane="illustration", source_name="c3.png", image_path="/tmp/c3.png"),
        }
        runs = [
            RunReport(
                run_id="r1",
                timestamp=1000,
                case_statuses={"c1": "FAIL", "c2": "PASS", "c3": "FAIL"},
            ),
            RunReport(
                run_id="r2",
                timestamp=1100,
                case_statuses={"c1": "PASS", "c2": "PASS", "c3": "FAIL"},
            ),
        ]

        report = build_growth_report(case_map=case_map, run_reports=runs, now_epoch=2100)
        metrics = report["metrics"]
        self.assertEqual(report["runs_total"], 2)
        self.assertEqual(report["cases_total"], 3)
        self.assertEqual(metrics["first_pass_fail_rate"], 0.6667)
        self.assertEqual(metrics["fail_to_pass_conversion_rate"], 0.5)
        self.assertEqual(metrics["median_runs_to_pass"], 1.5)
        self.assertEqual(metrics["unresolved_fail_cases"], 1)
        self.assertEqual(metrics["unresolved_fail_age"], 0.306)

        lane_metrics = report["lane_metrics"]
        self.assertIn("handwriting", lane_metrics)
        self.assertEqual(lane_metrics["handwriting"]["fail_to_pass_conversion_rate"], 1.0)
        self.assertEqual(lane_metrics["illustration"]["unresolved_fail_cases"], 1)

    def test_collect_run_reports_filters_by_cases_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cases_a = tmp / "cases_a.json"
            cases_b = tmp / "cases_b.json"
            cases_a.write_text("{}", encoding="utf-8")
            cases_b.write_text("{}", encoding="utf-8")
            runs_dir = tmp / "runs"
            runs_dir.mkdir(parents=True, exist_ok=True)

            (runs_dir / "a.json").write_text(
                """
                {
                  "run_id": "r-a",
                  "generated_at": 100,
                  "cases_path": "cases_a.json",
                  "cases": [{"id": "c1", "status": "PASS"}]
                }
                """.strip(),
                encoding="utf-8",
            )
            (runs_dir / "b.json").write_text(
                """
                {
                  "run_id": "r-b",
                  "generated_at": 101,
                  "cases_path": "cases_b.json",
                  "cases": [{"id": "c1", "status": "FAIL"}]
                }
                """.strip(),
                encoding="utf-8",
            )

            previous_cwd = Path.cwd()
            try:
                # Matching uses cwd-relative resolution for report cases_path.
                # Keep cwd scoped to the temp fixture to avoid host-path coupling.
                os.chdir(tmp)
                rows = _collect_run_reports(runs_dir=runs_dir, expected_cases_path=cases_a.resolve())
            finally:
                os.chdir(previous_cwd)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].run_id, "r-a")
            self.assertEqual(rows[0].case_statuses["c1"], "PASS")


if __name__ == "__main__":
    unittest.main()
