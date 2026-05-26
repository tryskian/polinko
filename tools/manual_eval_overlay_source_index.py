from __future__ import annotations

import json
import mimetypes
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION = (
    "polinko.manual_eval_overlay_source_context_index.v1"
)
OVERLAY_SOURCE_CONTEXT_INDEX_DRAFT_SCHEMA_VERSION = (
    "polinko.manual_eval_overlay_source_context_index_draft.v1"
)
OVERLAY_SOURCE_CONTEXT_INDEX_VALIDATION_SCHEMA_VERSION = (
    "polinko.manual_eval_overlay_source_context_index_validation.v1"
)
DEFAULT_OVERLAY_SOURCE_CONTEXT_INDEX_PATH = Path(
    ".local/manual_eval_decisions/overlay_source_context_index.json"
)


ReadinessBuilder = Callable[..., dict[str, Any]]


def _default_readiness_builder() -> ReadinessBuilder:
    from tools.manual_eval_overlay_readiness import (
        build_overlay_ocr_comparison_readiness_report,
    )

    return build_overlay_ocr_comparison_readiness_report


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


def _utc_timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _source_index_blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _comparison_blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def load_overlay_source_context_index(
    index_path: Path | None,
) -> tuple[dict[str, Any], dict[int, list[dict[str, Any]]]]:
    resolved_path = (
        index_path or DEFAULT_OVERLAY_SOURCE_CONTEXT_INDEX_PATH
    ).expanduser()
    explicit_path = index_path is not None
    source: dict[str, Any] = {
        "path": str(resolved_path),
        "exists": resolved_path.is_file(),
        "explicit_path": explicit_path,
        "state": "missing",
        "schema_version": "",
        "entries": 0,
        "indexed_source_images": 0,
        "blockers": [],
    }
    if not resolved_path.is_file():
        if explicit_path:
            source["state"] = "blocked"
            source["blockers"] = [
                _source_index_blocker(
                    "overlay_source_index_not_found",
                    "explicit overlay/source image index file was not found.",
                )
            ]
        return source, {}

    try:
        payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        source["state"] = "blocked"
        source["blockers"] = [
            _source_index_blocker(
                "overlay_source_index_unreadable",
                f"overlay/source image index could not be read: {exc}",
            )
        ]
        return source, {}

    if not isinstance(payload, dict):
        source["state"] = "blocked"
        source["blockers"] = [
            _source_index_blocker(
                "overlay_source_index_not_object",
                "overlay/source image index root must be a JSON object.",
            )
        ]
        return source, {}

    source["schema_version"] = str(payload.get("schema_version") or "")
    if source["schema_version"] != OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION:
        source["state"] = "blocked"
        source["blockers"] = [
            _source_index_blocker(
                "overlay_source_index_schema_mismatch",
                "overlay/source image index schema version is not supported.",
            )
        ]
        return source, {}

    raw_entries = payload.get("entries")
    if not isinstance(raw_entries, list):
        source["state"] = "blocked"
        source["blockers"] = [
            _source_index_blocker(
                "overlay_source_index_entries_not_list",
                "overlay/source image index entries must be a list.",
            )
        ]
        return source, {}

    entries_by_feedback: dict[int, list[dict[str, Any]]] = {}
    blockers: list[dict[str, str]] = []
    indexed_source_images = 0
    for position, raw_entry in enumerate(raw_entries, start=1):
        if not isinstance(raw_entry, dict):
            blockers.append(
                _source_index_blocker(
                    "overlay_source_index_entry_not_object",
                    f"overlay/source image index entry {position} is not an object.",
                )
            )
            continue
        feedback_id = _int_value(raw_entry.get("feedback_id"))
        if feedback_id <= 0:
            blockers.append(
                _source_index_blocker(
                    "overlay_source_index_entry_missing_feedback_id",
                    f"overlay/source image index entry {position} has no feedback_id.",
                )
            )
            continue
        raw_images = raw_entry.get("source_images")
        if not isinstance(raw_images, list):
            raw_images = []
        indexed_source_images += len(
            [item for item in raw_images if isinstance(item, dict)]
        )
        normalized_entry = {
            "feedback_id": feedback_id,
            "source_session_id": str(raw_entry.get("source_session_id") or ""),
            "session_id": str(raw_entry.get("session_id") or ""),
            "message_id": str(raw_entry.get("message_id") or ""),
            "source_context_fingerprint": str(
                raw_entry.get("source_context_fingerprint") or ""
            ),
            "source_images": raw_images,
            "notes": str(raw_entry.get("notes") or ""),
        }
        entries_by_feedback.setdefault(feedback_id, []).append(normalized_entry)

    source["entries"] = sum(len(entries) for entries in entries_by_feedback.values())
    source["indexed_source_images"] = indexed_source_images
    source["blockers"] = blockers
    source["state"] = "blocked" if blockers else "loaded"
    return source, entries_by_feedback


