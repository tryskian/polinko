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

PARKED_OCR_EVAL_ALIASES = frozenset(
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


def expected_manualdb_alias(canonical: str) -> str:
    if canonical == "manual-evals-db":
        return "manualdb"
    if canonical.startswith("manual-evals-db-"):
        return f"manualdb-{canonical.removeprefix('manual-evals-db-')}"
    return f"manualdb-{canonical.removeprefix('manual-evals-')}"


def check_manual_eval_aliases(text: str) -> list[str]:
    failures: list[str] = []
    phony = phony_targets(text)
    rules = make_rules(text)
    rules_by_target: dict[str, list[MakeRule]] = {}
    for rule in rules:
        for target in rule.targets:
            rules_by_target.setdefault(target, []).append(rule)

    canonical_targets = sorted(
        target for target in phony if target.startswith("manual-evals-")
    )
    for canonical in canonical_targets:
        alias = expected_manualdb_alias(canonical)
        if alias not in phony:
            failures.append(f"{canonical}: missing .PHONY compatibility alias {alias}")
            continue
        if canonical not in rules_by_target:
            failures.append(f"{canonical}: missing recipe target")
            continue
        matching_rules = [
            rule for rule in rules_by_target[canonical] if alias in rule.targets
        ]
        if not matching_rules:
            line_numbers = ", ".join(
                str(rule.line) for rule in rules_by_target[canonical]
            )
            failures.append(
                f"{canonical}: alias {alias} is not on the same recipe line "
                f"(canonical line(s): {line_numbers})"
            )

    return failures


def check_parked_ocr_aliases(text: str) -> list[str]:
    failures: list[str] = []
    rules = make_rules(text)
    rules_by_target: dict[str, list[MakeRule]] = {}
    for rule in rules:
        for target in rule.targets:
            rules_by_target.setdefault(target, []).append(rule)

    for alias in ("ocr-inventory", "ocr-inventory-json"):
        if alias not in rules_by_target:
            failures.append(f"{alias}: missing read-only OCR inventory target")

    for entrypoint in AUTOMATION_ENTRYPOINTS:
        for rule in rules_by_target.get(entrypoint, []):
            blocked = sorted(PARKED_OCR_EVAL_ALIASES.intersection(rule.deps))
            if blocked:
                failures.append(
                    f"{entrypoint}: automation dependency includes parked OCR "
                    f"eval alias(es): {', '.join(blocked)}"
                )

    return failures


def run(root: Path) -> list[str]:
    text = makefile_text(root)
    failures: list[str] = []
    failures.extend(check_manual_eval_aliases(text))
    failures.extend(check_parked_ocr_aliases(text))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check manual eval and OCR operator alias contracts.",
    )
    parser.parse_args(argv)

    failures = run(ROOT)
    if failures:
        print("operator-alias-check: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("[ok] operator alias check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
