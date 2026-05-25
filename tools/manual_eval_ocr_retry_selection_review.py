from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_rerun_plan import (
    build_ocr_retry_rerun_plan_report,
    ocr_retry_plan_source_preview,
)


OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_review.v1"
)
OCR_RETRY_SELECTION_ALLOWED_ACTIONS = ("rerun_input", "curated_case", "context_only")


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


def _ocr_retry_selection_source_key(artifact: dict[str, Any]) -> str:
    for key in ("resolved_path", "source_image_name", "artifact_id"):
        value = str(artifact.get(key) or "").strip()
        if value:
            return value
    return "unknown-source-artifact"


def _ocr_retry_selection_shortlist_id(
    *,
    source_session_id: str,
    source_key: str,
    artifact: dict[str, Any],
) -> str:
    source_name = str(artifact.get("source_image_name") or "").strip()
    if not source_name:
        source_name = Path(source_key).name.strip()
    if not source_name:
        source_name = str(artifact.get("artifact_id") or "").strip()
    return (
        f"{source_session_id or 'unknown-session'}::{source_name or 'source-artifact'}"
    )


def _extend_unique_ints(target: list[int], values: object) -> None:
    if not isinstance(values, list):
        return
    seen = set(target)
    for value in values:
        item = _int_value(value)
        if item and item not in seen:
            seen.add(item)
            target.append(item)


def _append_unique_preview(
    target: list[dict[str, Any]],
    preview: dict[str, Any],
    seen: set[tuple[int, str, str]],
) -> None:
    key = (
        _int_value(preview.get("feedback_id")),
        str(preview.get("message_id") or ""),
        str(preview.get("source_preview") or ""),
    )
    if key in seen:
        return
    seen.add(key)
    target.append(preview)


def _ocr_retry_selection_decision(candidate_count: int) -> dict[str, Any]:
    reason_code = (
        "duplicate_source_artifacts_collapsed"
        if candidate_count > 1
        else "source_artifact_needs_review"
    )
    return {
        "state": "needs_human_selection",
        "allowed_actions": list(OCR_RETRY_SELECTION_ALLOWED_ACTIONS),
        "default_action": "undecided",
        "reason_code": reason_code,
        "next_action": "choose_source_artifact_disposition",
    }


