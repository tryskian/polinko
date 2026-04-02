import unittest

from tools.eval_ocr_stability import _normalise_text
from tools.eval_ocr_stability import _summarise_reports
from tools.eval_ocr_stability import build_parser


def _report(run_id: str, cases: list[dict[str, object]]) -> dict[str, object]:
    return {
        "run_id": run_id,
        "summary": {
            "total": len(cases),
            "passed": sum(1 for case in cases if case.get("status") == "PASS"),
            "failed": sum(1 for case in cases if case.get("status") != "PASS"),
            "errors": sum(1 for case in cases if case.get("status") == "ERROR"),
        },
        "cases": cases,
    }


class OcrStabilityTests(unittest.TestCase):
    def test_build_parser_defaults_timeout_to_eval_ocr_timeout(self) -> None:
        args = build_parser().parse_args(["--cases", "dummy.json"])
        self.assertEqual(args.timeout, 90)
        self.assertEqual(args.max_consecutive_rate_limit_errors, 0)
        self.assertEqual(args.case_delay_ms, 0)
        self.assertEqual(args.rate_limit_cooldown_ms, 0)
        self.assertFalse(args.stop_on_rate_limit_abort)

    def test_build_parser_accepts_stop_on_rate_limit_abort(self) -> None:
        args = build_parser().parse_args(
            ["--cases", "dummy.json", "--stop-on-rate-limit-abort"]
        )
        self.assertTrue(args.stop_on_rate_limit_abort)

    def test_normalise_text_collapses_whitespace(self) -> None:
        self.assertEqual(_normalise_text(" a   b \n c "), "a b c")

    def test_summarise_reports_marks_flaky_mixed_outcome(self) -> None:
        reports = [
            _report(
                "r1",
                [
                    {
                        "id": "case-1",
                        "status": "PASS",
                        "char_count": 10,
                        "extracted_text": "alpha",
                    },
                ],
            ),
            _report(
                "r2",
                [
                    {
                        "id": "case-1",
                        "status": "FAIL",
                        "char_count": 9,
                        "extracted_text": "alpha",
                    },
                ],
            ),
        ]

        summary, cases = _summarise_reports(reports=reports, expected_runs=2)
        self.assertEqual(summary["cases_total"], 1)
        self.assertEqual(summary["decision_flaky_cases"], 1)
        self.assertEqual(summary["stable_decision_cases"], 0)
        self.assertFalse(cases[0]["decision_stable"])
        self.assertEqual(cases[0]["pass_runs"], 1)
        self.assertEqual(cases[0]["fail_runs"], 1)

    def test_summarise_reports_tracks_output_variants_for_pass_cases(self) -> None:
        reports = [
            _report(
                "r1",
                [
                    {
                        "id": "case-1",
                        "status": "PASS",
                        "char_count": 12,
                        "extracted_text": "alpha beta",
                    },
                ],
            ),
            _report(
                "r2",
                [
                    {
                        "id": "case-1",
                        "status": "PASS",
                        "char_count": 13,
                        "extracted_text": "alpha  beta !",
                    },
                ],
            ),
        ]

        summary, cases = _summarise_reports(reports=reports, expected_runs=2)
        self.assertEqual(summary["stable_decision_cases"], 1)
        self.assertEqual(summary["output_variant_cases"], 1)
        self.assertTrue(cases[0]["always_pass"])
        self.assertEqual(cases[0]["text_variant_count"], 2)


if __name__ == "__main__":
    unittest.main()
