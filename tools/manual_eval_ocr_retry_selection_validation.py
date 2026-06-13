from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_selection_formatters import (
    format_feedback_ids as _format_feedback_ids,
    format_input_blocker_state as _format_input_blocker_state,
    format_terminal_source_path as _format_terminal_source_path,
    int_value as _int_value,
)
from tools.manual_eval_ocr_retry_selection_review import (
    OCR_RETRY_SELECTION_ALLOWED_ACTIONS,
)
from tools.manual_eval_ocr_retry_selection_template import (
    build_ocr_retry_selection_template_report,
)


OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_validation.v1"
)


def _load_ocr_retry_selection_decision_payload(
    selection_path: Path | None,
) -> tuple[object | None, dict[str, Any], list[str]]:
    if selection_path is None:
        return (
            None,
            {
                "state": "missing",
                "path": "",
                "schema_version": "",
            },
            ["no OCR retry selection decision file was provided"],
        )
    resolved_path = selection_path.expanduser()
    source = {
        "state": "loaded",
        "path": str(resolved_path),
        "schema_version": "",
    }
    if not resolved_path.exists():
        source["state"] = "error"
        return (
            None,
            source,
            [f"OCR retry selection decision file was not found: {resolved_path}"],
        )
    if not resolved_path.is_file():
        source["state"] = "error"
        return (
            None,
            source,
            [f"OCR retry selection decision path is not a file: {resolved_path}"],
        )
    try:
        payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        source["state"] = "error"
        return (
            None,
            source,
            [
                "OCR retry selection decision file is not valid JSON: "
                f"line {exc.lineno} column {exc.colno}"
            ],
        )
    if isinstance(payload, dict):
        source["schema_version"] = str(payload.get("schema_version") or "")
    return payload, source, []


def _clean_selected_artifact_ids(value: object) -> list[str]:
    if isinstance(value, str):
        raw_values: Sequence[object] = value.split(",")
    elif isinstance(value, list):
        raw_values = value
    else:
        return []
    selected: list[str] = []
    seen: set[str] = set()
    for raw_value in raw_values:
        artifact_id = str(raw_value).strip()
        if artifact_id and artifact_id not in seen:
            seen.add(artifact_id)
            selected.append(artifact_id)
    return selected


def _selection_decision_items_from_payload(
    payload: object,
) -> tuple[list[dict[str, Any]], list[str]]:
    if payload is None:
        return [], []

    raw_items: list[object]
    if isinstance(payload, list):
        raw_items = payload
    elif isinstance(payload, dict):
        decision_payload = payload.get("decisions")
        if isinstance(decision_payload, list):
            raw_items = decision_payload
        else:
            template = payload.get("selection_template")
            if isinstance(template, dict) and isinstance(template.get("items"), list):
                raw_items = template["items"]
            elif isinstance(payload.get("items"), list):
                raw_items = payload["items"]
            elif payload.get("shortlist_id"):
                raw_items = [payload]
            else:
                return [], [
                    "OCR retry selection decision JSON does not contain a "
                    "`decisions` list or `selection_template.items` list"
                ]
    else:
        return [], ["OCR retry selection decision JSON must be an object or list"]

    extracted_decisions: list[dict[str, Any]] = []
    warnings: list[str] = []
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            warnings.append(f"decision item {index} is not an object")
            continue
        decision_input = raw_item.get("decision_input")
        if isinstance(decision_input, dict):
            source = decision_input
        else:
            source = raw_item
        extracted_decisions.append(
            {
                "index": index,
                "shortlist_id": str(raw_item.get("shortlist_id") or "").strip(),
                "selected_action": str(source.get("selected_action") or "").strip(),
                "selected_artifact_ids": _clean_selected_artifact_ids(
                    source.get("selected_artifact_ids")
                ),
                "rationale": str(source.get("rationale") or "").strip(),
                "notes": str(source.get("notes") or "").strip(),
            }
        )
    return extracted_decisions, warnings


