from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_candidates import OCR_RETRY_TERMINAL_CONTEXT_LIMIT
from tools.manual_eval_ocr_retry_source_provenance import (
    OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION,
    build_ocr_retry_source_provenance_items,
    source_message_reference,
)
from tools.manual_eval_ocr_retry_selection_formatters import (
    display_text as _display_text,
    format_feedback_ids as _format_feedback_ids,
    format_input_blocker_state as _format_input_blocker_state,
    format_readiness_flags as _format_readiness_flags,
    int_value as _int_value,
    truncate_text as _truncate_text,
)
from tools.manual_eval_ocr_retry_source_verification import (
    build_ocr_retry_source_verification_report,
)


OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION = "polinko.manual_eval_ocr_retry_input_packet.v1"


def _ocr_retry_input_blocker_state(
    *,
    confirmation: dict[str, Any],
    exact_feedback_result_links: int,
    source_message_ids_present: int,
    result_message_ids_present: int,
) -> dict[str, Any]:
    if confirmation.get("state") == "confirmed" and exact_feedback_result_links > 0:
        return {
            "state": "ready",
            "reason_code": "",
            "reason": "",
            "next_action": "review_exact_link_before_feedback_closure",
        }
    if source_message_ids_present == 0 and result_message_ids_present == 0:
        return {
            "state": "blocked",
            "reason_code": "missing_ocr_source_result_message_ids",
            "reason": (
                "candidate OCR rows do not carry source/result message IDs, so "
                "the next decision is rerun input preparation or case curation"
            ),
            "next_action": "prepare_rerun_or_case_curation",
        }
    if exact_feedback_result_links == 0:
        return {
            "state": "blocked",
            "reason_code": "missing_exact_feedback_result_link",
            "reason": (
                "OCR source/result message IDs are present, but none exactly "
                "matches the feedback message"
            ),
            "next_action": "select_exact_case_or_prepare_rerun",
        }
    return {
        "state": "needs_review",
        "reason_code": "unconfirmed_source_context",
        "reason": "source context exists but confirmation is not ready for closure",
        "next_action": "review_source_verification_packet",
    }


