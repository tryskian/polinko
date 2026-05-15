from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent

TRACKED_SCOPE = "tracked"
LOCAL_SCOPE = "local"

LOCAL_ROOTS = (
    Path(".history"),
    Path(".local"),
    Path("docs/peanut"),
    Path(".vscode"),
    Path("api"),
    Path("tools"),
    Path("tests"),
    Path("Makefile"),
)

ALLOWLIST_PATHS = {
    Path("tools/path_leak_check.py"),
    Path("tests/test_path_leak_check.py"),
}

ALLOWLIST_PREFIXES = (
    Path("docs/peanut/transcripts"),
)

SKIP_SUFFIXES = {
    ".db",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".pyc",
    ".sqlite",
    ".svg",
    ".webp",
}

SKIP_NAMES = {
    ".DS_Store",
}

LEAK_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("macos-home", re.compile(r"/Users/[^/\s\"'`]+")),
    ("home-relative", re.compile(r"~/(?:[^\s\"'`]+)")),
    ("homebrew", re.compile(r"/opt/homebrew(?:/|\b)")),
    ("file-url", re.compile(r"file://")),
    ("devcontainer-workspace", re.compile(r"/workspaces/[^/\s\"'`]+")),
)


def _is_text_candidate(path: Path) -> bool:
    if path in ALLOWLIST_PATHS:
        return False
    if any(path == prefix or prefix in path.parents for prefix in ALLOWLIST_PREFIXES):
        return False
    if path.name in SKIP_NAMES:
        return False
    if any(part in {"node_modules", ".venv", ".git"} for part in path.parts):
        return False
    return path.suffix.lower() not in SKIP_SUFFIXES


def _tracked_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        text=False,
        check=True,
    )
    entries = [entry.decode("utf-8") for entry in proc.stdout.split(b"\x00") if entry]
    return [ROOT / entry for entry in entries if _is_text_candidate(Path(entry))]


def _local_files() -> list[Path]:
    files: list[Path] = []
    for rel_root in LOCAL_ROOTS:
        root = ROOT / rel_root
        if not root.exists():
            continue
        if root.is_file():
            if _is_text_candidate(root.relative_to(ROOT)):
                files.append(root)
            continue
        for path in root.rglob("*"):
            if path.is_file() and _is_text_candidate(path.relative_to(ROOT)):
                files.append(path)
    return sorted(set(files))


def _scan_file(path: Path) -> list[tuple[int, str, str]]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    findings: list[tuple[int, str, str]] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        for label, pattern in LEAK_PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            findings.append((line_number, label, line.strip()))
            break
    return findings


def _format_path(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _scan_paths(paths: Iterable[Path]) -> list[str]:
    failures: list[str] = []
    for path in paths:
        for line_number, label, snippet in _scan_file(path):
            failures.append(f"{_format_path(path)}:{line_number}: {label}: {snippet}")
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fail on local path leaks in repo text surfaces.")
    parser.add_argument(
        "--scope",
        choices=(TRACKED_SCOPE, LOCAL_SCOPE),
        default=TRACKED_SCOPE,
        help="tracked: git-tracked files only; local: repo-owned text lanes including ignored local artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.scope == TRACKED_SCOPE:
        paths = _tracked_files()
    else:
        paths = _local_files()

    failures = _scan_paths(paths)
    if failures:
        label = "tracked" if args.scope == TRACKED_SCOPE else "local"
        print(f"[fail] {label} path leak check found {len(failures)} issue(s):")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    label = "tracked" if args.scope == TRACKED_SCOPE else "local"
    print(f"[ok] {label} path leak check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
