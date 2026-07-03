"""Print or launch local runtime URLs for Make targets."""

from __future__ import annotations

import argparse
import subprocess
import sys

VALID_LAUNCH_MODES = {"none", "system"}


def run_local_url(
    *,
    url: str,
    label: str,
    mode: str,
    launcher: str | None = None,
) -> int:
    if mode not in VALID_LAUNCH_MODES:
        print(
            f"Invalid LOCAL_BROWSER_LAUNCH='{mode}' (expected none or system).",
            file=sys.stderr,
        )
        return 2

    if mode == "system":
        if not launcher:
            print(
                "local URL helper: launcher script is required for system launch",
                file=sys.stderr,
            )
            return 2
        result = subprocess.run(["bash", launcher, url], check=False)
        if result.returncode != 0:
            return result.returncode

    print(f"{label}: {url}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print or launch a local runtime URL.")
    parser.add_argument("--url", required=True, help="Local URL to print or launch.")
    parser.add_argument("--label", required=True, help="Operator-facing URL label.")
    parser.add_argument(
        "--mode",
        default="none",
        help="Launch mode. Expected values: none or system.",
    )
    parser.add_argument(
        "--launcher",
        help="Launcher script used when --mode is system.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return run_local_url(
        url=args.url,
        label=args.label,
        mode=args.mode,
        launcher=args.launcher,
    )


if __name__ == "__main__":
    raise SystemExit(main())
