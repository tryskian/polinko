from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.build_eval_dashboard import build_dashboard_dataset
from tools.build_eval_dashboard import build_eval_dashboard


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class BuildEvalDashboardTests(unittest.TestCase):
    def test_build_dataset_uses_latest_report_and_extracts_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_dir = root / "eval_reports"

            _write_json(
                report_dir / "retrieval-20260329-100000.json",
                {
                    "run_id": "20260329-100000",
                    "summary": {"total": 1, "passed": 0, "failed": 1, "errors": 0},
                    "cases": [
                        {
                            "id": "old-case",
                            "status": "FAIL",
                            "query": "old query",
                            "must_include": ["old"],
                            "detail": "old detail",
                        }
                    ],
                },
            )
            _write_json(
                report_dir / "retrieval-20260329-110000.json",
                {
                    "run_id": "20260329-110000",
                    "summary": {"total": 1, "passed": 1, "failed": 0, "errors": 0},
                    "cases": [
                        {
                            "id": "ret-1",
                            "status": "PASS",
                            "query": "find notes about manifold",
                            "must_include": ["manifold", "notes"],
                            "detail": "global recall + session isolation",
                            "seed_session": "seed-s1",
                            "target_session": "target-s1",
                        }
                    ],
                },
            )
            _write_json(
                report_dir / "ocr-20260329-120000.json",
                {
                    "run_id": "20260329-120000",
                    "summary": {"total": 1, "passed": 1, "failed": 0, "errors": 0},
                    "cases": [
                        {
                            "id": "ocr-1",
                            "status": "PASS",
                            "source_name": "IMG_9141.jpg",
                            "image_path": "/tmp/IMG_9141.jpg",
                            "transcription_mode": "verbatim",
                            "extracted_text": "The shapes have returned: 26.",
                            "session_id": "ocr-session-1",
                        }
                    ],
                },
            )

            dataset = build_dashboard_dataset(
                report_dir=report_dir,
                db_path=root / ".local/runtime_dbs/active/history.db",
                max_cases_per_suite=100,
            )

            retrieval_suite = next(item for item in dataset["suites"] if item["suite"] == "retrieval")
            self.assertEqual(retrieval_suite["run_id"], "20260329-110000")
            self.assertEqual(retrieval_suite["summary"]["passed"], 1)

            retrieval_case = next(item for item in dataset["cases"] if item["suite"] == "retrieval")
            self.assertIn("find notes about manifold", retrieval_case["tested_value"])
            self.assertIn("session:seed-s1", retrieval_case["references"])
            self.assertIn("session:target-s1", retrieval_case["references"])

            ocr_case = next(item for item in dataset["cases"] if item["suite"] == "ocr")
            self.assertIn("/tmp/IMG_9141.jpg", ocr_case["references"])
            self.assertIn("source:IMG_9141.jpg", ocr_case["references"])
            self.assertIn("The shapes have returned", ocr_case["outcome_summary"])

    def test_runtime_overview_marks_missing_db_as_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_dir = root / "eval_reports"
            _write_json(
                report_dir / "style-20260329-130000.json",
                {
                    "run_id": "20260329-130000",
                    "summary": {"total": 1, "passed": 1, "failed": 0},
                    "cases": [{"id": "style-1", "status": "PASS", "query": "x", "answer": "y"}],
                },
            )
            dataset = build_dashboard_dataset(
                report_dir=report_dir,
                db_path=root / ".local/runtime_dbs/active/history.db",
                max_cases_per_suite=20,
            )
            self.assertFalse(dataset["runtime"]["available"])
            self.assertIn("not found", dataset["runtime"]["error"].lower())

    def test_build_eval_dashboard_writes_html_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_dir = root / "eval_reports"
            _write_json(
                report_dir / "hallucination-20260329-140000.json",
                {
                    "run_id": "20260329-140000",
                    "total_cases": 1,
                    "passed": 1,
                    "failed": 0,
                    "cases": [{"id": "hall-1", "pass": True, "answer": "grounded answer", "risk": "low"}],
                },
            )
            output_html = root / ".local/dashboard/eval_dashboard.html"
            output_json = root / ".local/dashboard/eval_dashboard.json"
            dataset = build_eval_dashboard(
                report_dir=report_dir,
                db_path=root / ".local/runtime_dbs/active/history.db",
                output_html=output_html,
                output_json=output_json,
                max_cases_per_suite=50,
            )

            self.assertTrue(output_html.exists())
            self.assertTrue(output_json.exists())
            html = output_html.read_text(encoding="utf-8")
            self.assertIn("Eval Dashboard", html)
            self.assertIn("hall-1", html)
            self.assertEqual(dataset["overview"]["suite_count"], 1)


if __name__ == "__main__":
    unittest.main()
