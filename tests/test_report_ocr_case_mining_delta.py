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
                    {"lane": "handwriting", "signal_strength": "medium"},
                    {"lane": "typed", "signal_strength": "low"},
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
                    {"lane": "handwriting", "signal_strength": "high"},
                    {"lane": "handwriting", "signal_strength": "medium"},
                    {"lane": "typed", "signal_strength": "low"},
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
            self.assertEqual(report["signal_strength"]["before"]["medium"], 1)
            self.assertEqual(report["signal_strength"]["after"]["high"], 1)
            self.assertEqual(report["lane_signal_strength"]["after"]["handwriting"]["high"], 1)
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
                "episodes": [{"lane": "handwriting", "signal_strength": "medium"}],
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
            self.assertEqual(report["signal_strength"]["before"]["medium"], 0)
            self.assertEqual(report["signal_strength"]["after"]["medium"], 1)

    def test_build_delta_report_includes_actionable_backlog_preview(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            curr_path = root / "curr.json"
            out_md = root / "delta.md"
            out_json = root / "delta.json"

            curr_payload = {
                "summary": {
                    "episodes": 3,
                    "emit_status_counts": {
                        "emitted": 1,
                        "skipped_low_confidence": 2,
                        "skipped_duplicate_image_path": 0,
                        "skipped_unstable_source": 0,
                    },
                },
                "episodes": [
                    {
                        "lane": "typed",
                        "signal_strength": "medium",
                        "emit_status": "emitted",
                    },
                    {
                        "lane": "typed",
                        "signal_strength": "medium",
                        "emit_status": "skipped_low_confidence",
                        "conversation_title": "typed lane case",
                        "source_name": "file_a.png",
                        "image_path": "/tmp/file_a.png",
                        "anchor_terms_count": 2,
                        "ask_text": "can you read this screenshot?",
                        "chosen_phrases": ["alpha", "beta"],
                        "ocr_literal_intent_signal": True,
                    },
                    {
                        "lane": "handwriting",
                        "signal_strength": "high",
                        "emit_status": "skipped_unstable_source",
                        "conversation_title": "handwriting unstable",
                        "source_name": "file_b.png",
                        "image_path": "/tmp/file_b.png",
                        "anchor_terms": ["open", "fold", "within"],
                        "ask_text": "please transcribe this notebook page",
                        "chosen_phrases": ["open", "fold", "within"],
                    },
                    {
                        "lane": "typed",
                        "signal_strength": "low",
                        "emit_status": "skipped_low_confidence",
                        "conversation_title": "off-topic visual chat",
                        "source_name": "file_c.png",
                        "image_path": "/tmp/file_c.png",
                        "anchor_terms_count": 0,
                        "ask_text": "look at this little ASCII dude",
                        "chosen_phrases": [],
                        "ocr_literal_intent_signal": False,
                        "ocr_framing_signal": False,
                        "correction_signal": False,
                        "correction_overlap_signal": False,
                        "transcription_phrases": [],
                    },
                    {
                        "lane": "typed",
                        "signal_strength": "low",
                        "emit_status": "skipped_low_confidence",
                        "conversation_title": "ocr framing but no anchors",
                        "source_name": "file_d.png",
                        "image_path": "/tmp/file_d.png",
                        "anchor_terms_count": 0,
                        "ask_text": "please transcribe this image",
                        "chosen_phrases": [],
                        "ocr_literal_intent_signal": False,
                        "ocr_framing_signal": True,
                        "correction_signal": True,
                        "correction_overlap_signal": False,
                        "transcription_phrases": ["hello there"],
                    },
                ],
            }
            curr_path.write_text(json.dumps(curr_payload), encoding="utf-8")

            report = build_delta_report(
                current_review_path=curr_path,
                previous_review_path=None,
                output_markdown_path=out_md,
                output_json_path=out_json,
                max_actionable_items=5,
            )

            backlog = report.get("actionable_backlog")
            self.assertIsInstance(backlog, list)
            assert isinstance(backlog, list)
            self.assertEqual(len(backlog), 2)
            self.assertEqual(backlog[0]["emit_status"], "skipped_unstable_source")
            self.assertEqual(backlog[0]["image_path"], "/tmp/file_b.png")
            self.assertEqual(backlog[1]["image_path"], "/tmp/file_a.png")
            markdown = out_md.read_text(encoding="utf-8")
            self.assertIn("## Actionable Skipped Episodes", markdown)
            self.assertIn("/tmp/file_b.png", markdown)
            self.assertNotIn("/tmp/file_c.png", markdown)
            self.assertNotIn("/tmp/file_d.png", markdown)


if __name__ == "__main__":
    unittest.main()
