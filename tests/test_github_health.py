from __future__ import annotations

import io
from contextlib import redirect_stdout
import unittest

from tools import github_health


class GitHubHealthTests(unittest.TestCase):
    def test_failed_workflow_run_is_reported(self) -> None:
        runs = [
            {
                "databaseId": 123,
                "workflowName": "CI",
                "displayTitle": "Refactor scripts",
                "headBranch": "codex/bigbrain/example",
                "conclusion": "failure",
            },
            {
                "databaseId": 124,
                "workflowName": "Dependency Review",
                "displayTitle": "Clean dependency check",
                "headBranch": "main",
                "conclusion": "success",
            },
        ]

        failures = github_health.failed_runs(runs)

        self.assertEqual([run["databaseId"] for run in failures], [123])

    def test_status_check_rollup_failure_is_reported(self) -> None:
        prs = [
            {
                "number": 9,
                "title": "Update helper scripts",
                "statusCheckRollup": [
                    {
                        "name": "build-hygiene",
                        "status": "COMPLETED",
                        "conclusion": "FAILURE",
                    },
                    {
                        "name": "markdownlint",
                        "status": "COMPLETED",
                        "conclusion": "SUCCESS",
                    },
                ],
            }
        ]

        failures = github_health.pr_failures(prs)

        self.assertEqual(list(failures), [9])
        self.assertEqual(failures[9][0].name, "build-hygiene")
        self.assertEqual(failures[9][0].bucket, "fail")

    def test_pending_status_check_rollup_is_not_failure(self) -> None:
        prs = [
            {
                "number": 10,
                "title": "Watch checks",
                "statusCheckRollup": [
                    {"name": "test", "status": "IN_PROGRESS", "conclusion": None},
                ],
            }
        ]

        self.assertEqual(github_health.pr_failures(prs), {})
        self.assertEqual(github_health.pr_pending(prs)[10][0].bucket, "pending")

    def test_check_name_prefers_context_for_status_contexts(self) -> None:
        signal = github_health.classify_check(
            {"context": "dependency-review", "state": "SUCCESS"}
        )

        self.assertEqual(signal.name, "dependency-review")
        self.assertEqual(signal.bucket, "pass")

    def test_unknown_status_check_rollup_is_reported(self) -> None:
        prs = [
            {
                "number": 11,
                "title": "Unexpected check shape",
                "statusCheckRollup": [
                    {"name": "new-check", "status": "COMPLETED", "conclusion": None},
                ],
            }
        ]

        unknown = github_health.pr_unknown(prs)

        self.assertEqual(list(unknown), [11])
        self.assertEqual(unknown[11][0].name, "new-check")
        self.assertEqual(unknown[11][0].bucket, "unknown")

    def test_report_pr_checks_fails_unknown_rollup(self) -> None:
        prs = [
            {
                "number": 12,
                "title": "Needs attention",
                "statusCheckRollup": [
                    {"name": "new-check", "status": "COMPLETED", "conclusion": None},
                ],
            }
        ]
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = github_health.report_pr_checks(prs)

        self.assertEqual(result, 1)
        self.assertIn("[fail] open PR checks", stdout.getvalue())
        self.assertIn("new-check: COMPLETED", stdout.getvalue())

    def test_gh_command_adds_repo_when_supplied(self) -> None:
        command = github_health.gh_command(
            "gh",
            ["pr", "list"],
            "tryskian/polinko",
        )

        self.assertEqual(command, ["gh", "pr", "list", "--repo", "tryskian/polinko"])


if __name__ == "__main__":
    unittest.main()
