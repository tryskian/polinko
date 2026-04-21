from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from api.portfolio_sankey import build_portfolio_sankey_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
NODE_RENDERER = REPO_ROOT / "tools" / "render_public_d3_diagrams.mjs"
OUTPUT_PATH = REPO_ROOT / "docs" / "public" / "diagrams" / "polinko-evidence-sankey.svg"


def main() -> None:
    if not NODE_RENDERER.is_file():
        raise FileNotFoundError(f"D3 renderer not found: {NODE_RENDERER}")

    payload = build_portfolio_sankey_payload(max_reports=120)
    if not payload.get("available"):
        raise RuntimeError(
            "Portfolio Sankey payload is unavailable; cannot render public D3 Sankey."
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False)
        temp_json = Path(handle.name)

    try:
        subprocess.run(
            ["node", str(NODE_RENDERER), str(temp_json), str(OUTPUT_PATH)],
            cwd=REPO_ROOT,
            check=True,
        )
    finally:
        temp_json.unlink(missing_ok=True)

    print(f"Rendered D3 evidence Sankey: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
