from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_rerun_manifest import (
    build_ocr_retry_rerun_manifest_report,
    format_manifest_selection_gate,
)
from tools.manual_eval_ocr_retry_selection_formatters import (
    display_text as _display_text,
    format_feedback_ids as _format_feedback_ids,
    format_input_blocker_state as _format_input_blocker_state,
    format_plan_source_preview as _format_plan_source_preview,
    format_plan_thumbnail as _format_plan_thumbnail,
    format_readiness_flags as _format_readiness_flags,
    format_terminal_source_path as _format_terminal_source_path,
    int_value as _int_value,
    truncate_text as _truncate_text,
)


OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION = "polinko.manual_eval_ocr_retry_rerun_plan.v1"


def _split_artifact_ids(artifact_ids: Sequence[str] | None) -> list[str]:
    if not artifact_ids:
        return []
    clean_ids: list[str] = []
    seen: set[str] = set()
    for value in artifact_ids:
        for item in str(value).split(","):
            artifact_id = item.strip()
            if artifact_id and artifact_id not in seen:
                seen.add(artifact_id)
                clean_ids.append(artifact_id)
    return clean_ids


def _ocr_retry_plan_artifact_id(
    *,
    manifest_item: dict[str, Any],
    artifact: dict[str, Any],
) -> str:
    group_id = str(manifest_item.get("group_id") or "")
    run_id = str(artifact.get("run_id") or "")
    source_image_name = str(artifact.get("source_image_name") or "")
    artifact_key = run_id or source_image_name or "unknown-source-artifact"
    return f"{group_id}::{artifact_key}"


def _ocr_retry_plan_artifact_action(selection_gate: dict[str, Any]) -> str:
    if selection_gate.get("state") == "ready_for_review":
        return "review_exact_link_before_rerun"
    return "rerun_or_curate_source_artifact"


def _ocr_retry_plan_payload_inputs(
    *,
    artifact_id: str,
    manifest_item: dict[str, Any],
    artifact: dict[str, Any],
) -> dict[str, Any]:
    image = artifact.get("image")
    if not isinstance(image, dict):
        image = {}
    thumbnail = image.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    return {
        "artifact_id": artifact_id,
        "operation": "ocr_retry_rerun_or_case_curation",
        "preview_only": True,
        "feedback_ids": manifest_item.get("feedback_ids")
        if isinstance(manifest_item.get("feedback_ids"), list)
        else [],
        "source_session_id": str(manifest_item.get("source_session_id") or ""),
        "session_id": str(manifest_item.get("session_id") or ""),
        "ocr_run_id": str(artifact.get("run_id") or ""),
        "source_image_name": str(artifact.get("source_image_name") or ""),
        "resolved_path": str(image.get("resolved_path") or ""),
        "mime_type": str(image.get("mime_type") or ""),
        "source_size_bytes": _int_value(image.get("source_size_bytes")),
        "thumbnail": {
            "available": bool(thumbnail.get("available")),
            "width": _int_value(thumbnail.get("width")),
            "height": _int_value(thumbnail.get("height")),
        },
    }


