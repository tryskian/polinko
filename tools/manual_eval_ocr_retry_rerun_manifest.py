from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_candidates import OCR_RETRY_TERMINAL_CONTEXT_LIMIT
from tools.manual_eval_ocr_retry_input_packet import build_ocr_retry_input_packet_report


OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_rerun_manifest.v1"
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


def _ocr_retry_manifest_selection_gate(
    *,
    resolved_source_artifacts: int,
    closure_state: dict[str, Any],
) -> dict[str, Any]:
    if resolved_source_artifacts <= 0:
        return {
            "state": "blocked",
            "reason_code": "no_resolved_source_artifacts",
            "reason": "no resolved source artifact is available for rerun selection",
            "next_action": "resolve_or_curate_source_artifact",
        }
    if closure_state.get("state") == "ready":
        return {
            "state": "ready_for_review",
            "reason_code": "exact_feedback_result_link_available",
            "reason": (
                "source artifact is available, but an exact feedback-result "
                "link already exists"
            ),
            "next_action": "review_exact_link_before_feedback_closure",
        }
    return {
        "state": "ready_for_selection",
        "reason_code": str(closure_state.get("reason_code") or ""),
        "reason": str(closure_state.get("reason") or ""),
        "next_action": "select_source_artifacts_for_rerun_or_case_curation",
    }


def _ocr_retry_manifest_source_artifact(
    *,
    source_item: dict[str, Any],
) -> dict[str, Any]:
    image_asset = source_item.get("image_asset")
    if not isinstance(image_asset, dict):
        image_asset = {}
    thumbnail = image_asset.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    return {
        "run_id": str(source_item.get("run_id") or ""),
        "source_image_name": str(source_item.get("source_image_name") or ""),
        "source_name": str(source_item.get("source_name") or ""),
        "status": str(source_item.get("status") or ""),
        "created_at": _int_value(source_item.get("created_at")),
        "ocr_text_chars": _int_value(source_item.get("extracted_text_chars")),
        "ocr_text_preview": str(source_item.get("extracted_text_preview") or ""),
        "source_message_id": str(source_item.get("source_message_id") or ""),
        "result_message_id": str(source_item.get("result_message_id") or ""),
        "exact_feedback_result_link": bool(
            source_item.get("exact_feedback_result_link")
        ),
        "image": {
            "resolved": bool(image_asset.get("resolved")),
            "status": str(image_asset.get("status") or "unknown"),
            "source_filename": str(image_asset.get("source_filename") or ""),
            "resolved_path": str(image_asset.get("resolved_path") or ""),
            "mime_type": str(image_asset.get("mime_type") or ""),
            "source_size_bytes": _int_value(image_asset.get("source_size_bytes")),
            "thumbnail": {
                "available": bool(thumbnail.get("available")),
                "width": _int_value(thumbnail.get("width")),
                "height": _int_value(thumbnail.get("height")),
            },
        },
    }