def source_index_public(source_index: dict[str, Any]) -> dict[str, Any]:
    blockers = source_index.get("blockers")
    if not isinstance(blockers, list):
        blockers = []
    return {
        "path": str(source_index.get("path") or ""),
        "exists": bool(source_index.get("exists")),
        "explicit_path": bool(source_index.get("explicit_path")),
        "state": str(source_index.get("state") or "missing"),
        "schema_version": str(source_index.get("schema_version") or ""),
        "entries": _int_value(source_index.get("entries")),
        "indexed_source_images": _int_value(source_index.get("indexed_source_images")),
        "blockers": blockers,
    }


def _overlay_index_source_image_candidate(
    raw_image: dict[str, Any],
    *,
    source_index_path: str,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    raw_path = str(raw_image.get("resolved_path") or raw_image.get("path") or "")
    resolved_path = Path(raw_path).expanduser() if raw_path.strip() else None
    source_name = str(
        raw_image.get("source_image_name")
        or raw_image.get("source_name")
        or (resolved_path.name if resolved_path is not None else "")
    )
    source_filename = (
        Path(source_name).name
        if source_name
        else (resolved_path.name if resolved_path is not None else "")
    )
    blockers: list[dict[str, str]] = []
    source_file_exists = resolved_path.is_file() if resolved_path is not None else False
    source_size_bytes = 0
    if resolved_path is None:
        blockers.append(
            _comparison_blocker(
                "overlay_source_index_image_path_missing",
                "indexed overlay/source image does not name a local source path.",
            )
        )
    elif not source_file_exists:
        blockers.append(
            _comparison_blocker(
                "overlay_source_index_image_not_found",
                "indexed overlay/source image path does not exist.",
            )
        )
    else:
        try:
            source_size_bytes = int(resolved_path.stat().st_size)
        except OSError:
            source_size_bytes = 0
    mime_type = (
        str(raw_image.get("mime_type") or "")
        or mimetypes.guess_type(str(resolved_path or source_filename), strict=False)[0]
    )
    return (
        {
            "run_id": "",
            "source_name": source_name,
            "source_message_id": "",
            "result_message_id": "",
            "status": "indexed",
            "created_at": 0,
            "extracted_text_chars": 0,
            "extracted_text_preview": "",
            "image_asset": {
                "source_filename": source_filename,
                "resolved_path": str(resolved_path or ""),
                "mime_type": str(mime_type or ""),
                "status": "resolved" if source_file_exists else "missing",
                "error": "" if source_file_exists else "indexed_path_unavailable",
                "source_size_bytes": source_size_bytes,
                "thumbnail": {
                    "available": False,
                    "width": 0,
                    "height": 0,
                },
            },
            "context_source": "overlay_source_index",
            "source_index": {
                "path": source_index_path,
                "role": str(raw_image.get("role") or "overlay_source"),
                "notes": str(raw_image.get("notes") or ""),
            },
        },
        blockers,
    )


def _overlay_index_entry_blockers(
    *,
    entry: dict[str, Any],
    source_item: dict[str, Any],
    source_context: dict[str, Any],
) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    if str(entry.get("source_session_id") or "") and str(
        entry.get("source_session_id") or ""
    ) != str(source_item.get("source_session_id") or ""):
        blockers.append(
            _comparison_blocker(
                "overlay_source_index_source_session_mismatch",
                "overlay/source image index entry targets a different source session.",
            )
        )
    if str(entry.get("session_id") or "") and str(entry.get("session_id") or "") != str(
        source_item.get("session_id") or ""
    ):
        blockers.append(
            _comparison_blocker(
                "overlay_source_index_session_mismatch",
                "overlay/source image index entry targets a different session.",
            )
        )
    if str(entry.get("message_id") or "") and str(entry.get("message_id") or "") != str(
        source_item.get("message_id") or ""
    ):
        blockers.append(
            _comparison_blocker(
                "overlay_source_index_message_mismatch",
                "overlay/source image index entry targets a different feedback message.",
            )
        )
    if not str(entry.get("source_context_fingerprint") or ""):
        blockers.append(
            _comparison_blocker(
                "overlay_source_index_missing_fingerprint",
                "overlay/source image index entry must include the current source-context fingerprint.",
            )
        )
    elif str(entry.get("source_context_fingerprint") or "") != str(
        source_context.get("fingerprint") or ""
    ):
        blockers.append(
            _comparison_blocker(
                "overlay_source_index_fingerprint_mismatch",
                "overlay/source image index entry is stale for the current source context.",
            )
        )
    return blockers


def overlay_index_source_images(
    *,
    source_item: dict[str, Any],
    source_context: dict[str, Any],
    source_index_entries: Sequence[dict[str, Any]],
    source_index_path: str,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    source_images: list[dict[str, Any]] = []
    blockers: list[dict[str, str]] = []
    for entry in source_index_entries:
        entry_blockers = _overlay_index_entry_blockers(
            entry=entry,
            source_item=source_item,
            source_context=source_context,
        )
        if entry_blockers:
            blockers.extend(entry_blockers)
            continue
        raw_images = entry.get("source_images")
        if not isinstance(raw_images, list) or not raw_images:
            blockers.append(
                _comparison_blocker(
                    "overlay_source_index_entry_has_no_images",
                    "overlay/source image index entry has no source images.",
                )
            )
            continue
        for raw_image in raw_images:
            if not isinstance(raw_image, dict):
                blockers.append(
                    _comparison_blocker(
                        "overlay_source_index_image_not_object",
                        "overlay/source image index source_images item is not an object.",
                    )
                )
                continue
            source_image, image_blockers = _overlay_index_source_image_candidate(
                raw_image,
                source_index_path=source_index_path,
            )
            source_images.append(source_image)
            blockers.extend(image_blockers)
    return source_images, blockers


def _draft_entry(item: dict[str, Any]) -> dict[str, Any]:
    source_context = item.get("source_context")
    if not isinstance(source_context, dict):
        source_context = {}
    return {
        "feedback_id": _int_value(item.get("feedback_id")),
        "source_session_id": str(item.get("source_session_id") or ""),
        "session_id": str(item.get("session_id") or ""),
        "message_id": str(item.get("message_id") or ""),
        "source_context_fingerprint": str(source_context.get("fingerprint") or ""),
        "notes": "",
        "source_images": [
            {
                "role": "overlay_source",
                "source_image_name": "",
                "resolved_path": "",
                "notes": "human-reviewed local source image path required",
            }
        ],
        "fill_template": (
            "source_images[0].resolved_path=<local image path>; "
            "source_images[0].source_image_name=<optional display name>; "
            "notes=<human review notes>"
        ),
    }


def build_overlay_source_context_index_draft_payload(
    *,
    db_path: Path,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_overlay_hypothesis",
    limit: int = 100,
    readiness_builder: ReadinessBuilder | None = None,
) -> dict[str, Any]:
    actual_readiness_builder = readiness_builder or _default_readiness_builder()
    readiness = actual_readiness_builder(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    items = readiness.get("items")
    if not isinstance(items, list):
        items = []
    filters = readiness.get("filters")
    if not isinstance(filters, dict):
        filters = {}
    return {
        "schema_version": OVERLAY_SOURCE_CONTEXT_INDEX_SCHEMA_VERSION,
        "generated_at": _utc_timestamp(),
        "source_readiness_schema_version": readiness.get("schema_version", ""),
        "filters": {
            "status": filters.get("status") or "open",
            "outcome": filters.get("outcome") or "",
            "cohort": filters.get("cohort") or "",
            "limit": _int_value(filters.get("limit")),
            "packet_basis": "overlay_source_context_index_authoring",
        },
        "authoring_contract": {
            "local_only": True,
            "human_review_required": True,
            "requires_local_source_image_paths": True,
            "source_context_fingerprint_required": True,
            "execution": "none",
            "mutation": "none",
            "validation_command": (
                "make manual-evals-overlay-source-index-validate "
                "COHORT=ocr_overlay_hypothesis OUTCOME=fail"
            ),
        },
        "entries": [_draft_entry(item) for item in items if isinstance(item, dict)],
    }


def write_overlay_source_context_index_draft(
    *,
    db_path: Path,
    output_path: Path | None = None,
    force: bool = False,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_overlay_hypothesis",
    limit: int = 100,
    readiness_builder: ReadinessBuilder | None = None,
) -> dict[str, Any]:
    resolved_path = (
        output_path or DEFAULT_OVERLAY_SOURCE_CONTEXT_INDEX_PATH
    ).expanduser()
    payload = build_overlay_source_context_index_draft_payload(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        readiness_builder=readiness_builder,
    )
    entries = payload.get("entries")
    if not isinstance(entries, list):
        entries = []
    existed_before = resolved_path.exists()
    if existed_before and not force:
        return {
            "schema_version": OVERLAY_SOURCE_CONTEXT_INDEX_DRAFT_SCHEMA_VERSION,
            "state": "blocked",
            "manual_evals_db": {
                "path": str(db_path),
                "exists": db_path.is_file(),
            },
            "output": {
                "path": str(resolved_path),
                "exists": True,
                "written": False,
                "force": False,
                "overwritten": False,
                "local_only": True,
            },
            "counts": {
                "draft_entries": len(entries),
                "source_image_placeholders": sum(
                    len(entry.get("source_images", []))
                    for entry in entries
                    if isinstance(entry, dict)
                    and isinstance(entry.get("source_images"), list)
                ),
            },
            "payload": payload,
            "blockers": [
                _source_index_blocker(
                    "overlay_source_index_draft_exists",
                    "overlay/source image context index already exists; pass FORCE=1 to overwrite.",
                )
            ],
            "warnings": [
                "overlay/source image context index already exists; pass FORCE=1 to overwrite."
            ],
        }
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "schema_version": OVERLAY_SOURCE_CONTEXT_INDEX_DRAFT_SCHEMA_VERSION,
        "state": "written",
        "manual_evals_db": {
            "path": str(db_path),
            "exists": db_path.is_file(),
        },
        "output": {
            "path": str(resolved_path),
            "exists": True,
            "written": True,
            "force": bool(force),
            "overwritten": bool(existed_before),
            "local_only": True,
        },
        "counts": {
            "draft_entries": len(entries),
            "source_image_placeholders": sum(
                len(entry.get("source_images", []))
                for entry in entries
                if isinstance(entry, dict)
                and isinstance(entry.get("source_images"), list)
            ),
        },
        "payload": payload,
        "blockers": [],
        "warnings": [],
    }


def build_overlay_source_context_index_validation_report(
    *,
    db_path: Path,
    overlay_source_index_path: Path | None = None,
    outcome: str | None = "fail",
    cohort: str | None = "ocr_overlay_hypothesis",
    limit: int = 100,
    readiness_builder: ReadinessBuilder | None = None,
) -> dict[str, Any]:
    resolved_path = (
        overlay_source_index_path or DEFAULT_OVERLAY_SOURCE_CONTEXT_INDEX_PATH
    ).expanduser()
    actual_readiness_builder = readiness_builder or _default_readiness_builder()
    readiness = actual_readiness_builder(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        overlay_source_index_path=resolved_path,
    )
    source_index = readiness.get("source_index")
    if not isinstance(source_index, dict):
        source_index = {}
    counts = readiness.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    readiness_state = str(readiness.get("state") or "unknown")
    state = "ready" if readiness_state == "ready" else "blocked"
    if readiness_state == "error":
        state = "error"
    return {
        "schema_version": OVERLAY_SOURCE_CONTEXT_INDEX_VALIDATION_SCHEMA_VERSION,
        "readiness_schema_version": readiness.get("schema_version", ""),
        "state": state,
        "source_index": source_index,
        "manual_evals_db": readiness.get("manual_evals_db", {}),
        "filters": readiness.get("filters", {}),
        "counts": {
            "returned_rows": _int_value(counts.get("returned_rows")),
            "ready_items": _int_value(counts.get("ready_items")),
            "blocked_items": _int_value(counts.get("blocked_items")),
            "source_images": _int_value(counts.get("source_images")),
            "indexed_source_images": _int_value(counts.get("indexed_source_images")),
            "source_index_entries": _int_value(counts.get("source_index_entries")),
            "blockers": _int_value(counts.get("blockers")),
        },
        "validation_contract": {
            "local_only": True,
            "human_review_required": True,
            "requires_local_source_image_paths": True,
            "source_context_fingerprint_required": True,
            "execution": "none",
            "mutation": "none",
        },
        "mutation_boundary": readiness.get("mutation_boundary", {}),
        "items": readiness.get("items", []),
        "blockers": readiness.get("blockers", []),
        "warnings": readiness.get("warnings", []),
        "path": str(resolved_path),
    }


def format_overlay_source_context_index_draft_report(report: dict[str, Any]) -> str:
    output = report.get("output")
    if not isinstance(output, dict):
        output = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    payload = report.get("payload")
    if not isinstance(payload, dict):
        payload = {}
    filters = payload.get("filters")
    if not isinstance(filters, dict):
        filters = {}
    lines = [
        "manual eval overlay source index draft: "
        f"state={report.get('state') or 'unknown'} "
        f"entries={_int_value(counts.get('draft_entries'))} "
        f"placeholders={_int_value(counts.get('source_image_placeholders'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"force={'yes' if output.get('force') else 'no'} "
        f"overwritten={'yes' if output.get('overwritten') else 'no'} "
        f"local_only={'yes' if output.get('local_only') else 'no'} "
        f"output={output.get('path') or 'none'}",
        "next_validate=make manual-evals-overlay-source-index-validate "
        "COHORT=ocr_overlay_hypothesis OUTCOME=fail",
    ]
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
    return "\n".join(lines)


def format_overlay_source_context_index_validation_report(
    report: dict[str, Any],
) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    source_index = report.get("source_index")
    if not isinstance(source_index, dict):
        source_index = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    lines = [
        "manual eval overlay source index validation: "
        f"state={report.get('state') or 'unknown'} "
        f"rows={_int_value(counts.get('returned_rows'))} "
        f"ready={_int_value(counts.get('ready_items'))} "
        f"blocked={_int_value(counts.get('blocked_items'))} "
        f"source_images={_int_value(counts.get('source_images'))} "
        f"indexed_source_images={_int_value(counts.get('indexed_source_images'))} "
        f"source_index={source_index.get('state') or 'missing'} "
        f"index_entries={_int_value(source_index.get('entries'))} "
        f"blockers={_int_value(counts.get('blockers'))} "
        f"warehouse_mutation={mutation.get('manual_evals_db') or 'unknown'} "
        f"execution={mutation.get('ocr_execution') or 'unknown'} "
        f"path={report.get('path') or 'none'}",
    ]
    items = report.get("items")
    if not isinstance(items, list) or not items:
        lines.append("items: none")
    else:
        for item in items:
            if not isinstance(item, dict):
                continue
            source_context = item.get("source_context")
            if not isinstance(source_context, dict):
                source_context = {}
            readiness = item.get("readiness")
            if not isinstance(readiness, dict):
                readiness = {}
            lines.append(
                "- "
                f"feedback={_int_value(item.get('feedback_id'))} "
                f"state={item.get('state') or 'unknown'} "
                f"fingerprint={source_context.get('fingerprint') or 'none'} "
                f"source_images={_int_value(readiness.get('source_image_count'))} "
                "indexed_source_images="
                f"{_int_value(readiness.get('indexed_source_image_count'))}"
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
    return "\n".join(lines)
