from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, NamedTuple

FinishReport = Callable[..., int]
CommandHandler = Callable[..., int | None]
DEFAULT_ERROR_STATUS = 2
OCR_RETRY_DEFAULT_COHORT = "ocr_retry_evidence"
OCR_RETRY_DEFAULT_OUTCOME = "partial"
STATUS_APPLIED_OK = {"applied": 0}
STATUS_BLOCKED_ERROR = {"blocked": DEFAULT_ERROR_STATUS}
STATUS_ERROR = {"error": DEFAULT_ERROR_STATUS}
STATUS_OK = {"ok": 0}
STATUS_READY_OK = {"ready": 0}
STATUS_RESTORED_OK = {"restored": 0}
STATUS_WRITTEN_OK = {"written": 0}
STATUS_OCR_EXECUTION = {
    "completed": 0,
    "failed": 1,
    "partial_failure": 1,
}


class DefaultFilters(NamedTuple):
    outcome: str
    cohort: str


class FilteredCommandArgs(NamedTuple):
    outcome: str
    cohort: str
    limit: int


class OcrRetryCommandArgs(NamedTuple):
    outcome: str
    cohort: str
    limit: int
    artifact_ids: list[str]


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


def ocr_retry_filters(args: Any) -> DefaultFilters:
    return default_filters(
        args,
        outcome=OCR_RETRY_DEFAULT_OUTCOME,
        cohort=OCR_RETRY_DEFAULT_COHORT,
    )


def filtered_command_args(
    args: Any, *, outcome: str, cohort: str
) -> FilteredCommandArgs:
    filters = default_filters(args, outcome=outcome, cohort=cohort)
    return FilteredCommandArgs(
        outcome=filters.outcome,
        cohort=filters.cohort,
        limit=positive_limit(args.limit),
    )


def ocr_retry_command_args(args: Any) -> OcrRetryCommandArgs:
    filters = ocr_retry_filters(args)
    return OcrRetryCommandArgs(
        outcome=filters.outcome,
        cohort=filters.cohort,
        limit=positive_limit(args.limit),
        artifact_ids=args.artifact_id,
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