def build_ocr_retry_input_items(
    *,
    verification_items: Sequence[dict[str, Any]],
    provenance_items: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    provenance_by_group_id = {
        str(item.get("group_id") or ""): item
        for item in provenance_items
        if isinstance(item, dict)
    }
    input_items: list[dict[str, Any]] = []
    for item in verification_items:
        group_id = str(item.get("group_id") or "")
        provenance = provenance_by_group_id.get(group_id, {})
        if not isinstance(provenance, dict):
            provenance = {}
        provenance_counts = provenance.get("counts")
        if not isinstance(provenance_counts, dict):
            provenance_counts = {}
        source_history = provenance.get("source_history")
        if not isinstance(source_history, dict):
            source_history = {}

        feedback_messages_by_id = {
            _int_value(row.get("feedback_id")): row
            for row in provenance.get("feedback_messages", [])
            if isinstance(row, dict)
        }
        ocr_provenance_by_run_id = {
            str(row.get("run_id") or ""): row
            for row in provenance.get("ocr_message_provenance", [])
            if isinstance(row, dict)
        }

        feedback_rows = item.get("feedback_rows")
        if not isinstance(feedback_rows, list):
            feedback_rows = []
        feedback_inputs: list[dict[str, Any]] = []
        for feedback_row in feedback_rows:
            if not isinstance(feedback_row, dict):
                continue
            feedback_id = _int_value(feedback_row.get("feedback_id"))
            feedback_provenance = feedback_messages_by_id.get(feedback_id, {})
            if not isinstance(feedback_provenance, dict):
                feedback_provenance = {}
            source_message = feedback_provenance.get("source_message")
            if not isinstance(source_message, dict):
                source_message = source_message_reference(
                    message_id=str(feedback_row.get("message_id") or ""),
                    message_lookup={},
                )
            feedback_inputs.append(
                {
                    "feedback_id": feedback_id,
                    "message_id": str(feedback_row.get("message_id") or ""),
                    "outcome": str(feedback_row.get("outcome") or ""),
                    "note": str(feedback_row.get("note") or ""),
                    "recommended_action": str(
                        feedback_row.get("recommended_action") or ""
                    ),
                    "action_taken": str(feedback_row.get("action_taken") or ""),
                    "source_message": source_message,
                }
            )

        source_candidates = item.get("source_candidates")
        if not isinstance(source_candidates, list):
            source_candidates = []
        rerun_inputs: list[dict[str, Any]] = []
        for candidate in source_candidates:
            if not isinstance(candidate, dict):
                continue
            run_id = str(candidate.get("run_id") or "")
            candidate_provenance = ocr_provenance_by_run_id.get(run_id, {})
            if not isinstance(candidate_provenance, dict):
                candidate_provenance = {}
            source_message = candidate_provenance.get("source_message")
            if not isinstance(source_message, dict):
                source_message = source_message_reference(
                    message_id=str(candidate.get("source_message_id") or ""),
                    message_lookup={},
                )
            result_message = candidate_provenance.get("result_message")
            if not isinstance(result_message, dict):
                result_message = source_message_reference(
                    message_id=str(candidate.get("result_message_id") or ""),
                    message_lookup={},
                )
            image_asset = candidate.get("image_asset")
            if not isinstance(image_asset, dict):
                image_asset = {}
            rerun_inputs.append(
                {
                    "run_id": run_id,
                    "source_image_name": str(candidate.get("source_image_name") or ""),
                    "source_name": str(candidate.get("source_name") or ""),
                    "status": str(candidate.get("status") or ""),
                    "created_at": _int_value(candidate.get("created_at")),
                    "extracted_text_chars": _int_value(
                        candidate.get("extracted_text_chars")
                    ),
                    "extracted_text_preview": str(
                        candidate.get("extracted_text_preview") or ""
                    ),
                    "source_message_id": str(candidate.get("source_message_id") or ""),
                    "result_message_id": str(candidate.get("result_message_id") or ""),
                    "exact_feedback_result_link": bool(
                        candidate_provenance.get("exact_feedback_result_link")
                    ),
                    "source_message": source_message,
                    "result_message": result_message,
                    "image_asset": image_asset,
                }
            )

        exact_links = _int_value(provenance_counts.get("exact_feedback_result_links"))
        source_message_ids_present = _int_value(
            provenance_counts.get("ocr_source_message_ids_present")
        )
        result_message_ids_present = _int_value(
            provenance_counts.get("ocr_result_message_ids_present")
        )
        resolved_inputs = sum(
            1
            for row in rerun_inputs
            if isinstance(row.get("image_asset"), dict)
            and row["image_asset"].get("resolved")
        )
        confirmation = item.get("confirmation")
        if not isinstance(confirmation, dict):
            confirmation = {}
        feedback_sources_found = sum(
            1 for row in feedback_inputs if row["source_message"].get("present")
        )
        blocker_state = _ocr_retry_input_blocker_state(
            confirmation=confirmation,
            exact_feedback_result_links=exact_links,
            source_message_ids_present=source_message_ids_present,
            result_message_ids_present=result_message_ids_present,
        )
        input_items.append(
            {
                "group_id": group_id,
                "source_label": str(item.get("source_label") or ""),
                "source_history": source_history,
                "source_session_id": str(item.get("source_session_id") or ""),
                "session_id": str(item.get("session_id") or ""),
                "title": str(item.get("title") or ""),
                "feedback_ids": item.get("feedback_ids")
                if isinstance(item.get("feedback_ids"), list)
                else [],
                "readiness": item.get("readiness")
                if isinstance(item.get("readiness"), dict)
                else {},
                "confirmation": confirmation,
                "blocker_state": blocker_state,
                "feedback_inputs": feedback_inputs,
                "rerun_inputs": rerun_inputs,
                "counts": {
                    "feedback_inputs": len(feedback_inputs),
                    "feedback_sources_found": feedback_sources_found,
                    "rerun_inputs": len(rerun_inputs),
                    "resolved_rerun_inputs": resolved_inputs,
                    "unresolved_rerun_inputs": len(rerun_inputs) - resolved_inputs,
                    "ocr_source_message_ids_present": source_message_ids_present,
                    "ocr_result_message_ids_present": result_message_ids_present,
                    "exact_feedback_result_links": exact_links,
                },
            }
        )
    return input_items


def build_ocr_retry_input_packet_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    verification_report = build_ocr_retry_source_verification_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    verification_items = verification_report.get("verification_items")
    if not isinstance(verification_items, list):
        verification_items = []
    verification_items = [item for item in verification_items if isinstance(item, dict)]
    provenance_items = build_ocr_retry_source_provenance_items(verification_items)
    input_items = build_ocr_retry_input_items(
        verification_items=verification_items,
        provenance_items=provenance_items,
    )
    verification_counts = verification_report.get("counts")
    if not isinstance(verification_counts, dict):
        verification_counts = {}
    verification_filters = verification_report.get("filters")
    if not isinstance(verification_filters, dict):
        verification_filters = {}
    item_counts = [item.get("counts") for item in input_items]

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_INPUT_PACKET_SCHEMA_VERSION,
        "verification_schema_version": verification_report.get("schema_version", ""),
        "provenance_schema_version": OCR_RETRY_SOURCE_PROVENANCE_SCHEMA_VERSION,
        "state": verification_report.get("state", "unknown"),
        "manual_evals_db": verification_report.get("manual_evals_db", {}),
        "filters": {
            "status": verification_filters.get("status") or "open",
            "outcome": verification_filters.get("outcome") or "",
            "cohort": verification_filters.get("cohort") or "",
            "limit": _int_value(verification_filters.get("limit")),
            "packet_basis": "verified_source_candidates_and_source_history_provenance",
        },
        "counts": {
            "total_feedback_rows": _int_value(
                verification_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                verification_counts.get("returned_feedback_rows")
            ),
            "input_items": len(input_items),
            "blocked_input_items": sum(
                1
                for item in input_items
                if isinstance(item.get("blocker_state"), dict)
                and item["blocker_state"].get("state") == "blocked"
            ),
            "feedback_inputs": sum(
                _int_value(counts.get("feedback_inputs"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "feedback_sources_found": sum(
                _int_value(counts.get("feedback_sources_found"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "rerun_inputs": sum(
                _int_value(counts.get("rerun_inputs"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "resolved_rerun_inputs": sum(
                _int_value(counts.get("resolved_rerun_inputs"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "unresolved_rerun_inputs": sum(
                _int_value(counts.get("unresolved_rerun_inputs"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_source_message_ids_present": sum(
                _int_value(counts.get("ocr_source_message_ids_present"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "ocr_result_message_ids_present": sum(
                _int_value(counts.get("ocr_result_message_ids_present"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "exact_feedback_result_links": sum(
                _int_value(counts.get("exact_feedback_result_links"))
                for counts in item_counts
                if isinstance(counts, dict)
            ),
            "limit_applied": bool(verification_counts.get("limit_applied")),
        },
        "input_items": input_items,
    }
    warnings = verification_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _format_source_message_ref(value: object) -> str:
    if not isinstance(value, dict):
        return "unknown"
    state = str(value.get("state") or "unknown")
    if state == "empty":
        return "none"
    if state != "found":
        return state
    preview = _truncate_text(value.get("content_preview"), max_chars=80)
    return (
        f"found role={value.get('role') or 'unknown'} "
        f"chars={_int_value(value.get('content_chars'))} "
        f"preview={preview or 'none'}"
    )


def _format_ocr_retry_input_line(item: dict[str, Any]) -> str:
    image_asset = item.get("image_asset")
    if not isinstance(image_asset, dict):
        image_asset = {}
    thumbnail = image_asset.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    thumbnail_text = "none"
    if thumbnail.get("available"):
        thumbnail_text = (
            f"{_int_value(thumbnail.get('width'))}x"
            f"{_int_value(thumbnail.get('height'))}"
        )
    preview = _truncate_text(item.get("extracted_text_preview"), max_chars=80)
    return (
        f"ocr={item.get('run_id') or 'none'} "
        f"source_image={item.get('source_image_name') or 'none'} "
        f"image_status={image_asset.get('status') or 'unknown'} "
        f"resolved={'yes' if image_asset.get('resolved') else 'no'} "
        f"thumbnail={thumbnail_text} "
        f"source_message={item.get('source_message_id') or 'none'} "
        f"result_message={item.get('result_message_id') or 'none'} "
        "exact_feedback_link="
        f"{'yes' if item.get('exact_feedback_result_link') else 'no'} "
        f"preview={preview or 'none'}"
    )


def format_ocr_retry_input_packet_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry input packet: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('input_items'))} "
        f"blocked={_int_value(counts.get('blocked_input_items'))} "
        "feedback_inputs="
        f"{_int_value(counts.get('feedback_sources_found'))}/"
        f"{_int_value(counts.get('feedback_inputs'))} "
        f"rerun_inputs={_int_value(counts.get('rerun_inputs'))} "
        "resolved="
        f"{_int_value(counts.get('resolved_rerun_inputs'))}/"
        f"{_int_value(counts.get('rerun_inputs'))} "
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

    input_items = report.get("input_items")
    if not isinstance(input_items, list) or not input_items:
        lines.append("input_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in input_items:
        if not isinstance(item, dict):
            continue
        readiness = item.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        item_counts = item.get("counts")
        if not isinstance(item_counts, dict):
            item_counts = {}
        lines.extend(
            [
                "- "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                f"blocker={_format_input_blocker_state(item.get('blocker_state'))} "
                f"rerun_inputs={_int_value(item_counts.get('rerun_inputs'))} "
                "exact_links="
                f"{_int_value(item_counts.get('exact_feedback_result_links'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)} "
                "explicit_links="
                f"{_int_value(readiness.get('explicit_feedback_to_result_links'))} "
                "unlinked_feedback="
                f"{_int_value(readiness.get('unlinked_feedback_rows'))}",
            ]
        )
        feedback_inputs = item.get("feedback_inputs")
        if not isinstance(feedback_inputs, list):
            feedback_inputs = []
        if feedback_inputs:
            lines.append("  feedback_inputs:")
        for row in feedback_inputs:
            if not isinstance(row, dict):
                continue
            lines.extend(
                [
                    "  - "
                    f"feedback={_int_value(row.get('feedback_id'))} "
                    f"message={row.get('message_id') or 'unknown'} "
                    "source_state="
                    f"{_format_source_message_ref(row.get('source_message'))}",
                    f"    note={_display_text(row.get('note'))}",
                    "    recommended_action="
                    f"{_display_text(row.get('recommended_action'))}",
                ]
            )
        rerun_inputs = item.get("rerun_inputs")
        if not isinstance(rerun_inputs, list):
            rerun_inputs = []
        context_rows = [
            row
            for row in rerun_inputs[:OCR_RETRY_TERMINAL_CONTEXT_LIMIT]
            if isinstance(row, dict)
        ]
        if context_rows:
            lines.append("  rerun_inputs:")
            for row in context_rows:
                lines.append(f"  - {_format_ocr_retry_input_line(row)}")
            hidden_rows = len(rerun_inputs) - len(context_rows)
            if hidden_rows > 0:
                lines.append(f"  rerun_inputs_more={hidden_rows}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)
