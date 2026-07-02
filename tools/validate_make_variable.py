"""Validate required Make variable values before target work begins."""

from __future__ import annotations

import argparse
import sys


def validate_required_value(value: str, *, usage: str) -> int:
    if value.strip():
        return 0
    print(usage)
    return 2


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a required Make variable value."
    )
    parser.add_argument(
        "--value",
        required=True,
        help="Make variable value to validate.",
    )
    parser.add_argument(
        "--usage",
        required=True,
        help="Usage line to print when the value is blank.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return validate_required_value(args.value, usage=args.usage)


if __name__ == "__main__":
    raise SystemExit(main())
