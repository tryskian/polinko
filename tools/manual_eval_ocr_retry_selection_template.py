from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_selection_review import (
    OCR_RETRY_SELECTION_ALLOWED_ACTIONS,
    build_ocr_retry_selection_review_report,
)


OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_template.v1"
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


def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def _display_text(value: object) -> str:
    text = _normalize_text(value)
    return text if text else "none"


def _truncate_text(value: object, *, max_chars: int = 180) -> str:
    text = _normalize_text(value)
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "..."


def _format_feedback_ids(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    return ",".join(str(_int_value(item)) for item in value)


def _format_readiness_flags(readiness: dict[str, Any]) -> str:
    flags = readiness.get("flags")
    if not isinstance(flags, list) or not flags:
        return "none"
    return ",".join(str(item) for item in flags)


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


def _format_plan_thumbnail(value: object) -> str:
    if not isinstance(value, dict) or not value.get("available"):
        return "none"
    return f"{_int_value(value.get('width'))}x{_int_value(value.get('height'))}"


def _format_terminal_source_path(value: object) -> str:
    raw_path = str(value or "").strip()
    if not raw_path:
        return "none"
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path.name or "none"
    return raw_path


def _format_plan_source_preview(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    preview = _truncate_text(value.get("source_preview"), max_chars=100)
    return (
        f"feedback={_int_value(value.get('feedback_id'))} "
        f"message={value.get('message_id') or 'unknown'} "
        f"source_state={value.get('source_state') or 'unknown'} "
        f"role={value.get('source_role') or 'unknown'} "
        f"preview={preview or 'none'}"
    )


def _ocr_retry_selection_template_item(
    item: dict[str, Any],
) -> dict[str, Any]:
    decision = item.get("selection_decision")
    if not isinstance(decision, dict):
        decision = {}
    allowed_actions = decision.get("allowed_actions")
    if not isinstance(allowed_actions, list):
        allowed_actions = list(OCR_RETRY_SELECTION_ALLOWED_ACTIONS)
    candidate_rows = item.get("candidate_ocr_runs")
    if not isinstance(candidate_rows, list):
        candidate_rows = []
    candidate_artifacts: list[dict[str, Any]] = []
    for candidate in candidate_rows:
        if not isinstance(candidate, dict):
            continue
        candidate_artifacts.append(
            {
                "artifact_id": str(candidate.get("artifact_id") or ""),
                "ocr_run_id": str(candidate.get("ocr_run_id") or ""),
                "action": str(candidate.get("action") or ""),
                "preview_only": bool(candidate.get("preview_only")),
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
                "payload_inputs": candidate.get("payload_inputs")
                if isinstance(candidate.get("payload_inputs"), dict)
                else {},
                "command_preview": candidate.get("command_preview")
                if isinstance(candidate.get("command_preview"), dict)
                else {},
            }
        )
    item_counts = item.get("counts")
    if not isinstance(item_counts, dict):
        item_counts = {}
    return {
        "shortlist_id": str(item.get("shortlist_id") or ""),
        "source_key": str(item.get("source_key") or ""),
        "session_id": str(item.get("session_id") or ""),
        "source_session_id": str(item.get("source_session_id") or ""),
        "title": str(item.get("title") or ""),
        "feedback_ids": item.get("feedback_ids")
        if isinstance(item.get("feedback_ids"), list)
        else [],
        "source_image_name": str(item.get("source_image_name") or ""),
        "source_name": str(item.get("source_name") or ""),
        "resolved_path": str(item.get("resolved_path") or ""),
        "thumbnail": item.get("thumbnail")
        if isinstance(item.get("thumbnail"), dict)
        else {},
        "source_preview": item.get("source_preview")
        if isinstance(item.get("source_preview"), dict)
        else {},
        "readiness": item.get("readiness")
        if isinstance(item.get("readiness"), dict)
        else {},
        "feedback_closure_state": item.get("feedback_closure_state")
        if isinstance(item.get("feedback_closure_state"), dict)
        else {},
        "decision_input": {
            "selected_action": "undecided",
            "allowed_actions": [str(action) for action in allowed_actions],
            "selected_artifact_ids": [],
            "rationale": "",
            "notes": "",
            "requires_human_selection": True,
        },
        "candidate_artifacts": candidate_artifacts,
        "counts": {
            "candidate_artifacts": len(candidate_artifacts),
            "duplicate_source_artifacts": _int_value(
                item_counts.get("duplicate_source_artifacts")
            ),
            "feedback_inputs": _int_value(item_counts.get("feedback_inputs")),
        },
    }


def build_ocr_retry_selection_template_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    selection_review = build_ocr_retry_selection_review_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    selection_items = selection_review.get("selection_review_items")
    if not isinstance(selection_items, list):
        selection_items = []
    template_items = [
        _ocr_retry_selection_template_item(item)
        for item in selection_items
        if isinstance(item, dict)
    ]
    review_counts = selection_review.get("counts")
    if not isinstance(review_counts, dict):
        review_counts = {}
    review_filters = selection_review.get("filters")
    if not isinstance(review_filters, dict):
        review_filters = {}
    duplicate_count = sum(
        _int_value(item.get("counts", {}).get("duplicate_source_artifacts"))
        for item in template_items
        if isinstance(item.get("counts"), dict)
    )

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_TEMPLATE_SCHEMA_VERSION,
        "selection_review_schema_version": selection_review.get("schema_version", ""),
        "state": selection_review.get("state", "unknown"),
        "manual_evals_db": selection_review.get("manual_evals_db", {}),
        "filters": {
            "status": review_filters.get("status") or "open",
            "outcome": review_filters.get("outcome") or "",
            "cohort": review_filters.get("cohort") or "",
            "limit": _int_value(review_filters.get("limit")),
            "packet_basis": "selection_review_human_decision_template",
            "selection_mode": review_filters.get("selection_mode") or "",
            "artifact_ids": review_filters.get("artifact_ids")
            if isinstance(review_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(review_counts.get("total_feedback_rows")),
            "returned_feedback_rows": _int_value(
                review_counts.get("returned_feedback_rows")
            ),
            "shortlist_items": _int_value(review_counts.get("shortlist_items")),
            "template_items": len(template_items),
            "candidate_artifacts": sum(
                _int_value(item.get("counts", {}).get("candidate_artifacts"))
                for item in template_items
                if isinstance(item.get("counts"), dict)
            ),
            "collapsed_duplicate_source_artifacts": duplicate_count,
            "default_undecided_items": len(template_items),
            "feedback_closure_blocked_items": _int_value(
                review_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                review_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                review_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                review_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": _int_value(
                review_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                review_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(review_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": selection_review.get("unmatched_artifact_ids", []),
        "selection_template": {
            "template_version": "manual_ocr_retry_selection.v1",
            "default_action": "undecided",
            "allowed_actions": list(OCR_RETRY_SELECTION_ALLOWED_ACTIONS),
            "mutation": "none",
            "items": template_items,
        },
    }
    warnings = selection_review.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _format_template_decision_input(value: object) -> str:
    if not isinstance(value, dict):
        return "selected_action=unknown allowed=none"
    allowed_actions = value.get("allowed_actions")
    if isinstance(allowed_actions, list):
        allowed_text = ",".join(str(item) for item in allowed_actions)
    else:
        allowed_text = "none"
    selected_ids = value.get("selected_artifact_ids")
    if isinstance(selected_ids, list) and selected_ids:
        selected_text = ",".join(str(item) for item in selected_ids)
    else:
        selected_text = "none"
    return (
        f"selected_action={value.get('selected_action') or 'unknown'} "
        f"allowed={allowed_text or 'none'} "
        f"selected_artifacts={selected_text}"
    )


def _format_template_candidate_line(item: dict[str, Any]) -> str:
    preview = _truncate_text(item.get("ocr_text_preview"), max_chars=80)
    return (
        f"artifact={item.get('artifact_id') or 'none'} "
        f"ocr={item.get('ocr_run_id') or 'none'} "
        f"action={item.get('action') or 'unknown'} "
        f"preview_only={'yes' if item.get('preview_only') else 'no'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
        f"source_path={_format_terminal_source_path(item.get('resolved_path'))} "
        f"ocr_preview={preview or 'none'}"
    )


def format_ocr_retry_selection_template_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    lines = [
        "manual eval OCR retry selection template: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('template_items'))} "
        f"shortlist={_int_value(counts.get('shortlist_items'))} "
        f"candidate_artifacts={_int_value(counts.get('candidate_artifacts'))} "
        "collapsed_duplicates="
        f"{_int_value(counts.get('collapsed_duplicate_source_artifacts'))} "
        f"undecided={_int_value(counts.get('default_undecided_items'))} "
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
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    unmatched_artifact_ids = report.get("unmatched_artifact_ids")
    if isinstance(unmatched_artifact_ids, list) and unmatched_artifact_ids:
        lines.append(
            "unmatched_artifact_ids: "
            + ",".join(str(item) for item in unmatched_artifact_ids)
        )

    template = report.get("selection_template")
    if not isinstance(template, dict):
        template = {}
    template_items = template.get("items")
    if not isinstance(template_items, list) or not template_items:
        lines.append("selection_template_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in template_items:
        if not isinstance(item, dict):
            continue
        item_counts = item.get("counts")
        if not isinstance(item_counts, dict):
            item_counts = {}
        readiness = item.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        lines.extend(
            [
                "- "
                f"shortlist={item.get('shortlist_id') or 'unknown'} "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                f"{_format_template_decision_input(item.get('decision_input'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                f"source_image={item.get('source_image_name') or 'none'} "
                f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
                "candidate_artifacts="
                f"{_int_value(item_counts.get('candidate_artifacts'))} "
                "duplicate_artifacts="
                f"{_int_value(item_counts.get('duplicate_source_artifacts'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)}",
                "  source_path="
                f"{_format_terminal_source_path(item.get('resolved_path'))}",
                "  source_preview="
                f"{_format_plan_source_preview(item.get('source_preview'))}",
                "  fill_template="
                "selected_action=<rerun_input|curated_case|context_only> "
                "selected_artifact_ids=<artifact_id,...> rationale=<text>",
            ]
        )
        candidate_rows = item.get("candidate_artifacts")
        if not isinstance(candidate_rows, list):
            candidate_rows = []
        if candidate_rows:
            lines.append("  candidate_artifacts:")
            for candidate in candidate_rows:
                if isinstance(candidate, dict):
                    lines.append(f"  - {_format_template_candidate_line(candidate)}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)
