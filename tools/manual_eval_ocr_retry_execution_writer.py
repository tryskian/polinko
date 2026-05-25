from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_execution_bundle_report import (
    OCR_RETRY_EXECUTION_SCHEMA_VERSION,
    ocr_retry_execution_mutation_boundary,
)
from tools.manual_eval_ocr_retry_execution_providers import (
    run_default_ocr_retry_request,
)
from tools.manual_eval_ocr_retry_execution_readiness import (
    build_ocr_retry_execution_readiness_report,
)
from tools.manual_eval_ocr_retry_execution_requests import (
    OcrRetryRunner,
    build_ocr_retry_execution_requests,
    error_ocr_retry_response,
    normalize_ocr_retry_response,
)


OCR_RETRY_EXECUTION_CONFIRM_TOKEN = "ocr-retry-execute"
DEFAULT_OCR_RETRY_EXECUTION_DIR = Path(".local/manual_eval_runs/ocr_retry")
DEFAULT_OCR_RETRY_MODEL = "gpt-4.1-mini"
DEFAULT_OCR_RETRY_PROMPT = (
    "Extract all readable text from this image. Preserve line breaks and symbols "
    "exactly. Do not invent letters or words; if uncertain, output [?]."
)


def _int_value(value: object) -> int:
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


def _utc_run_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def _selection_file_fingerprint(selection_path: Path | None) -> str:
    if selection_path is None or not selection_path.is_file():
        return ""
    return hashlib.sha256(selection_path.read_bytes()).hexdigest()