def selection_template_items_by_shortlist_id(
    template_report: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    template = template_report.get("selection_template")
    if not isinstance(template, dict):
        return {}
    items = template.get("items")
    if not isinstance(items, list):
        return {}
    by_shortlist_id: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        shortlist_id = str(item.get("shortlist_id") or "").strip()
        if shortlist_id:
            by_shortlist_id[shortlist_id] = item
    return by_shortlist_id


def _candidate_artifact_ids(item: dict[str, Any]) -> set[str]:
    candidates = item.get("candidate_artifacts")
    if not isinstance(candidates, list):
        return set()
    return {
        str(candidate.get("artifact_id") or "").strip()
        for candidate in candidates
        if isinstance(candidate, dict)
        and str(candidate.get("artifact_id") or "").strip()
    }


def feedback_closure_blocked(item: dict[str, Any]) -> bool:
    closure_state = item.get("feedback_closure_state")
    return isinstance(closure_state, dict) and closure_state.get("state") == "blocked"


def _validate_ocr_retry_selection_decision(
    *,
    item: dict[str, Any],
    decision: dict[str, Any] | None,
    duplicate_count: int,
) -> dict[str, Any]:
    shortlist_id = str(item.get("shortlist_id") or "")
    candidate_ids = _candidate_artifact_ids(item)
    selected_action = ""
    selected_artifact_ids: list[str] = []
    rationale = ""
    notes = ""
    issues: list[str] = []
    if decision is None:
        issues.append("missing_decision")
    else:
        selected_action = str(decision.get("selected_action") or "").strip()
        selected_artifact_ids = _clean_selected_artifact_ids(
            decision.get("selected_artifact_ids")
        )
        rationale = str(decision.get("rationale") or "").strip()
        notes = str(decision.get("notes") or "").strip()
        if duplicate_count:
            issues.append("duplicate_decision")
        if not selected_action or selected_action == "undecided":
            issues.append("pending_selected_action")
        elif selected_action not in OCR_RETRY_SELECTION_ALLOWED_ACTIONS:
            issues.append("invalid_selected_action")
        elif selected_action in {"rerun_input", "curated_case"}:
            if not selected_artifact_ids:
                issues.append("missing_selected_artifact")
        elif selected_action == "context_only" and selected_artifact_ids:
            issues.append("context_only_must_not_select_artifacts")
        missing_artifact_ids = [
            artifact_id
            for artifact_id in selected_artifact_ids
            if artifact_id not in candidate_ids
        ]
        if missing_artifact_ids:
            issues.append("selected_artifact_not_in_shortlist")

    invalid_issue_codes = {
        "duplicate_decision",
        "invalid_selected_action",
        "missing_selected_artifact",
        "context_only_must_not_select_artifacts",
        "selected_artifact_not_in_shortlist",
    }
    pending_issue_codes = {"missing_decision", "pending_selected_action"}
    if any(issue in invalid_issue_codes for issue in issues):
        state = "invalid"
    elif any(issue in pending_issue_codes for issue in issues):
        state = "pending"
    else:
        state = "valid"

    return {
        "shortlist_id": shortlist_id,
        "state": state,
        "issues": issues,
        "selected_action": selected_action or "undecided",
        "allowed_actions": list(OCR_RETRY_SELECTION_ALLOWED_ACTIONS),
        "selected_artifact_ids": selected_artifact_ids,
        "candidate_artifact_ids": sorted(candidate_ids),
        "invalid_selected_artifact_ids": [
            artifact_id
            for artifact_id in selected_artifact_ids
            if artifact_id not in candidate_ids
        ],
        "rationale": rationale,
        "notes": notes,
        "feedback_ids": item.get("feedback_ids")
        if isinstance(item.get("feedback_ids"), list)
        else [],
        "feedback_closure_state": item.get("feedback_closure_state")
        if isinstance(item.get("feedback_closure_state"), dict)
        else {},
        "feedback_closure_blocked": feedback_closure_blocked(item),
        "source_image_name": str(item.get("source_image_name") or ""),
        "resolved_path": str(item.get("resolved_path") or ""),
        "preview_only": True,
    }


def build_ocr_retry_selection_validation_report(
    *,
    db_path: Path,
    selection_path: Path | None = None,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    template_report = build_ocr_retry_selection_template_report(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    payload, decision_source, decision_warnings = (
        _load_ocr_retry_selection_decision_payload(selection_path)
    )
    submitted_decisions, extraction_warnings = _selection_decision_items_from_payload(
        payload
    )
    template_items = selection_template_items_by_shortlist_id(template_report)
    decisions_by_shortlist_id: dict[str, dict[str, Any]] = {}
    duplicate_counts: dict[str, int] = {}
    stale_decisions: list[dict[str, Any]] = []

    for decision in submitted_decisions:
        shortlist_id = str(decision.get("shortlist_id") or "").strip()
        if not shortlist_id:
            stale_decisions.append(
                {
                    "shortlist_id": "",
                    "state": "invalid",
                    "issues": ["missing_shortlist_id"],
                    "selected_action": decision.get("selected_action") or "undecided",
                    "selected_artifact_ids": decision.get("selected_artifact_ids")
                    if isinstance(decision.get("selected_artifact_ids"), list)
                    else [],
                    "candidate_artifact_ids": [],
                    "invalid_selected_artifact_ids": decision.get(
                        "selected_artifact_ids"
                    )
                    if isinstance(decision.get("selected_artifact_ids"), list)
                    else [],
                    "preview_only": True,
                }
            )
            continue
        if shortlist_id not in template_items:
            stale_decisions.append(
                {
                    "shortlist_id": shortlist_id,
                    "state": "invalid",
                    "issues": ["stale_shortlist_id"],
                    "selected_action": decision.get("selected_action") or "undecided",
                    "selected_artifact_ids": decision.get("selected_artifact_ids")
                    if isinstance(decision.get("selected_artifact_ids"), list)
                    else [],
                    "candidate_artifact_ids": [],
                    "invalid_selected_artifact_ids": decision.get(
                        "selected_artifact_ids"
                    )
                    if isinstance(decision.get("selected_artifact_ids"), list)
                    else [],
                    "preview_only": True,
                }
            )
            continue
        if shortlist_id in decisions_by_shortlist_id:
            duplicate_counts[shortlist_id] = duplicate_counts.get(shortlist_id, 0) + 1
            continue
        decisions_by_shortlist_id[shortlist_id] = decision

    validation_items = [
        _validate_ocr_retry_selection_decision(
            item=item,
            decision=decisions_by_shortlist_id.get(shortlist_id),
            duplicate_count=duplicate_counts.get(shortlist_id, 0),
        )
        for shortlist_id, item in template_items.items()
    ]
    validation_items.extend(stale_decisions)

    invalid_decisions = sum(
        1 for item in validation_items if item.get("state") == "invalid"
    )
    pending_decisions = sum(
        1 for item in validation_items if item.get("state") == "pending"
    )
    valid_decisions = sum(
        1 for item in validation_items if item.get("state") == "valid"
    )
    missing_decisions = sum(
        1
        for item in validation_items
        if isinstance(item.get("issues"), list) and "missing_decision" in item["issues"]
    )
    invalid_selected_artifacts = sum(
        len(item.get("invalid_selected_artifact_ids", []))
        for item in validation_items
        if isinstance(item.get("invalid_selected_artifact_ids"), list)
    )
    selected_artifacts = sum(
        len(item.get("selected_artifact_ids", []))
        for item in validation_items
        if isinstance(item.get("selected_artifact_ids"), list)
    )
    duplicate_decisions = sum(duplicate_counts.values())
    source_state = str(decision_source.get("state") or "unknown")
    if source_state == "error" or invalid_decisions or duplicate_decisions:
        state = "error"
    elif pending_decisions or source_state == "missing":
        state = "attention"
    else:
        state = "ok"

    template_counts = template_report.get("counts")
    if not isinstance(template_counts, dict):
        template_counts = {}
    template_filters = template_report.get("filters")
    if not isinstance(template_filters, dict):
        template_filters = {}

    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION,
        "selection_template_schema_version": template_report.get("schema_version", ""),
        "state": state,
        "manual_evals_db": template_report.get("manual_evals_db", {}),
        "decision_source": decision_source,
        "filters": {
            "status": template_filters.get("status") or "open",
            "outcome": template_filters.get("outcome") or "",
            "cohort": template_filters.get("cohort") or "",
            "limit": _int_value(template_filters.get("limit")),
            "packet_basis": "selection_template_human_decision_validation",
            "selection_mode": template_filters.get("selection_mode") or "",
            "artifact_ids": template_filters.get("artifact_ids")
            if isinstance(template_filters.get("artifact_ids"), list)
            else [],
        },
        "counts": {
            "total_feedback_rows": _int_value(
                template_counts.get("total_feedback_rows")
            ),
            "returned_feedback_rows": _int_value(
                template_counts.get("returned_feedback_rows")
            ),
            "shortlist_items": len(template_items),
            "candidate_artifacts": _int_value(
                template_counts.get("candidate_artifacts")
            ),
            "submitted_decisions": len(submitted_decisions),
            "valid_decisions": valid_decisions,
            "pending_decisions": pending_decisions,
            "invalid_decisions": invalid_decisions,
            "missing_decisions": missing_decisions,
            "stale_decisions": len(stale_decisions),
            "duplicate_decisions": duplicate_decisions,
            "selected_artifacts": selected_artifacts,
            "invalid_selected_artifacts": invalid_selected_artifacts,
            "feedback_closure_blocked_items": _int_value(
                template_counts.get("feedback_closure_blocked_items")
            ),
            "ocr_source_message_ids_present": _int_value(
                template_counts.get("ocr_source_message_ids_present")
            ),
            "ocr_result_message_ids_present": _int_value(
                template_counts.get("ocr_result_message_ids_present")
            ),
            "exact_feedback_result_links": _int_value(
                template_counts.get("exact_feedback_result_links")
            ),
            "requested_artifact_ids": _int_value(
                template_counts.get("requested_artifact_ids")
            ),
            "unmatched_artifact_ids": _int_value(
                template_counts.get("unmatched_artifact_ids")
            ),
            "preview_only": True,
            "limit_applied": bool(template_counts.get("limit_applied")),
        },
        "unmatched_artifact_ids": template_report.get("unmatched_artifact_ids", []),
        "selection_validation_items": validation_items,
    }
    warnings = template_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        report["warnings"] = list(warnings)
    for warning in [*decision_warnings, *extraction_warnings]:
        report.setdefault("warnings", []).append(warning)
    return report


def format_validation_issues(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    return ",".join(str(item) for item in value)


def format_validation_artifact_ids(value: object) -> str:
    if not isinstance(value, list) or not value:
        return "none"
    return ",".join(str(item) for item in value)


def format_ocr_retry_selection_validation_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry selection validation: "
        f"state={report.get('state', 'unknown')} "
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
        f"selected_artifacts={_int_value(counts.get('selected_artifacts'))} "
        "invalid_artifacts="
        f"{_int_value(counts.get('invalid_selected_artifacts'))} "
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

    unmatched_artifact_ids = report.get("unmatched_artifact_ids")
    if isinstance(unmatched_artifact_ids, list) and unmatched_artifact_ids:
        lines.append(
            "unmatched_artifact_ids: "
            + ",".join(str(item) for item in unmatched_artifact_ids)
        )

    validation_items = report.get("selection_validation_items")
    if not isinstance(validation_items, list) or not validation_items:
        lines.append("selection_validation_items: none")
        warnings = report.get("warnings")
        if isinstance(warnings, list) and warnings:
            lines.append("warnings:")
            lines.extend(f"- {str(item)}" for item in warnings)
        return "\n".join(lines)

    for item in validation_items:
        if not isinstance(item, dict):
            continue
        lines.append(
            "- "
            f"shortlist={item.get('shortlist_id') or 'none'} "
            f"state={item.get('state') or 'unknown'} "
            f"action={item.get('selected_action') or 'undecided'} "
            f"issues={format_validation_issues(item.get('issues'))} "
            "feedback="
            f"{_format_feedback_ids(item.get('feedback_ids'))} "
            "closure="
            f"{_format_input_blocker_state(item.get('feedback_closure_state'))} "
            "selected_artifacts="
            f"{format_validation_artifact_ids(item.get('selected_artifact_ids'))} "
            "invalid_artifacts="
            f"{format_validation_artifact_ids(item.get('invalid_selected_artifact_ids'))} "
            "candidate_artifacts="
            f"{format_validation_artifact_ids(item.get('candidate_artifact_ids'))} "
            f"source_image={item.get('source_image_name') or 'none'} "
            f"source_path={_format_terminal_source_path(item.get('resolved_path'))} "
            f"preview_only={'yes' if item.get('preview_only') else 'no'}"
        )
    if counts.get("limit_applied"):
        lines.append("limit_applied: true")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)
