import unittest
from unittest import mock

from tools.eval_ocr import _check_case
from tools.eval_ocr import _is_rate_limit_ocr_error_message
from tools.eval_ocr import _is_transient_ocr_error
from tools.eval_ocr import _ocr_with_retries
from tools.eval_ocr import _select_cases
from tools.eval_ocr import OcrRequestError
from tools.eval_ocr import build_parser


class OcrEvalRuleTests(unittest.TestCase):
    @staticmethod
    def _base_case() -> dict[str, object]:
        return {
            "case_sensitive": False,
            "must_contain": [],
            "must_contain_any": [],
            "must_not_contain": [],
            "must_not_contain_words": [],
            "must_appear_in_order": [],
            "must_match_regex": [],
            "must_not_match_regex": [],
            "min_chars": None,
            "max_chars": None,
        }

    def test_whole_word_forbidden_does_not_match_substring(self) -> None:
        case = self._base_case()
        case["must_not_contain_words"] = ["art"]
        passed, reasons = _check_case(case, "partial")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_whole_word_forbidden_matches_word_boundary(self) -> None:
        case = self._base_case()
        case["must_not_contain_words"] = ["art"]
        passed, reasons = _check_case(case, "this has art inside")
        self.assertFalse(passed)
        self.assertTrue(any("forbidden whole word" in reason for reason in reasons))

    def test_ordered_phrases_pass_when_in_order(self) -> None:
        case = self._base_case()
        case["must_appear_in_order"] = ["we", "perceive", "through"]
        passed, reasons = _check_case(case, "we now perceive motion through lenses")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_ordered_phrases_fail_when_out_of_order(self) -> None:
        case = self._base_case()
        case["must_appear_in_order"] = ["we", "perceive", "through"]
        passed, reasons = _check_case(case, "we move through and then perceive")
        self.assertFalse(passed)
        self.assertTrue(any("missing ordered phrase" in reason for reason in reasons))

    def test_regex_required_and_forbidden_rules(self) -> None:
        case = self._base_case()
        case["must_match_regex"] = [r"\bCROSSED_OUT:\w+\b"]
        case["must_not_match_regex"] = [r"\bor\b"]
        passed, reasons = _check_case(case, "WE [CROSSED_OUT:UNDERSTAND] PERCEIVE")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_invalid_regex_is_reported(self) -> None:
        case = self._base_case()
        case["must_match_regex"] = ["("]
        passed, reasons = _check_case(case, "text")
        self.assertFalse(passed)
        self.assertTrue(
            any("invalid must_match_regex pattern" in reason for reason in reasons)
        )

    def test_length_bounds_are_enforced(self) -> None:
        case = self._base_case()
        case["min_chars"] = 5
        case["max_chars"] = 10

        passed_short, reasons_short = _check_case(case, "hey")
        self.assertFalse(passed_short)
        self.assertTrue(any("text too short" in reason for reason in reasons_short))

        passed_long, reasons_long = _check_case(case, "this is definitely too long")
        self.assertFalse(passed_long)
        self.assertTrue(any("text too long" in reason for reason in reasons_long))

    def test_must_contain_any_matches_spaced_letter_tokens(self) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["chattiest"]
        passed, reasons = _check_case(case, "C H A T T I E S T day in 2025")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_matches_mixed_split_letter_tokens(self) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["chattiest"]
        passed, reasons = _check_case(case, "CHAT T IEST day in 2025")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_matches_punctuation_split_tokens(self) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["toah"]
        passed, reasons = _check_case(case, "Sotterrt To-AH")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_matches_multiline_phrase_tokens(self) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["beyond existence"]
        passed, reasons = _check_case(case, "some\nBEYOND\nEXISTENCE\nINTERCEIVABLE")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_matches_connector_punctuation_phrase_tokens(self) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["interceivable vs. perceivable"]
        passed, reasons = _check_case(case, "INTERCEIVABLE v.s PERCEIVABLE")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_matches_marked_up_phrase_tokens(self) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["### Impact on human psyche"]
        passed, reasons = _check_case(case, "- impact on human psyche\nNAR + DESIGN")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_allows_single_char_ocr_drift(self) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["chattiest"]
        passed, reasons = _check_case(case, "CHATTEST day in 2025")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_allows_vowel_drop_signature_match(self) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["stirring"]
        passed, reasons = _check_case(case, "There seems to be something strong.")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_appear_in_order_allows_vowel_drop_signature_match(self) -> None:
        case = self._base_case()
        case["must_appear_in_order"] = ["something", "stirring"]
        passed, reasons = _check_case(case, "There seems to be something strong.")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_allows_terminal_char_ocr_drift_for_long_anchor(
        self,
    ) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["stirring"]
        passed, reasons = _check_case(case, "something - stirriny")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_appear_in_order_allows_terminal_char_ocr_drift_for_long_anchor(
        self,
    ) -> None:
        case = self._base_case()
        case["must_appear_in_order"] = ["something", "stirring"]
        passed, reasons = _check_case(case, "something - stirriny")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_allows_near_signature_match_for_long_anchor(self) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["stirring"]
        passed, reasons = _check_case(case, "something - starving")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_appear_in_order_allows_near_signature_match_for_long_anchor(
        self,
    ) -> None:
        case = self._base_case()
        case["must_appear_in_order"] = ["something", "stirring"]
        passed, reasons = _check_case(case, "something - starving")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_allows_signature_match_with_different_last_letter(
        self,
    ) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["stirring"]
        passed, reasons = _check_case(case, "There seems to be something strange.")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_must_contain_any_allows_terminal_char_drift_for_seven_char_anchor(
        self,
    ) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["tumbles"]
        passed_tumbler, reasons_tumbler = _check_case(case, "archive tumbler floating")
        self.assertTrue(passed_tumbler)
        self.assertEqual(reasons_tumbler, [])

        passed_tumblies, reasons_tumblies = _check_case(
            case,
            "archive tumblies floating",
        )
        self.assertTrue(passed_tumblies)
        self.assertEqual(reasons_tumblies, [])

    def test_must_appear_in_order_allows_terminal_char_drift_for_seven_char_anchor(
        self,
    ) -> None:
        case = self._base_case()
        case["must_appear_in_order"] = ["archive", "tumbles", "floating"]
        passed_tumbler, reasons_tumbler = _check_case(case, "archive tumbler floating")
        self.assertTrue(passed_tumbler)
        self.assertEqual(reasons_tumbler, [])

        passed_tumblies, reasons_tumblies = _check_case(
            case,
            "archive tumblies floating",
        )
        self.assertTrue(passed_tumblies)
        self.assertEqual(reasons_tumblies, [])

    def test_forbidden_word_matches_spaced_letter_tokens(self) -> None:
        case = self._base_case()
        case["must_not_contain_words"] = ["guess"]
        passed, reasons = _check_case(case, "G U E S S it says matrix")
        self.assertFalse(passed)
        self.assertTrue(any("forbidden whole word" in reason for reason in reasons))

    def test_forbidden_word_matches_mixed_split_letter_tokens(self) -> None:
        case = self._base_case()
        case["must_not_contain_words"] = ["guess"]
        passed, reasons = _check_case(case, "GU ESS it says matrix")
        self.assertFalse(passed)
        self.assertTrue(any("forbidden whole word" in reason for reason in reasons))

    def test_forbidden_phrase_does_not_use_near_match(self) -> None:
        case = self._base_case()
        case["must_not_contain"] = ["chattiest"]
        passed, reasons = _check_case(case, "CHATTEST day in 2025")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

    def test_select_cases_returns_all_by_default(self) -> None:
        cases = [{"id": "c1"}, {"id": "c2"}, {"id": "c3"}]
        selected = _select_cases(cases)
        self.assertEqual(selected, cases)

    def test_select_cases_applies_offset_and_max(self) -> None:
        cases = [{"id": "c1"}, {"id": "c2"}, {"id": "c3"}, {"id": "c4"}]
        selected = _select_cases(cases, offset=1, max_cases=2)
        self.assertEqual(selected, [{"id": "c2"}, {"id": "c3"}])

    def test_select_cases_accepts_offset_beyond_end(self) -> None:
        cases = [{"id": "c1"}]
        selected = _select_cases(cases, offset=2, max_cases=0)
        self.assertEqual(selected, [])

    def test_select_cases_rejects_negative_values(self) -> None:
        with self.assertRaises(RuntimeError):
            _select_cases([{"id": "c1"}], offset=-1)
        with self.assertRaises(RuntimeError):
            _select_cases([{"id": "c1"}], max_cases=-1)

    def test_is_transient_ocr_error_detects_timeout_signatures(self) -> None:
        self.assertTrue(
            _is_transient_ocr_error(
                RuntimeError(
                    "POST /skills/ocr failed: connection error - Read timed out."
                ),
            )
        )
        self.assertTrue(
            _is_transient_ocr_error(
                RuntimeError("POST /skills/ocr failed: HTTP 503 - service unavailable"),
            )
        )
        self.assertTrue(
            _is_transient_ocr_error(
                RuntimeError("POST /skills/ocr failed: HTTP 429 - too many requests"),
            )
        )
        self.assertFalse(
            _is_transient_ocr_error(
                RuntimeError("POST /skills/ocr failed: HTTP 422 - validation error"),
            )
        )

    def test_is_rate_limit_ocr_error_message_detects_expected_signatures(self) -> None:
        self.assertTrue(
            _is_rate_limit_ocr_error_message("HTTP 429 - OCR rate limit reached.")
        )
        self.assertTrue(_is_rate_limit_ocr_error_message("provider rate limit reached"))
        self.assertFalse(
            _is_rate_limit_ocr_error_message("HTTP 503 - service unavailable")
        )

    def test_build_parser_defaults_max_consecutive_rate_limit_errors_to_zero(
        self,
    ) -> None:
        args = build_parser().parse_args([])
        self.assertEqual(args.max_consecutive_rate_limit_errors, 0)
        self.assertEqual(args.case_delay_ms, 0)
        self.assertEqual(args.rate_limit_cooldown_ms, 0)

    def test_ocr_with_retries_retries_transient_then_succeeds(self) -> None:
        side_effects = [
            RuntimeError("POST /skills/ocr failed: connection error - Read timed out."),
            {"run": {"extracted_text": "ok"}},
        ]
        with (
            mock.patch("tools.eval_ocr._ocr", side_effect=side_effects) as mock_ocr,
            mock.patch("tools.eval_ocr.time.sleep") as mock_sleep,
        ):
            payload = _ocr_with_retries(
                base_url="http://127.0.0.1:8000",
                headers={},
                session_id="s-retry",
                source_name="case.png",
                mime_type="image/png",
                data_base64="MA==",
                text_hint=None,
                visual_context_hint=None,
                transcription_mode="verbatim",
                timeout=90,
                ocr_retries=2,
                ocr_retry_delay_ms=1,
            )
        self.assertEqual(payload, {"run": {"extracted_text": "ok"}})
        self.assertEqual(mock_ocr.call_count, 2)
        mock_sleep.assert_called_once()

    def test_ocr_with_retries_does_not_retry_non_transient(self) -> None:
        with mock.patch(
            "tools.eval_ocr._ocr",
            side_effect=RuntimeError(
                "POST /skills/ocr failed: HTTP 422 - validation error"
            ),
        ) as mock_ocr:
            with self.assertRaises(RuntimeError):
                _ocr_with_retries(
                    base_url="http://127.0.0.1:8000",
                    headers={},
                    session_id="s-noretry",
                    source_name="case.png",
                    mime_type="image/png",
                    data_base64="MA==",
                    text_hint=None,
                    visual_context_hint=None,
                    transcription_mode="verbatim",
                    timeout=90,
                    ocr_retries=2,
                    ocr_retry_delay_ms=1,
                )
        self.assertEqual(mock_ocr.call_count, 1)

    def test_ocr_with_retries_honors_retry_after_on_429(self) -> None:
        side_effects = [
            OcrRequestError(
                method="POST",
                path="/skills/ocr",
                status_code=429,
                detail="rate limit",
                retry_after_s=7,
            ),
            {"run": {"extracted_text": "ok"}},
        ]
        with (
            mock.patch("tools.eval_ocr._ocr", side_effect=side_effects) as mock_ocr,
            mock.patch("tools.eval_ocr.time.sleep") as mock_sleep,
        ):
            payload = _ocr_with_retries(
                base_url="http://127.0.0.1:8000",
                headers={},
                session_id="s-retry-after",
                source_name="case.png",
                mime_type="image/png",
                data_base64="MA==",
                text_hint=None,
                visual_context_hint=None,
                transcription_mode="verbatim",
                timeout=90,
                ocr_retries=2,
                ocr_retry_delay_ms=250,
            )
        self.assertEqual(payload, {"run": {"extracted_text": "ok"}})
        self.assertEqual(mock_ocr.call_count, 2)
        mock_sleep.assert_called_once_with(7.0)


if __name__ == "__main__":
    unittest.main()
