"""Build the static portfolio doorway for Netlify.

The public doorway is currently maintained as the FastAPI fallback HTML so the
local app and static deploy cannot drift. This build step extracts that literal
without importing the API package or requiring runtime dependencies.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
APP_FACTORY = REPO_ROOT / "api" / "app_factory.py"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "netlify"
CANONICAL_URL = "https://www.krystian.io/"


def _portfolio_html() -> str:
    module = ast.parse(APP_FACTORY.read_text(encoding="utf-8"))
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "_PORTFOLIO_FALLBACK_HTML":
                return ast.literal_eval(node.value)
    raise RuntimeError("Could not find _PORTFOLIO_FALLBACK_HTML in api/app_factory.py")


def main() -> None:
    output_dir = Path(os.environ.get("POLINKO_PORTFOLIO_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    index_path = output_dir / "index.html"
    redirects_path = output_dir / "_redirects"
    robots_path = output_dir / "robots.txt"
    sitemap_path = output_dir / "sitemap.xml"

    index_path.write_text(_portfolio_html(), encoding="utf-8")
    redirects_path.write_text("/portfolio / 301!\n", encoding="utf-8")
    robots_path.write_text(
        f"User-agent: *\nAllow: /\nSitemap: {CANONICAL_URL}sitemap.xml\n",
        encoding="utf-8",
    )
    sitemap_path.write_text(
        "\n".join(
            [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
                "  <url>",
                f"    <loc>{CANONICAL_URL}</loc>",
                "  </url>",
                "</urlset>",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {index_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {redirects_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {robots_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {sitemap_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
