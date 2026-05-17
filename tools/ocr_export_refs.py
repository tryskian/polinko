from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CGPT_EXPORT_ROOT = (
    Path.home() / "Library" / "CloudStorage" / "Dropbox" / "CGPT-DATA-EXPORT"
)


def current_export_root() -> Path:
    for name in ("CGPT_EXPORT_ROOT", "CGPT_EXPORT_ROOT_DEFAULT"):
        value = str(os.environ.get(name, "")).strip()
        if value:
            return Path(value).expanduser().resolve()
    return DEFAULT_CGPT_EXPORT_ROOT.resolve()


def to_export_ref(pathish: str | Path, *, export_root: Path | None = None) -> str:
    value = str(pathish or "").strip()
    if not value:
        return ""
    path = Path(value).expanduser()
    if not path.is_absolute():
        return path.as_posix()
    normalized_root = (export_root or current_export_root()).expanduser().resolve()
    try:
        return path.resolve().relative_to(normalized_root).as_posix()
    except ValueError:
        return path.name


def resolve_export_ref(pathish: str | Path, *, export_root: Path | None = None) -> Path:
    value = str(pathish or "").strip()
    if not value:
        return Path("")
    path = Path(value).expanduser()
    if path.is_absolute():
        return path.resolve()
    return ((export_root or current_export_root()).expanduser().resolve() / path).resolve()


def to_repo_ref(pathish: str | Path, *, repo_root: Path = ROOT) -> str:
    value = str(pathish or "").strip()
    if not value:
        return ""
    path = Path(value).expanduser()
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return path.name
