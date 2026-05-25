from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_candidates import (
    OCR_RETRY_TERMINAL_CONTEXT_LIMIT,
    build_ocr_retry_candidates_report,
)


OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_source_verification.v1"
)

OCR_RETRY_SOURCE_VERIFICATION_REASONS = {
    "multiple_same_session_ocr_runs": (
        "same source session has multiple OCR runs, so same-session OCR remains "
        "context until an exact feedback result link is selected"
    ),
    "missing_feedback_to_result_link": (
        "feedback message_id does not match any OCR result_message_id in this "
        "candidate group"
    ),
    "latest_ocr_is_context_only": (
        "latest same-session OCR run is context only because it is not an exact "
        "feedback result link"
    ),
    "no_same_session_ocr_context": ("no OCR run is available for this source session"),
    "no_latest_same_session_ocr": (
        "no latest same-session OCR run is available for this source session"
    ),
}


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


def _unconfirmed_reasons(
    readiness: dict[str, Any],
) -> list[dict[str, str]]:
    flags = readiness.get("flags")
    if not isinstance(flags, list):
        flags = []
    reasons: list[dict[str, str]] = []
    for flag in flags:
        code = str(flag)
        reasons.append(
            {
                "code": code,
                "reason": OCR_RETRY_SOURCE_VERIFICATION_REASONS.get(
                    code,
                    "candidate group needs review before it is confirmed",
                ),
            }
        )
    if readiness.get("state") == "needs_review" and not reasons:
        reasons.append(
            {
                "code": "needs_review",
                "reason": "candidate group is not confirmed by readiness signals",
            }
        )
    return reasons


def _source_candidate(ocr_run: dict[str, Any]) -> dict[str, Any]:
    image_asset = ocr_run.get("image_asset")
    if not isinstance(image_asset, dict):
        image_asset = {}
    thumbnail = image_asset.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    source_image_name = str(
        image_asset.get("source_filename") or ocr_run.get("source_name") or ""
    )
    resolved_path = str(image_asset.get("resolved_path") or "")
    return {
        "run_id": str(ocr_run.get("run_id") or ""),
        "source_image_name": source_image_name,
        "source_name": str(ocr_run.get("source_name") or ""),
        "source_message_id": str(ocr_run.get("source_message_id") or ""),
        "result_message_id": str(ocr_run.get("result_message_id") or ""),
        "status": str(ocr_run.get("status") or ""),
        "created_at": _int_value(ocr_run.get("created_at")),
        "extracted_text_chars": _int_value(ocr_run.get("extracted_text_chars")),
        "extracted_text_preview": str(ocr_run.get("extracted_text_preview") or ""),
        "image_asset": {
            "source_filename": str(image_asset.get("source_filename") or ""),
            "resolved": bool(resolved_path),
            "resolved_path": resolved_path,
            "mime_type": str(image_asset.get("mime_type") or ""),
            "status": str(image_asset.get("status") or "unlinked"),
            "error": str(image_asset.get("error") or ""),
            "source_size_bytes": _int_value(image_asset.get("source_size_bytes")),
            "thumbnail": {
                "available": bool(thumbnail.get("available")),
                "width": _int_value(thumbnail.get("width")),
                "height": _int_value(thumbnail.get("height")),
            },
        },
    }


def _build_verification_items(
    candidate_groups: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    verification_items: list[dict[str, Any]] = []
    for group in candidate_groups:
        readiness = group.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        ocr_runs = group.get("ocr_runs")
        if not isinstance(ocr_runs, list):
            ocr_runs = []
        source_candidates = [
            _source_candidate(ocr_run)
            for ocr_run in ocr_runs
            if isinstance(ocr_run, dict)
        ]
        reasons = _unconfirmed_reasons(readiness)
        confirmation_state = "confirmed" if not reasons else "not_confirmed"
        verification_items.append(
            {
                "group_id": str(group.get("group_id") or ""),
                "source_label": str(group.get("source_label") or ""),
                "source_history_db": str(group.get("source_history_db") or ""),
                "source_session_id": str(group.get("source_session_id") or ""),
                "session_id": str(group.get("session_id") or ""),
                "title": str(group.get("title") or ""),
                "feedback_ids": group.get("feedback_ids")
                if isinstance(group.get("feedback_ids"), list)
                else [],
                "feedback_rows": group.get("feedback_rows")
                if isinstance(group.get("feedback_rows"), list)
                else [],
                "readiness": readiness,
                "confirmation": {
                    "state": confirmation_state,
                    "basis": "explicit_feedback_result_links_before_rerun",
                    "reasons": reasons,
                },
                "latest_same_session_ocr": group.get("latest_same_session_ocr")
                if isinstance(group.get("latest_same_session_ocr"), dict)
                else {},
                "same_session_ocr_runs": _int_value(group.get("same_session_ocr_runs")),
                "source_candidates": source_candidates,
            }
        )
    return verification_items


def build_ocr_retry_source_verification_report(
    *,
    db_path: Path,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
) -> dict[str, Any]:
    candidate_report = build_ocr_retry_candidates_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    candidate_groups = candidate_report.get("candidate_groups")
    if not isinstance(candidate_groups, list):
        candidate_groups = []
    verification_items = _build_verification_items(
        [group for group in candidate_groups if isinstance(group, dict)]
    )
    needs_review_items = sum(
        1
        for item in verification_items
        if isinstance(item.get("confirmation"), dict)
        and item["confirmation"].get("state") == "not_confirmed"
    )
    source_candidate_count = 0
    for item in verification_items:
        source_candidates = item.get("source_candidates")
        if isinstance(source_candidates, list):
            source_candidate_count += len(source_candidates)
    candidate_counts = candidate_report.get("counts")
    if not isinstance(candidate_counts, dict):
        candidate_counts = {}
    candidate_filters = candidate_report.get("filters")
    if not isinstance(candidate_filters, dict):
        candidate_filters = {}

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SOURCE_VERIFICATION_SCHEMA_VERSION,
        "candidate_schema_version": candidate_report.get("schema_version", ""),
        "state": candidate_report.get("state", "unknown"),
        "manual_evals_db": candidate_report.get("manual_evals_db", {}),
        "filters": {
            "status": candidate_filters.get("status") or "open",
            "outcome": candidate_filters.get("outcome") or "",
            "cohort": candidate_filters.get("cohort") or "",
            "limit": _int_value(candidate_filters.get("limit")),
            "packet_basis": (
                "feedback_note_action_readiness_and_source_candidate_context"
            ),
        },
        "counts": {
            "total_feedback_rows": _int_value(
                candidate_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                candidate_counts.get("returned_feedback_rows")
            ),
            "verification_items": len(verification_items),
            "ready_verification_items": len(verification_items) - needs_review_items,
            "needs_review_verification_items": needs_review_items,
            "source_candidates": source_candidate_count,
            "limit_applied": bool(candidate_counts.get("limit_applied")),
        },
        "verification_items": verification_items,
    }
    warnings = candidate_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = warnings
    return report


