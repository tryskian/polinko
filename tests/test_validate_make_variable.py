from __future__ import annotations

import contextlib
import io
import unittest

from tools import validate_make_variable


class ValidateMakeVariableTests(unittest.TestCase):
    def test_nonblank_value_passes_without_output(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            status = validate_make_variable.validate_required_value(
                "tests.test_repo_search",
                usage="Usage: make test-one TEST=tests.test_repo_search",
            )

        self.assertEqual(status, 0)
        self.assertEqual(stdout.getvalue(), "")

    def test_blank_value_reports_usage_and_exits_two(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            status = validate_make_variable.validate_required_value(
                "  ",
                usage="Usage: make pycheck FILES=tools/repo_search.py",
            )

        self.assertEqual(status, 2)
        self.assertEqual(
            stdout.getvalue(),
            "Usage: make pycheck FILES=tools/repo_search.py\n",
        )

    def test_main_uses_supplied_usage(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            status = validate_make_variable.main(
                [
                    "--value",
                    "",
                    "--usage",
                    "Usage: make test-targeted TESTS=tests.test_repo_search",
                ]
            )

        self.assertEqual(status, 2)
        self.assertEqual(
            stdout.getvalue(),
            "Usage: make test-targeted TESTS=tests.test_repo_search\n",
        )


if __name__ == "__main__":
    unittest.main()
