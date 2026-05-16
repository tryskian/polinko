import json
import tempfile
import unittest
from pathlib import Path

from tools.build_ocr_cases_from_export import (
    ASK_RX,
    CORRECTION_RX,
    _to_msg,
    _has_correction_signal,
    _anchor_terms_for_phrases,
    _classify_lane,
    _expand_anchor_variants,
    _extract_candidate_phrases,
    _extract_transcribed_lines,
    _is_ocr_like_phrase,
    _ordered_terms_for_phrases,
    _ordered_terms_supported_by_anchors,
    _regex_patterns_for_phrases,
    build_from_export,
)


class OcrCaseMiningHeuristicsTests(unittest.TestCase):
    def test_ask_regex_does_not_match_recursive_text(self) -> None:
        text = "I am getting trapped in recursive analysis of our prompt dynamics."
        self.assertIsNone(ASK_RX.search(text))

    def test_correction_regex_does_not_match_generic_read_request(self) -> None:
        text = "can you read this?"
        self.assertIsNone(CORRECTION_RX.search(text))

    def test_ask_regex_matches_ocrable_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("is this OCRable with your binareyes?"))

    def test_ask_regex_matches_ocr_dash_able_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("this one should be ocr-able"))

    def test_ask_regex_matches_new_drop_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("new drop: can your binareyes read this?"))

    def test_ask_regex_matches_newdrop_compact_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("newdrop can your binareyes read this?"))

    def test_ask_regex_matches_scribbles_and_bibbles_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("can you still OCR my scribbles and bibbles?"))

    def test_ask_regex_matches_scribbles_ampersand_bibbles_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("can you still OCR my scribbles & bibbles?"))

    def test_ask_regex_matches_scrumbles_and_bibbles_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("can you still OCR my scrumbles and bibbles?"))

    def test_ask_regex_matches_squibbles_and_bibbles_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("can you still OCR my squibbles and bibbles?"))

    def test_ask_regex_matches_peanut_cursive_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("this one is peanut cursive from my notebook"))

    def test_ask_regex_matches_scratched_out_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("this line is scratched out, can you still read it?"))

    def test_ask_regex_matches_scratch_out_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("this line is scratch out but still ocrable"))

    def test_ask_regex_matches_crossed_out_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("this line is crossed out, can you still read it?"))

    def test_ask_regex_matches_strikethrough_variant(self) -> None:
        self.assertIsNotNone(ASK_RX.search("did another strikethrough for focus on this one"))

    def test_ask_regex_does_not_match_read_it_and_weep_idiom(self) -> None:
        self.assertIsNone(ASK_RX.search("read it and weep binch!"))

    def test_to_msg_unescapes_html_entities_in_text(self) -> None:
        raw = {
            "create_time": 1,
            "author": {"role": "user"},
            "content": {"parts": ["yeah, it&#x27;s the theory itself"]},
            "metadata": {},
        }
        msg = _to_msg(raw)
        self.assertEqual(msg.text, "yeah, it's the theory itself")

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

    def test_phrase_filter_accepts_compact_timestamp_and_date_tokens(self) -> None:
        self.assertTrue(_is_ocr_like_phrase("1745"))
        self.assertTrue(_is_ocr_like_phrase("200226"))
        self.assertFalse(_is_ocr_like_phrase("2460"))

    def test_phrase_filter_rejects_label_only_headers(self) -> None:
        self.assertFalse(_is_ocr_like_phrase("Timestamp"))
        self.assertFalse(_is_ocr_like_phrase("Crossed-out header"))
        self.assertFalse(_is_ocr_like_phrase("Bullet 1"))
        self.assertFalse(_is_ocr_like_phrase("archived and translated as"))

    def test_expand_anchor_variants_adds_stems(self) -> None:
        anchors = _expand_anchor_variants(["archival", "tumbles", "floating"])
        self.assertIn("tumble", anchors)
        self.assertIn("archival", anchors)
        self.assertIn("floating", anchors)
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

    def test_expand_anchor_variants_preserves_ics_suffix(self) -> None:
        anchors = _expand_anchor_variants(["physics", "mechanics"])
        self.assertIn("physics", anchors)
        self.assertIn("mechanics", anchors)
        self.assertNotIn("physic", anchors)
        self.assertNotIn("mechanic", anchors)

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

    def test_classify_lane_detects_topology_illustration_hint(self) -> None:
        lane = _classify_lane(
            ask_text="today's drop starts with topological impossibles",
            title="shape notes",
            image_path="/tmp/file-xyz-note.png",
            followups=[],
        )
        self.assertEqual(lane, "illustration")

    def test_classify_lane_does_not_match_ink_inside_polinko_token(self) -> None:
        lane = _classify_lane(
            ask_text='`beab init "Operation Polinko"`',
            title="org cleanup",
            image_path="/tmp/file-xyz-note.png",
            followups=[],
        )
        self.assertEqual(lane, "typed")

    def test_classify_lane_promotes_symbolic_script_to_illustration(self) -> None:
        lane = _classify_lane(
            ask_text="can you transcribe this?",
            title="glyph notes",
            image_path="/tmp/file-xyz-note.png",
            followups=[],
            assistant_text="𓂀𓏏𓅓𓅱𓂋𓏏𓏤",
        )
        self.assertEqual(lane, "illustration")

    def test_extract_candidate_phrases_from_quotes_and_emphasis(self) -> None:
        text = 'correction: "Only Alpha Spiral Field" and *Beta Grid*'
        phrases = _extract_candidate_phrases(text)
        self.assertIn("Alpha Spiral Field", phrases)
        self.assertIn("Beta Grid", phrases)

    def test_extract_candidate_phrases_from_not_pair(self) -> None:
        text = "binareyes: bully not bull-fly"
        phrases = _extract_candidate_phrases(text)
        self.assertIn("bully", phrases)

    def test_extract_candidate_phrases_from_marker_without_colon(self) -> None:
        text = "it says alpha spiral field."
        phrases = _extract_candidate_phrases(text)
        self.assertIn("alpha spiral field", [p.lower() for p in phrases])

    def test_extract_candidate_phrases_keeps_timestamp_and_date_tokens(self) -> None:
        text = "correction: timestamp 1745; date 200226"
        phrases = _extract_candidate_phrases(text)
        joined = " ".join(phrases)
        self.assertIn("1745", joined)
        self.assertIn("200226", joined)

    def test_has_correction_signal_detects_not_pair(self) -> None:
        text = "bully not bull-fly"
        self.assertFalse(_has_correction_signal(text))

    def test_has_correction_signal_detects_not_pair_with_ocr_context(self) -> None:
        text = "word bully not bull-fly"
        self.assertTrue(_has_correction_signal(text))

    def test_has_correction_signal_rejects_non_ocr_not_pair(self) -> None:
        text = "normal bigbrain, not all seriousberious"
        self.assertFalse(_has_correction_signal(text))

    def test_extract_transcribed_lines_from_framed_quoted_text(self) -> None:
        assistant_text = 'yes — binareyes locked on. it reads, *"There seems to be something stirring."*'
        phrases, had_code_block = _extract_transcribed_lines(assistant_text)
        self.assertFalse(had_code_block)
        self.assertIn("There seems to be something stirring.", phrases)

    def test_extract_transcribed_lines_accepts_numeric_entry_tokens(self) -> None:
        assistant_text = "it reads: 1745\nand line two is 200226."
        phrases, had_code_block = _extract_transcribed_lines(assistant_text)
        self.assertFalse(had_code_block)
        self.assertIn("1745", phrases)
        self.assertTrue(any("200226" in phrase for phrase in phrases))

    def test_extract_transcribed_lines_from_ocr_bullet_lines(self) -> None:
        assistant_text = "Here’s the OCR from your page:\n- field notes\n- record wow."
        phrases, _ = _extract_transcribed_lines(assistant_text)
        self.assertIn("field notes", phrases)
        self.assertIn("record wow.", phrases)

    def test_extract_transcribed_lines_filters_non_ocr_narrative_lines(self) -> None:
        assistant_text = (
            "Here’s the OCR:\n"
            "- open fold within\n"
            "the web branch was like a pocket timeline that could not sustain itself once deleted."
        )
        phrases, _ = _extract_transcribed_lines(assistant_text)
        self.assertIn("open fold within", phrases)
        self.assertFalse(any("pocket timeline" in phrase.lower() for phrase in phrases))

    def test_extract_transcribed_lines_keeps_head_fragment_from_long_line(self) -> None:
        assistant_text = (
            "Transforms human lived experience into structured notes; "
            "archived and translated as field log."
        )
        phrases, _ = _extract_transcribed_lines(assistant_text)
        self.assertIn("Transforms human lived experience", phrases)

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

    def test_anchor_terms_filter_meta_transcription_words(self) -> None:
        anchors = _anchor_terms_for_phrases(
            [
                "please transcribe this journal thing",
                "gyrus folds within",
            ]
        )
        self.assertIn("gyrus", anchors)
        self.assertNotIn("transcribe", anchors)
        self.assertNotIn("journal", anchors)
        self.assertNotIn("thing", anchors)

    def test_anchor_and_ordered_terms_drop_cropping_metadata_tokens(self) -> None:
        anchors = _anchor_terms_for_phrases(
            [
                "page partial single line cropped",
                "continuation previous entry more accessible updated",
                "conversation found screenshot html",
                "find chat",
            ]
        )
        ordered = _ordered_terms_for_phrases(
            [
                "page partial single line cropped",
                "continuation previous entry more accessible updated",
                "conversation found screenshot html",
                "find chat",
            ]
        )
        self.assertEqual(anchors, [])
        self.assertEqual(ordered, [])

    def test_anchor_and_ordered_terms_include_entry_numeric_tokens(self) -> None:
        anchors = _anchor_terms_for_phrases(["1745", "200226", "field notes"])
        ordered = _ordered_terms_for_phrases(["1745 field notes"])
        self.assertIn("1745", anchors)
        self.assertIn("200226", anchors)
        self.assertIn("1745", ordered)

    def test_ordered_terms_drop_ui_prefix_tokens_in_long_phrase(self) -> None:
        ordered = _ordered_terms_for_phrases(["Restore Deleted Chat"])
        self.assertEqual(ordered, [])

    def test_ordered_terms_keep_non_ui_trailing_sequence(self) -> None:
        ordered = _ordered_terms_for_phrases(["Restore Deleted Spectral Branch Phenomenon"])
        self.assertEqual(ordered, ["branch", "phenomenon"])

    def test_regex_patterns_drop_ui_not_found_phrase(self) -> None:
        patterns = _regex_patterns_for_phrases(["Conversation not found"])
        self.assertEqual(patterns, [])

    def test_regex_patterns_drop_ui_chat_html_phrase(self) -> None:
        patterns = _regex_patterns_for_phrases(["chat html"])
        self.assertEqual(patterns, [])

    def test_ordered_terms_supported_by_anchors_singularizes_plural_when_available(self) -> None:
        ordered = _ordered_terms_supported_by_anchors(["folds", "within"], ["fold", "within"])
        self.assertEqual(ordered, ["fold", "within"])

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

            self.assertEqual(summary["medium_signal_strength"], 1)
            self.assertEqual(summary["cases_written"], 1)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "medium")
            self.assertEqual(review["confidence"], "medium")
            self.assertEqual(review["selected_confidence"], "medium")
            self.assertEqual(review["selected_phrase"], "Alpha spiral field")
            self.assertTrue(str(review["candidate_id"]).startswith("cv-conv-123-"))
            self.assertTrue(review["ocr_intent_signal"])
            self.assertTrue(review["ocr_framing_signal"])
            self.assertIn("Alpha spiral field", review["chosen_phrases"])

    def test_build_respects_include_title_regex(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)
            (assets / "img_001.jpg").write_bytes(b"not-a-real-image")
            (assets / "img_002.jpg").write_bytes(b"not-a-real-image")

            def make_conversation(conversation_id: str, title: str, image_name: str) -> dict[str, object]:
                return {
                    "conversation_id": conversation_id,
                    "title": title,
                    "mapping": {
                        "1": {
                            "message": {
                                "create_time": 1,
                                "author": {"role": "user"},
                                "content": {"parts": ["can you transcribe this note?"]},
                                "metadata": {"attachments": [{"name": image_name, "id": f"file_{conversation_id}"}]},
                            }
                        },
                        "2": {
                            "message": {
                                "create_time": 2,
                                "author": {"role": "assistant"},
                                "content": {"parts": ['it reads: "alpha spiral field"']},
                                "metadata": {},
                            }
                        },
                    },
                }

            (conversations / "conv_focus.json").write_text(
                json.dumps(make_conversation("conv-focus", "Focus Session", "img_001.jpg")),
                encoding="utf-8",
            )
            (conversations / "conv_misc.json").write_text(
                json.dumps(make_conversation("conv-misc", "Misc Session", "img_002.jpg")),
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
                include_title_regex="focus",
            )

            self.assertEqual(summary["conversation_files"], 2)
            self.assertEqual(summary["skipped_filtered_conversations"], 1)
            self.assertEqual(summary["cases_written"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))
            self.assertEqual(review["summary"]["skipped_filtered_conversations"], 1)
            self.assertEqual(len(review["episodes"]), 1)
            self.assertEqual(review["episodes"][0]["conversation_title"], "Focus Session")

    def test_build_respects_include_conversation_regex(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)
            (assets / "img_001.jpg").write_bytes(b"not-a-real-image")
            (assets / "img_002.jpg").write_bytes(b"not-a-real-image")

            def make_conversation(conversation_id: str, image_name: str) -> dict[str, object]:
                return {
                    "conversation_id": conversation_id,
                    "title": "OCR Session",
                    "mapping": {
                        "1": {
                            "message": {
                                "create_time": 1,
                                "author": {"role": "user"},
                                "content": {"parts": ["can you transcribe this note?"]},
                                "metadata": {"attachments": [{"name": image_name, "id": f"file_{conversation_id}"}]},
                            }
                        },
                        "2": {
                            "message": {
                                "create_time": 2,
                                "author": {"role": "assistant"},
                                "content": {"parts": ['it reads: "alpha spiral field"']},
                                "metadata": {},
                            }
                        },
                    },
                }

            (conversations / "conv_focus.json").write_text(
                json.dumps(make_conversation("conv-focus-001", "img_001.jpg")),
                encoding="utf-8",
            )
            (conversations / "conv_misc.json").write_text(
                json.dumps(make_conversation("conv-misc-002", "img_002.jpg")),
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
                include_conversation_regex="focus-001",
            )

            self.assertEqual(summary["conversation_files"], 2)
            self.assertEqual(summary["skipped_filtered_conversations"], 1)
            self.assertEqual(summary["cases_written"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))
            self.assertEqual(len(review["episodes"]), 1)
            self.assertEqual(review["episodes"][0]["conversation_id"], "conv-focus-001")

    def test_build_respects_include_lanes_and_counts_filtered_episodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)
            (assets / "img_001.jpg").write_bytes(b"not-a-real-image")
            (assets / "Screenshot_2026-03-29.png").write_bytes(b"not-a-real-image")

            conversation_handwriting = {
                "conversation_id": "conv-lanes-hand",
                "title": "Handwriting Session",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this note?"]},
                            "metadata": {"attachments": [{"name": "img_001.jpg", "id": "file_lane_a"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ['it reads: "alpha spiral field"']},
                            "metadata": {},
                        }
                    },
                },
            }
            conversation_typed = {
                "conversation_id": "conv-lanes-typed",
                "title": "Typed Session",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this screenshot text?"]},
                            "metadata": {
                                "attachments": [
                                    {"name": "Screenshot_2026-03-29.png", "id": "file_lane_b"}
                                ]
                            },
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ['it reads: "tensor matrix ledger"']},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conv_lanes_hand.json").write_text(
                json.dumps(conversation_handwriting),
                encoding="utf-8",
            )
            (conversations / "conv_lanes_typed.json").write_text(
                json.dumps(conversation_typed),
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
                include_lanes={"typed"},
            )

            self.assertEqual(summary["conversation_files"], 2)
            self.assertEqual(summary["skipped_filtered_conversations"], 0)
            self.assertEqual(summary["skipped_filtered_episodes"], 1)
            self.assertEqual(summary["cases_written"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))
            self.assertEqual(review["summary"]["skipped_filtered_episodes"], 1)
            self.assertEqual(len(review["episodes"]), 1)
            self.assertEqual(review["episodes"][0]["lane"], "typed")

    def test_build_rejects_unknown_lane_filters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)
            (assets / "img_001.jpg").write_bytes(b"not-a-real-image")
            conversation = {
                "conversation_id": "conv-lanes-invalid",
                "title": "Lane Validation Session",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this note?"]},
                            "metadata": {"attachments": [{"name": "img_001.jpg", "id": "file_lane_invalid"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ['it reads: "alpha spiral field"']},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conv_lanes_invalid.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            with self.assertRaisesRegex(ValueError, "Invalid lane filters"):
                build_from_export(
                    export_root,
                    output_cases=output_cases,
                    output_cases_handwriting=output_handwriting,
                    output_cases_typed=output_typed,
                    output_cases_illustration=output_illustration,
                    output_review=output_review,
                    max_cases=50,
                    include_lanes={"typed", "sketch"},
                )

    def test_build_respects_include_signal_strengths_and_counts_filtered_episodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)
            (assets / "img_high.jpg").write_bytes(b"not-a-real-image")
            (assets / "img_medium.jpg").write_bytes(b"not-a-real-image")

            conversation_high = {
                "conversation_id": "conv-signal-high",
                "title": "Signal High",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this exactly?"]},
                            "metadata": {"attachments": [{"name": "img_high.jpg", "id": "file_signal_high"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Here's the OCR:\n- alpha spiral field\n- tensor matrix ledger"]},
                            "metadata": {},
                        }
                    },
                },
            }
            conversation_medium = {
                "conversation_id": "conv-signal-medium",
                "title": "Signal Medium",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this exactly?"]},
                            "metadata": {"attachments": [{"name": "img_medium.jpg", "id": "file_signal_medium"}]},
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
            (conversations / "conv_signal_high.json").write_text(
                json.dumps(conversation_high),
                encoding="utf-8",
            )
            (conversations / "conv_signal_medium.json").write_text(
                json.dumps(conversation_medium),
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
                include_signal_strengths={"high"},
            )

            self.assertEqual(summary["conversation_files"], 2)
            self.assertEqual(summary["skipped_filtered_conversations"], 0)
            self.assertEqual(summary["skipped_filtered_episodes"], 1)
            self.assertEqual(summary["high_signal_strength"], 1)
            self.assertEqual(summary["medium_signal_strength"], 0)
            review = json.loads(output_review.read_text(encoding="utf-8"))
            self.assertEqual(review["summary"]["skipped_filtered_episodes"], 1)
            self.assertEqual(len(review["episodes"]), 1)
            self.assertEqual(review["episodes"][0]["signal_strength"], "high")

    def test_build_respects_include_emit_statuses_and_counts_filtered_episodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)
            (assets / "img_emitted.jpg").write_bytes(b"not-a-real-image")
            (assets / "img_low.jpg").write_bytes(b"not-a-real-image")

            conversation_emitted = {
                "conversation_id": "conv-emit-emitted",
                "title": "Emit Status Emitted",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this exactly?"]},
                            "metadata": {"attachments": [{"name": "img_emitted.jpg", "id": "file_emit_ok"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Here's the OCR:\n- alpha spiral field\n- tensor matrix ledger"]},
                            "metadata": {},
                        }
                    },
                },
            }
            conversation_low = {
                "conversation_id": "conv-emit-low",
                "title": "Emit Status Low",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this?"]},
                            "metadata": {"attachments": [{"name": "img_low.jpg", "id": "file_emit_low"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["I cannot tell."]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conv_emit_emitted.json").write_text(
                json.dumps(conversation_emitted),
                encoding="utf-8",
            )
            (conversations / "conv_emit_low.json").write_text(
                json.dumps(conversation_low),
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
                include_emit_statuses={"skipped_low_confidence"},
            )

            self.assertEqual(summary["conversation_files"], 2)
            self.assertEqual(summary["skipped_filtered_conversations"], 0)
            self.assertEqual(summary["skipped_filtered_episodes"], 1)
            self.assertEqual(summary["cases_written"], 0)
            self.assertEqual(summary["skipped_low_confidence"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))
            self.assertEqual(review["summary"]["skipped_filtered_episodes"], 1)
            self.assertEqual(len(review["episodes"]), 1)
            self.assertEqual(review["episodes"][0]["emit_status"], "skipped_low_confidence")

    def test_build_respects_include_source_regex_and_counts_filtered_episodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)
            (assets / "IMG_7001.jpg").write_bytes(b"not-a-real-image")
            (assets / "Screenshot_2026-03-29.png").write_bytes(b"not-a-real-image")

            def make_conversation(conversation_id: str, image_name: str) -> dict[str, object]:
                return {
                    "conversation_id": conversation_id,
                    "title": "OCR Session",
                    "mapping": {
                        "1": {
                            "message": {
                                "create_time": 1,
                                "author": {"role": "user"},
                                "content": {"parts": ["can you transcribe this note?"]},
                                "metadata": {"attachments": [{"name": image_name, "id": f"file_{conversation_id}"}]},
                            }
                        },
                        "2": {
                            "message": {
                                "create_time": 2,
                                "author": {"role": "assistant"},
                                "content": {"parts": ['it reads: "alpha spiral field"']},
                                "metadata": {},
                            }
                        },
                    },
                }

            (conversations / "conv_hand.json").write_text(
                json.dumps(make_conversation("conv-hand-001", "IMG_7001.jpg")),
                encoding="utf-8",
            )
            (conversations / "conv_typed.json").write_text(
                json.dumps(make_conversation("conv-typed-001", "Screenshot_2026-03-29.png")),
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
                include_source_regex=r"^IMG_",
            )

            self.assertEqual(summary["conversation_files"], 2)
            self.assertEqual(summary["skipped_filtered_conversations"], 0)
            self.assertEqual(summary["skipped_filtered_episodes"], 1)
            self.assertEqual(summary["cases_written"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))
            self.assertEqual(review["summary"]["skipped_filtered_episodes"], 1)
            self.assertEqual(len(review["episodes"]), 1)
            self.assertEqual(review["episodes"][0]["source_name"], "IMG_7001.jpg")

    def test_build_keeps_askless_typed_low_without_correction_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "Screenshot_2026-03-29.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-askless-typed",
                "title": "Askless typed OCR",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["attached sample for reference"]},
                            "metadata": {
                                "attachments": [
                                    {
                                        "name": "Screenshot_2026-03-29.png",
                                        "id": "file_askless_typed",
                                    }
                                ]
                            },
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "Here's the OCR:\n- alpha spiral field\n- tensor matrix ledger"
                                ]
                            },
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-askless-typed.json").write_text(
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
                output_cases_growth=Path(tmp_dir) / "cases_growth.json",
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
            )

            self.assertEqual(summary["episodes"], 0)
            self.assertEqual(summary["medium_signal_strength"], 0)
            self.assertEqual(summary["cases_written"], 0)
            self.assertEqual(summary["growth_cases_written"], 0)
            self.assertEqual(
                json.loads(output_review.read_text(encoding="utf-8"))["episodes"],
                [],
            )

    def test_build_promotes_askless_typed_with_correction_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "Screenshot_2026-03-29.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-askless-typed-correction",
                "title": "Askless typed OCR correction",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["attached sample for reference"]},
                            "metadata": {
                                "attachments": [
                                    {
                                        "name": "Screenshot_2026-03-29.png",
                                        "id": "file_askless_typed_correction",
                                    }
                                ]
                            },
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "Here's the OCR:\n- alpha spiral field\n- tensor matrix ledger"
                                ]
                            },
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {"parts": ["it says alpha spiral field"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-askless-typed-correction.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
            )

            self.assertEqual(summary["high_signal_strength"], 1)
            self.assertEqual(summary["typed_cases_written"], 1)
            self.assertEqual(summary["growth_cases_written"], 1)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["lane"], "typed")
            self.assertEqual(review["signal_strength"], "high")
            self.assertTrue(review["ocr_framing_signal"])
            self.assertTrue(review["correction_signal"])
            self.assertTrue(review["correction_overlap_signal"])
            self.assertEqual(len(json.loads(output_growth.read_text(encoding="utf-8"))["cases"]), 1)

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

            self.assertEqual(summary["medium_signal_strength"], 1)
            self.assertEqual(summary["cases_written"], 1)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "medium")
            self.assertTrue(review["ocr_literal_intent_signal"])
            self.assertFalse(review["ocr_framing_signal"])

    def test_build_promotes_high_with_literal_framed_multi_phrase_transcription(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_013.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-high-framed",
                "title": "Literal OCR ask framed",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this exactly?"]},
                            "metadata": {"attachments": [{"name": "img_013.jpg", "id": "file_high"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "Here's the OCR:\n- alpha spiral field\n- tensor matrix ledger"
                                ]
                            },
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-high-framed.json").write_text(
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

            self.assertEqual(summary["high_signal_strength"], 1)
            self.assertEqual(summary["cases_written"], 1)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "high")
            self.assertTrue(review["ocr_literal_intent_signal"])
            self.assertTrue(review["ocr_framing_signal"])

    def test_build_emits_high_signal_strength_when_correction_phrase_is_numeric_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_014.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-high-correction-numeric",
                "title": "Numeric correction on OCR transcription",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["please OCR this note exactly"]},
                            "metadata": {"attachments": [{"name": "img_014.jpg", "id": "file_high_numeric"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "Here is the OCR:\n- 7 is the step slip singularity\n- outlier logic anchors the sequence"
                                ]
                            },
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {"parts": ['correction: "0, 1, 1, 2, 3, 3"']},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-high-correction-numeric.json").write_text(
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

            self.assertEqual(summary["cases_written"], 1)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertIn(review["signal_strength"], {"high", "medium"})
            self.assertEqual(review["emit_status"], "emitted")
            self.assertGreaterEqual(review["anchor_terms_count"], 3)

    def test_build_ignores_correction_phrase_after_next_assistant_turn(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_015.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-late-correction",
                "title": "Late correction should be ignored",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this?"]},
                            "metadata": {"attachments": [{"name": "img_015.jpg", "id": "file_late_corr"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Here's the OCR:\n- WISHING YOU\n- PEACEFUL WINTER LIGHT"]},
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {"parts": ["looks right, thanks"]},
                            "metadata": {},
                        }
                    },
                    "4": {
                        "message": {
                            "create_time": 4,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["great!"]},
                            "metadata": {},
                        }
                    },
                    "5": {
                        "message": {
                            "create_time": 5,
                            "author": {"role": "user"},
                            "content": {"parts": ['correction: "done keep like receive simple fade wreath star"']},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-late-correction.json").write_text(
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

            self.assertEqual(summary["cases_written"], 1)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertTrue(review["correction_signal"])
            self.assertFalse(review["correction_overlap_signal"])
            self.assertEqual(review["emit_status"], "emitted")
            self.assertNotIn("done", review["anchor_terms"])
            self.assertNotIn("wreath", review["anchor_terms"])

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

            self.assertEqual(summary["medium_signal_strength"], 0)
            self.assertEqual(summary["cases_written"], 0)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "low")
            self.assertTrue(review["ocr_literal_intent_signal"])
            self.assertFalse(review["ocr_framing_signal"])
            self.assertEqual(review["skip_reason"], "low_confidence")
            self.assertIn("transcribe this exactly", review["query_text"])
            self.assertIn("alpha", review["expected_text"].lower())

    def test_build_widens_growth_lane_for_low_confidence_literal_intent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_017.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-growth-low",
                "title": "Literal OCR ask weak",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this exactly?"]},
                            "metadata": {"attachments": [{"name": "img_017.jpg", "id": "file_growth_low"}]},
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
            (conversations / "conversation-growth-low.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
                max_growth_cases=50,
            )

            self.assertEqual(summary["cases_written"], 0)
            self.assertEqual(summary["growth_cases_written"], 1)
            growth_payload = json.loads(output_growth.read_text(encoding="utf-8"))
            growth_cases = growth_payload["cases"]
            self.assertEqual(len(growth_cases), 1)
            self.assertEqual(growth_cases[0]["id"], "gx-conv-gro-001")
            self.assertEqual(growth_cases[0]["lane"], "handwriting")

    def test_build_does_not_widen_growth_lane_for_framed_low_confidence_without_intent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_018.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-growth-frame",
                "title": "Framed OCR weak ask",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["thoughts?"]},
                            "metadata": {"attachments": [{"name": "img_018.png", "id": "file_growth_frame"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Here is the OCR:\n- Delta bridge ledger"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-growth-frame.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
                max_growth_cases=50,
            )

            self.assertEqual(summary["cases_written"], 0)
            self.assertEqual(summary["growth_cases_written"], 0)
            growth_payload = json.loads(output_growth.read_text(encoding="utf-8"))
            growth_cases = growth_payload["cases"]
            self.assertEqual(len(growth_cases), 0)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "low")
            self.assertFalse(review["ocr_literal_intent_signal"])
            self.assertTrue(review["ocr_framing_signal"])

    def test_build_does_not_widen_growth_lane_for_correction_without_ocr_intent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_020.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-growth-correction-no-intent",
                "title": "Concept dialogue with correction wording",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["thoughts on this concept sketch?"]},
                            "metadata": {"attachments": [{"name": "img_020.png", "id": "file_growth_corr"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["it reads: human perception, machine cognition"]},
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {"parts": ["this should be related"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-growth-correction-no-intent.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
                max_growth_cases=50,
            )

            self.assertEqual(summary["cases_written"], 0)
            self.assertEqual(summary["growth_cases_written"], 0)

            growth_payload = json.loads(output_growth.read_text(encoding="utf-8"))
            self.assertEqual(growth_payload["cases"], [])

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "low")
            self.assertFalse(review["ocr_intent_signal"])
            self.assertTrue(review["correction_signal"])
            self.assertTrue(review["ocr_framing_signal"])

    def test_build_does_not_promote_overlap_correction_without_ocr_intent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_021.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-overlap-correction-no-intent",
                "title": "Style dialogue with overlap correction wording",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["maybe even this!"]},
                            "metadata": {"attachments": [{"name": "img_021.png", "id": "file_overlap_corr"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "it reads almost architectural — as if the words were machined out of alloy.\n"
                                    "you could anchor your entire visual language off this — the title becomes a mirror."
                                ]
                            },
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {"parts": ["the title reads \"the mirror blinked back\" when only then is stylized"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-overlap-correction-no-intent.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
                max_growth_cases=50,
            )

            self.assertEqual(summary["cases_written"], 0)
            self.assertEqual(summary["growth_cases_written"], 0)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "low")
            self.assertEqual(review["emit_status"], "skipped_low_confidence")
            self.assertFalse(review["ocr_intent_signal"])
            self.assertFalse(review["ocr_literal_intent_signal"])
            self.assertTrue(review["correction_signal"])
            self.assertTrue(review["ocr_framing_signal"])

    def test_build_widens_growth_lane_with_regex_only_constraints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_019.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-growth-regex-only",
                "title": "Regex-only growth constraints",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you transcribe this exactly?"]},
                            "metadata": {"attachments": [{"name": "img_019.png", "id": "file_growth_regex"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["Here is the OCR:\n- central circle grid wave"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-growth-regex-only.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
                max_growth_cases=50,
            )

            self.assertEqual(summary["cases_written"], 0)
            self.assertEqual(summary["growth_cases_written"], 1)
            self.assertEqual(summary["growth_regex_only_cases_written"], 1)

            growth_payload = json.loads(output_growth.read_text(encoding="utf-8"))
            growth_case = growth_payload["cases"][0]
            self.assertEqual(growth_case["must_contain_any"], [])
            self.assertEqual(growth_case["must_appear_in_order"], [])
            self.assertTrue(growth_case["must_match_regex"])

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

            self.assertEqual(summary["medium_signal_strength"], 0)
            self.assertEqual(summary["cases_written"], 0)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "low")
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

            self.assertEqual(summary["medium_signal_strength"], 0)
            self.assertEqual(summary["cases_written"], 0)

            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "low")
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

            self.assertEqual(summary["medium_signal_strength"], 1)
            self.assertEqual(summary["illustration_cases_written"], 1)
            cases_payload = json.loads(output_cases.read_text(encoding="utf-8"))
            self.assertIn("summary", cases_payload)
            self.assertEqual(cases_payload["summary"]["cases_total"], 1)
            self.assertEqual(cases_payload["summary"]["lane_case_counts"]["illustration"], 1)
            case = cases_payload["cases"][0]
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

            self.assertEqual(summary["high_signal_strength"], 0)
            self.assertEqual(summary["medium_signal_strength"], 1)
            self.assertEqual(summary["handwriting_cases_written"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "medium")
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

            self.assertEqual(summary["medium_signal_strength"], 0)
            self.assertEqual(summary["cases_written"], 0)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "low")
            self.assertFalse(review["ocr_framing_signal"])
            self.assertEqual(review["correction_phrases"], [])
            self.assertFalse(review["correction_signal"])

    def test_build_drops_binareyes_chatter_without_ocr_signals(self) -> None:
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
            self.assertEqual(summary["episodes"], 0)

    def test_build_promotes_non_literal_intent_when_correction_phrase_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "img_900.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-nonliteral-correction",
                "title": "Binareyes correction",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {
                                "parts": [
                                    "lol bully! not bull-fly! binareyes"
                                ]
                            },
                            "metadata": {"attachments": [{"name": "img_900.jpg", "id": "file_900"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ['it reads: "word bully"']},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-9.json").write_text(
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

            self.assertEqual(summary["medium_signal_strength"], 1)
            self.assertEqual(summary["cases_written"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "medium")
            self.assertTrue(review["ocr_intent_signal"])
            self.assertFalse(review["ocr_literal_intent_signal"])

    def test_build_keeps_askless_handwriting_low_without_correction_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "IMG_2001.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-askless-hand",
                "title": "Journal page",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["new notebook page from today"]},
                            "metadata": {"attachments": [{"name": "IMG_2001.jpg", "id": "file_askless_hand"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "Here’s the OCR:\n- alpha spiral field\n- tensor mapping notes"
                                ]
                            },
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-askless-hand.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
            )

            self.assertEqual(summary["medium_signal_strength"], 0)
            self.assertEqual(summary["handwriting_cases_written"], 0)
            self.assertEqual(summary["growth_cases_written"], 0)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "low")
            self.assertFalse(review["ocr_literal_intent_signal"])
            self.assertTrue(review["ocr_framing_signal"])
            self.assertFalse(review["correction_signal"])
            self.assertFalse(review["correction_overlap_signal"])
            self.assertEqual(json.loads(output_growth.read_text(encoding="utf-8"))["cases"], [])

    def test_build_promotes_markup_handwriting_with_framed_transcription(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "IMG_2004.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-markup-hand-medium",
                "title": "Journal page",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["Did another strikethrough for focus on this one :)"]},
                            "metadata": {"attachments": [{"name": "IMG_2004.jpg", "id": "file_markup_hand"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "Here’s the OCR:\n- gyrus folds within\n- tensor field remains stable"
                                ]
                            },
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-markup-hand-medium.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
            )

            self.assertEqual(summary["medium_signal_strength"], 1)
            self.assertEqual(summary["handwriting_cases_written"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "medium")
            self.assertTrue(review["ocr_intent_signal"])
            self.assertFalse(review["ocr_literal_intent_signal"])
            self.assertTrue(review["ocr_framing_signal"])

    def test_build_promotes_askless_handwriting_with_followup_correction_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "IMG_2002.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-askless-hand-correction",
                "title": "Journal page",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["new notebook page from today"]},
                            "metadata": {"attachments": [{"name": "IMG_2002.jpg", "id": "file_askless_hand_correction"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "Here’s the OCR:\n- alpha spiral field\n- tensor mapping notes"
                                ]
                            },
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {"parts": ["correction: it says alpha spiral field"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-askless-hand-correction.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
            )

            self.assertEqual(summary["high_signal_strength"], 1)
            self.assertEqual(summary["handwriting_cases_written"], 1)
            self.assertEqual(summary["growth_cases_written"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "high")
            self.assertTrue(review["ocr_framing_signal"])
            self.assertTrue(review["correction_signal"])
            self.assertTrue(review["correction_overlap_signal"])
            self.assertEqual(len(json.loads(output_growth.read_text(encoding="utf-8"))["cases"]), 1)

    def test_build_keeps_askless_handwriting_low_with_non_overlapping_correction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "IMG_2003.jpg").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-askless-hand-correction-no-overlap",
                "title": "Journal page",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["new notebook page from today"]},
                            "metadata": {"attachments": [{"name": "IMG_2003.jpg", "id": "file_askless_hand_no_overlap"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "Here’s the OCR:\n- alpha spiral field\n- tensor mapping notes"
                                ]
                            },
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {"parts": ["correction: date should be 2024"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-askless-hand-correction-no-overlap.json").write_text(
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

            self.assertEqual(summary["medium_signal_strength"], 0)
            self.assertEqual(summary["handwriting_cases_written"], 0)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["signal_strength"], "low")
            self.assertTrue(review["ocr_framing_signal"])
            self.assertTrue(review["correction_signal"])
            self.assertFalse(review["correction_overlap_signal"])

    def test_build_emits_single_anchor_case_with_ordered_token_fallback(self) -> None:
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
                            "content": {"parts": ['it reads: "There seems to be something - stirring."']},
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

            self.assertEqual(summary["medium_signal_strength"], 1)
            self.assertEqual(summary["cases_written"], 1)
            self.assertEqual(summary["skipped_insufficient_anchor_terms"], 0)
            review_payload = json.loads(output_review.read_text(encoding="utf-8"))
            self.assertEqual(review_payload["summary"]["episodes"], 1)
            self.assertEqual(review_payload["summary"]["emit_status_counts"]["emitted"], 1)
            review = review_payload["episodes"][0]
            self.assertEqual(review_payload["summary"]["lane_emit_status_counts"][review["lane"]]["emitted"], 1)
            self.assertEqual(review["emit_status"], "emitted")
            self.assertEqual(review["anchor_terms_count"], 1)
            self.assertEqual(review["anchor_terms"], ["stirring"])
            case = json.loads(output_cases.read_text(encoding="utf-8"))["cases"][0]
            self.assertEqual(case["must_contain_any"], ["stirring"])
            self.assertEqual(case["must_appear_in_order"], ["something", "stirring"])

    def test_build_growth_lane_limits_ordered_terms_to_anchor_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            (assets / "tiny_growth_001.png").write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-growth-anchor-filter",
                "title": "single concept growth",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can u see with your binareyes?"]},
                            "metadata": {
                                "attachments": [{"name": "tiny_growth_001.png", "id": "file_tiny_growth"}]
                            },
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ['it reads: "There seems to be something - stirring."']},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-growth-anchor-filter.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
                max_growth_cases=50,
            )

            self.assertEqual(summary["cases_written"], 1)
            self.assertEqual(summary["growth_cases_written"], 1)
            growth_case = json.loads(output_growth.read_text(encoding="utf-8"))["cases"][0]
            self.assertEqual(growth_case["must_contain_any"], ["stirring"])
            self.assertEqual(growth_case["must_appear_in_order"], [])
            self.assertEqual(growth_case["must_match_regex"], [])
            self.assertNotIn("something", growth_case["must_appear_in_order"])

    def test_build_skips_known_unstable_handwriting_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            unstable_name = "file_00000000b01871fdac46c44584b95d6a-sanitized.png"
            (assets / unstable_name).write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-unstable-source",
                "title": "unstable source",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you read this handwritten notebook note?"]},
                            "metadata": {"attachments": [{"name": unstable_name, "id": "file_unstable"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": [
                                    "OCR:\n- SOH CAH TOAH\n- open / fold / within\n- moment the mnemonic became mythic."
                                ]
                            },
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-unstable-source.json").write_text(
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
            self.assertEqual(summary["skipped_unstable_source"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["emit_status"], "skipped_unstable_source")
            self.assertEqual(review["source_name"], unstable_name)

    def test_build_skips_known_unstable_typed_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            unstable_name = "file_0000000047f871f7af65c1ce3955cc2e-sanitized.png"
            (assets / unstable_name).write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-unstable-typed-source",
                "title": "unstable typed source",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you read this?"]},
                            "metadata": {"attachments": [{"name": unstable_name, "id": "file_unstable_typed"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["it reads: word bully"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-unstable-typed-source.json").write_text(
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
            self.assertEqual(summary["skipped_unstable_source"], 1)
            review = json.loads(output_review.read_text(encoding="utf-8"))["episodes"][0]
            self.assertEqual(review["emit_status"], "skipped_unstable_source")
            self.assertEqual(review["source_name"], unstable_name)

    def test_build_routes_strong_unstable_source_to_growth_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            unstable_name = "file_0000000047f871f7af65c1ce3955cc2e-sanitized.png"
            (assets / unstable_name).write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-unstable-growth",
                "title": "unstable growth route",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you read this?"]},
                            "metadata": {"attachments": [{"name": unstable_name, "id": "file_unstable_growth"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {
                                "parts": ["it reads: word bull-fly\nma’am, let the plot breathe.\nword bully"]
                            },
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {"parts": ["lol bully! not bull-fly!"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-unstable-growth.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                max_cases=50,
            )

            self.assertEqual(summary["cases_written"], 0)
            self.assertEqual(summary["skipped_unstable_source"], 1)
            self.assertEqual(summary["growth_cases_written"], 1)
            self.assertEqual(summary["growth_quarantine_cases_written"], 1)
            growth_cases = json.loads(output_growth.read_text(encoding="utf-8"))["cases"]
            self.assertEqual(len(growth_cases), 1)
            self.assertTrue(growth_cases[0]["source_quarantine"])

    def test_build_does_not_promote_ask_phrases_without_correction_signal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            image_name = "file_ocrable_note.png"
            (assets / image_name).write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-no-correction-ask-phrase",
                "title": "org switcher crumbs",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ['`beab init "Operation Polinko"` with binareyes']},
                            "metadata": {"attachments": [{"name": image_name, "id": "file_nocorr"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["No OCR output here; this is org settings guidance only."]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-no-correction-ask-phrase.json").write_text(
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
            self.assertEqual(summary["episodes"], 0)
            self.assertEqual(summary["skipped_low_confidence"], 0)

    def test_build_surfaces_same_conversation_unmined_generalization_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            export_root = Path(tmp_dir) / "export"
            conversations = export_root / "conversations"
            assets = export_root / "assets"
            conversations.mkdir(parents=True, exist_ok=True)
            assets.mkdir(parents=True, exist_ok=True)

            primary_name = "IMG_9001.JPG"
            extra_name = "supplemental-ledger-page.png"
            (assets / primary_name).write_bytes(b"not-a-real-image")
            (assets / extra_name).write_bytes(b"not-a-real-image")

            conversation = {
                "conversation_id": "conv-generalization-gap",
                "title": "mixed ocr intake",
                "mapping": {
                    "1": {
                        "message": {
                            "create_time": 1,
                            "author": {"role": "user"},
                            "content": {"parts": ["can you read this notebook page?"]},
                            "metadata": {"attachments": [{"name": primary_name, "id": "file_primary"}]},
                        }
                    },
                    "2": {
                        "message": {
                            "create_time": 2,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["it reads: spiral field ledger"]},
                            "metadata": {},
                        }
                    },
                    "3": {
                        "message": {
                            "create_time": 3,
                            "author": {"role": "user"},
                            "content": {
                                "parts": [
                                    "we can scan every insight later and distill it into a ledger"
                                ]
                            },
                            "metadata": {"attachments": [{"name": extra_name, "id": "file_extra"}]},
                        }
                    },
                    "4": {
                        "message": {
                            "create_time": 4,
                            "author": {"role": "assistant"},
                            "content": {"parts": ["yes, that can become one continuous ledger block"]},
                            "metadata": {},
                        }
                    },
                },
            }
            (conversations / "conversation-generalization-gap.json").write_text(
                json.dumps(conversation),
                encoding="utf-8",
            )

            output_cases = Path(tmp_dir) / "cases_all.json"
            output_growth = Path(tmp_dir) / "cases_growth.json"
            output_handwriting = Path(tmp_dir) / "cases_handwriting.json"
            output_typed = Path(tmp_dir) / "cases_typed.json"
            output_illustration = Path(tmp_dir) / "cases_illustration.json"
            output_review = Path(tmp_dir) / "review.json"
            output_generalization = Path(tmp_dir) / "generalization.json"

            summary = build_from_export(
                export_root,
                output_cases=output_cases,
                output_cases_growth=output_growth,
                output_cases_handwriting=output_handwriting,
                output_cases_typed=output_typed,
                output_cases_illustration=output_illustration,
                output_review=output_review,
                output_generalization_candidates=output_generalization,
                max_cases=50,
                max_growth_cases=50,
            )

            self.assertEqual(summary["episodes"], 1)
            self.assertEqual(summary["generalization_candidates_written"], 1)
            self.assertEqual(summary["same_conversation_unmined_candidates"], 1)
            generalization = json.loads(output_generalization.read_text(encoding="utf-8"))
            self.assertEqual(generalization["summary"]["same_conversation_unmined"], 1)
            candidate = generalization["candidates"][0]
            self.assertEqual(candidate["source_name"], extra_name)
            self.assertEqual(candidate["intake_reason"], "same_conversation_unmined")


if __name__ == "__main__":
    unittest.main()