def _format_confirmation_reasons(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    reason_parts: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        code = str(item.get("code") or "unknown")
        reason = _display_text(item.get("reason"))
        reason_parts.append(f"{code}: {reason}")
    return " | ".join(reason_parts) if reason_parts else "none"


def _format_source_candidate_line(candidate: dict[str, Any]) -> str:
    image_asset = candidate.get("image_asset")
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
    preview = _truncate_text(candidate.get("extracted_text_preview"), max_chars=80)
    return (
        f"ocr={candidate.get('run_id') or 'none'} "
        f"source_image={candidate.get('source_image_name') or 'none'} "
        f"source_message={candidate.get('source_message_id') or 'none'} "
        f"result_message={candidate.get('result_message_id') or 'none'} "
        f"status={candidate.get('status') or 'none'} "
        f"image_status={image_asset.get('status') or 'unknown'} "
        f"resolved={'yes' if image_asset.get('resolved') else 'no'} "
        f"thumbnail={thumbnail_text} "
        f"preview={preview or 'none'}"
    )


def format_ocr_retry_source_verification_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry source verification: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('verification_items'))} "
        "needs_review="
        f"{_int_value(counts.get('needs_review_verification_items'))} "
        f"source_candidates={_int_value(counts.get('source_candidates'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]

    verification_items = report.get("verification_items")
    if not isinstance(verification_items, list) or not verification_items:
        lines.append("verification_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in verification_items:
        if not isinstance(item, dict):
            continue
        readiness = item.get("readiness")
        if not isinstance(readiness, dict):
            readiness = {}
        confirmation = item.get("confirmation")
        if not isinstance(confirmation, dict):
            confirmation = {}
        source_candidates = item.get("source_candidates")
        if not isinstance(source_candidates, list):
            source_candidates = []
        reasons = confirmation.get("reasons")
        lines.extend(
            [
                "- "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_session={item.get('source_session_id') or 'unknown'} "
                f"feedback={_format_feedback_ids(item.get('feedback_ids'))} "
                f"confirmation={confirmation.get('state') or 'unknown'} "
                f"ocr_runs={_int_value(item.get('same_session_ocr_runs'))}",
                f"  title={_display_text(item.get('title'))}",
                "  readiness="
                f"{readiness.get('state') or 'unknown'} "
                f"flags={_format_readiness_flags(readiness)} "
                "explicit_links="
                f"{_int_value(readiness.get('explicit_feedback_to_result_links'))} "
                "unlinked_feedback="
                f"{_int_value(readiness.get('unlinked_feedback_rows'))}",
                f"  reasons={_format_confirmation_reasons(reasons)}",
            ]
        )
        feedback_rows = item.get("feedback_rows")
        if not isinstance(feedback_rows, list):
            feedback_rows = []
        if feedback_rows:
            lines.append("  feedback_rows:")
        for row in feedback_rows:
            if not isinstance(row, dict):
                continue
            lines.extend(
                [
                    "  - "
                    f"feedback={_int_value(row.get('feedback_id'))} "
                    f"message={row.get('message_id') or 'unknown'} "
                    f"outcome={row.get('outcome') or 'unknown'}",
                    f"    note={_display_text(row.get('note'))}",
                    "    recommended_action="
                    f"{_display_text(row.get('recommended_action'))}",
                    f"    action_taken={_display_text(row.get('action_taken'))}",
                ]
            )
        context_rows = [
            candidate
            for candidate in source_candidates[:OCR_RETRY_TERMINAL_CONTEXT_LIMIT]
            if isinstance(candidate, dict)
        ]
        if context_rows:
            lines.append("  source_candidates:")
            for candidate in context_rows:
                lines.append(f"  - {_format_source_candidate_line(candidate)}")
            hidden_rows = len(source_candidates) - len(context_rows)
            if hidden_rows > 0:
                lines.append(f"  source_candidates_more={hidden_rows}")
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)
