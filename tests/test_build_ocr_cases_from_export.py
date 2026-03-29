import json
import tempfile
import unittest
from pathlib import Path

from tools.build_ocr_cases_from_export import (
    ASK_RX,
    _extract_candidate_phrases,
    _extract_transcribed_lines,
    _is_ocr_like_phrase,
    build_from_export,
)


class OcrCaseMiningHeuristicsTests(unittest.TestCase):
    def test_ask_regex_does_not_match_recursive_text(self) -> None:
        text = "I am getting trapped in recursive analysis of our prompt dynamics."
        self.assertIsNone(ASK_RX.search(text))

    def test_phrase_filter_rejects_stopword_singletons(self) -> None:
        self.assertFalse(_is_ocr_like_phrase("and"))
        self.assertFalse(_is_ocr_like_phrase("see"))
        self.assertTrue(_is_ocr_like_phrase("spiral"))

    def test_extract_candidate_phrases_from_quotes_and_emphasis(self) -> None:
        text = 'correction: "Only Alpha Spiral Field" and *Beta Grid*'
        phrases = _extract_candidate_phrases(text)
        self.assertIn("Alpha Spiral Field", phrases)
        self.assertIn("Beta Grid", phrases)

    def test_extract_transcribed_lines_from_framed_quoted_text(self) -> None:
        assistant_text = 'yes — binareyes locked on. it reads, *"There seems to be something stirring."*'
        phrases, had_code_block = _extract_transcribed_lines(assistant_text)
        self.assertFalse(had_code_block)
        self.assertIn("There seems to be something stirring.", phrases)

    def test_build_promotes_medium_with_framing_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_001.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-123",
                "title": "Cursive OCR",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this cursive note with binareyes?"]},
                            "metadata": {"attachments": [{"name": "img_001.jpg", "id": "file_abc"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ['yes — binareyes locked on. it reads, *"Alpha spiral field"*']},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-1.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
            )

            self.assertEqual(summary["medium_confidence"], 1)
            self.assertEqual(summary["cases_written"], 1)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["confidence"], "medium")
            self.assertTrue(review["ocr_intent_signal"])
            self.assertTrue(review["ocr_framing_signal"])
            self.assertIn("Alpha spiral field", review["chosen_phrases"])

    def test_build_does_not_promote_on_positive_only_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_002.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-456",
                "title": "Loose OCR",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["what does this say?"]},
                            "metadata": {"attachments": [{"name": "img_002.jpg", "id": "file_xyz"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Alpha spiral field"]},
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {"parts": ["perfect!"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-2.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
            )

            self.assertEqual(summary["medium_confidence"], 0)
            self.assertEqual(summary["cases_written"], 0)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["confidence"], "low")
            self.assertTrue(review["positive_signal"])
            self.assertFalse(review["ocr_framing_signal"])

    def test_build_ignores_non_ocr_cursive_commentary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_003.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-789",
                "title": "Cursive practice note",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {
                                "parts": [
                                    "i started teaching myself cursive from a workbook so i practiced occasionally in my notes"
                                ]
                            },
                            "metadata": {"attachments": [{"name": "img_003.jpg", "id": "file_ghi"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "the cursive peeking through your print looks expressive; you can *see* the shift."
                                ]
                            },
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-3.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
            )

            self.assertEqual(summary["episodes"], 0)
            self.assertEqual(summary["cases_written"], 0)


if __name__ == "__main__":
    unittest.main()
