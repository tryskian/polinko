from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from tools.manual_eval_ocr_retry_execution_bundle_report import (
    build_ocr_retry_execution_bundle_report,
    execution_bundle_report_file_path,
    ocr_retry_execution_mutation_boundary,
    read_jsonl_objects,
)
from tools.manual_eval_ocr_retry_feedback_db import int_value as _int_value


OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_feedback_closure_preview.v1"
)


def _feedback_ids_from_request(request: dict[str, Any]) -> list[str]:
    feedback_ids = request.get("feedback_ids")
    if not isinstance(feedback_ids, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for value in feedback_ids:
        feedback_id = str(value or "").strip()
        if not feedback_id or feedback_id in seen:
            continue
        normalized.append(feedback_id)
        seen.add(feedback_id)
    return normalized


def _request_source_image_name(request: dict[str, Any]) -> str:
    source = request.get("source")
    if not isinstance(source, dict):
        return ""
    return str(source.get("source_image_name") or "").strip()


def _append_feedback_closure_evidence(
    item: dict[str, Any],
    *,
    request: dict[str, Any],
    response: dict[str, Any] | None,
) -> None:
    response_status = (
        str(response.get("status") or "unknown")
        if isinstance(response, dict)
        else "missing_response"
    )
    evidence = {
        "request_id": str(request.get("request_id") or ""),
        "artifact_id": str(request.get("artifact_id") or ""),
        "shortlist_id": str(request.get("shortlist_id") or ""),
        "source_image_name": _request_source_image_name(request),
        "response_status": response_status,
        "extracted_text_preview": str(response.get("extracted_text_preview") or "")
        if isinstance(response, dict)
        else "",
        "extracted_text_chars": _int_value(response.get("extracted_text_chars"))
        if isinstance(response, dict)
        else 0,
    }
    cast(list[dict[str, Any]], item["evidence"]).append(evidence)


def _finalize_feedback_closure_item(
    item: dict[str, Any],
    *,
    run_id: str,
) -> dict[str, Any]:
    evidence = item.get("evidence")
    if not isinstance(evidence, list):
        evidence = []
    statuses = [
        str(row.get("response_status") or "unknown")
        for row in evidence
        if isinstance(row, dict)
    ]
    ok_count = sum(1 for status in statuses if status == "ok")
    non_ok_count = len(statuses) - ok_count
    state = "blocked"
    reason = "no_successful_ocr_retry_response"
    proposed_status = "open"
    action_taken_preview = (
        "Preview only: no successful OCR retry response is available; keep "
        "feedback open."
    )
    if ok_count and not non_ok_count:
        state = "ready"
        reason = "successful_ocr_retry_response"
        proposed_status = "closed"
        action_taken_preview = (
            "Preview only: OCR retry bundle "
            f"{run_id} produced successful retry evidence for feedback "
            f"{item.get('feedback_id')}; inspect the local bundle before closure."
        )
    elif ok_count and non_ok_count:
        state = "attention"
        reason = "mixed_ocr_retry_response_status"
        action_taken_preview = (
            "Preview only: mixed OCR retry statuses are present; review the "
            "local bundle before deciding whether to close feedback."
        )

    return {
        **item,
        "state": state,
        "reason": reason,
        "response_statuses": statuses,
        "proposed_feedback_status": proposed_status,
        "action_taken_preview": action_taken_preview,
        "feedback_closure": "preview_only",
        "mutation": "none",
    }


def _blocked_feedback_closure_preview_report(
    *,
    bundle_report: dict[str, Any],
    run_id: str,
    bundle_state: str,
    counts: dict[str, int],
    blockers: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
        "state": "blocked",
        "run_dir": str(bundle_report.get("run_dir") or ""),
        "run_id": run_id,
        "bundle_state": bundle_state,
        "counts": {
            "bundle_requests": counts.get("bundle_requests", 0),
            "bundle_responses": counts.get("bundle_responses", 0),
            "feedback_items": 0,
            "ready_feedback": 0,
            "attention_feedback": 0,
            "blocked_feedback": 0,
            "requests_without_feedback_ids": 0,
        },
        "mutation_boundary": ocr_retry_execution_mutation_boundary(),
        "closure_items": [],
        "preview_blockers": blockers,
        "warnings": [blocker["detail"] for blocker in blockers],
    }


def build_ocr_retry_feedback_closure_preview_report(
    *,
    run_dir: Path | None,
) -> dict[str, Any]:
    bundle_report = build_ocr_retry_execution_bundle_report(run_dir=run_dir)
    bundle_state = str(bundle_report.get("state") or "unknown")
    run_id = str(bundle_report.get("run_id") or "")
    mutation_boundary = ocr_retry_execution_mutation_boundary()
    if bundle_state == "error":
        inspection_blockers = bundle_report.get("inspection_blockers")
        if not isinstance(inspection_blockers, list):
            inspection_blockers = []
        return {
            "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
            "state": "blocked",
            "run_dir": str(bundle_report.get("run_dir") or ""),
            "run_id": run_id,
            "bundle_state": bundle_state,
            "counts": {
                "bundle_requests": 0,
                "bundle_responses": 0,
                "feedback_items": 0,
                "ready_feedback": 0,
                "attention_feedback": 0,
                "blocked_feedback": 0,
                "requests_without_feedback_ids": 0,
            },
            "mutation_boundary": mutation_boundary,
            "closure_items": [],
            "preview_blockers": inspection_blockers,
            "warnings": [str(item) for item in bundle_report.get("warnings", [])],
        }

    requests_path = execution_bundle_report_file_path(bundle_report, "requests.jsonl")
    responses_path = execution_bundle_report_file_path(bundle_report, "responses.jsonl")
    blockers: list[dict[str, str]] = []
    if requests_path is None or responses_path is None:
        blockers.append(
            {
                "code": "missing_bundle_rows",
                "detail": "requests.jsonl and responses.jsonl are required for closure preview.",
            }
        )
        return _blocked_feedback_closure_preview_report(
            bundle_report=bundle_report,
            run_id=run_id,
            bundle_state=bundle_state,
            counts={"bundle_requests": 0, "bundle_responses": 0},
            blockers=blockers,
        )

    requests, request_errors = read_jsonl_objects(requests_path)
    responses, response_errors = read_jsonl_objects(responses_path)
    for error in (*request_errors, *response_errors):
        blockers.append({"code": "bundle_parse_error", "detail": error})
    if blockers:
        return _blocked_feedback_closure_preview_report(
            bundle_report=bundle_report,
            run_id=run_id,
            bundle_state=bundle_state,
            counts={
                "bundle_requests": len(requests),
                "bundle_responses": len(responses),
            },
            blockers=blockers,
        )

    response_by_request_id = {
        str(response.get("request_id") or ""): response for response in responses
    }
    closure_items_by_feedback: dict[str, dict[str, Any]] = {}
    requests_without_feedback_ids = 0
    for request in requests:
        feedback_ids = _feedback_ids_from_request(request)
        if not feedback_ids:
            requests_without_feedback_ids += 1
            continue
        response = response_by_request_id.get(str(request.get("request_id") or ""))
        for feedback_id in feedback_ids:
            item = closure_items_by_feedback.setdefault(
                feedback_id,
                {
                    "feedback_id": feedback_id,
                    "evidence": [],
                },
            )
            _append_feedback_closure_evidence(
                item,
                request=request,
                response=response,
            )

    closure_items = [
        _finalize_feedback_closure_item(item, run_id=run_id)
        for item in closure_items_by_feedback.values()
    ]
    ready_feedback = sum(1 for item in closure_items if item["state"] == "ready")
    attention_feedback = sum(
        1 for item in closure_items if item["state"] == "attention"
    )
    blocked_feedback = sum(1 for item in closure_items if item["state"] == "blocked")
    warnings = [str(item) for item in bundle_report.get("warnings", [])]
    if requests_without_feedback_ids:
        warnings.append("one or more requests do not carry feedback IDs")
    state = (
        "ok" if closure_items and ready_feedback == len(closure_items) else "attention"
    )
    return {
        "schema_version": OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_SCHEMA_VERSION,
        "state": state,
        "run_dir": str(bundle_report.get("run_dir") or ""),
        "run_id": run_id,
        "bundle_state": bundle_state,
        "counts": {
            "bundle_requests": len(requests),
            "bundle_responses": len(responses),
            "feedback_items": len(closure_items),
            "ready_feedback": ready_feedback,
            "attention_feedback": attention_feedback,
            "blocked_feedback": blocked_feedback,
            "requests_without_feedback_ids": requests_without_feedback_ids,
        },
        "mutation_boundary": mutation_boundary,
        "closure_items": closure_items,
        "preview_blockers": [],
        "warnings": warnings,
    }
