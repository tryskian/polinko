from __future__ import annotations

from pathlib import Path


def int_value(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return 0
        return int(value)
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def terminal_path_name(value: object) -> str:
    raw_value = str(value or "").strip()
    if not raw_value:
        return "none"
    return Path(raw_value).name or "none"
