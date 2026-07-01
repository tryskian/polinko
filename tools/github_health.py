from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


FAILED_CONCLUSIONS = {
    "ACTION_REQUIRED",
    "CANCELLED",
    "FAILURE",
    "STARTUP_FAILURE",
    "TIMED_OUT",
}

PENDING_STATES = {
    "EXPECTED",
    "IN_PROGRESS",
    "PENDING",
    "QUEUED",
    "REQUESTED",
    "WAITING",
}

PASS_CONCLUSIONS = {"NEUTRAL", "SKIPPED", "SUCCESS"}
PASS_STATES = {"SUCCESS"}


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class CheckSignal:
    name: str
    state: str
    bucket: str


class GitHubCommandError(RuntimeError):
    def __init__(self, command: tuple[str, ...], result: CommandResult) -> None:
        self.command = command
        self.result = result
        super().__init__(f"{' '.join(command)} failed with {result.returncode}")


def _normalise(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def check_name(check: dict[str, Any]) -> str:
    for key in ("name", "context", "workflowName", "appName"):
        value = check.get(key)
        if value:
            return str(value)
    return "unnamed check"


def classify_check(check: dict[str, Any]) -> CheckSignal:
    state = _normalise(check.get("state") or check.get("status"))
    conclusion = _normalise(check.get("conclusion"))
    if conclusion in FAILED_CONCLUSIONS or state in FAILED_CONCLUSIONS:
        bucket = "fail"
    elif state in PENDING_STATES:
        bucket = "pending"
    elif conclusion in PASS_CONCLUSIONS or state in PASS_STATES:
        bucket = "pass"
    else:
        bucket = "unknown"
    label = conclusion or state or "UNKNOWN"
    return CheckSignal(name=check_name(check), state=label, bucket=bucket)


def run_surface_key(run: dict[str, Any]) -> tuple[str, str, str]:
    workflow = str(run.get("workflowName") or "workflow")
    branch = str(run.get("headBranch") or "unknown branch")
    event = str(run.get("event") or "unknown event")
    return (workflow, branch, event)


def latest_runs_by_surface(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[tuple[str, str, str], dict[str, Any]] = {}
    for run in sorted(
        runs, key=lambda item: str(item.get("createdAt") or ""), reverse=True
    ):
        latest.setdefault(run_surface_key(run), run)
    return list(latest.values())


def failed_runs(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        run
        for run in latest_runs_by_surface(runs)
        if _normalise(run.get("conclusion")) in FAILED_CONCLUSIONS
    ]


def pr_check_signals(pr: dict[str, Any]) -> list[CheckSignal]:
    rollup = pr.get("statusCheckRollup") or []
    return [classify_check(check) for check in rollup if isinstance(check, dict)]


def pr_failures(prs: list[dict[str, Any]]) -> dict[int, list[CheckSignal]]:
    failures: dict[int, list[CheckSignal]] = {}
    for pr in prs:
        number = int(pr["number"])
        failed = [signal for signal in pr_check_signals(pr) if signal.bucket == "fail"]
        if failed:
            failures[number] = failed
    return failures


def pr_pending(prs: list[dict[str, Any]]) -> dict[int, list[CheckSignal]]:
    pending: dict[int, list[CheckSignal]] = {}
    for pr in prs:
        number = int(pr["number"])
        waiting = [
            signal for signal in pr_check_signals(pr) if signal.bucket == "pending"
        ]
        if waiting:
            pending[number] = waiting
    return pending


def pr_unknown(prs: list[dict[str, Any]]) -> dict[int, list[CheckSignal]]:
    unknown: dict[int, list[CheckSignal]] = {}
    for pr in prs:
        number = int(pr["number"])
        signals = [
            signal for signal in pr_check_signals(pr) if signal.bucket == "unknown"
        ]
        if signals:
            unknown[number] = signals
    return unknown


def run_command(command: list[str]) -> CommandResult:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        return CommandResult(returncode=127, stdout="", stderr=str(exc))
    return CommandResult(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def gh_command(gh: str, args: list[str], repo: str | None = None) -> list[str]:
    command = [gh, *args]
    if repo:
        command.extend(["--repo", repo])
    return command


def gh_json(gh: str, args: list[str], repo: str | None = None) -> Any:
    command = gh_command(gh, args, repo)
    result = run_command(command)
    if result.returncode != 0:
        raise GitHubCommandError(tuple(command), result)
    try:
        return json.loads(result.stdout or "null")
    except json.JSONDecodeError as exc:
        raise GitHubCommandError(
            tuple(command),
            CommandResult(
                returncode=1,
                stdout=result.stdout,
                stderr=f"invalid JSON output: {exc}",
            ),
        ) from exc


def print_command_failure(exc: GitHubCommandError) -> None:
    print(f"[fail] {' '.join(exc.command)}", file=sys.stderr)
    stderr = exc.result.stderr.strip()
    if stderr:
        print(f"  {stderr}", file=sys.stderr)


def auth_status(gh: str) -> bool:
    result = run_command([gh, "auth", "status"])
    if result.returncode == 0:
        print("[ok] gh auth status")
        return True

    print("[fail] gh auth status", file=sys.stderr)
    stderr = result.stderr.strip()
    if stderr:
        print(f"  {stderr}", file=sys.stderr)
    print("[action] gh auth login", file=sys.stderr)
    return False


def report_failed_runs(runs: list[dict[str, Any]]) -> int:
    failures = failed_runs(runs)
    if not failures:
        print("[ok] latest workflow surfaces")
        return 0

    print("[fail] latest workflow surfaces")
    for run in failures:
        run_id = run.get("databaseId")
        workflow = run.get("workflowName") or "workflow"
        title = run.get("displayTitle") or "untitled run"
        branch = run.get("headBranch") or "unknown branch"
        conclusion = run.get("conclusion") or "unknown"
        print(f"  - {workflow} #{run_id}: {conclusion} on {branch} - {title}")
        if run_id:
            print(f"    action: gh run view {run_id} --log-failed")
    return 1


def _pr_title(prs: list[dict[str, Any]], number: int) -> str:
    for pr in prs:
        if int(pr["number"]) == number:
            return str(pr.get("title") or "")
    return ""


def report_pr_checks(prs: list[dict[str, Any]]) -> int:
    failures = pr_failures(prs)
    pending = pr_pending(prs)
    unknown = pr_unknown(prs)

    if not prs:
        print("[ok] open PR checks")
        return 0

    if not failures and not pending and not unknown:
        print("[ok] open PR checks")
        return 0

    if pending:
        print("[info] open PR checks pending")
        for number, signals in pending.items():
            print(f"  - #{number}: {_pr_title(prs, number)}")
            for signal in signals:
                print(f"    - {signal.name}: {signal.state}")
            print(f"    action: gh pr checks {number} --watch --interval 10")

    if not failures and not unknown:
        return 0

    print("[fail] open PR checks")
    for number in sorted(set(failures) | set(unknown)):
        signals = failures.get(number, []) + unknown.get(number, [])
        print(f"  - #{number}: {_pr_title(prs, number)}")
        for signal in signals:
            print(f"    - {signal.name}: {signal.state}")
        print(f"    action: gh pr checks {number}")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report GitHub PR and workflow health for this repository."
    )
    parser.add_argument(
        "--gh",
        default="gh",
        help="GitHub CLI executable; defaults to gh",
    )
    parser.add_argument(
        "--repo",
        help="GitHub repository in owner/name form; defaults to the current checkout",
    )
    parser.add_argument(
        "--run-limit",
        type=int,
        default=20,
        help="number of recent workflow runs to inspect",
    )
    parser.add_argument(
        "--pr-limit",
        type=int,
        default=20,
        help="number of open pull requests to inspect",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print("GitHub health")

    if not auth_status(args.gh):
        return 1

    try:
        runs = gh_json(
            args.gh,
            [
                "run",
                "list",
                "--limit",
                str(args.run_limit),
                "--json",
                "databaseId,status,conclusion,workflowName,displayTitle,"
                "headBranch,event,createdAt,url",
            ],
            args.repo,
        )
        prs = gh_json(
            args.gh,
            [
                "pr",
                "list",
                "--state",
                "open",
                "--limit",
                str(args.pr_limit),
                "--json",
                "number,title,headRefName,statusCheckRollup,url",
            ],
            args.repo,
        )
    except GitHubCommandError as exc:
        print_command_failure(exc)
        return 1

    status = 0
    status |= report_failed_runs(runs if isinstance(runs, list) else [])
    status |= report_pr_checks(prs if isinstance(prs, list) else [])
    return status


if __name__ == "__main__":
    raise SystemExit(main())
