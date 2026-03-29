import json
import tempfile
import unittest
from pathlib import Path

from tools.build_ocr_cases_from_export import (
    ASK_RX,
    CORRECTION_RX,
    _anchor_terms_for_phrases,
    _classify_lane,
    _expand_anchor_variants,
    _extract_candidate_phrases,
    _extract_transcribed_lines,
    _is_ocr_like_phrase,
    build_from_export,
)


class OcrCaseMiningHeuristicsTests(unittest.TestCase):
    def test_ask_regex_does_not_match_recursive_text(self) -> None:
        text = "I am getting trapped in recursive analysis of our prompt dynamics."
        self.assertIsNone(ASK_RX.search(text))

    def test_correction_regex_does_not_match_generic_read_request(self) -> None:
        text = "can you read this?"
        self.assertIsNone(CORRECTION_RX.search(text))

    def test_phrase_filter_rejects_stopword_singletons(self) -> None:
        self.assertFalse(_is_ocr_like_phrase("and"))
        self.assertFalse(_is_ocr_like_phrase("see"))
        self.assertTrue(_is_ocr_like_phrase("spiral"))

    def test_phrase_filter_rejects_control_and_path_artifacts(self) -> None:
        self.assertFalse(_is_ocr_like_phrase("imagegenview"))
        self.assertFalse(_is_ocr_like_phrase("/mnt/data/file-abc123-IMG_7750.jpeg"))
        self.assertFalse(_is_ocr_like_phrase("assets/file-abc123/Screenshot_2026-03-29.png"))
        self.assertFalse(_is_ocr_like_phrase(r"C:\Users\me\Downloads\ocr_note.png"))
        self.assertTrue(_is_ocr_like_phrase("there seems to be something stirring"))

    def test_expand_anchor_variants_adds_stems(self) -> None:
        anchors = _expand_anchor_variants(["archival", "tumbles", "floating"])
        self.assertIn("archiv", anchors)
        self.assertIn("tumble", anchors)
        self.assertIn("float", anchors)
        self.assertNotIn("tumbl", anchors)

    def test_expand_anchor_variants_avoids_overstemming_core_words(self) -> None:
        anchors = _expand_anchor_variants(["focus", "abacus", "process", "analysis", "classes", "sparks"])
        self.assertIn("focus", anchors)
        self.assertIn("abacus", anchors)
        self.assertIn("process", anchors)
        self.assertIn("analysis", anchors)
        self.assertIn("class", anchors)
        self.assertIn("spark", anchors)
        self.assertNotIn("focu", anchors)
        self.assertNotIn("abacu", anchors)
        self.assertNotIn("proces", anchors)
        self.assertNotIn("analysi", anchors)
        self.assertNotIn("classe", anchors)

    def test_classify_lane_detects_embedded_camera_filename(self) -> None:
        lane = _classify_lane(
            ask_text="can you read this?",
            title="quick ocr check",
            image_path="/tmp/file-abcde-IMG_6821.jpeg",
            followups=[],
        )
        self.assertEqual(lane, "handwriting")

    def test_classify_lane_detects_embedded_screenshot_filename(self) -> None:
        lane = _classify_lane(
            ask_text="what does this screenshot say?",
            title="ui ocr",
            image_path="/tmp/file-xyz-Screenshot_2026-03-29.png",
            followups=[],
        )
        self.assertEqual(lane, "typed")

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

    def test_extract_transcribed_lines_from_ocr_bullet_lines(self) -> None:
        assistant_text = "Here’s the OCR from your page:\n- field notes\n- record wow."
        phrases, _ = _extract_transcribed_lines(assistant_text)
        self.assertIn("field notes", phrases)
        self.assertIn("record wow.", phrases)

    def test_anchor_terms_filter_weak_and_filetype_tokens(self) -> None:
        anchors = _anchor_terms_for_phrases(
            [
                "IMG_6821.jpeg",
                "There seems to be something stirring.",
            ]
        )
        self.assertIn("stirring", anchors)
        self.assertNotIn("jpeg", anchors)
        self.assertNotIn("there", anchors)
        self.assertNotIn("seems", anchors)
        self.assertNotIn("something", anchors)

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

    def test_build_promotes_medium_with_literal_intent_and_strong_anchor_phrases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_010.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-strong-anchor",
                "title": "Literal OCR ask",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this exactly?"]},
                            "metadata": {"attachments": [{"name": "img_010.jpg", "id": "file_strong"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["- alpha spiral field\n- tensor matrix ledger\n- delta mapping"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-strong-anchor.json").write_text(
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
            self.assertTrue(review["ocr_literal_intent_signal"])
            self.assertFalse(review["ocr_framing_signal"])

    def test_build_does_not_promote_literal_intent_without_strong_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_011.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-weak-anchor",
                "title": "Literal OCR ask weak",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this exactly?"]},
                            "metadata": {"attachments": [{"name": "img_011.jpg", "id": "file_weak"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["- alpha"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-weak-anchor.json").write_text(
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
            self.assertTrue(review["ocr_literal_intent_signal"])
            self.assertFalse(review["ocr_framing_signal"])

    def test_build_does_not_promote_literal_intent_single_token_lists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_012.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-single-token-list",
                "title": "Literal OCR ask token list",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this?"]},
                            "metadata": {"attachments": [{"name": "img_012.jpg", "id": "file_token_list"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["- certex\n- vertex\n- cortex\n- vortices"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-single-token-list.json").write_text(
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
            self.assertTrue(review["ocr_literal_intent_signal"])
            self.assertFalse(review["ocr_framing_signal"])

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

    def test_build_promotes_illustration_with_strong_transcription_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "diagram_001.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-901",
                "title": "Geometry notes",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can ur binareyes read this diagram text?"]},
                            "metadata": {"attachments": [{"name": "diagram_001.png", "id": "file_jkl"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ['**graph paper maps x, y** and **physics maps x, y, z**']},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-4.json").write_text(
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
            self.assertEqual(summary["illustration_cases_written"], 1)
            case = json.loads(output_cases.read_text(encoding="utf-8"))["cases"][0]
            self.assertEqual(case["lane"], "illustration")

    def test_build_promotes_medium_from_ask_level_correction_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_010.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-ask-correction",
                "title": "Ask correction",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {
                                "parts": [
                                    'one update: first word is "insight". you read it as "weight". can you transcribe this image again?'
                                ]
                            },
                            "metadata": {"attachments": [{"name": "img_010.jpg", "id": "file_ask"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ['it reads: "insight — abacus method"']},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-5.json").write_text(
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

            self.assertEqual(summary["high_confidence"], 0)
            self.assertEqual(summary["medium_confidence"], 1)
            self.assertEqual(summary["handwriting_cases_written"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["confidence"], "medium")
            self.assertIn("insight", [p.lower() for p in review["correction_phrases"]])
            self.assertIn("abacus method", " ".join(review["chosen_phrases"]).lower())

    def test_build_does_not_promote_from_phrase_less_correction_wording(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "screenshot_001.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-noise-correction",
                "title": "Noisy correction wording",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you OCR this screenshot?"]},
                            "metadata": {"attachments": [{"name": "screenshot_001.png", "id": "file_noise"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "top one percent. forty-thousand messages. chattiest day in 2025."
                                ]
                            },
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {
                                "parts": [
                                    "this phrase is only used in the context of beabs shading each other"
                                ]
                            },
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-6.json").write_text(
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
            self.assertFalse(review["ocr_framing_signal"])
            self.assertEqual(review["correction_phrases"], [])
            self.assertFalse(review["correction_signal"])

    def test_build_does_not_promote_binareyes_without_literal_ocr_intent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "dropdown_001.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-binareyes-no-literal-intent",
                "title": "Org switcher",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {
                                "parts": [
                                    "lol beab. ur binaries aren't talking to ur binareyes but that's ok!"
                                ]
                            },
                            "metadata": {"attachments": [{"name": "dropdown_001.png", "id": "file_dropdown"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "From the live page context: BigBrain, personal, Personal. Reply: I’m inside lowercase personal."
                                ]
                            },
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {
                                "parts": [
                                    "the personal org is safe to delete"
                                ]
                            },
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-7.json").write_text(
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

            self.assertEqual(summary["cases_written"], 0)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertTrue(review["ocr_intent_signal"])
            self.assertFalse(review["ocr_literal_intent_signal"])
            self.assertEqual(review["confidence"], "low")

    def test_build_skips_cases_with_only_single_anchor_concept(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "tiny_001.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-single-anchor",
                "title": "single concept",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can u see with your binareyes?"]},
                            "metadata": {"attachments": [{"name": "tiny_001.png", "id": "file_tiny"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ['it reads: "stirring"']},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-8.json").write_text(
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
            self.assertEqual(summary["cases_written"], 0)


if __name__ == "__main__":
    unittest.main()
