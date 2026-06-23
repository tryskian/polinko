from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path


REQUIRED_DOCS = (Path("docs/governance/STATE.md"),)
OPTIONAL_LOCAL_DOCS = (Path("docs/peanut/governance/SESSION_HANDOFF.md"),)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that current-truth end docs were refreshed today."
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Expected ISO date for Last updated markers.",
    )
    parser.add_argument(
        "--expected-commit",
        default=None,
        help="Expected short commit hash for local SESSION_HANDOFF freshness.",
    )
    return parser.parse_args()


def find_last_updated(path: Path) -> str | None:
    match = re.search(
        r"^Last updated:\s*(\d{4}-\d{2}-\d{2})\s*$", path.read_text(), re.MULTILINE
    )
    if match is None:
        return None
    return match.group(1)


def current_git_commit() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def handoff_mentions_commit(path: Path, commit: str) -> bool:
    return commit in path.read_text(encoding="utf-8")


def main() -> int:
    args = parse_args()
    expected_commit = args.expected_commit or current_git_commit()
    failures: list[str] = []
    checked_docs: list[Path] = []

    for path in REQUIRED_DOCS:
        checked_docs.append(path)
        if not path.exists():
            failures.append(f"{path}: missing required current-truth doc")
            continue
        actual = find_last_updated(path)
        if actual != args.date:
            failures.append(
                f"{path}: Last updated is {actual or 'missing'}, expected {args.date}"
            )

    for path in OPTIONAL_LOCAL_DOCS:
        if not path.exists():
            continue
        checked_docs.append(path)
        actual = find_last_updated(path)
        if actual != args.date:
            failures.append(
                f"{path}: Last updated is {actual or 'missing'}, expected {args.date}"
            )
            continue
        if expected_commit is not None and not handoff_mentions_commit(
            path, expected_commit
        ):
            failures.append(
                f"{path}: missing current commit {expected_commit} in active handoff"
            )

    if failures:
        print("end-docs-check: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        print(
            "Update current-truth docs before end: docs/governance/STATE.md and "
            "local docs/peanut/governance/SESSION_HANDOFF.md if present",
            file=sys.stderr,
        )
        return 1

    print(f"end-docs-check: PASS ({len(checked_docs)} docs updated for {args.date})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