def _ocr_retry_execution_blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _blocked_ocr_retry_execution_report(
    *,
    readiness_report: dict[str, Any] | None,
    selection_path: Path | None,
    confirm_token: str,
    execution_blockers: Sequence[dict[str, str]],
    ocr_provider: str,
    ocr_model: str,
    execution_dir: Path | None,
) -> dict[str, Any]:
    readiness_counts: dict[str, Any] = {}
    if isinstance(readiness_report, dict):
        counts = readiness_report.get("counts")
        if isinstance(counts, dict):
            readiness_counts = counts
    return {
        "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
        "state": "blocked",
        "execution_mode": "local_bundle",
        "selection_path": str(selection_path or ""),
        "selection_fingerprint": _selection_file_fingerprint(selection_path),
        "readiness_schema_version": readiness_report.get("schema_version", "")
        if isinstance(readiness_report, dict)
        else "",
        "readiness_state": readiness_report.get("state", "not_checked")
        if isinstance(readiness_report, dict)
        else "not_checked",
        "confirmation": {
            "required": OCR_RETRY_EXECUTION_CONFIRM_TOKEN,
            "provided": bool(confirm_token),
            "state": "ok"
            if confirm_token == OCR_RETRY_EXECUTION_CONFIRM_TOKEN
            else "blocked",
        },
        "ocr_provider": ocr_provider,
        "ocr_model": ocr_model,
        "counts": {
            "readiness_items": _int_value(readiness_counts.get("readiness_items")),
            "executable_items": _int_value(readiness_counts.get("executable_items")),
            "requests": 0,
            "responses": 0,
            "succeeded": 0,
            "failed": 0,
            "context_only_skipped": _int_value(
                readiness_counts.get("context_only_items")
            ),
        },
        "mutation_boundary": ocr_retry_execution_mutation_boundary(),
        "output": {
            "written": False,
            "root": str(execution_dir or ""),
            "run_dir": "",
        },
        "execution_blockers": list(execution_blockers),
        "warnings": [blocker["detail"] for blocker in execution_blockers],
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _write_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_ocr_retry_execution_bundle(
    *,
    db_path: Path,
    selection_path: Path | None,
    confirm_token: str,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
    execution_dir: Path | None = None,
    ocr_provider: str = "scaffold",
    ocr_model: str = DEFAULT_OCR_RETRY_MODEL,
    ocr_prompt: str = DEFAULT_OCR_RETRY_PROMPT,
    run_id: str | None = None,
    ocr_runner: OcrRetryRunner | None = None,
) -> dict[str, Any]:
    resolved_selection_path = selection_path.expanduser() if selection_path else None
    resolved_execution_root = (
        execution_dir.expanduser() if execution_dir else DEFAULT_OCR_RETRY_EXECUTION_DIR
    )
    normalized_provider = (ocr_provider or "scaffold").strip().lower()
    normalized_model = (ocr_model or DEFAULT_OCR_RETRY_MODEL).strip()
    normalized_prompt = (ocr_prompt or DEFAULT_OCR_RETRY_PROMPT).strip()

    readiness_report = (
        build_ocr_retry_execution_readiness_report(
            db_path=db_path,
            selection_path=resolved_selection_path,
            outcome=outcome,
            cohort=cohort,
            limit=limit,
            artifact_ids=artifact_ids,
        )
        if resolved_selection_path is not None
        else None
    )

    blockers: list[dict[str, str]] = []
    if resolved_selection_path is None:
        blockers.append(
            _ocr_retry_execution_blocker(
                "missing_selection_path",
                "SELECTION_PATH is required before OCR retry execution.",
            )
        )
    elif not resolved_selection_path.is_file():
        blockers.append(
            _ocr_retry_execution_blocker(
                "selection_path_not_found",
                f"OCR retry selection decision file was not found: {resolved_selection_path}",
            )
        )
    if confirm_token != OCR_RETRY_EXECUTION_CONFIRM_TOKEN:
        blockers.append(
            _ocr_retry_execution_blocker(
                "missing_confirmation",
                "CONFIRM=ocr-retry-execute is required before OCR retry execution.",
            )
        )
    readiness_state = (
        str(readiness_report.get("state") or "unknown")
        if isinstance(readiness_report, dict)
        else "not_checked"
    )
    readiness_counts = (
        readiness_report.get("counts") if isinstance(readiness_report, dict) else {}
    )
    if not isinstance(readiness_counts, dict):
        readiness_counts = {}
    if isinstance(readiness_report, dict) and readiness_state != "ready":
        blockers.append(
            _ocr_retry_execution_blocker(
                "readiness_not_ready",
                f"OCR retry execution readiness is {readiness_state}.",
            )
        )
    if (
        isinstance(readiness_report, dict)
        and readiness_state == "ready"
        and _int_value(readiness_counts.get("executable_items")) < 1
    ):
        blockers.append(
            _ocr_retry_execution_blocker(
                "no_executable_items",
                "No executable OCR retry items were selected.",
            )
        )
    if resolved_execution_root.exists() and not resolved_execution_root.is_dir():
        blockers.append(
            _ocr_retry_execution_blocker(
                "execution_dir_not_directory",
                f"OCR retry execution output path is not a directory: {resolved_execution_root}",
            )
        )
    if blockers:
        return _blocked_ocr_retry_execution_report(
            readiness_report=readiness_report,
            selection_path=resolved_selection_path,
            confirm_token=confirm_token,
            execution_blockers=blockers,
            ocr_provider=normalized_provider,
            ocr_model=normalized_model,
            execution_dir=resolved_execution_root,
        )

    assert readiness_report is not None
    actual_run_id = run_id or (
        f"ocr-retry-{_utc_run_timestamp()}-"
        f"{_selection_file_fingerprint(resolved_selection_path)[:10]}-"
        f"{uuid.uuid4().hex[:8]}"
    )
    run_dir = resolved_execution_root / actual_run_id
    if run_dir.exists():
        return _blocked_ocr_retry_execution_report(
            readiness_report=readiness_report,
            selection_path=resolved_selection_path,
            confirm_token=confirm_token,
            execution_blockers=[
                _ocr_retry_execution_blocker(
                    "execution_run_dir_exists",
                    f"OCR retry execution run directory already exists: {run_dir}",
                )
            ],
            ocr_provider=normalized_provider,
            ocr_model=normalized_model,
            execution_dir=resolved_execution_root,
        )

    requests = build_ocr_retry_execution_requests(
        run_id=actual_run_id,
        readiness_report=readiness_report,
        ocr_provider=normalized_provider,
        ocr_model=normalized_model,
    )
    if not requests:
        return _blocked_ocr_retry_execution_report(
            readiness_report=readiness_report,
            selection_path=resolved_selection_path,
            confirm_token=confirm_token,
            execution_blockers=[
                _ocr_retry_execution_blocker(
                    "no_execution_requests",
                    "No OCR retry execution requests could be built.",
                )
            ],
            ocr_provider=normalized_provider,
            ocr_model=normalized_model,
            execution_dir=resolved_execution_root,
        )

    run_dir.mkdir(parents=True)
    files = {
        "manifest": str(run_dir / "manifest.json"),
        "requests": str(run_dir / "requests.jsonl"),
        "responses": str(run_dir / "responses.jsonl"),
        "summary": str(run_dir / "summary.json"),
    }
    manifest = {
        "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
        "run_id": actual_run_id,
        "created_at": datetime.now(UTC).isoformat(),
        "execution_mode": "local_bundle",
        "selection_path": str(resolved_selection_path),
        "selection_fingerprint": _selection_file_fingerprint(resolved_selection_path),
        "readiness_schema_version": readiness_report.get("schema_version", ""),
        "readiness_state": readiness_report.get("state", "unknown"),
        "readiness_counts": readiness_counts,
        "filters": readiness_report.get("filters")
        if isinstance(readiness_report.get("filters"), dict)
        else {},
        "decision_source": readiness_report.get("decision_source")
        if isinstance(readiness_report.get("decision_source"), dict)
        else {},
        "ocr_provider": normalized_provider,
        "ocr_model": normalized_model,
        "request_count": len(requests),
        "mutation_boundary": ocr_retry_execution_mutation_boundary(),
        "files": files,
    }
    _write_json(run_dir / "manifest.json", manifest)
    _write_jsonl(run_dir / "requests.jsonl", requests)

    runner = ocr_runner or (
        lambda request: run_default_ocr_retry_request(
            request,
            ocr_provider=normalized_provider,
            ocr_model=normalized_model,
            ocr_prompt=normalized_prompt,
        )
    )
    responses: list[dict[str, Any]] = []
    stop_reason = ""
    for request in requests:
        try:
            responses.append(
                normalize_ocr_retry_response(
                    request=request,
                    raw_response=runner(request),
                )
            )
        except Exception as exc:  # noqa: BLE001 - provider errors must be recorded
            response = error_ocr_retry_response(request=request, exc=exc)
            responses.append(response)
            if response["status"] in {"rate_limited", "provider_unavailable"}:
                stop_reason = str(response["status"])
                break

    _write_jsonl(run_dir / "responses.jsonl", responses)
    succeeded = sum(1 for response in responses if response.get("status") == "ok")
    failed = len(responses) - succeeded
    skipped = len(requests) - len(responses)
    state = "completed"
    if failed and succeeded:
        state = "partial_failure"
    elif failed:
        state = "failed"
    summary = {
        "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
        "run_id": actual_run_id,
        "state": state,
        "execution_mode": "local_bundle",
        "selection_path": str(resolved_selection_path),
        "selection_fingerprint": manifest["selection_fingerprint"],
        "readiness_schema_version": manifest["readiness_schema_version"],
        "readiness_state": readiness_report.get("state", "unknown"),
        "ocr_provider": normalized_provider,
        "ocr_model": normalized_model,
        "counts": {
            "readiness_items": _int_value(readiness_counts.get("readiness_items")),
            "executable_items": _int_value(readiness_counts.get("executable_items")),
            "requests": len(requests),
            "responses": len(responses),
            "succeeded": succeeded,
            "failed": failed,
            "skipped_after_stop": skipped,
            "context_only_skipped": _int_value(
                readiness_counts.get("context_only_items")
            ),
        },
        "stop_reason": stop_reason,
        "mutation_boundary": ocr_retry_execution_mutation_boundary(),
        "output": {
            "written": True,
            "root": str(resolved_execution_root),
            "run_dir": str(run_dir),
            "files": files,
        },
    }
    _write_json(run_dir / "summary.json", summary)
    return summary
