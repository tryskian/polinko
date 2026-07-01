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
                "event": "pull_request",
                "conclusion": "failure",
                "createdAt": "2026-06-30T10:00:00Z",
            },
            {
                "databaseId": 124,
                "workflowName": "Dependency Review",
                "displayTitle": "Clean dependency check",
                "headBranch": "main",
                "event": "pull_request",
                "conclusion": "success",
                "createdAt": "2026-06-30T10:01:00Z",
            },
        ]

        failures = github_health.failed_runs(runs)

        self.assertEqual([run["databaseId"] for run in failures], [123])

    def test_superseded_failed_workflow_run_is_ignored(self) -> None:
        runs = [
            {
                "databaseId": 125,
                "workflowName": "CI",
                "displayTitle": "First attempt",
                "headBranch": "codex/bigbrain/example",
                "event": "pull_request",
                "conclusion": "failure",
                "createdAt": "2026-06-30T10:00:00Z",
            },
            {
                "databaseId": 126,
                "workflowName": "CI",
                "displayTitle": "Second attempt",
                "headBranch": "codex/bigbrain/example",
                "event": "pull_request",
                "conclusion": "success",
                "createdAt": "2026-06-30T10:02:00Z",
            },
        ]

        failures = github_health.failed_runs(runs)

        self.assertEqual(failures, [])

    def test_latest_failed_workflow_run_is_reported(self) -> None:
        runs = [
            {
                "databaseId": 127,
                "workflowName": "CI",
                "displayTitle": "First attempt",
                "headBranch": "codex/bigbrain/example",
                "event": "pull_request",
                "conclusion": "success",
                "createdAt": "2026-06-30T10:00:00Z",
            },
            {
                "databaseId": 128,
                "workflowName": "CI",
                "displayTitle": "Second attempt",
                "headBranch": "codex/bigbrain/example",
                "event": "pull_request",
                "conclusion": "failure",
                "createdAt": "2026-06-30T10:02:00Z",
            },
        ]

        failures = github_health.failed_runs(runs)

        self.assertEqual([run["databaseId"] for run in failures], [128])

    def test_report_failed_runs_uses_latest_surface_label(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            result = github_health.report_failed_runs([])

        self.assertEqual(result, 0)
        self.assertIn("[ok] latest workflow surfaces", stdout.getvalue())

    def test_pending_workflow_run_is_reported_without_failure(self) -> None:
        runs = [
            {
                "databaseId": 129,
                "workflowName": "CI",
                "displayTitle": "Run checks",
                "headBranch": "codex/bigbrain/example",
                "event": "pull_request",
                "status": "in_progress",
                "conclusion": None,
                "createdAt": "2026-06-30T10:03:00Z",
            }
        ]
        stdout = io.StringIO()

        self.assertEqual(
            [run["databaseId"] for run in github_health.pending_runs(runs)], [129]
        )
        with redirect_stdout(stdout):
            result = github_health.report_failed_runs(runs)

        self.assertEqual(result, 0)
        self.assertIn("[info] latest workflow surfaces pending", stdout.getvalue())
        self.assertIn("CI #129: in_progress", stdout.getvalue())
        self.assertIn("action: gh run watch 129", stdout.getvalue())

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
