import unittest
from typing import Any

from tools.eval_clip_ab import _aggregate_arm_results
from tools.eval_clip_ab import _parse_csv
from tools.eval_clip_ab import build_parser


class ClipABEvalTests(unittest.TestCase):
    def test_build_parser_defaults_to_clip_ab_cases(self) -> None:
        args = build_parser().parse_args([])
        self.assertEqual(args.cases, "docs/eval/cases/clip_ab_eval_cases.json")

    def test_parse_csv_normalizes_values(self) -> None:
        self.assertEqual(_parse_csv("image, OCR , pdf"), ["image", "ocr", "pdf"])

    def test_aggregate_arm_results_computes_rates(self) -> None:
        records: list[dict[str, Any]] = [
            {"arm": "baseline_mixed", "top1_hit": True, "any_hit": True},
            {"arm": "baseline_mixed", "top1_hit": False, "any_hit": True},
            {"arm": "clip_proxy_image_only", "top1_hit": True, "any_hit": True},
            {"arm": "clip_proxy_image_only", "top1_hit": True, "any_hit": True},
        ]
        summary = _aggregate_arm_results(records)
        self.assertAlmostEqual(summary["baseline_mixed"]["top1_rate"], 0.5)
        self.assertAlmostEqual(summary["baseline_mixed"]["any_rate"], 1.0)
        self.assertAlmostEqual(summary["clip_proxy_image_only"]["top1_rate"], 1.0)
        self.assertAlmostEqual(summary["clip_proxy_image_only"]["any_rate"], 1.0)

    def test_aggregate_arm_results_tracks_errors(self) -> None:
        records: list[dict[str, Any]] = [
            {"arm": "baseline_mixed", "error": "boom"},
            {"arm": "baseline_mixed", "top1_hit": True, "any_hit": True},
        ]
        summary = _aggregate_arm_results(records)
        self.assertEqual(summary["baseline_mixed"]["errors"], 1)
        self.assertEqual(summary["baseline_mixed"]["cases"], 2)


if __name__ == "__main__":
    unittest.main()
