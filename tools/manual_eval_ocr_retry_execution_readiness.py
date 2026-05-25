from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_selection_apply_preview import (
    build_ocr_retry_selection_apply_preview_report,
)
from tools.manual_eval_ocr_retry_selection_review import (
    OCR_RETRY_SELECTION_ALLOWED_ACTIONS,
)
from tools.manual_eval_ocr_retry_selection_validation import (
    format_validation_artifact_ids,
    format_validation_issues,
)


OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_execution_readiness.v1"
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


def _format_feedback_ids(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    return ",".join(str(_int_value(item)) for item in value)


def _format_input_blocker_state(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    state = str(value.get("state") or "unknown")
    reason_code = str(value.get("reason_code") or "")
    next_action = str(value.get("next_action") or "")
    if not reason_code and not next_action:
        return state
    parts = [state]
    if reason_code:
        parts.append(f"reason={reason_code}")
    if next_action:
        parts.append(f"next={next_action}")
    return " ".join(parts)


def _format_terminal_source_path(value: object) -> str:
    raw_path = str(value or "").strip()
    if not raw_path:
        return "none"
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path.name or "none"
    return raw_path


def _execution_readiness_artifact(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    payload_inputs = artifact.get("payload_inputs")
    if not isinstance(payload_inputs, dict):
        payload_inputs = {}
    command_preview = artifact.get("command_preview")
    if not isinstance(command_preview, dict):
        command_preview = {}
    resolved_path = str(artifact.get("resolved_path") or "").strip()
    artifact_id = str(artifact.get("artifact_id") or "").strip()
    issues: list[str] = []
    if not artifact_id:
        issues.append("missing_artifact_id")
    if not resolved_path:
        issues.append("missing_resolved_path")
        source_file_exists = False
    else:
        source_file_exists = Path(resolved_path).is_file()
        if not source_file_exists:
            issues.append("source_file_missing")
    if str(payload_inputs.get("operation") or "") != "ocr_retry_rerun_or_case_curation":
        issues.append("unexpected_payload_operation")
    if str(command_preview.get("mode") or "payload_only") != "payload_only":
        issues.append("unexpected_command_preview_mode")
    return {
        "artifact_id": artifact_id,
        "state": "blocked" if issues else "ready",
        "issues": issues,
        "source_file_exists": source_file_exists,
        "resolved_path": resolved_path,
        "source_image_name": str(artifact.get("source_image_name") or ""),
        "ocr_run_id": str(artifact.get("ocr_run_id") or ""),
        "source_session_id": str(artifact.get("source_session_id") or ""),
        "session_id": str(artifact.get("session_id") or ""),
        "payload_inputs": payload_inputs,
        "command_preview": {
            "mode": str(command_preview.get("mode") or "payload_only"),
            "label": str(command_preview.get("label") or ""),
            "payload_schema": str(command_preview.get("payload_schema") or ""),
        },
        "preview_only": True,
    }


def _execution_readiness_item(item: dict[str, Any]) -> dict[str, Any]:
    action = str(item.get("selected_action") or "")
    selected_artifacts = item.get("selected_artifacts")
    if not isinstance(selected_artifacts, list):
        selected_artifacts = []
    readiness_artifacts = [
        _execution_readiness_artifact(artifact)
        for artifact in selected_artifacts
        if isinstance(artifact, dict)
    ]
    issues: list[str] = []
    if action not in OCR_RETRY_SELECTION_ALLOWED_ACTIONS:
        issues.append("invalid_selected_action")
    elif action in {"rerun_input", "curated_case"} and not readiness_artifacts:
        issues.append("missing_selected_artifact")
    elif action == "context_only" and readiness_artifacts:
        issues.append("context_only_must_not_select_artifacts")
    if any(artifact["state"] != "ready" for artifact in readiness_artifacts):
        issues.append("selected_artifact_not_executable")
    state = "blocked" if issues else "ready"
    return {
        "shortlist_id": str(item.get("shortlist_id") or ""),
        "state": state,
        "issues": issues,
        "selected_action": action,
        "executable": state == "ready" and action in {"rerun_input", "curated_case"},
        "execution_gate": "explicit_follow_up_required",
        "mutation": "none",
        "execution": "none",
        "feedback_ids": item.get("feedback_ids")
        if isinstance(item.get("feedback_ids"), list)
        else [],
        "source_session_id": str(item.get("source_session_id") or ""),
        "session_id": str(item.get("session_id") or ""),
        "source_image_name": str(item.get("source_image_name") or ""),
        "resolved_path": str(item.get("resolved_path") or ""),
        "selected_artifact_ids": item.get("selected_artifact_ids")
        if isinstance(item.get("selected_artifact_ids"), list)
        else [],
        "selected_artifacts": readiness_artifacts,
        "feedback_closure_state": item.get("feedback_closure_state")
        if isinstance(item.get("feedback_closure_state"), dict)
        else {},
        "feedback_closure_blocked": bool(item.get("feedback_closure_blocked")),
        "preview_only": True,
    }


def build_ocr_retry_execution_readiness_report(
    *,
    db_path: Path,
    selection_path: Path | None = None,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    apply_report = build_ocr_retry_selection_apply_preview_report(
        db_path=db_path,
        selection_path=selection_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    apply_counts = apply_report.get("counts")
    if not isinstance(apply_counts, dict):
        apply_counts = {}
    apply_filters = apply_report.get("filters")
    if not isinstance(apply_filters, dict):
        apply_filters = {}
    decision_source = apply_report.get("decision_source")
    if not isinstance(decision_source, dict):
        decision_source = {}
    preview = apply_report.get("application_preview")
    if not isinstance(preview, dict):
        preview = {}
    apply_items = preview.get("items")
    if not isinstance(apply_items, list):
        apply_items = []

    apply_state = str(apply_report.get("state") or "unknown")
    readiness_items = (
        [
            _execution_readiness_item(item)
            for item in apply_items
            if isinstance(item, dict)
        ]
        if apply_state == "ok"
        else []
    )
    item_blockers = [item for item in readiness_items if item.get("state") != "ready"]
    validation_blockers = apply_report.get("validation_blockers")
    if not isinstance(validation_blockers, list):
        validation_blockers = []
    state = "ready" if apply_state == "ok" and not item_blockers else "blocked"
    source_files_ready = sum(
        1
        for item in readiness_items
        for artifact in item.get("selected_artifacts", [])
        if isinstance(artifact, dict) and artifact.get("source_file_exists")
    )
    source_files_missing = sum(
        1
        for item in readiness_items
        for artifact in item.get("selected_artifacts", [])
        if isinstance(artifact, dict) and not artifact.get("source_file_exists")
    )
    selected_artifacts = sum(
        len(item.get("selected_artifacts", []))
        for item in readiness_items
        if isinstance(item.get("selected_artifacts"), list)
    )

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_EXECUTION_READINESS_SCHEMA_VERSION,
        "selection_apply_preview_schema_version": apply_report.get(
            "schema_version", ""
        ),
        "state": state,
        "apply_preview_state": apply_state,
        "validation_state": str(apply_report.get("validation_state") or "unknown"),
        "manual_evals_db": apply_report.get("manual_evals_db", {}),
        "decision_source": decision_source,
        "filters": {
            "status": apply_filters.get("status") or "open",
            "outcome": apply_filters.get("outcome") or "",
            "cohort": apply_filters.get("cohort") or "",
            "limit": _int_value(apply_filters.get("limit")),
            "packet_basis": "selection_apply_preview_execution_readiness",
            "selection_mode": apply_filters.get("selection_mode") or "",
            "artifact_ids": apply_filters.get("artifact_ids")
            if isinstance(apply_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(apply_counts.get("total_feedback_rows")),
            "returned_feedback_rows": _int_value(
                apply_counts.get("returned_feedback_rows")
            ),
            "shortlist_items": _int_value(apply_counts.get("shortlist_items")),
            "candidate_artifacts": _int_value(apply_counts.get("candidate_artifacts")),
            "submitted_decisions": _int_value(apply_counts.get("submitted_decisions")),
            "valid_decisions": _int_value(apply_counts.get("valid_decisions")),
            "pending_decisions": _int_value(apply_counts.get("pending_decisions")),
            "invalid_decisions": _int_value(apply_counts.get("invalid_decisions")),
            "blocked_by_validation": _int_value(
                apply_counts.get("blocked_by_validation")
            ),
            "apply_preview_items": _int_value(apply_counts.get("preview_items")),
            "readiness_items": len(readiness_items),
            "ready_items": sum(
                1 for item in readiness_items if item.get("state") == "ready"
            ),
            "blocked_items": len(item_blockers),
            "executable_items": sum(
                1 for item in readiness_items if item.get("executable")
            ),
            "rerun_input_items": _int_value(apply_counts.get("rerun_input_items")),
            "curated_case_items": _int_value(apply_counts.get("curated_case_items")),
            "context_only_items": _int_value(apply_counts.get("context_only_items")),
            "selected_artifacts": selected_artifacts,
            "source_files_ready": source_files_ready,
            "source_files_missing": source_files_missing,
            "feedback_closure_blocked_items": _int_value(
                apply_counts.get("feedback_closure_blocked_items")
            ),
            "requested_artifact_ids": _int_value(
                apply_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                apply_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(apply_counts.get("limit_applied")),
        },
        "readiness_contract": {
            "mutation": "none",
            "execution": "none",
            "readiness_only": True,
            "requires_validation_state": "ok",
            "requires_apply_preview_state": "ok",
            "requires_explicit_follow_up_gate": True,
        },
        "validation_blockers": validation_blockers,
        "readiness_blockers": item_blockers,
        "execution_readiness_items": readiness_items,
    }
    warnings = apply_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = list(warnings)
    if apply_state != "ok":
        report.setdefault("warnings", []).append(
            "execution readiness is blocked until selection apply-preview state is ok"
        )
    elif item_blockers:
        report.setdefault("warnings", []).append(
            "one or more selected OCR retry artifacts are not executable yet"
        )
    return report


def _format_execution_readiness_artifact(item: dict[str, Any]) -> str:
    command = item.get("command_preview")
    if not isinstance(command, dict):
        command = {}
    payload = item.get("payload_inputs")
    if not isinstance(payload, dict):
        payload = {}
    return (
        f"artifact={item.get('artifact_id') or 'none'} "
        f"state={item.get('state') or 'unknown'} "
        f"issues={format_validation_issues(item.get('issues'))} "
        f"source_exists={'yes' if item.get('source_file_exists') else 'no'} "
        f"ocr={item.get('ocr_run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"source_path={_format_terminal_source_path(item.get('resolved_path'))} "
        f"operation={payload.get('operation') or 'none'} "
        f"command={command.get('mode') or 'payload_only'}"
    )


def format_ocr_retry_execution_readiness_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    decision_source = report.get("decision_source")
    if not isinstance(decision_source, dict):
        decision_source = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    lines = [
        "manual eval OCR retry execution readiness: "
        f"state={report.get('state', 'unknown')} "
        f"validation={report.get('validation_state', 'unknown')} "
        f"apply_preview={report.get('apply_preview_state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('shortlist_items'))} "
        f"candidate_artifacts={_int_value(counts.get('candidate_artifacts'))} "
        f"submitted={_int_value(counts.get('submitted_decisions'))} "
        f"valid={_int_value(counts.get('valid_decisions'))} "
        f"pending={_int_value(counts.get('pending_decisions'))} "
        f"invalid={_int_value(counts.get('invalid_decisions'))} "
        f"validation_blocked={_int_value(counts.get('blocked_by_validation'))} "
        f"apply_items={_int_value(counts.get('apply_preview_items'))} "
        f"ready={_int_value(counts.get('ready_items'))} "
        f"executable={_int_value(counts.get('executable_items'))} "
        f"blocked={_int_value(counts.get('blocked_items'))} "
        f"rerun_input={_int_value(counts.get('rerun_input_items'))} "
        f"curated_case={_int_value(counts.get('curated_case_items'))} "
        f"context_only={_int_value(counts.get('context_only_items'))} "
        f"selected_artifacts={_int_value(counts.get('selected_artifacts'))} "
        f"source_files_ready={_int_value(counts.get('source_files_ready'))} "
        f"source_files_missing={_int_value(counts.get('source_files_missing'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        f"selection={filters.get('selection_mode') or 'unknown'} "
        f"requested_artifacts={_int_value(counts.get('requested_artifact_ids'))} "
        f"unmatched={_int_value(counts.get('unmatched_artifact_ids'))} "
        f"preview_only={'yes' if counts.get('preview_only') else 'no'} "
        f"decision_source={decision_source.get('state') or 'unknown'} "
        f"decision_path={decision_source.get('path') or 'none'} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    validation_blockers = report.get("validation_blockers")
    if isinstance(validation_blockers, list) and validation_blockers:
        lines.append("validation_blockers:")
        for blocker in validation_blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"shortlist={blocker.get('shortlist_id') or 'none'} "
                f"state={blocker.get('state') or 'unknown'} "
                f"issues={format_validation_issues(blocker.get('issues'))} "
                f"feedback={_format_feedback_ids(blocker.get('feedback_ids'))}"
            )

    readiness_items = report.get("execution_readiness_items")
    if not isinstance(readiness_items, list) or not readiness_items:
        lines.append("execution_readiness_items: none")
    else:
        for item in readiness_items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"action={item.get('selected_action') or 'unknown'} "
                f"shortlist={item.get('shortlist_id') or 'none'} "
                f"readiness={item.get('state') or 'unknown'} "
                f"executable={'yes' if item.get('executable') else 'no'} "
                f"issues={format_validation_issues(item.get('issues'))} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                "selected_artifacts="
                f"{format_validation_artifact_ids(item.get('selected_artifact_ids'))} "
                f"source_image={item.get('source_image_name') or 'none'} "
                f"source_path={_format_terminal_source_path(item.get('resolved_path'))} "
                f"gate={item.get('execution_gate') or 'none'} "
                f"mutation={item.get('mutation') or 'none'} "
                f"execution={item.get('execution') or 'none'} "
                f"preview_only={'yes' if item.get('preview_only') else 'no'}"
            )
            selected_artifacts = item.get("selected_artifacts")
            if isinstance(selected_artifacts, list) and selected_artifacts:
                lines.append("  selected_artifacts:")
                for artifact in selected_artifacts:
                    if isinstance(artifact, dict):
                        lines.append(
                            f"  - {_format_execution_readiness_artifact(artifact)}"
                        )

    readiness_blockers = report.get("readiness_blockers")
    if isinstance(readiness_blockers, list) and readiness_blockers:
        lines.append("readiness_blockers:")
        for blocker in readiness_blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"shortlist={blocker.get('shortlist_id') or 'none'} "
                f"action={blocker.get('selected_action') or 'unknown'} "
                f"issues={format_validation_issues(blocker.get('issues'))}"
            )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)
