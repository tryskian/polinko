import unittest

from tools.eval_style import _resolve_case_status
from tools.eval_style import _should_stop_attempts
from tools.eval_style import build_parser


class StyleEvalTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
