from __future__ import annotations

import contextlib
import io
import subprocess
import unittest
from unittest import mock

from tools import repo_search


class RepoSearchTests(unittest.TestCase):
    def test_blank_query_reports_make_usage(self) -> None:
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            self.assertEqual(
                repo_search.validate_query("", make_target="repo-search"),
                2,
            )

        self.assertEqual(stdout.getvalue(), 'Usage: make repo-search Q="pattern"\n')

    def test_check_query_exits_before_search(self) -> None:
        with mock.patch("tools.repo_search.subprocess.run") as run:
            self.assertEqual(
                repo_search.main(
                    [
                        "--check-query",
                        "--make-target",
                        "repo-search-full",
                        "--query",
                        "needle",
                    ]
                ),
                0,
            )

        run.assert_not_called()

    def test_routine_search_uses_safe_source_set(self) -> None:
        command = repo_search.build_command("needle", mode="routine")

        self.assertIn("docs/runtime", command)
        self.assertIn("tools", command)
        self.assertIn("tests", command)
        self.assertIn("!docs/peanut/**", command)
        self.assertIn("!docs/eval/**", command)
        self.assertIn("!docs/governance/DECISIONS.md", command)
        self.assertNotIn(".", command[command.index("--") + 2 :])

    def test_full_search_is_explicit_repo_scope(self) -> None:
        command = repo_search.build_command("needle", mode="full")

        self.assertEqual(command[-3:], ["--", "needle", "."])
        self.assertNotIn("!docs/peanut/**", command)
        self.assertNotIn("!docs/governance/DECISIONS.md", command)
        self.assertIn("!.local/**", command)
        self.assertIn("!.history/**", command)

    def test_no_matches_are_not_a_tooling_failure(self) -> None:
        with mock.patch("tools.repo_search.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess(args=["rg"], returncode=1)

            self.assertEqual(repo_search.run("missing", mode="routine"), 0)

    def test_rg_errors_still_fail(self) -> None:
        with mock.patch("tools.repo_search.subprocess.run") as run:
            run.return_value = subprocess.CompletedProcess(args=["rg"], returncode=2)

            self.assertEqual(repo_search.run("bad", mode="routine"), 2)

    def test_missing_rg_reports_operator_error(self) -> None:
        with mock.patch("tools.repo_search.subprocess.run") as run:
            run.side_effect = FileNotFoundError
            stderr = io.StringIO()

            with contextlib.redirect_stderr(stderr):
                self.assertEqual(repo_search.run("needle", mode="routine"), 127)

        self.assertIn("repo-search: missing required command: rg", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
