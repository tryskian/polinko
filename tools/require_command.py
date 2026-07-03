"""Validate that a required local command is available."""

from __future__ import annotations

import argparse
import shutil
import sys


def validate_command(command: str, *, label: str) -> int:
    if command and shutil.which(command) is not None:
        return 0
    print(f"{label}: missing required command: {command}", file=sys.stderr)
    return 127


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate availability for a required local command."
    )
    parser.add_argument("--command", required=True, help="Command name or path.")
    parser.add_argument(
        "--label",
        required=True,
        help="Operator-facing helper label used in diagnostics.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return validate_command(args.command, label=args.label)


if __name__ == "__main__":
    raise SystemExit(main())
