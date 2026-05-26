from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

FinishReport = Callable[..., int]


def optional_path(value: Any) -> Path | None:
    if value is None:
        return None
    return Path(value) if str(value).strip() else None


def positive_limit(value: Any) -> int:
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1
