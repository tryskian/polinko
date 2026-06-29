from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from polinko.api.evidence_sankey import build_evidence_sankey_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
NODE_RENDERER = REPO_ROOT / "tools" / "render_public_d3_diagrams.mjs"
OUTPUT_PATH = REPO_ROOT / "docs" / "public" / "diagrams" / "polinko-evidence-sankey.svg"


def _write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> None:
    if not NODE_RENDERER.is_file():
        raise FileNotFoundError(f"D3 renderer not found: {NODE_RENDERER}")

    payload = build_evidence_sankey_payload(max_reports=120)
    if not payload.get("available"):
        raise RuntimeError(
            "Evidence Sankey payload is unavailable; cannot render public D3 Sankey."
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="polinko-d3-render-") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        temp_json = temp_dir / "payload.json"
        temp_svg = temp_dir / OUTPUT_PATH.name
        temp_json.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        subprocess.run(
            ["node", str(NODE_RENDERER), str(temp_json), str(temp_svg)],
            cwd=REPO_ROOT,
            check=True,
        )
        rendered_svg = temp_svg.read_text(encoding="utf-8")

    changed = _write_if_changed(OUTPUT_PATH, rendered_svg)
    relative_output = OUTPUT_PATH.relative_to(REPO_ROOT)
    if changed:
        print(f"Updated D3 evidence Sankey: {relative_output}")
    else:
        print(f"Skipped unchanged D3 evidence Sankey: {relative_output}")


if __name__ == "__main__":
    main()
