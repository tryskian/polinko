from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_selection_formatters import (
    format_feedback_ids as _format_feedback_ids,
    format_input_blocker_state as _format_input_blocker_state,
    format_plan_thumbnail as _format_plan_thumbnail,
    format_terminal_source_path as _format_terminal_source_path,
    int_value as _int_value,
    truncate_text as _truncate_text,
)
from tools.manual_eval_ocr_retry_selection_review import (
    OCR_RETRY_SELECTION_ALLOWED_ACTIONS,
)
from tools.manual_eval_ocr_retry_selection_template import (
    build_ocr_retry_selection_template_report,
)
from tools.manual_eval_ocr_retry_selection_validation import (
    build_ocr_retry_selection_validation_report,
    feedback_closure_blocked,
    format_validation_artifact_ids,
    format_validation_issues,
    selection_template_items_by_shortlist_id,
)


OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_apply_preview.v1"
)


def _empty_selection_apply_actions() -> dict[str, list[dict[str, Any]]]:
    return {action: [] for action in OCR_RETRY_SELECTION_ALLOWED_ACTIONS}


def _selection_apply_selected_artifacts(
    *,
    template_item: dict[str, Any],
    selected_artifact_ids: Sequence[str],
) -> list[dict[str, Any]]:
    candidates = template_item.get("candidate_artifacts")
    if not isinstance(candidates, list):
        return []
    by_artifact_id = {
        str(candidate.get("artifact_id") or ""): candidate
        for candidate in candidates
        if isinstance(candidate, dict) and str(candidate.get("artifact_id") or "")
    }
    selected_artifacts: list[dict[str, Any]] = []
    for artifact_id in selected_artifact_ids:
        candidate = by_artifact_id.get(str(artifact_id))
        if not isinstance(candidate, dict):
            continue
        payload_inputs = candidate.get("payload_inputs")
        if not isinstance(payload_inputs, dict):
            payload_inputs = {}
        command_preview = candidate.get("command_preview")
        if not isinstance(command_preview, dict):
            command_preview = {}
        selected_artifacts.append(
            {
                "artifact_id": str(candidate.get("artifact_id") or ""),
                "ocr_run_id": str(candidate.get("ocr_run_id") or ""),
                "preview_only": bool(candidate.get("preview_only")),
                "source_session_id": str(
                    payload_inputs.get("source_session_id")
                    or template_item.get("source_session_id")
                    or ""
                ),
                "session_id": str(
                    payload_inputs.get("session_id")
                    or template_item.get("session_id")
                    or ""
                ),
                "feedback_ids": candidate.get("feedback_ids")
                if isinstance(candidate.get("feedback_ids"), list)
                else [],
                "source_image_name": str(candidate.get("source_image_name") or ""),
                "source_name": str(candidate.get("source_name") or ""),
                "resolved_path": str(candidate.get("resolved_path") or ""),
                "thumbnail": candidate.get("thumbnail")
                if isinstance(candidate.get("thumbnail"), dict)
                else {},
                "ocr_text_preview": str(candidate.get("ocr_text_preview") or ""),
                "payload_inputs": payload_inputs,
                "command_preview": {
                    "mode": str(command_preview.get("mode") or "payload_only"),
                    "label": str(command_preview.get("label") or ""),
                    "payload_schema": str(command_preview.get("payload_schema") or ""),
                },
            }
        )
    return selected_artifacts


def _selection_apply_item(
    *,
    validation_item: dict[str, Any],
    template_item: dict[str, Any],
) -> dict[str, Any]:
    selected_action = str(validation_item.get("selected_action") or "")
    selected_artifact_ids = validation_item.get("selected_artifact_ids")
    if not isinstance(selected_artifact_ids, list):
        selected_artifact_ids = []
    selected_artifacts = _selection_apply_selected_artifacts(
        template_item=template_item,
        selected_artifact_ids=[str(item) for item in selected_artifact_ids],
    )
    closure_state = validation_item.get("feedback_closure_state")
    if not isinstance(closure_state, dict):
        closure_state = {}
    return {
        "shortlist_id": str(validation_item.get("shortlist_id") or ""),
        "selected_action": selected_action,
        "application_mode": "preview_only",
        "mutation": "none",
        "execution": "none",
        "feedback_ids": validation_item.get("feedback_ids")
        if isinstance(validation_item.get("feedback_ids"), list)
        else [],
        "source_session_id": str(template_item.get("source_session_id") or ""),
        "session_id": str(template_item.get("session_id") or ""),
        "source_image_name": str(template_item.get("source_image_name") or ""),
        "resolved_path": str(template_item.get("resolved_path") or ""),
        "selected_artifact_ids": [str(item) for item in selected_artifact_ids],
        "selected_artifacts": selected_artifacts,
        "rationale": str(validation_item.get("rationale") or ""),
        "notes": str(validation_item.get("notes") or ""),
        "feedback_closure_state": closure_state,
        "feedback_closure_blocked": feedback_closure_blocked(template_item),
        "preview_only": True,
    }


