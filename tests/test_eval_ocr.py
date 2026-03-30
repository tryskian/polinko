import unittest

from tools.eval_ocr import _check_case


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
        self.assertTrue(any("invalid must_match_regex pattern" in reason for reason in reasons))

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

    def test_must_contain_any_allows_single_char_ocr_drift(self) -> None:
        case = self._base_case()
        case["must_contain_any"] = ["chattiest"]
        passed, reasons = _check_case(case, "CHATTEST day in 2025")
        self.assertTrue(passed)
        self.assertEqual(reasons, [])

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


if __name__ == "__main__":
    unittest.main()