def build_ocr_retry_rerun_manifest_items(
    input_items: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    manifest_items: list[dict[str, Any]] = []
    for input_item in input_items:
        feedback_inputs = input_item.get("feedback_inputs")
        if not isinstance(feedback_inputs, list):
            feedback_inputs = []
        rerun_inputs = input_item.get("rerun_inputs")
        if not isinstance(rerun_inputs, list):
            rerun_inputs = []
        clean_feedback_inputs = [
            feedback_input
            for feedback_input in feedback_inputs
            if isinstance(feedback_input, dict)
        ]
        feedback_source_previews: list[dict[str, Any]] = []
        for feedback_input in clean_feedback_inputs:
            source_message = feedback_input.get("source_message")
            if not isinstance(source_message, dict):
                source_message = {}
            feedback_source_previews.append(
                {
                    "feedback_id": _int_value(feedback_input.get("feedback_id")),
                    "message_id": str(feedback_input.get("message_id") or ""),
                    "source_state": str(source_message.get("state") or "unknown"),
                    "source_role": str(source_message.get("role") or ""),
                    "source_preview": str(source_message.get("content_preview") or ""),
                }
            )
        source_artifacts = [
            _ocr_retry_manifest_source_artifact(
                source_item=row,
            )
            for row in rerun_inputs
            if isinstance(row, dict)
        ]
        resolved_source_artifacts = sum(
            1
            for artifact in source_artifacts
            if isinstance(artifact.get("image"), dict)
            and artifact["image"].get("resolved")
        )
        artifacts_with_thumbnail = sum(
            1
            for artifact in source_artifacts
            if isinstance(artifact.get("image"), dict)
            and isinstance(artifact["image"].get("thumbnail"), dict)
            and artifact["image"]["thumbnail"].get("available")
        )
        closure_state = input_item.get("blocker_state")
        if not isinstance(closure_state, dict):
            closure_state = {}
        selection_gate = _ocr_retry_manifest_selection_gate(
            resolved_source_artifacts=resolved_source_artifacts,
            closure_state=closure_state,
        )
        manifest_items.append(
            {
                "group_id": str(input_item.get("group_id") or ""),
                "source_label": str(input_item.get("source_label") or ""),
                "source_history": input_item.get("source_history")
                if isinstance(input_item.get("source_history"), dict)
                else {},
                "source_session_id": str(input_item.get("source_session_id") or ""),
                "session_id": str(input_item.get("session_id") or ""),
                "title": str(input_item.get("title") or ""),
                "feedback_ids": input_item.get("feedback_ids")
                if isinstance(input_item.get("feedback_ids"), list)
                else [],
                "readiness": input_item.get("readiness")
                if isinstance(input_item.get("readiness"), dict)
                else {},
                "feedback_closure_state": closure_state,
                "selection_gate": selection_gate,
                "feedback_source_previews": feedback_source_previews,
                "source_artifacts": source_artifacts,
                "counts": {
                    "feedback_inputs": len(clean_feedback_inputs),
                    "source_artifacts": len(source_artifacts),
                    "resolved_source_artifacts": resolved_source_artifacts,
                    "unresolved_source_artifacts": (
                        len(source_artifacts) - resolved_source_artifacts
                    ),
                    "artifacts_with_thumbnail": artifacts_with_thumbnail,
                },
            }
        )
    return manifest_items


def build_ocr_retry_rerun_manifest_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    input_report = build_ocr_retry_input_packet_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    input_items = input_report.get("input_items")
    if not isinstance(input_items, list):
        input_items = []
    input_items = [item for item in input_items if isinstance(item, dict)]
    manifest_items = build_ocr_retry_rerun_manifest_items(input_items)
    input_counts = input_report.get("counts")
    if not isinstance(input_counts, dict):
        input_counts = {}
    input_filters = input_report.get("filters")
    if not isinstance(input_filters, dict):
        input_filters = {}
    item_counts = [item.get("counts") for item in manifest_items]

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_RERUN_MANIFEST_SCHEMA_VERSION,
        "input_packet_schema_version": input_report.get("schema_version", ""),
        "state": input_report.get("state", "unknown"),
        "manual_evals_db": input_report.get("manual_evals_db", {}),
        "filters": {
            "status": input_filters.get("status") or "open",
            "outcome": input_filters.get("outcome") or "",
            "cohort": input_filters.get("cohort") or "",
            "limit": _int_value(input_filters.get("limit")),
            "packet_basis": "resolved_source_artifact_selection_gate",
        },
        "counts": {
            "total_feedback_rows": _int_value(input_counts.get("total_feedback_rows")),
            "returned_feedback_rows": _int_value(
                input_counts.get("returned_feedback_rows")
            ),
            "manifest_items": len(manifest_items),
            "selection_ready_items": sum(
                1
                for item in manifest_items
                if isinstance(item.get("selection_gate"), dict)
                and item["selection_gate"].get("state")
                in {"ready_for_selection", "ready_for_review"}
            ),
            "feedback_closure_blocked_items": sum(
                1
                for item in manifest_items
                if isinstance(item.get("feedback_closure_state"), dict)
                and item["feedback_closure_state"].get("state") == "blocked"
            ),
            "feedback_inputs": _int_value(input_counts.get("feedback_inputs")),
            "source_artifacts": sum(
                _int_value(counts.get("source_artifacts"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "resolved_source_artifacts": sum(
                _int_value(counts.get("resolved_source_artifacts"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "unresolved_source_artifacts": sum(
                _int_value(counts.get("unresolved_source_artifacts"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "artifacts_with_thumbnail": sum(
                _int_value(counts.get("artifacts_with_thumbnail"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_source_message_ids_present": _int_value(
                input_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                input_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                input_counts.get("exact_feedback_result_links")
            ),
            "limit_applied": bool(input_counts.get("limit_applied")),
        },
        "manifest_items": manifest_items,
    }
    warnings = input_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def format_manifest_selection_gate(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    state = str(value.get("state") or "unknown")
    reason_code = str(value.get("reason_code") or "")
    next_action = str(value.get("next_action") or "")
    parts = [state]
    if reason_code:
        parts.append(f"reason={reason_code}")
    if next_action:
        parts.append(f"next={next_action}")
    return " ".join(parts)


def _format_manifest_feedback_preview(item: dict[str, Any]) -> str:
    return (
        f"feedback={_int_value(item.get('feedback_id'))} "
        f"message={item.get('message_id') or 'unknown'} "
        f"source_state={item.get('source_state') or 'unknown'} "
        f"role={item.get('source_role') or 'unknown'} "
        "preview="
        f"{_truncate_text(item.get('source_preview'), max_chars=100) or 'none'}"
    )


def _format_manifest_source_artifact_line(item: dict[str, Any]) -> str:
    image = item.get("image")
    if not isinstance(image, dict):
        image = {}
    thumbnail = image.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    thumbnail_text = "none"
    if thumbnail.get("available"):
        thumbnail_text = (
            f"{_int_value(thumbnail.get('width'))}x"
            f"{_int_value(thumbnail.get('height'))}"
        )
    preview = _truncate_text(item.get("ocr_text_preview"), max_chars=80)
    return (
        f"ocr={item.get('run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"image_status={image.get('status') or 'unknown'} "
        f"resolved={'yes' if image.get('resolved') else 'no'} "
        f"thumbnail={thumbnail_text} "
        f"source_message={item.get('source_message_id') or 'none'} "
        f"result_message={item.get('result_message_id') or 'none'} "
        "exact_feedback_link="
        f"{'yes' if item.get('exact_feedback_result_link') else 'no'} "
        f"preview={preview or 'none'}"
    )


def format_ocr_retry_rerun_manifest_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}

    source_artifacts = _int_value(counts.get("source_artifacts"))
    resolved_source_artifacts = _int_value(counts.get("resolved_source_artifacts"))
    lines = [
        "manual eval OCR retry rerun manifest: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('manifest_items'))} "
        f"selection_ready={_int_value(counts.get('selection_ready_items'))} "
        "closure_blocked="
        f"{_int_value(counts.get('feedback_closure_blocked_items'))} "
        f"feedback_inputs={_int_value(counts.get('feedback_inputs'))} "
        f"source_artifacts={source_artifacts} "
        f"resolved={resolved_source_artifacts}/{source_artifacts} "
        f"thumbnails={_int_value(counts.get('artifacts_with_thumbnail'))} "
        "source_message_ids="
        f"{_int_value(counts.get('ocr_source_message_ids_present'))} "
        "result_message_ids="
        f"{_int_value(counts.get('ocr_result_message_ids_present'))} "
        "exact_links="
        f"{_int_value(counts.get('exact_feedback_result_links'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    manifest_items = report.get("manifest_items")
    if not isinstance(manifest_items, list) or not manifest_items:
        lines.append("manifest_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in manifest_items:
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
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                "selection="
                f"{format_manifest_selection_gate(item.get('selection_gate'))} "
                "closure="
                f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
                "source_artifacts="
                f"{_int_value(item_counts.get('source_artifacts'))} "
                "resolved="
                f"{_int_value(item_counts.get('resolved_source_artifacts'))}/"
                f"{_int_value(item_counts.get('source_artifacts'))} "
                "thumbnails="
                f"{_int_value(item_counts.get('artifacts_with_thumbnail'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)}",
            ]
        )

        feedback_previews = item.get("feedback_source_previews")
        if not isinstance(feedback_previews, list):
            feedback_previews = []
        artifacts = item.get("source_artifacts")
        if not isinstance(artifacts, list):
            artifacts = []
        preview_by_feedback = {
            _int_value(preview.get("feedback_id")): preview
            for preview in feedback_previews
            if isinstance(preview, dict)
        }
        if preview_by_feedback:
            lines.append("  source_previews:")
            for preview in preview_by_feedback.values():
                lines.append(f"  - {_format_manifest_feedback_preview(preview)}")

        context_rows = [row for row in artifacts[:OCR_RETRY_TERMINAL_CONTEXT_LIMIT]]
        if context_rows:
            lines.append("  source_artifacts:")
            for row in context_rows:
                if isinstance(row, dict):
                    lines.append(f"  - {_format_manifest_source_artifact_line(row)}")
            hidden_rows = len(artifacts) - len(context_rows)
            if hidden_rows > 0:
                lines.append(f"  source_artifacts_more={hidden_rows}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)