def _selection_apply_validation_blockers(
    validation_report: dict[str, Any],
) -> list[dict[str, Any]]:
    validation_items = validation_report.get("selection_validation_items")
    if not isinstance(validation_items, list):
        return []
    blockers: list[dict[str, Any]] = []
    for item in validation_items:
        if not isinstance(item, dict) or item.get("state") == "valid":
            continue
        blockers.append(
            {
                "shortlist_id": str(item.get("shortlist_id") or ""),
                "state": str(item.get("state") or "unknown"),
                "selected_action": str(item.get("selected_action") or "undecided"),
                "issues": item.get("issues")
                if isinstance(item.get("issues"), list)
                else [],
                "selected_artifact_ids": item.get("selected_artifact_ids")
                if isinstance(item.get("selected_artifact_ids"), list)
                else [],
                "invalid_selected_artifact_ids": item.get(
                    "invalid_selected_artifact_ids"
                )
                if isinstance(item.get("invalid_selected_artifact_ids"), list)
                else [],
                "feedback_ids": item.get("feedback_ids")
                if isinstance(item.get("feedback_ids"), list)
                else [],
                "preview_only": True,
            }
        )
    return blockers


def build_ocr_retry_selection_apply_preview_report(
    *,
    db_path: Path,
    selection_path: Path | None = None,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    validation_report = build_ocr_retry_selection_validation_report(
        db_path=db_path,
        selection_path=selection_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    validation_counts = validation_report.get("counts")
    if not isinstance(validation_counts, dict):
        validation_counts = {}
    validation_filters = validation_report.get("filters")
    if not isinstance(validation_filters, dict):
        validation_filters = {}
    decision_source = validation_report.get("decision_source")
    if not isinstance(decision_source, dict):
        decision_source = {}

    validation_state = str(validation_report.get("state") or "unknown")
    blocked = validation_state != "ok"
    apply_actions = _empty_selection_apply_actions()
    apply_items: list[dict[str, Any]] = []
    blockers = (
        _selection_apply_validation_blockers(validation_report) if blocked else []
    )

    if not blocked:
        template_report = build_ocr_retry_selection_template_report(
            db_path=db_path,
            outcome=outcome,
            cohort=cohort,
            limit=limit,
            artifact_ids=artifact_ids,
        )
        template_items = selection_template_items_by_shortlist_id(template_report)
        validation_items = validation_report.get("selection_validation_items")
        if not isinstance(validation_items, list):
            validation_items = []
        for validation_item in validation_items:
            if not isinstance(validation_item, dict):
                continue
            shortlist_id = str(validation_item.get("shortlist_id") or "")
            template_item = template_items.get(shortlist_id)
            if not isinstance(template_item, dict):
                continue
            apply_item = _selection_apply_item(
                validation_item=validation_item,
                template_item=template_item,
            )
            selected_action = str(apply_item.get("selected_action") or "")
            if selected_action in apply_actions:
                apply_actions[selected_action].append(apply_item)
            apply_items.append(apply_item)

    selected_artifacts = sum(
        len(item.get("selected_artifacts", []))
        for item in apply_items
        if isinstance(item.get("selected_artifacts"), list)
    )
    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION,
        "selection_validation_schema_version": validation_report.get(
            "schema_version", ""
        ),
        "state": "blocked" if blocked else "ok",
        "validation_state": validation_state,
        "manual_evals_db": validation_report.get("manual_evals_db", {}),
        "decision_source": decision_source,
        "filters": {
            "status": validation_filters.get("status") or "open",
            "outcome": validation_filters.get("outcome") or "",
            "cohort": validation_filters.get("cohort") or "",
            "limit": _int_value(validation_filters.get("limit")),
            "packet_basis": "selection_validation_application_preview",
            "selection_mode": validation_filters.get("selection_mode") or "",
            "artifact_ids": validation_filters.get("artifact_ids")
            if isinstance(validation_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(
                validation_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                validation_counts.get("returned_feedback_rows")
            ),
            "shortlist_items": _int_value(validation_counts.get("shortlist_items")),
            "candidate_artifacts": _int_value(
                validation_counts.get("candidate_artifacts")
            ),
            "submitted_decisions": _int_value(
                validation_counts.get("submitted_decisions")
            ),
            "valid_decisions": _int_value(validation_counts.get("valid_decisions")),
            "pending_decisions": _int_value(validation_counts.get("pending_decisions")),
            "invalid_decisions": _int_value(validation_counts.get("invalid_decisions")),
            "missing_decisions": _int_value(validation_counts.get("missing_decisions")),
            "stale_decisions": _int_value(validation_counts.get("stale_decisions")),
            "duplicate_decisions": _int_value(
                validation_counts.get("duplicate_decisions")
            ),
            "blocked_by_validation": len(blockers),
            "preview_items": len(apply_items),
            "rerun_input_items": len(apply_actions["rerun_input"]),
            "curated_case_items": len(apply_actions["curated_case"]),
            "context_only_items": len(apply_actions["context_only"]),
            "selected_artifacts": selected_artifacts,
            "feedback_closure_blocked_items": _int_value(
                validation_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                validation_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                validation_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                validation_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": _int_value(
                validation_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                validation_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(validation_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": validation_report.get("unmatched_artifact_ids", []),
        "validation_blockers": blockers,
        "application_preview": {
            "mutation": "none",
            "execution": "none",
            "requires_validation_state": "ok",
            "actions": apply_actions,
            "items": apply_items,
        },
    }
    warnings = validation_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    if blocked:
        report.setdefault("warnings", []).append(
            "selection application preview is blocked until validation state is ok"
        )
    return report


def _format_apply_selected_artifact_line(item: dict[str, Any]) -> str:
    preview = _truncate_text(item.get("ocr_text_preview"), max_chars=80)
    command = item.get("command_preview")
    if not isinstance(command, dict):
        command = {}
    return (
        f"artifact={item.get('artifact_id') or 'none'} "
        f"ocr={item.get('ocr_run_id') or 'none'} "
        f"session={item.get('session_id') or 'none'} "
        f"source_session={item.get('source_session_id') or 'none'} "
        f"preview_only={'yes' if item.get('preview_only') else 'no'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
        f"source_path={_format_terminal_source_path(item.get('resolved_path'))} "
        f"command={command.get('mode') or 'payload_only'} "
        f"ocr_preview={preview or 'none'}"
    )


def format_ocr_retry_selection_apply_preview_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry selection apply preview: "
        f"state={report.get('state', 'unknown')} "
        f"validation={report.get('validation_state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('shortlist_items'))} "
        f"candidate_artifacts={_int_value(counts.get('candidate_artifacts'))} "
        f"submitted={_int_value(counts.get('submitted_decisions'))} "
        f"valid={_int_value(counts.get('valid_decisions'))} "
        f"pending={_int_value(counts.get('pending_decisions'))} "
        f"invalid={_int_value(counts.get('invalid_decisions'))} "
        f"missing={_int_value(counts.get('missing_decisions'))} "
        f"stale={_int_value(counts.get('stale_decisions'))} "
        f"duplicates={_int_value(counts.get('duplicate_decisions'))} "
        f"blocked={_int_value(counts.get('blocked_by_validation'))} "
        f"preview_items={_int_value(counts.get('preview_items'))} "
        f"rerun_input={_int_value(counts.get('rerun_input_items'))} "
        f"curated_case={_int_value(counts.get('curated_case_items'))} "
        f"context_only={_int_value(counts.get('context_only_items'))} "
        f"selected_artifacts={_int_value(counts.get('selected_artifacts'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
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

    blockers = report.get("validation_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("validation_blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"shortlist={blocker.get('shortlist_id') or 'none'} "
                f"state={blocker.get('state') or 'unknown'} "
                f"action={blocker.get('selected_action') or 'undecided'} "
                f"issues={format_validation_issues(blocker.get('issues'))} "
                f"feedback={_format_feedback_ids(blocker.get('feedback_ids'))} "
                "selected_artifacts="
                f"{format_validation_artifact_ids(blocker.get('selected_artifact_ids'))} "
                "invalid_artifacts="
                f"{format_validation_artifact_ids(blocker.get('invalid_selected_artifact_ids'))}"
            )
    preview = report.get("application_preview")
    if not isinstance(preview, dict):
        preview = {}
    items = preview.get("items")
    if not isinstance(items, list) or not items:
        lines.append("application_preview_items: none")
    else:
        for item in items:
            if not isinstance(item, dict):
                continue
            lines.append(
                "- "
                f"action={item.get('selected_action') or 'unknown'} "
                f"shortlist={item.get('shortlist_id') or 'none'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                "selected_artifacts="
                f"{format_validation_artifact_ids(item.get('selected_artifact_ids'))} "
                f"source_image={item.get('source_image_name') or 'none'} "
                f"source_path={_format_terminal_source_path(item.get('resolved_path'))} "
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
                            f"  - {_format_apply_selected_artifact_line(artifact)}"
                        )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)
