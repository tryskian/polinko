from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

DOC_PATH_RE = re.compile(r"docs/(?:transcripts|research|theory)/[^\s`\)\]>\"']+\.md")


@dataclass(frozen=True)
class DocNode:
    path: str
    category: str
    label: str


def _category_for(path: str) -> str:
    if path.startswith("docs/peanut/transcripts/"):
        return "transcript"
    if path.startswith("docs/peanut/research/"):
        return "research"
    if path.startswith("docs/peanut/theory/"):
        return "theory"
    return "other"


def _label_for(path: str) -> str:
    name = Path(path).stem.replace("_", " ").replace("-", " ").strip()
    category = _category_for(path)
    prefix = {
        "transcript": "T",
        "research": "R",
        "theory": "Y",
    }.get(category, "D")
    return f"{prefix}: {name}"


def _iter_docs(repo_root: Path, roots: list[str]) -> list[str]:
    out: list[str] = []
    for rel_root in roots:
        base = repo_root / rel_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.is_file():
                out.append(path.relative_to(repo_root).as_posix())
    return out


def _extract_links(text: str) -> list[str]:
    return [match.group(0) for match in DOC_PATH_RE.finditer(text)]


def _escape_label(label: str) -> str:
    return label.replace('"', "\\\"")


def build_graph(repo_root: Path, roots: list[str], output: Path) -> None:
    docs = _iter_docs(repo_root, roots)
    doc_set = set(docs)
    nodes = [
        DocNode(path=path, category=_category_for(path), label=_label_for(path))
        for path in docs
    ]
    node_ids = {node.path: f"n{index}" for index, node in enumerate(nodes)}

    edges: set[tuple[str, str]] = set()
    for rel in docs:
        text = (repo_root / rel).read_text(encoding="utf-8")
        for target in _extract_links(text):
            if target in doc_set and target != rel:
                edges.add((rel, target))

    lines: list[str] = []
    lines.append("# Reference Graph")
    lines.append("")
    lines.append("Generated from markdown links across transcripts, research, and theory.")
    lines.append("")
    lines.append(f"- generated_utc: {datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append(f"- nodes: {len(nodes)}")
    lines.append(f"- edges: {len(edges)}")
    lines.append("")
    lines.append("```mermaid")
    lines.append("graph LR")

    for node in nodes:
        node_id = node_ids[node.path]
        label = _escape_label(node.label)
        lines.append(f'  {node_id}["{label}"]')

    for source, target in sorted(edges):
        source_id = node_ids[source]
        target_id = node_ids[target]
        lines.append(f"  {source_id} --> {target_id}")

    # Category styling
    lines.append("  classDef transcript fill:#1f77b4,stroke:#0e3d66,color:#ffffff")
    lines.append("  classDef research fill:#2ca02c,stroke:#145214,color:#ffffff")
    lines.append("  classDef theory fill:#9467bd,stroke:#4c2e6a,color:#ffffff")
    lines.append("  classDef other fill:#7f7f7f,stroke:#444444,color:#ffffff")

    for category in ("transcript", "research", "theory", "other"):
        category_nodes = [node_ids[node.path] for node in nodes if node.category == category]
        if category_nodes:
            lines.append(f"  class {','.join(category_nodes)} {category}")

    lines.append("```")
    lines.append("")
    lines.append("## Legend")
    lines.append("")
    lines.append("- `T:` transcript")
    lines.append("- `R:` research")
    lines.append("- `Y:` theory")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a markdown-native docs reference graph.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path.",
    )
    parser.add_argument(
        "--root",
        action="append",
        default=["docs/transcripts", "docs/research", "docs/theory"],
        help="Root directory to include (repeatable).",
    )
    parser.add_argument(
        "--output",
        default="docs/peanut/visuals/REFERENCE_GRAPH.md",
        help="Output markdown file path.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo_root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = (repo_root / output).resolve()
    roots = [str(item).strip() for item in args.root if str(item).strip()]
    build_graph(repo_root=repo_root, roots=roots, output=output)
    print(f"Reference graph written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
