import unittest

from tools.build_behaviour_backlog_from_export import _extract_snippet
from tools.build_behaviour_backlog_from_export import _score_lane
from tools.build_behaviour_backlog_from_export import build_backlog
from tools.build_behaviour_backlog_from_export import LANE_DEFINITIONS
from tools.build_behaviour_backlog_from_export import SignalPattern


def _lane(slug: str):
    for lane in LANE_DEFINITIONS:
        if lane.slug == slug:
            return lane
    raise AssertionError(f"missing lane: {slug}")


class BehaviourExportBacklogTests(unittest.TestCase):
    def test_co_reasoning_lane_accepts_working_style_and_constraint_language(self) -> None:
        lane = _lane("co_reasoning")
        result = _score_lane(
            lane,
            title="POL working style pass",
            text="We need a working style and collaboration protocol with clear constraint retention.",
            tags=["behaviour", "eval"],
        )
        self.assertIsNotNone(result)
        self.assertIn("working_style", result["matched_terms"])
        self.assertGreaterEqual(result["score"], lane.min_score)

    def test_operator_burden_lane_accepts_raw_pull_execution_contract(self) -> None:
        lane = _lane("operator_burden")
        result = _score_lane(
            lane,
            title="raw ledger pull",
            text=(
                "Recover the exact text segment as a raw pull with no commentary and no rephrasing."
            ),
            tags=["behaviour", "eval"],
        )
        self.assertIsNotNone(result)
        self.assertIn("raw_pull", result["matched_terms"])
        self.assertIn("no_commentary", result["matched_terms"])

    def test_operator_burden_lane_accepts_tight_execution_language(self) -> None:
        lane = _lane("operator_burden")
        result = _score_lane(
            lane,
            title="professor protocol",
            text=(
                "Professor protocol is active: tone fixed, syntax-obedient, no commentary, "
                "no meta-explanations."
            ),
            tags=["behaviour"],
        )
        self.assertIsNotNone(result)
        self.assertIn("tone_fixed", result["matched_terms"])
        self.assertIn("no_commentary", result["matched_terms"])

    def test_operator_burden_lane_rejects_lone_direct_mapping_match(self) -> None:
        lane = _lane("operator_burden")
        result = _score_lane(
            lane,
            title="origin mapping failure",
            text="This is a direct mapping task with a visual reference.",
            tags=["behaviour", "eval"],
        )
        self.assertIsNone(result)

    def test_ocr_confidence_boundary_requires_ocr_and_boundary_signals(self) -> None:
        lane = _lane("ocr_confidence_boundary")
        no_boundary = _score_lane(
            lane,
            title="simple OCR note",
            text="Can you OCR this handwriting and transcribe it?",
            tags=["behaviour", "ocr"],
        )
        self.assertIsNone(no_boundary)

        with_boundary = _score_lane(
            lane,
            title="OCR certainty boundary",
            text=(
                "Does accurate OCR reduce low signal inference? "
                "Keep explicit uncertainty instead of hallucination when the handwriting is unclear."
            ),
            tags=["behaviour", "ocr", "policy"],
        )
        self.assertIsNotNone(with_boundary)
        self.assertIn("ocr", with_boundary["preferred_tag_hits"])

    def test_extract_snippet_prefers_nearby_match_context(self) -> None:
        text = (
            "alpha prelude words "
            "explicit uncertainty should hold when confidence outruns evidence "
            "omega closing words"
        )
        snippet = _extract_snippet(text, [SignalPattern("explicit_uncertainty", r"\bexplicit uncertainty\b")])
        self.assertIn("explicit uncertainty", snippet)
        self.assertIn("confidence outruns evidence", snippet)

    def test_build_backlog_includes_untagged_candidates(self) -> None:
        search_rows = [
            {
                "id": "c-1",
                "title": "Working style lane",
                "text": "We need a working style and collaboration protocol with better constraint retention.",
            },
            {
                "id": "c-2",
                "title": "OCR uncertainty lane",
                "text": "Does OCR reduce low signal inference when explicit uncertainty is preserved?",
            },
        ]
        conversation_rows = [
            {
                "conversation_id": "c-2",
                "title": "OCR uncertainty lane",
                "tags": ["behaviour", "ocr", "policy"],
                "attachment_count": 4,
                "has_attachment": True,
            }
        ]
        backlog = build_backlog(search_rows=search_rows, conversation_rows=conversation_rows, limit_per_lane=10)
        co_reasoning = next(lane for lane in backlog["lanes"] if lane["lane"] == "co_reasoning")
        ocr_boundary = next(lane for lane in backlog["lanes"] if lane["lane"] == "ocr_confidence_boundary")

        self.assertEqual(co_reasoning["candidate_count"], 1)
        self.assertEqual(co_reasoning["family_count"], 1)
        self.assertFalse(co_reasoning["candidates"][0]["already_tagged"])
        self.assertEqual(ocr_boundary["candidate_count"], 1)
        self.assertTrue(ocr_boundary["candidates"][0]["already_tagged"])

    def test_build_backlog_collapses_branch_title_variants_into_one_family(self) -> None:
        search_rows = [
            {
                "id": "c-1",
                "title": "ORG-241225",
                "text": "Quick contextual mimicry and style adaptation under constraint retention.",
            },
            {
                "id": "c-2",
                "title": "Branch · ORG-241225",
                "text": "Quick contextual mimicry and style adaptation under constraint retention.",
            },
        ]
        conversation_rows = [
            {
                "conversation_id": "c-1",
                "title": "ORG-241225",
                "tags": ["behaviour", "policy"],
                "attachment_count": 2,
                "has_attachment": True,
            },
            {
                "conversation_id": "c-2",
                "title": "Branch · ORG-241225",
                "tags": ["behaviour", "policy"],
                "attachment_count": 3,
                "has_attachment": True,
            },
        ]
        backlog = build_backlog(search_rows=search_rows, conversation_rows=conversation_rows, limit_per_lane=10)
        co_reasoning = next(lane for lane in backlog["lanes"] if lane["lane"] == "co_reasoning")
        self.assertEqual(co_reasoning["candidate_count"], 2)
        self.assertEqual(co_reasoning["family_count"], 1)
        self.assertEqual(co_reasoning["candidates"][0]["family_title"], "ORG-241225")
        self.assertEqual(co_reasoning["candidates"][0]["variant_count"], 2)


if __name__ == "__main__":
    unittest.main()
