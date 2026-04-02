"""Validate curated peanut transcript structure.

Local confidentiality note:
- `docs/peanut/**` may be ignored in git for this repository.
- This validator is still useful as a local quality gate for consistent format.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path("docs/peanut/transcripts")
EXCLUDED_DIRS = {"sessions"}
EXCLUDED_FILES = {"README.md"}

REQUIRED_MARKERS = [
    "# ",
    "## Scope",
    "Identifiers:",
    "## Transcript (Verbatim Block)",
    "## Structured Insights (Assistant Interpretation)",
]

DISTILLED_HEADINGS = (
    "### Distilled Signal",
    "### Distilled Concept",
)


def curated_transcript_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*.md")):
        rel_parts = path.relative_to(root).parts
        if not rel_parts:
            continue
        if rel_parts[0] in EXCLUDED_DIRS:
            continue
        if path.name in EXCLUDED_FILES:
            continue
        files.append(path)
    return files


def insights_block(lines: list[str]) -> list[str]:
    try:
        start = lines.index("## Structured Insights (Assistant Interpretation)")
    except ValueError:
        return []
    block: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        block.append(line)
    return block


def validate_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []

    missing = [marker for marker in REQUIRED_MARKERS if marker not in text]
    if missing:
        errors.append(f"missing required markers: {', '.join(missing)}")
        return errors

    block = insights_block(lines)
    if not block:
        errors.append("structured insights block is empty or malformed")
        return errors

    if not any(heading in "\n".join(block) for heading in DISTILLED_HEADINGS):
        errors.append(
            "structured insights missing distillation heading "
            "(expected one of: Distilled Signal / Distilled Concept)"
        )

    h3_count = sum(1 for line in block if line.startswith("### "))
    if h3_count < 2:
        errors.append(
            "structured insights must include at least two H3 subsections "
            "(for rich insight format)"
        )

    return errors


def main() -> int:
    if not ROOT.exists():
        print(f"transcript-check: SKIP (missing {ROOT})")
        return 0

    files = curated_transcript_files(ROOT)
    if not files:
        print("transcript-check: SKIP (no curated transcript files found)")
        return 0

    all_errors: list[tuple[Path, list[str]]] = []
    for file_path in files:
        errors = validate_file(file_path)
        if errors:
            all_errors.append((file_path, errors))

    if all_errors:
        print("transcript-check: FAIL")
        for file_path, errors in all_errors:
            print(f"- {file_path}")
            for error in errors:
                print(f"  - {error}")
        return 1

    print(f"transcript-check: PASS ({len(files)} curated transcript files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