def build_ocr_retry_selection_review_items(
    plan_items: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped_items: dict[tuple[str, str], dict[str, Any]] = {}
    order: list[tuple[str, str]] = []
    preview_seen: dict[tuple[str, str], set[tuple[int, str, str]]] = {}

    for plan_item in plan_items:
        plan_artifacts = plan_item.get("plan_artifacts")
        if not isinstance(plan_artifacts, list):
            continue
        feedback_previews = plan_item.get("feedback_source_previews")
        if not isinstance(feedback_previews, list):
            feedback_previews = []
        clean_feedback_previews = [
            preview for preview in feedback_previews if isinstance(preview, dict)
        ]
        for artifact in plan_artifacts:
            if not isinstance(artifact, dict):
                continue
            source_session_id = str(
                artifact.get("source_session_id")
                or plan_item.get("source_session_id")
                or ""
            )
            source_key = _ocr_retry_selection_source_key(artifact)
            group_key = (source_session_id, source_key)
            if group_key not in grouped_items:
                order.append(group_key)
                preview_seen[group_key] = set()
                thumbnail = artifact.get("thumbnail")
                if not isinstance(thumbnail, dict):
                    thumbnail = {}
                grouped_items[group_key] = {
                    "shortlist_id": _ocr_retry_selection_shortlist_id(
                        source_session_id=source_session_id,
                        source_key=source_key,
                        artifact=artifact,
                    ),
                    "source_key": source_key,
                    "session_id": str(
                        artifact.get("session_id") or plan_item.get("session_id") or ""
                    ),
                    "source_session_id": source_session_id,
                    "title": str(plan_item.get("title") or ""),
                    "source_label": str(plan_item.get("source_label") or ""),
                    "source_history": plan_item.get("source_history")
                    if isinstance(plan_item.get("source_history"), dict)
                    else {},
                    "feedback_ids": [],
                    "source_image_name": str(artifact.get("source_image_name") or ""),
                    "source_name": str(artifact.get("source_name") or ""),
                    "resolved_path": str(artifact.get("resolved_path") or ""),
                    "thumbnail": thumbnail,
                    "source_image": {
                        "source_image_name": str(
                            artifact.get("source_image_name") or ""
                        ),
                        "source_name": str(artifact.get("source_name") or ""),
                        "resolved_path": str(artifact.get("resolved_path") or ""),
                        "thumbnail": thumbnail,
                    },
                    "selection_gate": plan_item.get("selection_gate")
                    if isinstance(plan_item.get("selection_gate"), dict)
                    else {},
                    "feedback_closure_state": plan_item.get("feedback_closure_state")
                    if isinstance(plan_item.get("feedback_closure_state"), dict)
                    else {},
                    "readiness": plan_item.get("readiness")
                    if isinstance(plan_item.get("readiness"), dict)
                    else {},
                    "feedback_source_previews": [],
                    "source_preview": ocr_retry_plan_source_preview(
                        clean_feedback_previews
                    ),
                    "candidate_ocr_runs": [],
                }

            item = grouped_items[group_key]
            _extend_unique_ints(item["feedback_ids"], artifact.get("feedback_ids"))
            for preview in clean_feedback_previews:
                _append_unique_preview(
                    item["feedback_source_previews"],
                    preview,
                    preview_seen[group_key],
                )
            candidate: dict[str, Any] = {
                "artifact_id": str(artifact.get("artifact_id") or ""),
                "ocr_run_id": str(artifact.get("ocr_run_id") or ""),
                "action": str(artifact.get("action") or ""),
                "preview_only": bool(artifact.get("preview_only")),
                "feedback_ids": artifact.get("feedback_ids")
                if isinstance(artifact.get("feedback_ids"), list)
                else [],
                "source_session_id": str(artifact.get("source_session_id") or ""),
                "session_id": str(artifact.get("session_id") or ""),
                "source_image_name": str(artifact.get("source_image_name") or ""),
                "source_name": str(artifact.get("source_name") or ""),
                "resolved_path": str(artifact.get("resolved_path") or ""),
                "thumbnail": artifact.get("thumbnail")
                if isinstance(artifact.get("thumbnail"), dict)
                else {},
                "ocr_text_preview": str(artifact.get("ocr_text_preview") or ""),
                "feedback_source_preview": artifact.get("feedback_source_preview")
                if isinstance(artifact.get("feedback_source_preview"), dict)
                else {},
                "payload_inputs": artifact.get("payload_inputs")
                if isinstance(artifact.get("payload_inputs"), dict)
                else {},
                "command_preview": artifact.get("command_preview")
                if isinstance(artifact.get("command_preview"), dict)
                else {},
            }
            item["candidate_ocr_runs"].append(candidate)

    shortlist_items: list[dict[str, Any]] = []
    for group_key in order:
        item = grouped_items[group_key]
        candidate_count = len(item["candidate_ocr_runs"])
        item["selection_decision"] = _ocr_retry_selection_decision(candidate_count)
        item["counts"] = {
            "candidate_ocr_runs": candidate_count,
            "duplicate_source_artifacts": max(0, candidate_count - 1),
            "feedback_inputs": len(item["feedback_source_previews"]),
        }
        shortlist_items.append(item)
    return shortlist_items


def build_ocr_retry_selection_review_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    plan_report = build_ocr_retry_rerun_plan_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    plan_items = plan_report.get("plan_items")
    if not isinstance(plan_items, list):
        plan_items = []
    plan_items = [item for item in plan_items if isinstance(item, dict)]
    selection_review_items = build_ocr_retry_selection_review_items(plan_items)

    plan_counts = plan_report.get("counts")
    if not isinstance(plan_counts, dict):
        plan_counts = {}
    plan_filters = plan_report.get("filters")
    if not isinstance(plan_filters, dict):
        plan_filters = {}
    planned_source_artifacts = _int_value(plan_counts.get("planned_source_artifacts"))
    duplicate_count = sum(
        _int_value(item.get("counts", {}).get("duplicate_source_artifacts"))
        for item in selection_review_items
        if isinstance(item.get("counts"), dict)
    )

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_REVIEW_SCHEMA_VERSION,
        "rerun_plan_schema_version": plan_report.get("schema_version", ""),
        "state": plan_report.get("state", "unknown"),
        "manual_evals_db": plan_report.get("manual_evals_db", {}),
        "filters": {
            "status": plan_filters.get("status") or "open",
            "outcome": plan_filters.get("outcome") or "",
            "cohort": plan_filters.get("cohort") or "",
            "limit": _int_value(plan_filters.get("limit")),
            "packet_basis": "rerun_plan_source_artifact_selection_review",
            "selection_mode": plan_filters.get("selection_mode") or "",
            "artifact_ids": plan_filters.get("artifact_ids")
            if isinstance(plan_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(plan_counts.get("total_feedback_rows")),
            "returned_feedback_rows": _int_value(
                plan_counts.get("returned_feedback_rows")
            ),
            "plan_items": _int_value(plan_counts.get("plan_items")),
            "planned_source_artifacts": planned_source_artifacts,
            "shortlist_items": len(selection_review_items),
            "collapsed_duplicate_source_artifacts": duplicate_count,
            "candidate_ocr_runs": sum(
                _int_value(item.get("counts", {}).get("candidate_ocr_runs"))
                for item in selection_review_items
                if isinstance(item.get("counts"), dict)
            ),
            "decision_pending_items": len(selection_review_items),
            "feedback_closure_blocked_items": _int_value(
                plan_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                plan_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                plan_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                plan_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": _int_value(
                plan_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                plan_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(plan_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": plan_report.get("unmatched_artifact_ids", []),
        "selection_review_items": selection_review_items,
    }
    warnings = plan_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _format_selection_decision(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    allowed_actions = value.get("allowed_actions")
    if isinstance(allowed_actions, list):
        actions_text = ",".join(str(item) for item in allowed_actions)
    else:
        actions_text = "none"
    parts = [str(value.get("state") or "unknown")]
    if actions_text:
        parts.append(f"actions={actions_text}")
    reason_code = str(value.get("reason_code") or "")
    next_action = str(value.get("next_action") or "")
    if reason_code:
        parts.append(f"reason={reason_code}")
    if next_action:
        parts.append(f"next={next_action}")
    return " ".join(parts)


def _format_selection_candidate_line(item: dict[str, Any]) -> str:
    preview = _truncate_text(item.get("ocr_text_preview"), max_chars=80)
    return (
        f"artifact={item.get('artifact_id') or 'none'} "
        f"action={item.get('action') or 'unknown'} "
        f"preview_only={'yes' if item.get('preview_only') else 'no'} "
        f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
        f"ocr={item.get('ocr_run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
        f"source_path={_format_terminal_source_path(item.get('resolved_path'))} "
        f"ocr_preview={preview or 'none'}"
    )


def format_ocr_retry_selection_review_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry selection review: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('shortlist_items'))} "
        f"planned_artifacts={_int_value(counts.get('planned_source_artifacts'))} "
        "collapsed_duplicates="
        f"{_int_value(counts.get('collapsed_duplicate_source_artifacts'))} "
        f"candidate_runs={_int_value(counts.get('candidate_ocr_runs'))} "
        f"decision_pending={_int_value(counts.get('decision_pending_items'))} "
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

    selection_items = report.get("selection_review_items")
    if not isinstance(selection_items, list) or not selection_items:
        lines.append("selection_review_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in selection_items:
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
                "decision="
                f"{_format_selection_decision(item.get('selection_decision'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                f"source_image={item.get('source_image_name') or 'none'} "
                f"thumbnail={_format_plan_thumbnail(item.get('thumbnail'))} "
                "candidate_runs="
                f"{_int_value(item_counts.get('candidate_ocr_runs'))} "
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
            ]
        )
        candidate_rows = item.get("candidate_ocr_runs")
        if not isinstance(candidate_rows, list):
            candidate_rows = []
        if candidate_rows:
            lines.append("  candidate_ocr_runs:")
            for candidate in candidate_rows:
                if isinstance(candidate, dict):
                    lines.append(f"  - {_format_selection_candidate_line(candidate)}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)
