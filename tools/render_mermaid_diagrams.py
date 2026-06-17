from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = (
    REPO_ROOT / "docs/public/diagrams/eval-contract.md",
    REPO_ROOT / "docs/public/diagrams/evidence-and-ocr.md",
    REPO_ROOT / "docs/public/diagrams/refactor-method.md",
    REPO_ROOT / "docs/public/diagrams/refactor-journey.md",
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs/public/diagrams"
MMDC = REPO_ROOT / "node_modules/.bin/mmdc"
MERMAID_CONFIG = REPO_ROOT / "tools" / "mermaid_config.json"
MERMAID_MANIFEST = REPO_ROOT / "tools" / "mermaid_diagram_manifest.json"


@dataclass(frozen=True)
class MermaidDiagram:
    title: str
    slug: str
    source: str


@dataclass(frozen=True)
class MermaidRenderResult:
    output_paths: list[Path]
    updated_paths: list[Path]
    skipped_paths: list[Path]


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


def _coerce_markdown_paths(markdown_paths: Path | Sequence[Path]) -> list[Path]:
    if isinstance(markdown_paths, Path):
        return [markdown_paths]
    return list(markdown_paths)


def _source_hash(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _read_manifest(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Mermaid manifest must be a JSON object: {path}")

    manifest: dict[str, str] = {}
    for slug, source_hash in data.items():
        if not isinstance(slug, str) or not isinstance(source_hash, str):
            raise ValueError(f"Mermaid manifest has invalid entry: {path}")
        manifest[slug] = source_hash
    return manifest


def _write_manifest(path: Path, manifest: dict[str, str]) -> None:
    content = json.dumps(dict(sorted(manifest.items())), indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    path.write_text(content, encoding="utf-8")


def render_mermaid_diagrams(
    markdown_paths: Path | Sequence[Path] = DEFAULT_SOURCES,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    manifest_path: Path = MERMAID_MANIFEST,
    *,
    force: bool = False,
) -> MermaidRenderResult:
    source_paths = _coerce_markdown_paths(markdown_paths)
    for markdown_path in source_paths:
        if not markdown_path.exists():
            raise FileNotFoundError(f"Markdown source not found: {markdown_path}")
    if not MMDC.exists():
        raise FileNotFoundError(
            "Mermaid CLI is not installed. Run `npm install` to install "
            "`@mermaid-js/mermaid-cli`."
        )
    if not MERMAID_CONFIG.exists():
        raise FileNotFoundError(f"Mermaid config not found: {MERMAID_CONFIG}")

    diagrams: list[MermaidDiagram] = []
    for source_path in source_paths:
        diagrams.extend(_extract_diagrams(source_path))
    if not diagrams:
        sources = ", ".join(str(path) for path in source_paths)
        raise RuntimeError(f"No mermaid diagrams found in: {sources}")
    slugs = [diagram.slug for diagram in diagrams]
    duplicate_slugs = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if duplicate_slugs:
        raise RuntimeError(
            "Duplicate Mermaid diagram slugs found: " + ", ".join(duplicate_slugs)
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths: list[Path] = []
    updated_paths: list[Path] = []
    skipped_paths: list[Path] = []
    manifest = _read_manifest(manifest_path)
    next_manifest: dict[str, str] = {}

    with tempfile.TemporaryDirectory(prefix="polinko-mermaid-") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        for diagram in diagrams:
            temp_input = temp_dir / f"{diagram.slug}.mmd"
            temp_output = temp_dir / f"{diagram.slug}.svg"
            output_path = output_dir / temp_output.name
            temp_input.write_text(diagram.source, encoding="utf-8")
            source_hash = _source_hash(diagram.source)
            next_manifest[diagram.slug] = source_hash
            should_render = (
                force
                or not output_path.exists()
                or (diagram.slug in manifest and manifest[diagram.slug] != source_hash)
            )

            if not should_render:
                skipped_paths.append(output_path)
                output_paths.append(output_path)
                continue

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
                    str(temp_output),
                ],
                check=True,
            )
            rendered_svg = temp_output.read_text(encoding="utf-8").rstrip("\n") + "\n"
            if (
                not output_path.exists()
                or output_path.read_text(encoding="utf-8") != rendered_svg
            ):
                output_path.write_text(rendered_svg, encoding="utf-8")
            updated_paths.append(output_path)
            output_paths.append(output_path)

    _write_manifest(manifest_path, next_manifest)
    return MermaidRenderResult(
        output_paths=output_paths,
        updated_paths=updated_paths,
        skipped_paths=skipped_paths,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Render public Mermaid diagrams.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-render every diagram, including unchanged existing SVGs.",
    )
    args = parser.parse_args()

    result = render_mermaid_diagrams(force=args.force)
    relative_sources = ", ".join(
        str(source.relative_to(REPO_ROOT)) for source in DEFAULT_SOURCES
    )
    print(
        f"Checked {len(result.output_paths)} Mermaid diagrams from {relative_sources}:"
    )
    if result.updated_paths:
        print(f"Updated {len(result.updated_paths)} SVG artifact(s):")
    else:
        print("Updated 0 SVG artifacts.")
    for output_path in result.updated_paths:
        print(f"- {output_path.relative_to(REPO_ROOT)}")
    if result.skipped_paths:
        print(f"Skipped {len(result.skipped_paths)} unchanged SVG artifact(s).")


if __name__ == "__main__":
    main()
