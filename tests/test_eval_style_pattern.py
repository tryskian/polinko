import unittest

from tools.eval_style_pattern import _assess_case
from tools.eval_style_pattern import _dominance_ratio
from tools.eval_style_pattern import _last_visible_char
from tools.eval_style_pattern import _max_consecutive_repeat


class StylePatternEvalTests(unittest.TestCase):
    def test_last_visible_char_ignores_trailing_whitespace(self) -> None:
        self.assertEqual(_last_visible_char("hello   "), "o")
        self.assertIsNone(_last_visible_char("   "))

    def test_max_consecutive_repeat_counts_runs(self) -> None:
        self.assertEqual(_max_consecutive_repeat([]), 0)
        self.assertEqual(_max_consecutive_repeat(["a"]), 1)
        self.assertEqual(_max_consecutive_repeat(["a", "a", "b", "b", "b"]), 3)

    def test_dominance_ratio(self) -> None:
        self.assertEqual(_dominance_ratio([]), 0.0)
        self.assertAlmostEqual(_dominance_ratio(["*", "*", "."]), 2 / 3)

    def test_assess_case_passes_when_metrics_within_thresholds(self) -> None:
        case = {
            "max_avg_words": 4.0,
            "max_words_per_turn": 8,
            "min_unique_ratio": 0.5,
            "max_consecutive_repeat": 2,
            "max_filler_hits": 0,
            "max_tail_motif_dominance": 0.9,
            "motif_chars": ["*"],
        }
        result = _assess_case(
            case=case,
            responses=["hi", "yo*", "ok"],
            word_counts=[1, 1, 1],
            filler_hits_by_turn=[[], [], []],
            tail_chars=["i", "*", "k"],
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["reasons"], [])
        self.assertAlmostEqual(result["metrics"]["unique_ratio"], 1.0)

    def test_assess_case_flags_collapse_and_filler_and_motif_dominance(self) -> None:
        case = {
            "max_avg_words": 3.0,
            "max_words_per_turn": 5,
            "min_unique_ratio": 0.8,
            "max_consecutive_repeat": 2,
            "max_filler_hits": 0,
            "max_tail_motif_dominance": 0.6,
            "motif_chars": ["*"],
        }
        result = _assess_case(
            case=case,
            responses=["steady.", "steady.", "steady.", "steady."],
            word_counts=[1, 1, 1, 1],
            filler_hits_by_turn=[["steady."], ["steady."], [], []],
            tail_chars=["*", "*", "*", "*"],
        )
        self.assertFalse(result["passed"])
        self.assertTrue(any("unique_ratio" in reason for reason in result["reasons"]))
        self.assertTrue(any("max_consecutive_repeat" in reason for reason in result["reasons"]))
        self.assertTrue(any("filler_hits" in reason for reason in result["reasons"]))
        self.assertTrue(any("tail_motif_dominance" in reason for reason in result["reasons"]))


if __name__ == "__main__":
    unittest.main()
