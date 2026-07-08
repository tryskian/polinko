from __future__ import annotations

import argparse
import shutil
from collections.abc import Iterable
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

CACHE_DIR_NAMES = frozenset(
    {
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
    }
)
PRUNE_DIR_NAMES = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
    }
)


def repo_relative(path: Path, *, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_runtime_cache_dirs(root: Path) -> Iterable[Path]:
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if not child.is_dir() or child.is_symlink():
            continue
        if child.name in PRUNE_DIR_NAMES:
            continue
        if child.name in CACHE_DIR_NAMES:
            yield child
            continue
        yield from iter_runtime_cache_dirs(child)


def clean_runtime_caches(*, root: Path, apply: bool) -> list[Path]:
    cache_dirs = list(iter_runtime_cache_dirs(root))
    if apply:
        for cache_dir in cache_dirs:
            shutil.rmtree(cache_dir)
    return cache_dirs


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List or remove repo-owned runtime cache directories.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Remove matching cache directories.",
    )
    parser.add_argument(
        "--root",
        default=str(REPO_ROOT),
        help=argparse.SUPPRESS,
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    cache_dirs = clean_runtime_caches(root=root, apply=args.apply)
    count = len(cache_dirs)

    if args.apply:
        print(f"runtime-cache-clean: removed {count} repo-owned cache directories")
        return 0

    if count == 0:
        print("runtime-cache-clean: no repo-owned cache directories found")
        return 0

    print(f"runtime-cache-clean: {count} repo-owned cache directories")
    for cache_dir in cache_dirs:
        print(f"  {repo_relative(cache_dir, root=root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
