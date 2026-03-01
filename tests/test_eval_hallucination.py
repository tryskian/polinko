import unittest

from tools.eval_hallucination import _MIN_ACCEPTABLE_SCORE
from tools.eval_hallucination import _apply_deterministic_gate
from tools.eval_hallucination import _contains_forbidden_phrases


class HallucinationEvalGateTests(unittest.TestCase):
    def test_contains_forbidden_phrases_matches_case_insensitive(self) -> None:
        answer = "This includes a Let Me Guess phrase."
        hits = _contains_forbidden_phrases(answer, ["let me guess", "cheers"])
        self.assertEqual(hits, ["let me guess"])

    def test_deterministic_gate_passes_clean_case(self) -> None:
        reasons = _apply_deterministic_gate(
            case={"expected_mode": "grounded", "must_not_contain": ["let me guess"]},
            answer="Answer grounded in available evidence.",
            score=_MIN_ACCEPTABLE_SCORE,
            risk="low",
            grounding="grounded",
        )
        self.assertEqual(reasons, [])

    def test_deterministic_gate_fails_forbidden_phrase(self) -> None:
        reasons = _apply_deterministic_gate(
            case={"expected_mode": "cautious", "must_not_contain": ["let me guess"]},
            answer="Let me guess, maybe this happened.",
            score=9,
            risk="low",
            grounding="grounded",
        )
        self.assertTrue(any("contains forbidden phrases" in reason for reason in reasons))

    def test_deterministic_gate_fails_high_risk(self) -> None:
        reasons = _apply_deterministic_gate(
            case={"expected_mode": "cautious", "must_not_contain": []},
            answer="Uncertain answer.",
            score=9,
            risk="high",
            grounding="partially_grounded",
        )
        self.assertIn("judge risk=high", reasons)

    def test_deterministic_gate_fails_low_score(self) -> None:
        reasons = _apply_deterministic_gate(
            case={"expected_mode": "cautious", "must_not_contain": []},
            answer="Uncertain answer.",
            score=_MIN_ACCEPTABLE_SCORE - 1,
            risk="low",
            grounding="partially_grounded",
        )
        self.assertTrue(any("score below minimum threshold" in reason for reason in reasons))

    def test_deterministic_gate_fails_grounded_mode_when_not_grounded(self) -> None:
        reasons = _apply_deterministic_gate(
            case={"expected_mode": "grounded", "must_not_contain": []},
            answer="Maybe true.",
            score=9,
            risk="low",
            grounding="partially_grounded",
        )
        self.assertIn("grounded case returned grounding='partially_grounded'", reasons)


if __name__ == "__main__":
    unittest.main()
