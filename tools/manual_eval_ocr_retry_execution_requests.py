from __future__ import annotations

import mimetypes
from collections.abc import Callable
from typing import Any

from tools.manual_eval_ocr_retry_execution_bundle_report import (
    OCR_RETRY_EXECUTION_SCHEMA_VERSION,
)


class OcrRetryExecutionProviderError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status: str = "provider_error",
        retry_after: str = "",
    ) -> None:
        super().__init__(message)
        self.status = status
        self.retry_after = retry_after


OcrRetryRunner = Callable[[dict[str, Any]], dict[str, Any]]


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


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def short_text_preview(value: object, *, limit: int = 240) -> str:
    normalized = _normalize_text(value)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def build_ocr_retry_execution_requests(
    *,
    run_id: str,
    readiness_report: dict[str, Any],
    ocr_provider: str,
    ocr_model: str,
) -> list[dict[str, Any]]:
    readiness_items = readiness_report.get("execution_readiness_items")
    if not isinstance(readiness_items, list):
        return []
    requests: list[dict[str, Any]] = []
    for item in readiness_items:
        if not isinstance(item, dict) or not item.get("executable"):
            continue
        artifacts = item.get("selected_artifacts")
        if not isinstance(artifacts, list):
            continue
        for artifact in artifacts:
            if not isinstance(artifact, dict) or artifact.get("state") != "ready":
                continue
            payload_inputs = artifact.get("payload_inputs")
            if not isinstance(payload_inputs, dict):
                payload_inputs = {}
            resolved_path = str(artifact.get("resolved_path") or "").strip()
            mime_type = str(
                payload_inputs.get("mime_type")
                or mimetypes.guess_type(resolved_path)[0]
                or "application/octet-stream"
            )
            request_index = len(requests) + 1
            requests.append(
                {
                    "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
                    "run_id": run_id,
                    "request_id": f"{run_id}::{request_index:04d}",
                    "sequence": request_index,
                    "operation": "ocr_retry_rerun_or_case_curation",
                    "selected_action": str(item.get("selected_action") or ""),
                    "shortlist_id": str(item.get("shortlist_id") or ""),
                    "artifact_id": str(artifact.get("artifact_id") or ""),
                    "feedback_ids": item.get("feedback_ids")
                    if isinstance(item.get("feedback_ids"), list)
                    else [],
                    "source_session_id": str(artifact.get("source_session_id") or ""),
                    "session_id": str(artifact.get("session_id") or ""),
                    "ocr_run_id": str(artifact.get("ocr_run_id") or ""),
                    "source": {
                        "resolved_path": resolved_path,
                        "source_image_name": str(
                            artifact.get("source_image_name") or ""
                        ),
                        "mime_type": mime_type,
                        "source_file_exists": bool(artifact.get("source_file_exists")),
                    },
                    "provider": {
                        "name": ocr_provider,
                        "model": ocr_model,
                    },
                    "payload_inputs": payload_inputs,
                    "command_preview": artifact.get("command_preview")
                    if isinstance(artifact.get("command_preview"), dict)
                    else {},
                    "warehouse_mutation": "none",
                }
            )
    return requests


def normalize_ocr_retry_response(
    *,
    request: dict[str, Any],
    raw_response: dict[str, Any],
) -> dict[str, Any]:
    status = str(raw_response.get("status") or "ok")
    extracted_text = str(raw_response.get("extracted_text") or "")
    return {
        "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
        "run_id": request.get("run_id", ""),
        "request_id": request.get("request_id", ""),
        "artifact_id": request.get("artifact_id", ""),
        "shortlist_id": request.get("shortlist_id", ""),
        "status": status,
        "provider": str(raw_response.get("provider") or ""),
        "model": str(raw_response.get("model") or ""),
        "extracted_text_preview": str(
            raw_response.get("extracted_text_preview")
            or short_text_preview(extracted_text)
        ),
        "extracted_text_chars": _int_value(
            raw_response.get("chars")
            if "chars" in raw_response
            else len(extracted_text)
        ),
        "retry_after": str(raw_response.get("retry_after") or ""),
        "error": str(raw_response.get("error") or ""),
        "warehouse_mutation": "none",
    }


def error_ocr_retry_response(
    *,
    request: dict[str, Any],
    exc: Exception,
) -> dict[str, Any]:
    status = "provider_error"
    retry_after = ""
    if isinstance(exc, OcrRetryExecutionProviderError):
        status = exc.status
        retry_after = exc.retry_after
    return {
        "schema_version": OCR_RETRY_EXECUTION_SCHEMA_VERSION,
        "run_id": request.get("run_id", ""),
        "request_id": request.get("request_id", ""),
        "artifact_id": request.get("artifact_id", ""),
        "shortlist_id": request.get("shortlist_id", ""),
        "status": status,
        "provider": "",
        "model": "",
        "extracted_text_preview": "",
        "extracted_text_chars": 0,
        "retry_after": retry_after,
        "error": str(exc),
        "warehouse_mutation": "none",
    }
