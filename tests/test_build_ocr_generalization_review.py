import unittest

from tools.build_ocr_generalization_review import build_review


class OcrGeneralizationReviewTests(unittest.TestCase):
    def test_build_review_balances_lanes(self) -> None:
        payload = {
            "candidates": [
                {
                    "candidate_id": "c-typed-1",
                    "conversation_id": "conv-typed-a",
                    "conversation_title": "typed thread a",
                    "image_path": "/tmp/Screenshot 2025-08-01.png",
                    "source_name": "Screenshot 2025-08-01.png",
                    "ask_text": "can you read this screenshot?",
                    "priority_score": 4,
                    "intake_reason": "same_conversation_unmined",
                },
                {
                    "candidate_id": "c-typed-2",
                    "conversation_id": "conv-typed-b",
                    "conversation_title": "typed thread b",
                    "image_path": "/tmp/file-typed-b.png",
                    "source_name": "file-typed-b.png",
                    "ask_text": "can you read this screenshot?",
                    "priority_score": 3,
                    "intake_reason": "same_conversation_unmined",
                },
                {
                    "candidate_id": "c-hand-1",
                    "conversation_id": "conv-hand",
                    "conversation_title": "handwritten notes",
                    "image_path": "/tmp/IMG_9001.JPG",
                    "source_name": "IMG_9001.JPG",
                    "ask_text": "can you read this notebook page?",
                    "priority_score": 2,
                    "intake_reason": "same_conversation_unmined",
                },
                {
                    "candidate_id": "c-illu-1",
                    "conversation_id": "conv-illu",
                    "conversation_title": "theory sketch",
                    "image_path": "/tmp/file_000000001234-sanitized.png",
                    "source_name": "file_000000001234-sanitized.png",
                    "ask_text": "today's drop starts with topological impossibles",
                    "priority_score": 5,
                    "intake_reason": "same_conversation_unmined",
                },
            ]
        }

        review = build_review(
            candidates_payload=payload,
            max_cases=3,
            max_per_conversation=2,
            include_candidate_ids=set(),
        )

        selected = review["selected_candidates"]
        lane_hints = {row["lane_hint"] for row in selected}
        self.assertEqual(len(selected), 3)
        self.assertEqual(lane_hints, {"typed", "handwriting", "illustration"})

    def test_build_review_keeps_pinned_include_despite_conversation_cap(self) -> None:
        payload = {
            "candidates": [
                {
                    "candidate_id": "c-top",
                    "conversation_id": "conv-a",
                    "conversation_title": "same thread",
                    "image_path": "/tmp/IMG_1000.JPG",
                    "source_name": "IMG_1000.JPG",
                    "ask_text": "can you read this notebook page?",
                    "priority_score": 5,
                    "intake_reason": "same_conversation_unmined",
                },
                {
                    "candidate_id": "c-pin",
                    "conversation_id": "conv-a",
                    "conversation_title": "same thread",
                    "image_path": "/tmp/file-pinned.png",
                    "source_name": "file-pinned.png",
                    "ask_text": "we can scan every insight later and distill it into a ledger",
                    "priority_score": 1,
                    "intake_reason": "same_conversation_unmined",
                },
                {
                    "candidate_id": "c-other",
                    "conversation_id": "conv-b",
                    "conversation_title": "other thread",
                    "image_path": "/tmp/Screenshot 2025-08-02.png",
                    "source_name": "Screenshot 2025-08-02.png",
                    "ask_text": "can you read this screenshot?",
                    "priority_score": 4,
                    "intake_reason": "same_conversation_unmined",
                },
            ]
        }

        review = build_review(
            candidates_payload=payload,
            max_cases=3,
            max_per_conversation=1,
            include_candidate_ids={"c-pin"},
        )

        selected_ids = [row["candidate_id"] for row in review["selected_candidates"]]
        self.assertIn("c-pin", selected_ids)
        pinned_row = next(row for row in review["selected_candidates"] if row["candidate_id"] == "c-pin")
        self.assertEqual(pinned_row["selection_reason"], "pinned_include")


if __name__ == "__main__":
    unittest.main()
