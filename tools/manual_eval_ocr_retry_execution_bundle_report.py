from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

from tools.manual_eval_ocr_retry_report_formatters import int_value as _int_value


OCR_RETRY_EXECUTION_SCHEMA_VERSION = "polinko.manual_eval_ocr_retry_execution.v1"
OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_execution_report.v1"
)


def ocr_retry_execution_mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "read_only",
        "feedback_closure": "none",
        "live_eval_rows": "none",
        "manual_eval_warehouse": "none",
    }


def read_json_object(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [f"{path.name} could not be read: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"{path.name} is not valid JSON: {exc}"]
    if not isinstance(payload, dict):
        return None, [f"{path.name} must contain a JSON object"]
    return payload, []


def read_jsonl_objects(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return rows, [f"{path.name} could not be read: {exc}"]
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{index} is not valid JSON: {exc}")
            continue
        if isinstance(payload, dict):
            rows.append(payload)
        else:
            errors.append(f"{path.name}:{index} must contain a JSON object")
    return rows, errors


def _bundle_path_under_run_dir(path: Path, run_dir: Path) -> bool:
    try:
        resolved_path = path.resolve()
        resolved_run_dir = run_dir.resolve()
    except OSError:
        return False
    return (
        resolved_path == resolved_run_dir or resolved_run_dir in resolved_path.parents
    )


def _bundle_file_path(value: object, *, run_dir: Path, fallback_name: str) -> Path:
    raw_path = str(value or "").strip()
    if not raw_path:
        return run_dir / fallback_name
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    if _bundle_path_under_run_dir(path, run_dir):
        return path
    return run_dir / path


def _bundle_mutation_boundary_ok(boundary: object) -> bool:
    return boundary == ocr_retry_execution_mutation_boundary()


def _append_execution_bundle_blocker(
    blockers: list[dict[str, str]],
    *,
    code: str,
    detail: str,
) -> None:
    blockers.append({"code": code, "detail": detail})


def _check_execution_bundle_schema_versions(
    *,
    manifest: dict[str, Any] | None,
    summary: dict[str, Any] | None,
    requests: Sequence[dict[str, Any]],
    responses: Sequence[dict[str, Any]],
    blockers: list[dict[str, str]],
) -> None:
    payloads: list[tuple[str, dict[str, Any]]] = []
    if manifest is not None:
        payloads.append(("manifest.json", manifest))
    if summary is not None:
        payloads.append(("summary.json", summary))
    payloads.extend(
        (f"requests.jsonl:{index}", row) for index, row in enumerate(requests, start=1)
    )
    payloads.extend(
        (f"responses.jsonl:{index}", row)
        for index, row in enumerate(responses, start=1)
    )
    for label, payload in payloads:
        if payload.get("schema_version") != OCR_RETRY_EXECUTION_SCHEMA_VERSION:
            _append_execution_bundle_blocker(
                blockers,
                code="schema_version_mismatch",
                detail=(
                    f"{label} schema_version must be "
                    f"{OCR_RETRY_EXECUTION_SCHEMA_VERSION}"
                ),
            )


def _check_execution_bundle_run_ids(
    *,
    manifest: dict[str, Any] | None,
    summary: dict[str, Any] | None,
    requests: Sequence[dict[str, Any]],
    responses: Sequence[dict[str, Any]],
    blockers: list[dict[str, str]],
) -> str:
    run_ids = [
        str(payload.get("run_id") or "")
        for payload in (manifest, summary)
        if isinstance(payload, dict)
    ]
    run_ids.extend(str(row.get("run_id") or "") for row in requests)
    run_ids.extend(str(row.get("run_id") or "") for row in responses)
    non_empty_run_ids = [run_id for run_id in run_ids if run_id]
    unique_run_ids = sorted(set(non_empty_run_ids))
    if not non_empty_run_ids:
        _append_execution_bundle_blocker(
            blockers,
            code="missing_run_id",
            detail="execution bundle does not contain a run_id",
        )
        return ""
    if len(unique_run_ids) != 1 or len(non_empty_run_ids) != len(run_ids):
        _append_execution_bundle_blocker(
            blockers,
            code="run_id_mismatch",
            detail="manifest, summary, requests, and responses must share one run_id",
        )
    return unique_run_ids[0]


def _check_execution_bundle_mutation_boundary(
    *,
    manifest: dict[str, Any] | None,
    summary: dict[str, Any] | None,
    requests: Sequence[dict[str, Any]],
    responses: Sequence[dict[str, Any]],
    blockers: list[dict[str, str]],
) -> None:
    for label, payload in (("manifest.json", manifest), ("summary.json", summary)):
        if not isinstance(payload, dict):
            continue
        if not _bundle_mutation_boundary_ok(payload.get("mutation_boundary")):
            _append_execution_bundle_blocker(
                blockers,
                code="mutation_boundary_mismatch",
                detail=f"{label} mutation_boundary must match local-bundle no-mutation contract",
            )
    for label, rows in (("requests.jsonl", requests), ("responses.jsonl", responses)):
        for index, row in enumerate(rows, start=1):
            if str(row.get("warehouse_mutation") or "") != "none":
                _append_execution_bundle_blocker(
                    blockers,
                    code="warehouse_mutation_not_none",
                    detail=f"{label}:{index} warehouse_mutation must be none",
                )
            for field in (
                "feedback_closure",
                "live_eval_rows",
                "manual_eval_warehouse",
            ):
                if field in row and str(row.get(field) or "") != "none":
                    _append_execution_bundle_blocker(
                        blockers,
                        code="unexpected_mutation_field",
                        detail=f"{label}:{index} {field} must be none when present",
                    )


def _check_execution_bundle_counts(
    *,
    manifest: dict[str, Any] | None,
    summary: dict[str, Any] | None,
    requests: Sequence[dict[str, Any]],
    responses: Sequence[dict[str, Any]],
    blockers: list[dict[str, str]],
) -> dict[str, int]:
    succeeded = sum(1 for response in responses if response.get("status") == "ok")
    failed = len(responses) - succeeded
    skipped = len(requests) - len(responses)
    counts = {
        "requests": len(requests),
        "responses": len(responses),
        "succeeded": succeeded,
        "failed": failed,
        "skipped_after_stop": max(0, skipped),
    }
    if not requests:
        _append_execution_bundle_blocker(
            blockers,
            code="missing_requests",
            detail="requests.jsonl must contain at least one OCR retry request",
        )
    if manifest is not None and _int_value(manifest.get("request_count")) != len(
        requests
    ):
        _append_execution_bundle_blocker(
            blockers,
            code="manifest_request_count_mismatch",
            detail="manifest request_count must match requests.jsonl rows",
        )
    summary_counts = summary.get("counts") if isinstance(summary, dict) else None
    if isinstance(summary_counts, dict):
        for key, expected in counts.items():
            if _int_value(summary_counts.get(key)) != expected:
                _append_execution_bundle_blocker(
                    blockers,
                    code="summary_count_mismatch",
                    detail=f"summary counts.{key} must be {expected}",
                )
    if skipped < 0:
        _append_execution_bundle_blocker(
            blockers,
            code="response_count_exceeds_requests",
            detail="responses.jsonl has more rows than requests.jsonl",
        )
    if (
        skipped > 0
        and summary is not None
        and not str(summary.get("stop_reason") or "")
    ):
        _append_execution_bundle_blocker(
            blockers,
            code="missing_stop_reason",
            detail="summary stop_reason is required when responses stop before all requests",
        )
    expected_summary_state = "completed"
    if failed and succeeded:
        expected_summary_state = "partial_failure"
    elif failed:
        expected_summary_state = "failed"
    if (
        isinstance(summary, dict)
        and str(summary.get("state") or "") != expected_summary_state
    ):
        _append_execution_bundle_blocker(
            blockers,
            code="summary_state_mismatch",
            detail=f"summary state must be {expected_summary_state}",
        )
    return counts


def _check_execution_bundle_request_response_alignment(
    *,
    requests: Sequence[dict[str, Any]],
    responses: Sequence[dict[str, Any]],
    blockers: list[dict[str, str]],
) -> None:
    request_ids = [str(request.get("request_id") or "") for request in requests]
    response_ids = [str(response.get("request_id") or "") for response in responses]
    if len(set(request_ids)) != len(request_ids) or any(
        not item for item in request_ids
    ):
        _append_execution_bundle_blocker(
            blockers,
            code="request_id_invalid",
            detail="requests.jsonl request_id values must be non-empty and unique",
        )
    unknown_response_ids = sorted(set(response_ids) - set(request_ids))
    if unknown_response_ids:
        _append_execution_bundle_blocker(
            blockers,
            code="response_request_id_unmatched",
            detail="responses.jsonl contains request_id values not present in requests.jsonl",
        )
    duplicate_response_ids = [
        request_id
        for request_id in sorted(set(response_ids))
        if response_ids.count(request_id) > 1
    ]
    if duplicate_response_ids:
        _append_execution_bundle_blocker(
            blockers,
            code="response_request_id_duplicate",
            detail="responses.jsonl request_id values must be unique",
        )


def _bundle_payload_value(
    primary: dict[str, Any] | None,
    secondary: dict[str, Any] | None,
    key: str,
) -> object:
    if isinstance(primary, dict) and primary.get(key):
        return primary.get(key)
    if isinstance(secondary, dict) and secondary.get(key):
        return secondary.get(key)
    return ""


def build_ocr_retry_execution_bundle_report(
    *,
    run_dir: Path | None,
) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    warnings: list[str] = []
    if run_dir is None:
        _append_execution_bundle_blocker(
            blockers,
            code="missing_run_dir",
            detail="RUN_DIR is required before inspecting an OCR retry execution bundle.",
        )
        return {
            "schema_version": OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION,
            "state": "error",
            "run_dir": "",
            "run_id": "",
            "execution_state": "unknown",
            "readiness_state": "unknown",
            "counts": {
                "requests": 0,
                "responses": 0,
                "succeeded": 0,
                "failed": 0,
                "skipped_after_stop": 0,
                "files_available": 0,
                "files_expected": 4,
            },
            "mutation_boundary": ocr_retry_execution_mutation_boundary(),
            "inspection_blockers": blockers,
            "warnings": [blocker["detail"] for blocker in blockers],
        }

    resolved_run_dir = run_dir.expanduser()
    if not resolved_run_dir.is_dir():
        _append_execution_bundle_blocker(
            blockers,
            code="run_dir_not_found",
            detail="OCR retry execution run directory was not found.",
        )
        return {
            "schema_version": OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION,
            "state": "error",
            "run_dir": str(resolved_run_dir),
            "run_id": resolved_run_dir.name,
            "execution_state": "unknown",
            "readiness_state": "unknown",
            "counts": {
                "requests": 0,
                "responses": 0,
                "succeeded": 0,
                "failed": 0,
                "skipped_after_stop": 0,
                "files_available": 0,
                "files_expected": 4,
            },
            "mutation_boundary": ocr_retry_execution_mutation_boundary(),
            "inspection_blockers": blockers,
            "warnings": [blocker["detail"] for blocker in blockers],
        }

    expected_files = {
        "manifest": "manifest.json",
        "requests": "requests.jsonl",
        "responses": "responses.jsonl",
        "summary": "summary.json",
    }
    manifest_path = resolved_run_dir / expected_files["manifest"]
    manifest: dict[str, Any] | None = None
    if manifest_path.is_file():
        manifest, parse_errors = read_json_object(manifest_path)
        for error in parse_errors:
            _append_execution_bundle_blocker(
                blockers, code="file_parse_error", detail=error
            )
    else:
        _append_execution_bundle_blocker(
            blockers,
            code="missing_bundle_file",
            detail="manifest.json is required in an OCR retry execution bundle.",
        )

    file_paths: dict[str, Path] = {
        key: resolved_run_dir / filename for key, filename in expected_files.items()
    }
    if isinstance(manifest, dict):
        manifest_files = manifest.get("files")
        if isinstance(manifest_files, dict):
            for key, filename in expected_files.items():
                file_paths[key] = _bundle_file_path(
                    manifest_files.get(key),
                    run_dir=resolved_run_dir,
                    fallback_name=filename,
                )

    file_reports: list[dict[str, Any]] = []
    files_under_run_dir: dict[str, bool] = {}
    for key, path in file_paths.items():
        exists = path.is_file()
        under_run_dir = _bundle_path_under_run_dir(path, resolved_run_dir)
        files_under_run_dir[key] = under_run_dir
        if not exists:
            _append_execution_bundle_blocker(
                blockers,
                code="missing_bundle_file",
                detail=f"{expected_files[key]} is required in an OCR retry execution bundle.",
            )
        if not under_run_dir:
            _append_execution_bundle_blocker(
                blockers,
                code="bundle_file_outside_run_dir",
                detail=f"{expected_files[key]} must be inside the run directory.",
            )
        file_reports.append(
            {
                "name": expected_files[key],
                "path": str(path),
                "exists": exists,
                "under_run_dir": under_run_dir,
            }
        )

    summary: dict[str, Any] | None = None
    requests: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    if file_paths["summary"].is_file() and files_under_run_dir.get("summary"):
        summary, parse_errors = read_json_object(file_paths["summary"])
        for error in parse_errors:
            _append_execution_bundle_blocker(
                blockers, code="file_parse_error", detail=error
            )
    if file_paths["requests"].is_file() and files_under_run_dir.get("requests"):
        requests, parse_errors = read_jsonl_objects(file_paths["requests"])
        for error in parse_errors:
            _append_execution_bundle_blocker(
                blockers, code="file_parse_error", detail=error
            )
    if file_paths["responses"].is_file() and files_under_run_dir.get("responses"):
        responses, parse_errors = read_jsonl_objects(file_paths["responses"])
        for error in parse_errors:
            _append_execution_bundle_blocker(
                blockers, code="file_parse_error", detail=error
            )

    _check_execution_bundle_schema_versions(
        manifest=manifest,
        summary=summary,
        requests=requests,
        responses=responses,
        blockers=blockers,
    )
    run_id = _check_execution_bundle_run_ids(
        manifest=manifest,
        summary=summary,
        requests=requests,
        responses=responses,
        blockers=blockers,
    )
    _check_execution_bundle_mutation_boundary(
        manifest=manifest,
        summary=summary,
        requests=requests,
        responses=responses,
        blockers=blockers,
    )
    counts = _check_execution_bundle_counts(
        manifest=manifest,
        summary=summary,
        requests=requests,
        responses=responses,
        blockers=blockers,
    )
    _check_execution_bundle_request_response_alignment(
        requests=requests,
        responses=responses,
        blockers=blockers,
    )

    if counts["failed"] or counts["skipped_after_stop"]:
        warnings.append("bundle contains provider failures or skipped requests")
    state = "error" if blockers else "attention" if warnings else "ok"
    files_available = sum(1 for item in file_reports if item["exists"])
    execution_state = str(summary.get("state") or "unknown") if summary else "unknown"
    readiness_state = str(
        _bundle_payload_value(summary, manifest, "readiness_state") or "unknown"
    )
    ocr_provider = str(_bundle_payload_value(summary, manifest, "ocr_provider"))
    ocr_model = str(_bundle_payload_value(summary, manifest, "ocr_model"))
    mutation_boundary = (
        summary.get("mutation_boundary")
        if isinstance(summary, dict)
        and isinstance(summary.get("mutation_boundary"), dict)
        else ocr_retry_execution_mutation_boundary()
    )
    return {
        "schema_version": OCR_RETRY_EXECUTION_REPORT_SCHEMA_VERSION,
        "state": state,
        "run_dir": str(resolved_run_dir),
        "run_id": run_id or resolved_run_dir.name,
        "execution_state": execution_state,
        "readiness_state": readiness_state,
        "ocr_provider": ocr_provider,
        "ocr_model": ocr_model,
        "counts": {
            **counts,
            "files_available": files_available,
            "files_expected": len(expected_files),
        },
        "mutation_boundary": mutation_boundary,
        "files": file_reports,
        "source_paths": {
            "terminal": "hidden",
            "request_sources": sum(
                1
                for request in requests
                if isinstance(request.get("source"), dict)
                and str(
                    cast(dict[str, Any], request["source"]).get("resolved_path") or ""
                )
            ),
        },
        "inspection_blockers": blockers,
        "warnings": warnings,
    }


def execution_bundle_report_file_path(
    report: dict[str, Any],
    filename: str,
) -> Path | None:
    files = report.get("files")
    if not isinstance(files, list):
        return None
    for item in files:
        if not isinstance(item, dict):
            continue
        if item.get("name") != filename:
            continue
        if not item.get("exists") or not item.get("under_run_dir"):
            return None
        return Path(str(item.get("path") or ""))
    return None
