"""Build the public portfolio doorway from the tracked frontend shell."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = REPO_ROOT / "frontend"
UI_DIR = REPO_ROOT / "ui"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "netlify"


def _run(*args: str) -> None:
    subprocess.run(args, cwd=REPO_ROOT, check=True)


def _rebuild_frontend() -> None:
    _run("npm", "--prefix", str(FRONTEND_DIR), "install")
    _run("npm", "--prefix", str(FRONTEND_DIR), "run", "build")


def _copy_ui(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(UI_DIR, output_dir)


def _write_redirects(output_dir: Path) -> None:
    redirects_path = output_dir / "_redirects"
    redirects_path.write_text(
        "/portfolio /index.html 200\n/* /index.html 200\n",
        encoding="utf-8",
    )


def main() -> None:
    output_dir = Path(os.environ.get("POLINKO_PORTFOLIO_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir

    _rebuild_frontend()
    _copy_ui(output_dir)
    _write_redirects(output_dir)

    print(f"Built tracked UI into {output_dir.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
