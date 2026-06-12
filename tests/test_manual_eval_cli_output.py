import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from typing import Any

from tools.manual_eval_cli_output import finish_manual_eval_report


def _format_report(report: dict[str, Any]) -> str:
    return f"state={report.get('state')}"


class ManualEvalCliOutputTests(unittest.TestCase):
    def test_finish_manual_eval_report_prints_text_and_default_status(self) -> None:
        stdout = StringIO()

        with redirect_stdout(stdout):
            status = finish_manual_eval_report(
                {"state": "ok"},
                _format_report,
                json_output=False,
            )

        self.assertEqual(stdout.getvalue(), "state=ok\n")
        self.assertEqual(status, 0)

    def test_finish_manual_eval_report_prints_json_and_mapped_status(self) -> None:
        stdout = StringIO()

        with redirect_stdout(stdout):
            status = finish_manual_eval_report(
                {"state": "blocked", "detail": "needs input"},
                _format_report,
                json_output=True,
                status_by_state={"blocked": 2},
            )

        self.assertEqual(
            json.loads(stdout.getvalue()),
            {"state": "blocked", "detail": "needs input"},
        )
        self.assertEqual(status, 2)

    def test_finish_manual_eval_report_uses_default_for_unknown_state(self) -> None:
        stdout = StringIO()

        with redirect_stdout(stdout):
            status = finish_manual_eval_report(
                {"state": "unexpected"},
                _format_report,
                json_output=False,
                status_by_state={"ok": 0},
                default_status=2,
            )

        self.assertEqual(stdout.getvalue(), "state=unexpected\n")
        self.assertEqual(status, 2)


if __name__ == "__main__":
    unittest.main()
