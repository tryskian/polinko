from __future__ import annotations

import argparse
import datetime as dt
import re
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
    return parser.parse_args()


def find_last_updated(path: Path) -> str | None:
    match = re.search(
        r"^Last updated:\s*(\d{4}-\d{2}-\d{2})\s*$", path.read_text(), re.MULTILINE
    )
    if match is None:
        return None
    return match.group(1)


def main() -> int:
    args = parse_args()
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
