from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any, NamedTuple

FinishReport = Callable[..., int]
ReportFormatter = Callable[[dict[str, Any]], str]
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


class LocalArtifactPaths(NamedTuple):
    backup_dir: Path | None
    backup_root: Path | None
    decision_path: Path | None
    execution_dir: Path | None
    output_path: Path | None
    overlay_source_index_path: Path | None
    plan_path: Path | None
    restore_root: Path | None
    run_dir: Path | None
    selection_path: Path | None


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


def finish_report_with_error_default(
    *,
    finish: FinishReport,
    report: dict[str, Any],
    formatter: ReportFormatter,
    status_by_state: Mapping[str, int],
) -> int:
    return finish(
        report,
        formatter,
        status_by_state=status_by_state,
        default_status=DEFAULT_ERROR_STATUS,
    )


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


def ocr_retry_report_kwargs(
    args: Any, *, include_artifact_ids: bool = False
) -> dict[str, Any]:
    command_args = ocr_retry_command_args(args)
    kwargs: dict[str, Any] = {
        "outcome": command_args.outcome,
        "cohort": command_args.cohort,
        "limit": command_args.limit,
    }
    if include_artifact_ids:
        kwargs["artifact_ids"] = command_args.artifact_ids
    return kwargs


def local_artifact_paths(args: Any) -> LocalArtifactPaths:
    return LocalArtifactPaths(
        backup_dir=optional_path(getattr(args, "backup_dir", None)),
        backup_root=optional_path(getattr(args, "backup_root", None)),
        decision_path=optional_path(getattr(args, "decision_path", None)),
        execution_dir=optional_path(getattr(args, "execution_dir", None)),
        output_path=optional_path(getattr(args, "output_path", None)),
        overlay_source_index_path=optional_path(
            getattr(args, "overlay_source_index", None)
        ),
        plan_path=optional_path(getattr(args, "plan_path", None)),
        restore_root=optional_path(getattr(args, "restore_root", None)),
        run_dir=optional_path(getattr(args, "run_dir", None)),
        selection_path=optional_path(getattr(args, "selection_path", None)),
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
