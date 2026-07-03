"""Run environment doctor with Make-provided interpreter context."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def interpreter_source_label(python_path: str, python_origin: str) -> str:
    if python_origin == "command line":
        return "command-line PYTHON override"
    if python_origin in {"environment", "environment override"}:
        return "environment PYTHON override"

    if python_path.startswith(("./.venv/", ".venv/")):
        return "repo .venv selected by Make"
    if python_path == "python3":
        return "host python3 fallback selected by Make"
    return "make PYTHON"


def active_venv_for_python(python_path: str, *, cwd: Path | None = None) -> str | None:
    path = Path(python_path)
    if path.name not in {"python", "python3"} and not path.name.startswith("python3."):
        return None
    if path.parent.name != "bin":
        return None

    root = cwd or Path.cwd()
    venv_path = path.parent.parent
    if not venv_path.is_absolute():
        venv_path = root / venv_path
    return str(venv_path.resolve())


def run_doctor_env(*, python_path: str, python_origin: str) -> int:
    env = os.environ.copy()
    active_venv = active_venv_for_python(python_path)
    env["POLINKO_DOCTOR_INTERPRETER_SOURCE"] = interpreter_source_label(
        python_path,
        python_origin,
    )

    if active_venv:
        env["VIRTUAL_ENV"] = active_venv
        env["PATH"] = f"{active_venv}/bin:{env.get('PATH', '')}"

    result = subprocess.run(
        [python_path, "-m", "tools.doctor_env"],
        env=env,
        check=False,
    )
    return result.returncode


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run tools.doctor_env with Make interpreter metadata."
    )
    parser.add_argument("--python", required=True, help="Python command from Make.")
    parser.add_argument(
        "--python-origin",
        required=True,
        help="Make origin for the PYTHON variable.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return run_doctor_env(python_path=args.python, python_origin=args.python_origin)


if __name__ == "__main__":
    raise SystemExit(main())