def ocr_retry_plan_source_preview(
    feedback_source_previews: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    for preview in feedback_source_previews:
        if not isinstance(preview, dict):
            continue
        if str(preview.get("source_preview") or ""):
            return {
                "feedback_id": _int_value(preview.get("feedback_id")),
                "message_id": str(preview.get("message_id") or ""),
                "source_state": str(preview.get("source_state") or "unknown"),
                "source_role": str(preview.get("source_role") or ""),
                "source_preview": str(preview.get("source_preview") or ""),
            }
    return {
        "feedback_id": 0,
        "message_id": "",
        "source_state": "unknown",
        "source_role": "",
        "source_preview": "",
    }


def build_ocr_retry_rerun_plan_items(
    *,
    manifest_items: Sequence[dict[str, Any]],
    selected_artifact_ids: Sequence[str],
) -> tuple[list[dict[str, Any]], set[str]]:
    requested_artifact_ids = set(selected_artifact_ids)
    found_artifact_ids: set[str] = set()
    plan_items: list[dict[str, Any]] = []
    for manifest_item in manifest_items:
        selection_gate = manifest_item.get("selection_gate")
        if not isinstance(selection_gate, dict):
            selection_gate = {}
        if selection_gate.get("state") not in {
            "ready_for_selection",
            "ready_for_review",
        }:
            continue

        feedback_source_previews = manifest_item.get("feedback_source_previews")
        if not isinstance(feedback_source_previews, list):
            feedback_source_previews = []
        clean_feedback_previews = [
            preview for preview in feedback_source_previews if isinstance(preview, dict)
        ]
        source_preview = ocr_retry_plan_source_preview(clean_feedback_previews)
        closure_state = manifest_item.get("feedback_closure_state")
        if not isinstance(closure_state, dict):
            closure_state = {}
        artifacts = manifest_item.get("source_artifacts")
        if not isinstance(artifacts, list):
            artifacts = []

        plan_artifacts: list[dict[str, Any]] = []
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            image = artifact.get("image")
            if not isinstance(image, dict) or not image.get("resolved"):
                continue
            artifact_id = _ocr_retry_plan_artifact_id(
                manifest_item=manifest_item,
                artifact=artifact,
            )
            found_artifact_ids.add(artifact_id)
            if requested_artifact_ids and artifact_id not in requested_artifact_ids:
                continue
            payload_inputs = _ocr_retry_plan_payload_inputs(
                artifact_id=artifact_id,
                manifest_item=manifest_item,
                artifact=artifact,
            )
            plan_artifacts.append(
                {
                    "artifact_id": artifact_id,
                    "action": _ocr_retry_plan_artifact_action(selection_gate),
                    "preview_only": True,
                    "selection_gate": selection_gate,
                    "feedback_closure_state": closure_state,
                    "feedback_ids": payload_inputs["feedback_ids"],
                    "source_session_id": payload_inputs["source_session_id"],
                    "session_id": payload_inputs["session_id"],
                    "ocr_run_id": payload_inputs["ocr_run_id"],
                    "source_image_name": payload_inputs["source_image_name"],
                    "source_name": str(artifact.get("source_name") or ""),
                    "resolved_path": payload_inputs["resolved_path"],
                    "thumbnail": payload_inputs["thumbnail"],
                    "ocr_text_preview": str(artifact.get("ocr_text_preview") or ""),
                    "feedback_source_preview": source_preview,
                    "payload_inputs": payload_inputs,
                    "command_preview": {
                        "mode": "payload_only",
                        "label": "manual_eval_ocr_retry_rerun_preview",
                        "payload_schema": "source_artifact_selection",
                    },
                }
            )
        if not plan_artifacts:
            continue
        plan_items.append(
            {
                "group_id": str(manifest_item.get("group_id") or ""),
                "source_label": str(manifest_item.get("source_label") or ""),
                "source_history": manifest_item.get("source_history")
                if isinstance(manifest_item.get("source_history"), dict)
                else {},
                "source_session_id": str(manifest_item.get("source_session_id") or ""),
                "session_id": str(manifest_item.get("session_id") or ""),
                "title": str(manifest_item.get("title") or ""),
                "feedback_ids": manifest_item.get("feedback_ids")
                if isinstance(manifest_item.get("feedback_ids"), list)
                else [],
                "readiness": manifest_item.get("readiness")
                if isinstance(manifest_item.get("readiness"), dict)
                else {},
                "selection_gate": selection_gate,
                "feedback_closure_state": closure_state,
                "feedback_source_previews": clean_feedback_previews,
                "plan_artifacts": plan_artifacts,
                "counts": {
                    "plan_artifacts": len(plan_artifacts),
                    "feedback_inputs": len(clean_feedback_previews),
                },
            }
        )
    return plan_items, found_artifact_ids


def build_ocr_retry_rerun_plan_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    manifest_report = build_ocr_retry_rerun_manifest_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    manifest_items = manifest_report.get("manifest_items")
    if not isinstance(manifest_items, list):
        manifest_items = []
    manifest_items = [item for item in manifest_items if isinstance(item, dict)]
    selected_artifact_ids = _split_artifact_ids(artifact_ids)
    plan_items, found_artifact_ids = build_ocr_retry_rerun_plan_items(
        manifest_items=manifest_items,
        selected_artifact_ids=selected_artifact_ids,
    )
    manifest_counts = manifest_report.get("counts")
    if not isinstance(manifest_counts, dict):
        manifest_counts = {}
    manifest_filters = manifest_report.get("filters")
    if not isinstance(manifest_filters, dict):
        manifest_filters = {}
    item_counts = [item.get("counts") for item in plan_items]
    unmatched_artifact_ids = [
        artifact_id
        for artifact_id in selected_artifact_ids
        if artifact_id not in found_artifact_ids
    ]

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_RERUN_PLAN_SCHEMA_VERSION,
        "manifest_schema_version": manifest_report.get("schema_version", ""),
        "state": manifest_report.get("state", "unknown"),
        "manual_evals_db": manifest_report.get("manual_evals_db", {}),
        "filters": {
            "status": manifest_filters.get("status") or "open",
            "outcome": manifest_filters.get("outcome") or "",
            "cohort": manifest_filters.get("cohort") or "",
            "limit": _int_value(manifest_filters.get("limit")),
            "packet_basis": "rerun_manifest_resolved_artifact_command_preview",
            "selection_mode": (
                "requested_artifact_ids"
                if selected_artifact_ids
                else "all_ready_resolved_source_artifacts"
            ),
            "artifact_ids": selected_artifact_ids,
        },
        "counts": {
            "total_feedback_rows": _int_value(
                manifest_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                manifest_counts.get("returned_feedback_rows")
            ),
            "manifest_items": _int_value(manifest_counts.get("manifest_items")),
            "plan_items": len(plan_items),
            "source_artifacts": _int_value(manifest_counts.get("source_artifacts")),
            "resolved_source_artifacts": _int_value(
                manifest_counts.get("resolved_source_artifacts")
            ),
            "planned_source_artifacts": sum(
                _int_value(counts.get("plan_artifacts"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "feedback_closure_blocked_items": _int_value(
                manifest_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                manifest_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                manifest_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                manifest_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": len(selected_artifact_ids),
            "unmatched_artifact_ids": len(unmatched_artifact_ids),
            "preview_only": True,
            "limit_applied": bool(manifest_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": unmatched_artifact_ids,
        "plan_items": plan_items,
    }
    warnings = manifest_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    if unmatched_artifact_ids:
        report.setdefault("warnings", []).append(
            "one or more requested artifact ids were not found in resolved "
            "source artifacts"
        )
    return report


def _format_plan_artifact_line(item: dict[str, Any]) -> str:
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


def format_ocr_retry_rerun_plan_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry rerun plan: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('plan_items'))} "
        f"planned_artifacts={_int_value(counts.get('planned_source_artifacts'))} "
        "resolved="
        f"{_int_value(counts.get('resolved_source_artifacts'))}/"
        f"{_int_value(counts.get('source_artifacts'))} "
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

    plan_items = report.get("plan_items")
    if not isinstance(plan_items, list) or not plan_items:
        lines.append("plan_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in plan_items:
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
                f"plan_artifacts={_int_value(item_counts.get('plan_artifacts'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)}",
            ]
        )
        plan_artifacts = item.get("plan_artifacts")
        if not isinstance(plan_artifacts, list):
            plan_artifacts = []
        for artifact in plan_artifacts:
            if not isinstance(artifact, dict):
                continue
            lines.append(f"  - {_format_plan_artifact_line(artifact)}")
            lines.append(
                "    source_preview="
                f"{_format_plan_source_preview(artifact.get('feedback_source_preview'))}"
            )
            payload = artifact.get("payload_inputs")
            if isinstance(payload, dict):
                lines.append(
                    "    payload="
                    f"artifact_id={payload.get('artifact_id') or 'none'} "
                    f"operation={payload.get('operation') or 'unknown'} "
                    "source_path="
                    f"{_format_terminal_source_path(payload.get('resolved_path'))}"
                )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)
