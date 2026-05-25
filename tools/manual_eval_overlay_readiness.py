from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from contextlib import closing
from pathlib import Path
from typing import Any

from tools.manual_eval_feedback_decisions import (
    feedback_decision_draft_source_preview,
)
from tools.manual_eval_ocr_evidence import build_ocr_retry_evidence_rows
from tools.manual_eval_open_feedback import (
    normalize_cohort_filter,
    normalize_outcome_filter,
)
from tools.manual_eval_overlay_source_index import (
    load_overlay_source_context_index,
    overlay_index_source_images,
    source_index_public,
)
from tools.manual_eval_source_context import build_feedback_source_context_report


OVERLAY_OCR_COMPARISON_READINESS_SCHEMA_VERSION = (
    "polinko.manual_eval_overlay_ocr_comparison_readiness.v1"
)


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


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


def _mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "read_only",
        "source_history_db": "read_only",
        "feedback_status": "unchanged",
        "ocr_runs": "unchanged",
        "image_assets": "unchanged",
        "eval_rows": "unchanged",
        "ocr_execution": "none",
        "browser": "excluded",
        "pulse": "excluded",
    }


def _blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _source_image_candidate(evidence_row: dict[str, Any]) -> dict[str, Any]:
    image_asset = evidence_row.get("image_asset")
    if not isinstance(image_asset, dict):
        image_asset = {}
    thumbnail = image_asset.get("thumbnail")
    if not isinstance(thumbnail, dict):
        thumbnail = {}
    return {
        "run_id": str(evidence_row.get("run_id") or ""),
        "source_name": str(evidence_row.get("source_name") or ""),
        "source_message_id": str(evidence_row.get("source_message_id") or ""),
        "result_message_id": str(evidence_row.get("result_message_id") or ""),
        "status": str(evidence_row.get("status") or ""),
        "created_at": _int_value(evidence_row.get("created_at")),
        "extracted_text_chars": _int_value(evidence_row.get("extracted_text_chars")),
        "extracted_text_preview": str(evidence_row.get("extracted_text_preview") or ""),
        "image_asset": {
            "source_filename": str(image_asset.get("source_filename") or ""),
            "resolved_path": str(image_asset.get("resolved_path") or ""),
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
        "context_source": "ocr_run",
    }


def _payload_preview(
    *,
    source_item: dict[str, Any],
    source_context: dict[str, Any],
    source_images: Sequence[dict[str, Any]],
    blockers: Sequence[dict[str, str]],
) -> dict[str, Any]:
    return {
        "label": "manual_eval_overlay_ocr_comparison_preview",
        "operation": "overlay_ocr_comparison_readiness",
        "state": "blocked" if blockers else "ready",
        "execution": "none",
        "mutation": "none",
        "feedback_id": _int_value(source_item.get("feedback_id")),
        "source_session_id": str(source_item.get("source_session_id") or ""),
        "session_id": str(source_item.get("session_id") or ""),
        "message_id": str(source_item.get("message_id") or ""),
        "source_context_fingerprint": str(source_context.get("fingerprint") or ""),
        "source_image_count": len(source_images),
        "required_inputs": [
            "attached_overlay_source_image_context",
            "human_selected_comparison_input",
        ],
        "next_gate": "future_overlay_ocr_comparison_execution",
        "next_gate_status": "not_implemented",
        "command_preview": (
            "make manual-evals-overlay-comparison-readiness "
            "COHORT=ocr_overlay_hypothesis OUTCOME=fail"
        ),
    }


def _readiness_item(
    source_item: dict[str, Any],
    evidence_rows: Sequence[dict[str, Any]],
    *,
    source_index_entries: Sequence[dict[str, Any]],
    source_index_path: str,
) -> dict[str, Any]:
    source_context = source_item.get("source_context")
    if not isinstance(source_context, dict):
        source_context = {}
    action_cohort = source_item.get("action_cohort")
    if not isinstance(action_cohort, dict):
        action_cohort = {}
    ocr_source_images = [_source_image_candidate(row) for row in evidence_rows]
    indexed_source_images, index_blockers = overlay_index_source_images(
        source_item=source_item,
        source_context=source_context,
        source_index_entries=source_index_entries,
        source_index_path=source_index_path,
    )
    source_images = [*ocr_source_images, *indexed_source_images]
    blockers: list[dict[str, str]] = []
    if source_context.get("state") != "found":
        blockers.append(
            _blocker(
                "source_context_not_found",
                "feedback row does not have source-history context for comparison.",
            )
        )
    blockers.extend(index_blockers)
    if not source_images:
        blockers.append(
            _blocker(
                "missing_overlay_source_image_context",
                "attach overlay/source image context before any OCR comparison run.",
            )
        )
    payload_preview = _payload_preview(
        source_item=source_item,
        source_context=source_context,
        source_images=source_images,
        blockers=blockers,
    )
    return {
        "feedback_id": _int_value(source_item.get("feedback_id")),
        "era": str(source_item.get("era") or ""),
        "source_label": str(source_item.get("source_label") or ""),
        "source_session_id": str(source_item.get("source_session_id") or ""),
        "session_id": str(source_item.get("session_id") or ""),
        "message_id": str(source_item.get("message_id") or ""),
        "title": str(source_item.get("title") or ""),
        "outcome": str(source_item.get("outcome") or ""),
        "status": str(source_item.get("status") or ""),
        "tags": source_item.get("tags")
        if isinstance(source_item.get("tags"), list)
        else [],
        "recommended_action": str(source_item.get("recommended_action") or ""),
        "action_taken": str(source_item.get("action_taken") or ""),
        "action_cohort": {
            "id": str(action_cohort.get("id") or ""),
            "description": str(action_cohort.get("description") or ""),
        },
        "source_context": {
            "state": str(source_context.get("state") or "unknown"),
            "fingerprint": str(source_context.get("fingerprint") or ""),
            "message_count": len(source_context.get("messages", []))
            if isinstance(source_context.get("messages"), list)
            else 0,
            "target_message": feedback_decision_draft_source_preview(source_context),
        },
        "source_images": source_images,
        "readiness": {
            "state": "blocked" if blockers else "ready",
            "basis": "source_context_and_attached_overlay_source_image_context",
            "source_context_state": str(source_context.get("state") or "unknown"),
            "source_image_count": len(source_images),
            "ocr_source_image_count": len(ocr_source_images),
            "indexed_source_image_count": len(indexed_source_images),
            "blockers": blockers,
        },
        "payload_preview": payload_preview,
        "state": "blocked" if blockers else "ready",
        "blockers": blockers,
    }


def build_overlay_ocr_comparison_readiness_report(
    *,
    db_path: Path,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_overlay_hypothesis",
    limit: int = 100,
    overlay_source_index_path: Path | None = None,
) -> dict[str, Any]:
    outcome_filter = normalize_outcome_filter(outcome) or "fail"
    cohort_filter = normalize_cohort_filter(cohort) or "ocr_overlay_hypothesis"
    row_limit = max(1, limit)
    source_index, source_index_entries = load_overlay_source_context_index(
        overlay_source_index_path
    )
    public_source_index = source_index_public(source_index)
    source_context_report = build_feedback_source_context_report(
        db_path=db_path,
        outcome=outcome_filter,
        cohort=cohort_filter,
        limit=row_limit,
    )
    source_items = source_context_report.get("items")
    if not isinstance(source_items, list):
        source_items = []
    evidence_by_session: dict[str, list[dict[str, Any]]] = {}
    if db_path.is_file():
        with closing(_connect_readonly(db_path)) as conn:
            evidence_by_session = build_ocr_retry_evidence_rows(
                conn,
                session_ids=[
                    str(item.get("session_id") or "")
                    for item in source_items
                    if isinstance(item, dict)
                ],
            )
    items = [
        _readiness_item(
            item,
            evidence_by_session.get(str(item.get("session_id") or ""), []),
            source_index_entries=source_index_entries.get(
                _int_value(item.get("feedback_id")), []
            ),
            source_index_path=str(public_source_index.get("path") or ""),
        )
        for item in source_items
        if isinstance(item, dict)
    ]
    item_blockers = [
        blocker
        for item in items
        if isinstance(item.get("blockers"), list)
        for blocker in item["blockers"]
        if isinstance(blocker, dict)
    ]
    source_report_blockers = source_context_report.get("blockers")
    if not isinstance(source_report_blockers, list):
        source_report_blockers = []
    report_blockers = [
        blocker for blocker in source_report_blockers if isinstance(blocker, dict)
    ]
    source_index_blockers = public_source_index.get("blockers")
    if not isinstance(source_index_blockers, list):
        source_index_blockers = []
    all_blockers = [*report_blockers, *source_index_blockers, *item_blockers]
    source_context_counts = source_context_report.get("counts")
    if not isinstance(source_context_counts, dict):
        source_context_counts = {}
    state = "ready"
    if source_context_report.get("state") == "error":
        state = "error"
    elif source_index_blockers or item_blockers:
        state = "blocked"
    return {
        "schema_version": OVERLAY_OCR_COMPARISON_READINESS_SCHEMA_VERSION,
        "source_context_schema_version": source_context_report.get(
            "schema_version", ""
        ),
        "state": state,
        "manual_evals_db": source_context_report.get("manual_evals_db", {}),
        "source_index": public_source_index,
        "filters": {
            "status": "open",
            "outcome": outcome_filter,
            "cohort": cohort_filter,
            "limit": row_limit,
            "packet_basis": "source_context_and_overlay_source_image_readiness",
        },
        "counts": {
            "total_rows": _int_value(source_context_counts.get("total_rows")),
            "returned_rows": len(items),
            "limit_applied": bool(source_context_counts.get("limit_applied")),
            "source_messages_found": _int_value(
                source_context_counts.get("source_messages_found")
            ),
            "source_images": sum(
                len(item.get("source_images", []))
                for item in items
                if isinstance(item.get("source_images"), list)
            ),
            "ocr_source_images": sum(
                _int_value(
                    item.get("readiness", {}).get("ocr_source_image_count")
                    if isinstance(item.get("readiness"), dict)
                    else 0
                )
                for item in items
            ),
            "indexed_source_images": sum(
                _int_value(
                    item.get("readiness", {}).get("indexed_source_image_count")
                    if isinstance(item.get("readiness"), dict)
                    else 0
                )
                for item in items
            ),
            "source_index_entries": _int_value(public_source_index.get("entries")),
            "ready_items": sum(1 for item in items if item.get("state") == "ready"),
            "blocked_items": sum(1 for item in items if item.get("state") != "ready"),
            "payload_previews": len(items),
            "blockers": len(all_blockers),
        },
        "readiness_contract": {
            "readiness_only": True,
            "execution": "none",
            "mutation": "none",
            "future_gate": "future_overlay_ocr_comparison_execution",
            "future_gate_status": "not_implemented",
        },
        "mutation_boundary": _mutation_boundary(),
        "items": items,
        "blockers": all_blockers,
        "warnings": [str(blocker.get("detail") or "") for blocker in all_blockers],
    }


def format_overlay_ocr_comparison_readiness_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    source_index = report.get("source_index")
    if not isinstance(source_index, dict):
        source_index = {}
    lines = [
        "manual eval overlay/OCR comparison readiness: "
        f"state={report.get('state', 'unknown')} "
        f"rows={_int_value(counts.get('returned_rows'))}/"
        f"{_int_value(counts.get('total_rows'))} "
        f"ready={_int_value(counts.get('ready_items'))} "
        f"blocked={_int_value(counts.get('blocked_items'))} "
        f"source_images={_int_value(counts.get('source_images'))} "
        f"payload_previews={_int_value(counts.get('payload_previews'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"source_index={source_index.get('state') or 'missing'} "
        f"index_entries={_int_value(source_index.get('entries'))} "
        f"warehouse_mutation={mutation.get('manual_evals_db') or 'unknown'} "
        f"execution={mutation.get('ocr_execution') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')}",
    ]
    items = report.get("items")
    if not isinstance(items, list) or not items:
        lines.append("items: none")
        return "\n".join(lines)
    for item in items:
        if not isinstance(item, dict):
            continue
        action_cohort = item.get("action_cohort")
        if not isinstance(action_cohort, dict):
            action_cohort = {}
        source_context = item.get("source_context")
        if not isinstance(source_context, dict):
            source_context = {}
        target = source_context.get("target_message")
        if not isinstance(target, dict):
            target = {}
        source_images = item.get("source_images")
        if not isinstance(source_images, list):
            source_images = []
        payload_preview = item.get("payload_preview")
        if not isinstance(payload_preview, dict):
            payload_preview = {}
        lines.extend(
            [
                "- "
                f"feedback={_int_value(item.get('feedback_id'))} "
                f"state={item.get('state') or 'unknown'} "
                f"cohort={action_cohort.get('id') or 'unknown'} "
                f"session={item.get('session_id') or 'unknown'} "
                f"source_state={source_context.get('state') or 'unknown'} "
                f"source_images={len(source_images)} "
                f"payload={payload_preview.get('state') or 'unknown'}",
                f"  title={_display_text(item.get('title'))}",
                "  "
                f"target={target.get('role') or 'unknown'} "
                f"message={target.get('message_id') or 'none'} "
                f"preview={_display_text(target.get('content_preview'))}",
                "  "
                f"payload_preview={payload_preview.get('label') or 'unknown'} "
                f"execution={payload_preview.get('execution') or 'unknown'} "
                f"mutation={payload_preview.get('mutation') or 'unknown'} "
                f"next_gate={payload_preview.get('next_gate') or 'unknown'}",
            ]
        )
        if source_images:
            lines.append("  source_images:")
            for source_image in source_images:
                if not isinstance(source_image, dict):
                    continue
                image_asset = source_image.get("image_asset")
                if not isinstance(image_asset, dict):
                    image_asset = {}
                thumbnail = image_asset.get("thumbnail")
                if not isinstance(thumbnail, dict):
                    thumbnail = {}
                lines.append(
                    "  - "
                    f"run={source_image.get('run_id') or 'none'} "
                    f"origin={source_image.get('context_source') or 'unknown'} "
                    f"source={_display_text(source_image.get('source_name'))} "
                    f"image_status={image_asset.get('status') or 'unknown'} "
                    f"thumbnail="
                    f"{'yes' if thumbnail.get('available') else 'no'}"
                )
        blockers = item.get("blockers")
        if isinstance(blockers, list) and blockers:
            lines.append("  blockers:")
            for blocker in blockers:
                if not isinstance(blocker, dict):
                    continue
                lines.append(
                    "  - "
                    f"code={blocker.get('code') or 'unknown'} "
                    f"detail={blocker.get('detail') or ''}"
                )
    blockers = report.get("blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("blockers:")
        for blocker in blockers:
            if not isinstance(blocker, dict):
                continue
            lines.append(
                "- "
                f"code={blocker.get('code') or 'unknown'} "
                f"detail={blocker.get('detail') or ''}"
            )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    return "\n".join(lines)
