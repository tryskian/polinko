"""Count cases in repo-native eval case JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def count_cases(payload: dict[str, Any]) -> int:
    cases = payload.get("cases", [])
    if not isinstance(cases, list):
        raise RuntimeError("Expected 'cases' to be a list.")
    return len(cases)


def count_cases_file(path: Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return count_cases(payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print the number of entries in a case JSON payload's cases list."
    )
    parser.add_argument("path", help="Path to eval case JSON.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    print(count_cases_file(Path(args.path)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
