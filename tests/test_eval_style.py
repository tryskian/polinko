import unittest

from tools.eval_style import _build_confidence_counts
from tools.eval_style import _case_confidence_bucket
from tools.eval_style import _contains_forbidden_phrases
from tools.eval_style import _load_cases
from tools.eval_style import _missing_required_all
from tools.eval_style import _missing_required_any_groups
from tools.eval_style import _normalize_text_for_match
from tools.eval_style import _resolve_case_status
from tools.eval_style import _should_stop_attempts
from tools.eval_style import build_parser
import json
import tempfile
from pathlib import Path


class StyleEvalTests(unittest.TestCase):
    def test_normalize_text_for_match_handles_curly_apostrophes_and_dashes(self) -> None:
        normalized = _normalize_text_for_match("I don’t have real‑time data.")
        self.assertEqual(normalized, "i don't have real-time data.")

    def test_contains_forbidden_phrases_matches_case_insensitive(self) -> None:
        hits = _contains_forbidden_phrases("Ready when you are.", ["ready when you are"])
        self.assertEqual(hits, ["ready when you are"])

    def test_missing_required_all_reports_missing_values(self) -> None:
        missing = _missing_required_all(
            "Human-led checks keep the loop grounded.",
            ["human-led", "checkpoints"],
        )
        self.assertEqual(missing, ["checkpoints"])

    def test_missing_required_any_groups_reports_unmatched_group(self) -> None:
        missing_groups = _missing_required_any_groups(
            "Tone-matching is useful when it stays grounded.",
            [["tone-matching", "tone matching"], ["without mimicry", "not mimicry"]],
        )
        self.assertEqual(missing_groups, [["without mimicry", "not mimicry"]])

    def test_missing_required_any_groups_accepts_repo_native_working_style_synonyms(self) -> None:
        missing_groups = _missing_required_any_groups(
            "Shared standards and review scope keep the loop legible.",
            [[
                "constraints",
                "constraint",
                "context",
                "intent",
                "scope",
                "standard",
                "standards",
                "ground rules",
                "ownership",
                "role",
                "roles",
                "clarify",
                "clarification",
            ]],
        )
        self.assertEqual(missing_groups, [])

    def test_missing_required_any_groups_accepts_traceable_merge_contract_language(self) -> None:
        missing_groups = _missing_required_any_groups(
            "Keep change logs traceable. Humans make final merge and scope decisions.",
            [[
                "constraints",
                "constraint",
                "context",
                "intent",
                "scope",
                "standard",
                "standards",
                "ground rules",
                "ownership",
                "role",
                "roles",
                "clarify",
                "clarification",
                "checkpoints",
                "review",
                "feedback",
                "validation",
                "traceability",
                "traceable",
                "checks",
                "sign-off",
                "merge",
                "prompt",
                "prompts",
                "template",
                "templates",
                "spec",
                "specs",
                "format",
                "formats",
                "rationale",
                "assumptions",
            ]],
        )
        self.assertEqual(missing_groups, [])

    def test_load_cases_accepts_required_phrase_fields(self) -> None:
        payload = {
            "global_forbidden_phrases": ["let me guess"],
            "cases": [
                {
                    "id": "co-reasoning-contract",
                    "query": "Summarise a working style.",
                    "style_notes": "Direct.",
                    "required_all": ["human-led"],
                    "required_any_groups": [["checkpoints", "feedback"]],
                    "forbidden_phrases": ["ready when you are"],
                    "max_words": 50,
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "cases.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            cases, global_forbidden = _load_cases(path)
        self.assertEqual(global_forbidden, ["let me guess"])
        self.assertEqual(cases[0]["required_all"], ["human-led"])
        self.assertEqual(cases[0]["required_any_groups"], [["checkpoints", "feedback"]])
        self.assertIn("ready when you are", cases[0]["forbidden_phrases"])
        self.assertIn("let me guess", cases[0]["forbidden_phrases"])

    def test_build_parser_accepts_attempt_flags(self) -> None:
        args = build_parser().parse_args(
            [
                "--case-attempts",
                "3",
                "--min-pass-attempts",
                "2",
            ]
        )
        self.assertEqual(args.case_attempts, 3)
        self.assertEqual(args.min_pass_attempts, 2)

    def test_resolve_case_status_pass_when_min_passes_met(self) -> None:
        status = _resolve_case_status(
            attempt_statuses=["FAIL", "PASS", "PASS"],
            pass_attempts=2,
            min_pass_attempts=2,
        )
        self.assertEqual(status, "PASS")

    def test_resolve_case_status_fail_when_any_fail_and_min_not_met(self) -> None:
        status = _resolve_case_status(
            attempt_statuses=["FAIL", "ERROR"],
            pass_attempts=0,
            min_pass_attempts=1,
        )
        self.assertEqual(status, "FAIL")

    def test_resolve_case_status_error_when_no_fail_and_min_not_met(self) -> None:
        status = _resolve_case_status(
            attempt_statuses=["ERROR", "ERROR"],
            pass_attempts=0,
            min_pass_attempts=1,
        )
        self.assertEqual(status, "ERROR")

    def test_should_stop_attempts_when_requirement_met(self) -> None:
        should_stop = _should_stop_attempts(
            pass_attempts=2,
            attempts_done=2,
            case_attempts=3,
            min_pass_attempts=2,
        )
        self.assertTrue(should_stop)

    def test_should_stop_attempts_when_requirement_unreachable(self) -> None:
        should_stop = _should_stop_attempts(
            pass_attempts=0,
            attempts_done=2,
            case_attempts=3,
            min_pass_attempts=2,
        )
        self.assertTrue(should_stop)

    def test_should_continue_when_requirement_still_reachable(self) -> None:
        should_stop = _should_stop_attempts(
            pass_attempts=0,
            attempts_done=1,
            case_attempts=3,
            min_pass_attempts=2,
        )
        self.assertFalse(should_stop)

    def test_case_confidence_high_for_clean_sweep(self) -> None:
        confidence = _case_confidence_bucket(
            final_status="PASS",
            attempt_statuses=["PASS", "PASS"],
            pass_attempts=2,
            attempts_used=2,
        )
        self.assertEqual(confidence, "high")

    def test_case_confidence_medium_for_recovered_pass(self) -> None:
        confidence = _case_confidence_bucket(
            final_status="PASS",
            attempt_statuses=["FAIL", "PASS", "PASS"],
            pass_attempts=2,
            attempts_used=3,
        )
        self.assertEqual(confidence, "medium")

    def test_case_confidence_low_for_failure(self) -> None:
        confidence = _case_confidence_bucket(
            final_status="FAIL",
            attempt_statuses=["FAIL", "FAIL"],
            pass_attempts=0,
            attempts_used=2,
        )
        self.assertEqual(confidence, "low")

    def test_build_confidence_counts(self) -> None:
        counts = _build_confidence_counts(
            [
                {"confidence": "high"},
                {"confidence": "high"},
                {"confidence": "medium"},
                {"confidence": "low"},
                {"confidence": "unknown"},
            ]
        )
        self.assertEqual(counts, {"high": 2, "medium": 1, "low": 1})


if __name__ == "__main__":
    unittest.main()
