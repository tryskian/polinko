import unittest
from typing import Any

from tools.report_ocr_focus_fail_patterns import build_report


class ReportOcrFocusFailPatternsTests(unittest.TestCase):
    def test_build_report_summarises_lane_and_missing_phrase_counts(self) -> None:
        stability_payload: dict[str, Any] = {
            "cases": [
                {
                    "id": "gx-1",
                    "fail_runs": 1,
                    "pass_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 0.0,
                    "sample_reasons": ["missing ordered phrase: 'focus' after offset 20"],
                    "text_variant_count": 1,
                    "char_count_span": 0,
                },
                {
                    "id": "gx-2",
                    "fail_runs": 0,
                    "pass_runs": 1,
                    "error_runs": 0,
                    "pass_rate": 1.0,
                    "sample_reasons": [],
                    "text_variant_count": 1,
                    "char_count_span": 0,
                },
                {
                    "id": "gx-3",
                    "fail_runs": 1,
                    "pass_runs": 0,
                    "error_runs": 0,
                    "pass_rate": 0.0,
                    "sample_reasons": ["missing ordered phrase: 'engineering' after offset 0"],
                    "text_variant_count": 2,
                    "char_count_span": 3,
                },
            ]
        }
        focus_case_map = {
            "gx-1": {
                "id": "gx-1",
                "lane": "handwriting",
                "must_appear_in_order": ["focus", "stillness"],
                "source_name": "focus-note.jpeg",
                "image_path": "/tmp/focus-note.jpeg",
            },
            "gx-2": {"id": "gx-2", "lane": "typed", "must_appear_in_order": ["origin", "binary"]},
            "gx-3": {
                "id": "gx-3",
                "lane": "typed",
                "must_appear_in_order": ["instance", "engineering"],
                "source_name": "eng-note.jpeg",
                "image_path": "/tmp/eng-note.jpeg",
            },
        }

        report = build_report(
            stability_payload=stability_payload,
            focus_case_map=focus_case_map,
        )

        summary = report["summary"]
        self.assertEqual(summary["cases_total"], 3)
        self.assertEqual(summary["failing_cases"], 2)
        self.assertEqual(summary["lane_summary"]["handwriting"]["failing_cases"], 1)
        self.assertEqual(summary["lane_summary"]["typed"]["failing_cases"], 1)
        top_missing = summary["top_missing_ordered_phrases"]
        self.assertEqual(top_missing[0]["phrase"], "focus")
        self.assertEqual(top_missing[0]["count"], 1)
        self.assertEqual(top_missing[1]["phrase"], "engineering")
        self.assertEqual(top_missing[1]["count"], 1)
        self.assertEqual(
            summary["missing_order_offset_buckets"],
            {
                "at_start": 1,
                "mid_sequence": 1,
                "late_sequence": 0,
                "unknown": 0,
            },
        )
        self.assertEqual(
            summary["missing_order_sequence_position_buckets"],
            {
                "head": 1,
                "mid": 0,
                "tail": 1,
                "unknown": 0,
            },
        )
        self.assertEqual(
            summary["lane_missing_order_sequence_position_buckets"],
            {
                "handwriting": {"head": 1, "mid": 0, "tail": 0, "unknown": 0},
                "typed": {"head": 0, "mid": 0, "tail": 1, "unknown": 0},
            },
        )
        self.assertEqual(
            summary["lane_sequence_hotspots"],
            [
                {"lane": "handwriting", "bucket": "head", "count": 1},
                {"lane": "typed", "bucket": "tail", "count": 1},
            ],
        )

        failing_case_ids = [row["id"] for row in report["failing_cases"]]
        self.assertEqual(failing_case_ids, ["gx-1", "gx-3"])
        self.assertEqual(report["failing_cases"][0]["top_missing_phrase"], "focus")
        self.assertEqual(report["failing_cases"][0]["top_missing_offset"], 20)
        self.assertEqual(report["failing_cases"][0]["top_missing_offset_bucket"], "mid_sequence")
        self.assertEqual(report["failing_cases"][0]["top_missing_sequence_position_bucket"], "head")
        self.assertEqual(report["failing_cases"][0]["top_missing_sequence_index"], 0)
        self.assertEqual(report["failing_cases"][0]["source_name"], "focus-note.jpeg")
        self.assertEqual(report["failing_cases"][0]["image_path"], "/tmp/focus-note.jpeg")
        self.assertEqual(report["failing_cases"][1]["top_missing_phrase"], "engineering")
        self.assertEqual(report["failing_cases"][1]["top_missing_offset"], 0)
        self.assertEqual(report["failing_cases"][1]["top_missing_offset_bucket"], "at_start")
        self.assertEqual(report["failing_cases"][1]["top_missing_sequence_position_bucket"], "tail")
        self.assertEqual(report["failing_cases"][1]["top_missing_sequence_index"], 1)
        self.assertEqual(report["failing_cases"][1]["source_name"], "eng-note.jpeg")
        self.assertEqual(report["failing_cases"][1]["image_path"], "/tmp/eng-note.jpeg")


if __name__ == "__main__":
    unittest.main()
