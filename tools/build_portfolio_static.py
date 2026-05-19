"""Build the public portfolio doorway from the tracked source app."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "netlify"


def _repo_path_from_env(env_name: str, default_relative_path: str) -> Path:
    raw_path = os.environ.get(env_name) or default_relative_path
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return REPO_ROOT / path


PORTFOLIO_APP_DIR = _repo_path_from_env("POLINKO_PORTFOLIO_APP_DIR", "apps/portfolio")
PORTFOLIO_STATIC_DIR = _repo_path_from_env(
    "POLINKO_PORTFOLIO_STATIC_DIR",
    "public/portfolio",
)


def _run(*args: str, env: dict[str, str] | None = None) -> None:
    subprocess.run(args, cwd=REPO_ROOT, check=True, env=env)


def _display_path(path: Path) -> Path:
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def _rebuild_portfolio_app() -> None:
    build_env = os.environ.copy()
    build_env.setdefault("POLINKO_PORTFOLIO_STATIC_DIR", str(PORTFOLIO_STATIC_DIR))

    _run("npm", "--prefix", str(PORTFOLIO_APP_DIR), "install")
    _run("npm", "--prefix", str(PORTFOLIO_APP_DIR), "run", "build", env=build_env)


def _copy_static(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(PORTFOLIO_STATIC_DIR, output_dir)


def _write_redirects(output_dir: Path) -> None:
    redirects_path = output_dir / "_redirects"
    redirects_path.write_text(
        "/portfolio /index.html 200\n/* /index.html 200\n",
        encoding="utf-8",
    )


def main() -> None:
    output_dir = _repo_path_from_env(
        "POLINKO_PORTFOLIO_OUTPUT_DIR",
        str(DEFAULT_OUTPUT_DIR.relative_to(REPO_ROOT)),
    )

    _rebuild_portfolio_app()
    _copy_static(output_dir)
    _write_redirects(output_dir)

    print(f"Built tracked portfolio static assets into {_display_path(output_dir)}")


if __name__ == "__main__":
    main()
