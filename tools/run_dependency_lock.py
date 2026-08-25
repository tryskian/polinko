"""Run dependency lockfile workflows with Make-provided paths."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def emit_process_output(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)


def piptools_available(python: str) -> bool:
    result = subprocess.run(
        [python, "-m", "piptools", "--version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def ensure_pip_tools(python: str, pip_tools_version: str) -> int:
    if piptools_available(python):
        return 0

    result = subprocess.run(
        [python, "-m", "pip", "install", f"pip-tools=={pip_tools_version}"],
        check=False,
    )
    return result.returncode


def compile_lockfile(
    *,
    python: str,
    requirements_in: str,
    requirements_lock: str,
) -> int:
    args = [
        python,
        "-m",
        "piptools",
        "compile",
        "--resolver=backtracking",
        "--allow-unsafe",
        "--strip-extras",
        "--output-file",
        requirements_lock,
        requirements_in,
    ]
    result = subprocess.run(
        args,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        emit_process_output(result)
        return result.returncode
    print(f"dependency-lock: compiled {requirements_lock} from {requirements_in}")
    return result.returncode


def read_lockfile_bytes(requirements_lock: str) -> bytes | None:
    try:
        return Path(requirements_lock).read_bytes()
    except FileNotFoundError:
        return None


def verify_lockfile_unchanged(
    requirements_lock: str, before_compile: bytes | None
) -> int:
    after_compile = read_lockfile_bytes(requirements_lock)
    if after_compile == before_compile:
        print(f"dependency-lock: {requirements_lock} is current")
        return 0

    print(
        f"dependency-lock: {requirements_lock} changed after compile; "
        "run make deps-lock and commit the generated lockfile"
    )
    return 1


def run_dependency_lock(
    *,
    python: str,
    requirements_in: str,
    requirements_lock: str,
    ensure_bootstrap: bool,
    pip_tools_version: str | None,
    check_lockfile: bool,
) -> int:
    if ensure_bootstrap:
        if not pip_tools_version:
            raise ValueError(
                "pip_tools_version is required when ensure_bootstrap is set"
            )
        bootstrap_status = ensure_pip_tools(python, pip_tools_version)
        if bootstrap_status != 0:
            return bootstrap_status

    lockfile_before_compile = (
        read_lockfile_bytes(requirements_lock) if check_lockfile else None
    )

    compile_status = compile_lockfile(
        python=python,
        requirements_in=requirements_in,
        requirements_lock=requirements_lock,
    )
    if compile_status != 0:
        return compile_status

    if check_lockfile:
        return verify_lockfile_unchanged(requirements_lock, lockfile_before_compile)

    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run pip-tools lockfile workflows from Make."
    )
    parser.add_argument("--python", required=True, help="Python command from Make.")
    parser.add_argument(
        "--requirements-in",
        required=True,
        help="Direct dependency input file.",
    )
    parser.add_argument(
        "--requirements-lock",
        required=True,
        help="Generated dependency lockfile.",
    )
    parser.add_argument(
        "--pip-tools-version",
        help="pip-tools version to install when bootstrapping is enabled.",
    )
    parser.add_argument(
        "--ensure-pip-tools",
        action="store_true",
        help="Install pip-tools when it is not available.",
    )
    parser.add_argument(
        "--check-lockfile",
        action="store_true",
        help="Fail when compiling changes the generated lockfile.",
    )
    args = parser.parse_args(argv)
    if args.ensure_pip_tools and not args.pip_tools_version:
        parser.error("--pip-tools-version is required with --ensure-pip-tools")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return run_dependency_lock(
        python=args.python,
        requirements_in=args.requirements_in,
        requirements_lock=args.requirements_lock,
        ensure_bootstrap=args.ensure_pip_tools,
        pip_tools_version=args.pip_tools_version,
        check_lockfile=args.check_lockfile,
    )


if __name__ == "__main__":
    raise SystemExit(main())
