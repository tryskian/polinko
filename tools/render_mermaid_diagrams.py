from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "docs/public/DIAGRAMS.md"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs/public/diagrams"
MMDC = REPO_ROOT / "node_modules/.bin/mmdc"
MERMAID_CONFIG = REPO_ROOT / "tools" / "mermaid_config.json"


@dataclass(frozen=True)
class MermaidDiagram:
    title: str
    slug: str
    source: str


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "diagram"


def _extract_diagrams(markdown_path: Path) -> list[MermaidDiagram]:
    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    diagrams: list[MermaidDiagram] = []
    current_title: str | None = None
    index = 0

    while index < len(lines):
        line = lines[index]
        if line.startswith("## "):
            current_title = line[3:].strip()
        if line.strip() == "```mermaid":
            index += 1
            block: list[str] = []
            while index < len(lines) and lines[index].strip() != "```":
                block.append(lines[index])
                index += 1
            title = current_title or f"diagram-{len(diagrams) + 1}"
            diagrams.append(
                MermaidDiagram(
                    title=title,
                    slug=_slugify(title),
                    source="\n".join(block).strip() + "\n",
                )
            )
        index += 1

    return diagrams


def render_mermaid_diagrams(
    markdown_path: Path = DEFAULT_SOURCE,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> list[Path]:
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown source not found: {markdown_path}")
    if not MMDC.exists():
        raise FileNotFoundError(
            "Mermaid CLI is not installed. Run `npm install` to install "
            "`@mermaid-js/mermaid-cli`."
        )
    if not MERMAID_CONFIG.exists():
        raise FileNotFoundError(f"Mermaid config not found: {MERMAID_CONFIG}")

    diagrams = _extract_diagrams(markdown_path)
    if not diagrams:
        raise RuntimeError(f"No mermaid diagrams found in {markdown_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    rendered_paths: list[Path] = []

    with tempfile.TemporaryDirectory(prefix="polinko-mermaid-") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        for diagram in diagrams:
            temp_input = temp_dir / f"{diagram.slug}.mmd"
            output_path = output_dir / f"{diagram.slug}.svg"
            temp_input.write_text(diagram.source, encoding="utf-8")
            subprocess.run(
                [
                    str(MMDC),
                    "-q",
                    "-c",
                    str(MERMAID_CONFIG),
                    "-b",
                    "transparent",
                    "-i",
                    str(temp_input),
                    "-o",
                    str(output_path),
                ],
                check=True,
            )
            rendered_paths.append(output_path)

    return rendered_paths


def main() -> None:
    rendered_paths = render_mermaid_diagrams()
    relative_source = DEFAULT_SOURCE.relative_to(REPO_ROOT)
    print(f"Rendered {len(rendered_paths)} Mermaid diagrams from {relative_source}:")
    for output_path in rendered_paths:
        print(f"- {output_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
