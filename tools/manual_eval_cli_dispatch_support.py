from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, NamedTuple

FinishReport = Callable[..., int]
CommandHandler = Callable[..., int | None]


class DefaultFilters(NamedTuple):
    outcome: str
    cohort: str


def dispatch_first_match(
    *,
    handlers: Iterable[CommandHandler],
    args: Any,
    db_path: Path,
    finish: FinishReport,
) -> int | None:
    for handler in handlers:
        status = handler(args=args, db_path=db_path, finish=finish)
        if status is not None:
            return status
    return None


def default_filters(args: Any, *, outcome: str, cohort: str) -> DefaultFilters:
    return DefaultFilters(
        outcome=args.outcome or outcome,
        cohort=args.cohort or cohort,
    )


def optional_path(value: Any) -> Path | None:
    if value is None:
        return None
    return Path(value) if str(value).strip() else None


def positive_limit(value: Any) -> int:
    try:
        return max(1, int(value))
    except (TypeError, ValueError):
        return 1
