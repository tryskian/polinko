"""Public-surface audit for tracked repo contents."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


BLOCKED_PREFIXES = (
    ".archive/",
    ".local/",
    "output/",
    "eval_reports/",
    "docs/peanut/",
    "docs/portfolio/",
    "docs/internal/",
)

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "OPENAI_API_KEY",
        re.compile(r"""OPENAI_API_KEY\s*=\s*["']?(?P<value>[^\s"',}]+)"""),
    ),
    (
        "BRAINTRUST_API_KEY",
        re.compile(r"""BRAINTRUST_API_KEY\s*=\s*["']?(?P<value>[^\s"',}]+)"""),
    ),
    (
        "OPENAI_TOKEN",
        re.compile(
            r"""(?<![A-Za-z0-9])(?P<value>sk-(?:proj-)?[A-Za-z0-9_-]{32,})(?![A-Za-z0-9_-])"""
        ),
    ),
)

MARKER_ALLOWED_PATHS = frozenset({".env.example"})


def _is_placeholder_value(value: str) -> bool:
    raw = value.strip().strip("\"'`")
    if not raw:
        return True
    if not any(ch.isalnum() for ch in raw):
        return True
    lower = raw.lower()
    if raw.startswith("${"):
        return True
    if "..." in raw:
        return True
    placeholder_terms = (
        "sk-test-key",
        "example",
        "placeholder",
        "redacted",
        "your_",
        "<your",
        "fake",
        "dummy",
    )
    return any(term in lower for term in placeholder_terms)


def find_blocked_paths(
    *, tracked_paths: Iterable[str], blocked_prefixes: Iterable[str]
) -> list[str]:
    out: list[str] = []
    prefixes = tuple(blocked_prefixes)
    for raw in tracked_paths:
        path = str(raw).strip()
        if not path:
            continue
        if path.startswith(prefixes):
            out.append(path)
    return sorted(out)


def find_secret_markers(*, repo_root: Path, tracked_paths: Iterable[str]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for raw in tracked_paths:
        path = str(raw).strip()
        if not path or path in MARKER_ALLOWED_PATHS:
            continue
        file_path = repo_root / path
        if not file_path.is_file():
            continue
        if file_path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".pdf"}:
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for marker, pattern in SECRET_PATTERNS:
            matched = False
            for match in pattern.finditer(content):
                value = match.groupdict().get("value", match.group(0))
                if _is_placeholder_value(value):
                    continue
                findings.append({"path": path, "marker": marker})
                matched = True
                break
            if matched:
                break
    return findings


def _git_tracked_paths(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit tracked files for public-safe release constraints."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root to audit.",
    )
    parser.add_argument(
        "--output-json",
        default=".local/eval_reports/public_repo_audit.json",
        help="Output JSON report path.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    output_json = Path(args.output_json).expanduser().resolve()

    tracked_paths = _git_tracked_paths(repo_root)
    blocked_paths = find_blocked_paths(
        tracked_paths=tracked_paths,
        blocked_prefixes=BLOCKED_PREFIXES,
    )
    secret_findings = find_secret_markers(repo_root=repo_root, tracked_paths=tracked_paths)

    report = {
        "tracked_count": len(tracked_paths),
        "blocked_prefixes": list(BLOCKED_PREFIXES),
        "blocked_paths": blocked_paths,
        "secret_findings": secret_findings,
        "pass": not blocked_paths and not secret_findings,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Public repo audit")
    print(f"  tracked_count: {report['tracked_count']}")
    print(f"  blocked_paths: {len(blocked_paths)}")
    print(f"  secret_findings: {len(secret_findings)}")
    print(f"  json: {output_json}")

    if blocked_paths:
        print("Blocked tracked paths:")
        for path in blocked_paths:
            print(f"  - {path}")
    if secret_findings:
        print("Secret marker findings:")
        for finding in secret_findings:
            print(f"  - {finding['path']} ({finding['marker']})")

    return 0 if report["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
