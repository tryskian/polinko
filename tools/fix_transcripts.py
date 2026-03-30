"""Auto-fix curated peanut transcript structure.

Scope:
- fixes curated files under docs/peanut/transcripts/**
- skips README and sessions exports
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path("docs/peanut/transcripts")
EXCLUDED_DIRS = {"sessions"}
EXCLUDED_FILES = {"README.md"}


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


def ensure_core_sections(lines: list[str]) -> tuple[list[str], bool]:
    changed = False

    if not any(line.startswith("## Structured Insights (Assistant Interpretation)") for line in lines):
        # Insert insights section at end when missing.
        if lines and lines[-1] != "":
            lines.append("")
        lines.extend(
            [
                "## Structured Insights (Assistant Interpretation)",
                "",
                "### Distilled Signal",
                "",
                "This record is preserved in verbatim form with structured interpretation for",
                "reuse in co-reasoning and benchmarking.",
                "",
                "### Key Points",
                "",
                "- Primary insights are captured in this section and adjacent subsections.",
                "- Verbatim transcript remains the source of truth for exact phrasing.",
                "- Structured interpretation should stay evidence-linked and non-speculative.",
            ]
        )
        return lines, True

    idx = lines.index("## Structured Insights (Assistant Interpretation)")
    end = len(lines)
    for i in range(idx + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break

    block = lines[idx + 1 : end]
    block_text = "\n".join(block)
    h3_count = sum(1 for line in block if line.startswith("### "))

    inserts: list[str] = []
    if "### Distilled Signal" not in block_text and "### Distilled Concept" not in block_text:
        inserts.extend(
            [
                "",
                "### Distilled Signal",
                "",
                "This record is preserved in verbatim form with structured interpretation for",
                "reuse in co-reasoning and benchmarking.",
            ]
        )

    if "### Key Points" not in block_text and h3_count < 2:
        inserts.extend(
            [
                "",
                "### Key Points",
                "",
                "- Primary insights are captured in this section and adjacent subsections.",
                "- Verbatim transcript remains the source of truth for exact phrasing.",
                "- Structured interpretation should stay evidence-linked and non-speculative.",
            ]
        )

    if inserts:
        lines = lines[: idx + 1] + inserts + lines[idx + 1 :]
        changed = True

    return lines, changed


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    new_lines, changed = ensure_core_sections(lines)
    if not changed:
        return False
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True


def main() -> int:
    if not ROOT.exists():
        print(f"transcript-fix: SKIP (missing {ROOT})")
        return 0

    files = curated_transcript_files(ROOT)
    if not files:
        print("transcript-fix: SKIP (no curated transcript files found)")
        return 0

    changed_files: list[Path] = []
    for path in files:
        if fix_file(path):
            changed_files.append(path)

    print(f"transcript-fix: DONE ({len(changed_files)} files updated)")
    for path in changed_files:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
