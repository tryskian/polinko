"""Run repo searches with explicit routine and full-source modes."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

COMMON_EXCLUDES = (
    ".git/**",
    ".venv/**",
    ".history/**",
    ".local/**",
    ".local_archive/**",
    "node_modules/**",
    "__pycache__/**",
    ".mypy_cache/**",
    "eval_reports/**",
    "output/**",
    ".pytest_cache/**",
    ".ruff_cache/**",
    ".playwright-cli/**",
)

ROUTINE_PATHS = (
    ".devcontainer",
    ".github",
    "apps",
    "docs/governance/CHARTER.md",
    "docs/governance/STATE.md",
    "docs/public",
    "docs/research",
    "docs/runtime",
    "makefiles",
    "src",
    "tests",
    "tools",
    ".dockerignore",
    ".gitattributes",
    ".gitignore",
    ".markdownlint-cli2.yaml",
    ".markdownlintignore",
    ".pre-commit-config.yaml",
    "Dockerfile",
    "Makefile",
    "README.md",
    "main.py",
    "mypy.ini",
    "package.json",
    "pyproject.toml",
    "pyrightconfig.json",
    "pytest.ini",
    "requirements.in",
    "requirements.notebook.txt",
    "server.py",
)

ROUTINE_EXCLUDES = (
    "docs/eval/**",
    "docs/governance/DECISIONS.md",
    "docs/peanut/**",
)


def _existing_paths(paths: tuple[str, ...]) -> list[str]:
    return [path for path in paths if (REPO_ROOT / path).exists()]


def build_command(query: str, *, mode: str) -> list[str]:
    command = ["rg", "-n", "--hidden"]
    for glob in COMMON_EXCLUDES:
        command.extend(["--glob", f"!{glob}"])

    if mode == "routine":
        for glob in ROUTINE_EXCLUDES:
            command.extend(["--glob", f"!{glob}"])
        command.extend(["--", query, *_existing_paths(ROUTINE_PATHS)])
        return command

    if mode == "full":
        command.extend(["--", query, "."])
        return command

    raise ValueError(f"Unsupported search mode: {mode}")


def run(query: str, *, mode: str) -> int:
    result = subprocess.run(build_command(query, mode=mode), cwd=REPO_ROOT)
    if result.returncode == 1:
        print("repo-search: no matches")
        return 0
    return result.returncode


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search Polinko with routine-safe or explicit full-source scope."
    )
    parser.add_argument("--query", required=True, help="Ripgrep pattern to search for.")
    parser.add_argument(
        "--mode",
        choices=("routine", "full"),
        default="routine",
        help="Search scope. routine avoids evidence/private/archive lanes; full is explicit.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    return run(args.query, mode=args.mode)


if __name__ == "__main__":
    raise SystemExit(main())
