import unittest
from unittest.mock import patch

from tools.eval_hallucination import _MIN_ACCEPTABLE_SCORE
from tools.eval_hallucination import _apply_deterministic_gate
from tools.eval_hallucination import _contains_forbidden_phrases
from tools.eval_hallucination import _deterministic_assessment
from tools.eval_hallucination import _resolve_judge_client
from tools.eval_hallucination import build_parser


class HallucinationEvalGateTests(unittest.TestCase):
    def test_resolve_judge_client_returns_none_when_env_key_missing(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            client, api_key = _resolve_judge_client(api_key_env="BRAINTRUST_API_KEY", base_url="")
        self.assertIsNone(client)
        self.assertIsNone(api_key)

    def test_resolve_judge_client_builds_client_with_base_url(self) -> None:
        with patch.dict("os.environ", {"BRAINTRUST_API_KEY": "bt-key"}, clear=True):
            with patch("tools.eval_hallucination.OpenAI") as openai_cls:
                _client, api_key = _resolve_judge_client(
                    api_key_env="BRAINTRUST_API_KEY",
                    base_url="https://braintrust.example/v1",
                )

        openai_cls.assert_called_once_with(
            api_key="bt-key",
            base_url="https://braintrust.example/v1",
        )
        self.assertEqual(api_key, "bt-key")

    def test_parser_accepts_judge_endpoint_flags(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--judge-api-key-env",
                "BRAINTRUST_API_KEY",
                "--judge-base-url",
                "https://braintrust.example/v1",
                "--evaluation-mode",
                "judge",
                "--min-acceptable-score",
                "70",
            ]
        )
        self.assertEqual(args.judge_api_key_env, "BRAINTRUST_API_KEY")
        self.assertEqual(args.judge_base_url, "https://braintrust.example/v1")
        self.assertEqual(args.evaluation_mode, "judge")
        self.assertEqual(args.min_acceptable_score, 70)

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
            min_acceptable_score=_MIN_ACCEPTABLE_SCORE,
        )
        self.assertEqual(reasons, [])

    def test_deterministic_gate_fails_forbidden_phrase(self) -> None:
        reasons = _apply_deterministic_gate(
            case={"expected_mode": "cautious", "must_not_contain": ["let me guess"]},
            answer="Let me guess, maybe this happened.",
            score=9,
            risk="low",
            grounding="grounded",
            min_acceptable_score=_MIN_ACCEPTABLE_SCORE,
        )
        self.assertTrue(any("contains forbidden phrases" in reason for reason in reasons))

    def test_deterministic_gate_fails_high_risk(self) -> None:
        reasons = _apply_deterministic_gate(
            case={"expected_mode": "cautious", "must_not_contain": []},
            answer="Uncertain answer.",
            score=9,
            risk="high",
            grounding="partially_grounded",
            min_acceptable_score=_MIN_ACCEPTABLE_SCORE,
        )
        self.assertIn("judge risk=high", reasons)

    def test_deterministic_gate_fails_low_score(self) -> None:
        reasons = _apply_deterministic_gate(
            case={"expected_mode": "cautious", "must_not_contain": []},
            answer="Uncertain answer.",
            score=_MIN_ACCEPTABLE_SCORE - 1,
            risk="low",
            grounding="partially_grounded",
            min_acceptable_score=_MIN_ACCEPTABLE_SCORE,
        )
        self.assertTrue(any("score below minimum threshold" in reason for reason in reasons))

    def test_deterministic_gate_fails_grounded_mode_when_not_grounded(self) -> None:
        reasons = _apply_deterministic_gate(
            case={"expected_mode": "grounded", "must_not_contain": []},
            answer="Maybe true.",
            score=9,
            risk="low",
            grounding="partially_grounded",
            min_acceptable_score=_MIN_ACCEPTABLE_SCORE,
        )
        self.assertIn("grounded case returned grounding='partially_grounded'", reasons)

    def test_deterministic_gate_respects_custom_threshold(self) -> None:
        reasons = _apply_deterministic_gate(
            case={"expected_mode": "cautious", "must_not_contain": []},
            answer="Concise grounded answer.",
            score=65,
            risk="low",
            grounding="grounded",
            min_acceptable_score=70,
        )
        self.assertIn("score below minimum threshold (65 < 70)", reasons)

    def test_deterministic_assessment_grounded_requires_memory(self) -> None:
        result = _deterministic_assessment(
            case={"expected_mode": "grounded", "must_not_contain": []},
            answer="Answer without citations.",
            memory_used=[],
        )
        self.assertFalse(result["pass"])
        self.assertEqual(result["risk"], "high")
        self.assertEqual(result["grounding"], "partially_grounded")

    def test_deterministic_assessment_cautious_passes_without_memory(self) -> None:
        result = _deterministic_assessment(
            case={"expected_mode": "cautious", "must_not_contain": []},
            answer="I cannot verify this claim from available evidence.",
            memory_used=[],
        )
        self.assertTrue(result["pass"])
        self.assertEqual(result["risk"], "low")
        self.assertEqual(result["grounding"], "grounded")

    def test_deterministic_assessment_flags_forbidden_phrase(self) -> None:
        result = _deterministic_assessment(
            case={"expected_mode": "cautious", "must_not_contain": ["let me guess"]},
            answer="Let me guess, this happened in 2029.",
            memory_used=[],
        )
        self.assertFalse(result["pass"])
        self.assertEqual(result["risk"], "high")


if __name__ == "__main__":
    unittest.main()
