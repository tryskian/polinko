import json
import tempfile
import unittest
from pathlib import Path

from tools.report_ocr_case_mining_delta import build_delta_report


class ReportOcrCaseMiningDeltaTests(unittest.TestCase):
    def test_build_delta_report_counts_confidence_and_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            prev_path = root / "prev.json"
            curr_path = root / "curr.json"
            out_md = root / "delta.md"
            out_json = root / "delta.json"

            prev_payload = {
                "summary": {
                    "episodes": 2,
                    "emit_status_counts": {
                        "emitted": 1,
                        "skipped_low_confidence": 1,
                        "skipped_duplicate_image_path": 0,
                    },
                },
                "episodes": [
                    {"lane": "handwriting", "confidence": "medium"},
                    {"lane": "typed", "confidence": "low"},
                ],
            }
            curr_payload = {
                "summary": {
                    "episodes": 3,
                    "emit_status_counts": {
                        "emitted": 2,
                        "skipped_low_confidence": 1,
                        "skipped_duplicate_image_path": 0,
                    },
                },
                "episodes": [
                    {"lane": "handwriting", "confidence": "high"},
                    {"lane": "handwriting", "confidence": "medium"},
                    {"lane": "typed", "confidence": "low"},
                ],
            }

            prev_path.write_text(json.dumps(prev_payload), encoding="utf-8")
            curr_path.write_text(json.dumps(curr_payload), encoding="utf-8")

            report = build_delta_report(
                current_review_path=curr_path,
                previous_review_path=prev_path,
                output_markdown_path=out_md,
                output_json_path=out_json,
            )

            self.assertEqual(report["totals"]["before"]["episodes"], 2)
            self.assertEqual(report["totals"]["after"]["episodes"], 3)
            self.assertEqual(report["totals"]["before"]["emitted_cases"], 1)
            self.assertEqual(report["totals"]["after"]["emitted_cases"], 2)
            self.assertEqual(report["confidence"]["before"]["medium"], 1)
            self.assertEqual(report["confidence"]["after"]["high"], 1)
            self.assertEqual(report["lane_confidence"]["after"]["handwriting"]["high"], 1)
            self.assertIn("typed", report["lanes"])
            self.assertTrue(out_md.is_file())
            self.assertTrue(out_json.is_file())

    def test_build_delta_report_without_previous_file_uses_zero_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            curr_path = root / "curr.json"
            out_md = root / "delta.md"
            out_json = root / "delta.json"

            curr_payload = {
                "summary": {
                    "episodes": 1,
                    "emit_status_counts": {
                        "emitted": 1,
                        "skipped_low_confidence": 0,
                        "skipped_duplicate_image_path": 0,
                    },
                },
                "episodes": [{"lane": "handwriting", "confidence": "medium"}],
            }
            curr_path.write_text(json.dumps(curr_payload), encoding="utf-8")

            report = build_delta_report(
                current_review_path=curr_path,
                previous_review_path=None,
                output_markdown_path=out_md,
                output_json_path=out_json,
            )
            self.assertEqual(report["totals"]["before"]["episodes"], 0)
            self.assertEqual(report["totals"]["after"]["episodes"], 1)
            self.assertEqual(report["confidence"]["before"]["medium"], 0)
            self.assertEqual(report["confidence"]["after"]["medium"], 1)


if __name__ == "__main__":
    unittest.main()
