from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

AUTOMATION_ENTRYPOINTS = (
    "start",
    "end",
    "end-preflight",
    "end-stop",
    "pr-preflight",
    "ci",
    "ci-docs",
)

PARKED_OCR_EVAL_SHORTCUTS = frozenset(
    {
        "ocrall",
        "ocrwiden",
        "ocrwidensync",
        "ocrwidenbatch",
        "ocrwidenall",
        "ocrhand",
        "ocrtype",
        "ocrillu",
        "ocrstable",
        "ocrstablegrowth",
        "ocrgrowth",
        "ocrfails",
        "ocrfocus",
        "ocrfocuscases",
        "ocrfocusreport",
        "ocrkernel",
        "ocrhandbench",
        "ocrtypebench",
        "ocrillubench",
        "ocrstablehand",
        "ocrstabletype",
        "ocrstableillu",
        "ocrdelta",
    }
)

NON_CANONICAL_OPERATOR_TARGET_PREFIXES = ("manualdb",)
NON_CANONICAL_OPERATOR_TARGETS = ("eod", "eod-stop")


@dataclass(frozen=True)
class MakeRule:
    targets: tuple[str, ...]
    deps: tuple[str, ...]
    line: int


def makefile_text(root: Path, path: Path = Path("Makefile")) -> str:
    return _makefile_source_text(root, path, set())


def _makefile_source_text(root: Path, path: Path, seen: set[Path]) -> str:
    absolute = (root / path).resolve()
    if absolute in seen:
        return ""
    seen.add(absolute)

    text = absolute.read_text(encoding="utf-8")
    parts = [text]
    for match in re.finditer(r"^include\s+(.+)$", text, re.MULTILINE):
        for include_path in match.group(1).split():
            parts.append(_makefile_source_text(root, Path(include_path), seen))
    return "\n".join(parts)


def phony_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for match in re.finditer(r"^\.PHONY:\s*(.*)$", text, re.MULTILINE):
        targets.update(match.group(1).split())
    return targets


def make_rules(text: str) -> list[MakeRule]:
    rules: list[MakeRule] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line or line.startswith(("\t", "#")) or ":" not in line:
            continue
        head, tail = line.split(":", 1)
        head = head.strip()
        if not head or any(marker in head for marker in ("=", "$", "(")):
            continue
        targets = tuple(head.split())
        deps = tuple(token for token in tail.strip().split() if "=" not in token)
        rules.append(MakeRule(targets=targets, deps=deps, line=line_number))
    return rules


def check_canonical_operator_targets(text: str) -> list[str]:
    failures: list[str] = []
    phony = phony_targets(text)
    rules = make_rules(text)

    for target in sorted(phony):
        if target in NON_CANONICAL_OPERATOR_TARGETS or target.startswith(
            NON_CANONICAL_OPERATOR_TARGET_PREFIXES
        ):
            failures.append(f"{target}: non-canonical operator target is active")

    for rule in rules:
        for target in rule.targets:
            if target in NON_CANONICAL_OPERATOR_TARGETS or target.startswith(
                NON_CANONICAL_OPERATOR_TARGET_PREFIXES
            ):
                failures.append(
                    f"{target}: non-canonical operator rule is active on line {rule.line}"
                )

    return failures


def check_parked_ocr_shortcuts(text: str) -> list[str]:
    failures: list[str] = []
    rules = make_rules(text)
    rules_by_target: dict[str, list[MakeRule]] = {}
    for rule in rules:
        for target in rule.targets:
            rules_by_target.setdefault(target, []).append(rule)

    for target in ("ocr-inventory", "ocr-inventory-json"):
        if target not in rules_by_target:
            failures.append(f"{target}: missing read-only OCR inventory target")

    for entrypoint in AUTOMATION_ENTRYPOINTS:
        for rule in rules_by_target.get(entrypoint, []):
            blocked = sorted(PARKED_OCR_EVAL_SHORTCUTS.intersection(rule.deps))
            if blocked:
                failures.append(
                    f"{entrypoint}: automation dependency includes parked OCR "
                    f"eval shortcut(s): {', '.join(blocked)}"
                )

    return failures


def run(root: Path) -> list[str]:
    text = makefile_text(root)
    failures: list[str] = []
    failures.extend(check_canonical_operator_targets(text))
    failures.extend(check_parked_ocr_shortcuts(text))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check canonical operator command contracts.",
    )
    parser.parse_args(argv)

    failures = run(ROOT)
    if failures:
        print("operator-command-check: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("[ok] operator command check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
