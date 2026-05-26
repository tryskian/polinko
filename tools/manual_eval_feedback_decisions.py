from __future__ import annotations

import json
import shlex
from collections.abc import Callable
from pathlib import Path
from typing import Any


FEEDBACK_DECISION_PREVIEW_SCHEMA_VERSION = (
    "polinko.manual_eval_feedback_decision_preview.v1"
)
FEEDBACK_DECISION_DRAFT_SCHEMA_VERSION = (
    "polinko.manual_eval_feedback_decision_draft.v1"
)
DEFAULT_FEEDBACK_DECISION_PATH = Path(
    ".local/manual_eval_decisions/feedback_decision.json"
)

FEEDBACK_DECISION_ACTION_DESCRIPTIONS = {
    "keep_open": "Keep the feedback row open as active evidence.",
    "reclassify": "Preview moving the row to a different manual-feedback cohort.",
    "close_feedback": "Preview closing the row through a future guarded apply gate.",
}
FEEDBACK_DECISION_ACTIONS = tuple(FEEDBACK_DECISION_ACTION_DESCRIPTIONS)

SourceContextBuilder = Callable[..., dict[str, Any]]
FeedbackActionCohort = Callable[[object], str]
FeedbackStatusIsOpen = Callable[[object], bool]


def _default_source_context_builder() -> SourceContextBuilder:
    from tools.manual_eval_source_context import build_feedback_source_context_report

    return build_feedback_source_context_report


def _default_feedback_action_cohort() -> FeedbackActionCohort:
    from tools.manual_eval_open_feedback import feedback_action_cohort

    return feedback_action_cohort


def _default_feedback_status_is_open() -> FeedbackStatusIsOpen:
    from tools.manual_eval_ocr_retry_feedback_db import feedback_status_is_open

    return feedback_status_is_open


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


def feedback_decision_draft_source_preview(
    source_context: dict[str, Any],
) -> dict[str, Any]:
    messages = source_context.get("messages")
    if not isinstance(messages, list):
        messages = []
    for raw_message in messages:
        if isinstance(raw_message, dict) and raw_message.get("position") == "target":
            return {
                "message_id": str(raw_message.get("message_id") or ""),
                "role": str(raw_message.get("role") or ""),
                "content_preview": str(raw_message.get("content_preview") or ""),
            }
    return {"message_id": "", "role": "", "content_preview": ""}


def _draft_item(source_item: dict[str, Any]) -> dict[str, Any]:
    source_context = source_item.get("source_context")
    if not isinstance(source_context, dict):
        source_context = {}
    action_cohort = source_item.get("action_cohort")
    if not isinstance(action_cohort, dict):
        action_cohort = {}
    messages = source_context.get("messages")
    if not isinstance(messages, list):
        messages = []
    return {
        "feedback_id": _int_value(source_item.get("feedback_id")),
        "selected_action": "undecided",
        "recommended_action": "",
        "closure_note": "",
        "source_context_fingerprint": str(source_context.get("fingerprint") or ""),
        "rationale": "",
        "current": {
            "status": str(source_item.get("status") or ""),
            "outcome": str(source_item.get("outcome") or ""),
            "cohort": str(action_cohort.get("id") or ""),
            "recommended_action": str(source_item.get("recommended_action") or ""),
            "message_id": str(source_item.get("message_id") or ""),
            "title": str(source_item.get("title") or ""),
        },
        "source_context": {
            "state": str(source_context.get("state") or "unknown"),
            "fingerprint": str(source_context.get("fingerprint") or ""),
            "message_count": len(messages),
            "target_message": feedback_decision_draft_source_preview(source_context),
        },
        "fill_template": (
            "selected_action=<keep_open|reclassify|close_feedback> "
            "recommended_action=<required for reclassify> "
            "closure_note=<required for close_feedback> rationale=<text>"
        ),
    }


def build_feedback_decision_draft_payload(
    *,
    db_path: Path,
    outcome: str | None = "fail",
    cohort: str | None = "grounding_source_verification",
    limit: int = 1,
    source_context_builder: SourceContextBuilder | None = None,
) -> dict[str, Any]:
    actual_source_context_builder = (
        source_context_builder or _default_source_context_builder()
    )
    source_context_report = actual_source_context_builder(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    source_items = source_context_report.get("items")
    if not isinstance(source_items, list):
        source_items = []
    draft_items = [_draft_item(item) for item in source_items if isinstance(item, dict)]
    source_counts = source_context_report.get("counts")
    if not isinstance(source_counts, dict):
        source_counts = {}
    source_filters = source_context_report.get("filters")
    if not isinstance(source_filters, dict):
        source_filters = {}
    return {
        "schema_version": FEEDBACK_DECISION_DRAFT_SCHEMA_VERSION,
        "source_context_schema_version": source_context_report.get(
            "schema_version", ""
        ),
        "state": source_context_report.get("state", "unknown"),
        "manual_evals_db": source_context_report.get("manual_evals_db", {}),
        "filters": {
            "status": source_filters.get("status") or "open",
            "outcome": source_filters.get("outcome") or "",
            "cohort": source_filters.get("cohort") or "",
            "limit": _int_value(source_filters.get("limit")),
            "packet_basis": "source_context_local_decision_draft",
        },
        "counts": {
            "total_rows": _int_value(source_counts.get("total_rows")),
            "returned_rows": _int_value(source_counts.get("returned_rows")),
            "draft_decisions": len(draft_items),
            "source_messages_found": _int_value(
                source_counts.get("source_messages_found")
            ),
            "context_messages": _int_value(source_counts.get("context_messages")),
            "blockers": _int_value(source_counts.get("blockers")),
            "limit_applied": bool(source_counts.get("limit_applied")),
            "preview_only": True,
        },
        "allowed_actions": [
            {
                "id": action_id,
                "description": FEEDBACK_DECISION_ACTION_DESCRIPTIONS[action_id],
            }
            for action_id in FEEDBACK_DECISION_ACTIONS
        ],
        "draft_contract": {
            "mutation": "none",
            "execution": "none",
            "local_only": True,
            "requires_preview": True,
            "next_preview_schema_version": FEEDBACK_DECISION_PREVIEW_SCHEMA_VERSION,
            "allowed_actions": list(FEEDBACK_DECISION_ACTIONS),
        },
        "decisions": draft_items,
        "blockers": source_context_report.get("blockers", []),
        "warnings": source_context_report.get("warnings", []),
    }


def write_feedback_decision_draft(
    *,
    db_path: Path,
    output_path: Path | None = None,
    force: bool = False,
    outcome: str | None = "fail",
    cohort: str | None = "grounding_source_verification",
    limit: int = 1,
    source_context_builder: SourceContextBuilder | None = None,
) -> dict[str, Any]:
    payload = build_feedback_decision_draft_payload(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        source_context_builder=source_context_builder,
    )
    resolved_path = (output_path or DEFAULT_FEEDBACK_DECISION_PATH).expanduser()
    quoted_output_path = shlex.quote(str(resolved_path))
    counts = payload.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    report: dict[str, Any] = {
        "schema_version": FEEDBACK_DECISION_DRAFT_SCHEMA_VERSION,
        "source_context_schema_version": payload.get(
            "source_context_schema_version", ""
        ),
        "state": "pending",
        "manual_evals_db": payload.get("manual_evals_db", {}),
        "filters": payload.get("filters", {}),
        "counts": counts,
        "output": {
            "path": str(resolved_path),
            "force": force,
            "overwritten": False,
            "local_only": True,
        },
        "next_commands": {
            "preview": (
                "make manual-evals-feedback-decision-preview "
                f"DECISION_PATH={quoted_output_path}"
            ),
        },
    }
    if resolved_path.exists() and resolved_path.is_dir():
        report["state"] = "blocked"
        report.setdefault("warnings", []).append(
            f"Manual eval feedback decision draft output path is a directory: {resolved_path}"
        )
        return report
    if resolved_path.exists() and not force:
        report["state"] = "blocked"
        report.setdefault("warnings", []).append(
            "Manual eval feedback decision draft already exists; pass --force "
            f"to overwrite: {resolved_path}"
        )
        return report

    existed = resolved_path.exists()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report["state"] = "written"
    output = report["output"]
    if isinstance(output, dict):
        output["overwritten"] = existed
    return report


def _preview_mutation_boundary() -> dict[str, str]:
    return {
        "manual_evals_db": "read_only",
        "source_history_db": "read_only",
        "feedback_status": "unchanged",
        "feedback_recommended_action": "unchanged",
        "feedback_action_taken": "unchanged",
        "ocr_runs": "unchanged",
        "image_assets": "unchanged",
        "eval_rows": "unchanged",
        "pulse": "excluded",
    }


def _preview_blocker(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _load_decision_payload(
    decision_path: Path,
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    resolved_decision_path = decision_path.expanduser()
    if not resolved_decision_path.is_file():
        return None, [
            _preview_blocker(
                "decision_file_not_found",
                f"feedback decision file was not found: {resolved_decision_path}",
            )
        ]
    try:
        payload = json.loads(resolved_decision_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [
            _preview_blocker(
                "decision_file_load_failed",
                f"feedback decision file could not be loaded: {exc}",
            )
        ]
    except json.JSONDecodeError as exc:
        return None, [
            _preview_blocker(
                "decision_file_load_failed",
                "feedback decision file is not valid JSON: "
                f"line {exc.lineno} column {exc.colno}",
            )
        ]
    if not isinstance(payload, dict):
        return None, [
            _preview_blocker(
                "decision_file_not_object",
                "feedback decision file must be a JSON object.",
            )
        ]
    return payload, []


def _decision_inputs(
    payload: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    if payload is None:
        return [], []
    raw_items = payload.get("decisions")
    if not isinstance(raw_items, list):
        return [], [
            _preview_blocker(
                "missing_decisions",
                "feedback decision file must contain a decisions array.",
            )
        ]
    decisions: list[dict[str, Any]] = []
    blockers: list[dict[str, str]] = []
    seen: set[int] = set()
    for index, raw_item in enumerate(raw_items):
        if not isinstance(raw_item, dict):
            blockers.append(
                _preview_blocker(
                    "decision_not_object",
                    f"decision {index} must be a JSON object.",
                )
            )
            continue
        feedback_id = _int_value(raw_item.get("feedback_id"))
        item_blockers: list[dict[str, str]] = []
        if feedback_id <= 0:
            item_blockers.append(
                _preview_blocker(
                    "invalid_feedback_id",
                    f"decision {index} has an invalid feedback_id.",
                )
            )
        elif feedback_id in seen:
            item_blockers.append(
                _preview_blocker(
                    "duplicate_feedback_id",
                    f"feedback {feedback_id} appears more than once.",
                )
            )
        selected_action = _normalize_text(raw_item.get("selected_action"))
        if selected_action not in FEEDBACK_DECISION_ACTIONS:
            item_blockers.append(
                _preview_blocker(
                    "invalid_selected_action",
                    "selected_action must be one of: "
                    + ", ".join(FEEDBACK_DECISION_ACTIONS),
                )
            )
        rationale = _normalize_text(raw_item.get("rationale"))
        if not rationale:
            item_blockers.append(
                _preview_blocker(
                    "missing_rationale",
                    f"feedback {feedback_id or index} needs a human rationale.",
                )
            )
        recommended_action = _normalize_text(
            raw_item.get("recommended_action") or raw_item.get("new_recommended_action")
        )
        if selected_action == "reclassify" and not recommended_action:
            item_blockers.append(
                _preview_blocker(
                    "missing_recommended_action",
                    "reclassify decisions must name recommended_action.",
                )
            )
        closure_note = _normalize_text(raw_item.get("closure_note"))
        if selected_action == "close_feedback" and not closure_note:
            item_blockers.append(
                _preview_blocker(
                    "missing_closure_note",
                    "close_feedback decisions must name closure_note.",
                )
            )
        if feedback_id > 0:
            seen.add(feedback_id)
        decisions.append(
            {
                "feedback_id": feedback_id,
                "selected_action": selected_action,
                "recommended_action": recommended_action,
                "rationale": rationale,
                "closure_note": closure_note,
                "source_context_fingerprint": _normalize_text(
                    raw_item.get("source_context_fingerprint")
                ),
                "blockers": item_blockers,
            }
        )
    return decisions, blockers


def _source_item_cohort_id(row: dict[str, Any]) -> str:
    action_cohort = row.get("action_cohort")
    if not isinstance(action_cohort, dict):
        action_cohort = {}
    return str(action_cohort.get("id") or "")


def _decision_would_apply(
    *,
    decision: dict[str, Any],
    row: dict[str, Any],
    feedback_action_cohort: FeedbackActionCohort,
) -> dict[str, Any]:
    selected_action = str(decision.get("selected_action") or "")
    current_action = str(row.get("recommended_action") or "")
    if selected_action == "keep_open":
        return {
            "selected_action": selected_action,
            "future_gate_required": False,
            "future_gate": "",
            "mutation": "none",
            "status_after": str(row.get("status") or ""),
            "recommended_action_after": current_action,
            "cohort_after": _source_item_cohort_id(row),
        }
    if selected_action == "reclassify":
        new_action = str(decision.get("recommended_action") or "")
        return {
            "selected_action": selected_action,
            "future_gate_required": True,
            "future_gate": "manual-evals-feedback-reclassify-apply",
            "mutation": "feedback_recommended_action_action_taken_updated_at_after_backup",
            "status_after": str(row.get("status") or ""),
            "recommended_action_after": new_action,
            "cohort_after": feedback_action_cohort(new_action),
        }
    if selected_action == "close_feedback":
        return {
            "selected_action": selected_action,
            "future_gate_required": True,
            "future_gate": "future_manual_feedback_closure_apply",
            "mutation": "feedback_status_action_taken_updated_at_after_backup",
            "status_after": "closed",
            "recommended_action_after": current_action,
            "cohort_after": _source_item_cohort_id(row),
        }
    return {
        "selected_action": selected_action,
        "future_gate_required": True,
        "future_gate": "unknown",
        "mutation": "blocked",
        "status_after": str(row.get("status") or ""),
        "recommended_action_after": current_action,
        "cohort_after": _source_item_cohort_id(row),
    }


def _preview_item(
    *,
    decision: dict[str, Any],
    source_item: dict[str, Any] | None,
    feedback_status_is_open: FeedbackStatusIsOpen,
    feedback_action_cohort: FeedbackActionCohort,
) -> dict[str, Any]:
    feedback_id = _int_value(decision.get("feedback_id"))
    blockers = [
        blocker for blocker in decision.get("blockers", []) if isinstance(blocker, dict)
    ]
    if source_item is None:
        blockers.append(
            _preview_blocker(
                "feedback_not_in_source_context_slice",
                f"feedback {feedback_id} is not in the selected source-context slice.",
            )
        )
        return {
            "feedback_id": feedback_id,
            "state": "blocked",
            "selected_action": str(decision.get("selected_action") or ""),
            "action_description": FEEDBACK_DECISION_ACTION_DESCRIPTIONS.get(
                str(decision.get("selected_action") or ""), ""
            ),
            "message_id": "",
            "outcome": "",
            "status": "",
            "current_cohort": "",
            "current_recommended_action": "",
            "source_context_state": "missing",
            "source_context_fingerprint": "",
            "submitted_source_context_fingerprint": str(
                decision.get("source_context_fingerprint") or ""
            ),
            "rationale": str(decision.get("rationale") or ""),
            "would_apply": {"mutation": "blocked"},
            "blockers": blockers,
        }

    source_context = source_item.get("source_context")
    if not isinstance(source_context, dict):
        source_context = {}
    action_cohort = source_item.get("action_cohort")
    if not isinstance(action_cohort, dict):
        action_cohort = {}
    if not feedback_status_is_open(source_item.get("status")):
        blockers.append(
            _preview_blocker(
                "feedback_row_not_open",
                f"feedback {feedback_id} is {source_item.get('status') or 'unknown'}, not open.",
            )
        )
    source_state = str(source_context.get("state") or "unknown")
    if source_state != "found":
        blockers.append(
            _preview_blocker(
                "source_context_not_found",
                f"feedback {feedback_id} source context state is {source_state}.",
            )
        )
    current_fingerprint = str(source_context.get("fingerprint") or "")
    submitted_fingerprint = str(decision.get("source_context_fingerprint") or "")
    if submitted_fingerprint and submitted_fingerprint != current_fingerprint:
        blockers.append(
            _preview_blocker(
                "source_context_fingerprint_mismatch",
                f"feedback {feedback_id} source context fingerprint is stale.",
            )
        )
    current_action = str(source_item.get("recommended_action") or "")
    selected_action = str(decision.get("selected_action") or "")
    if (
        selected_action == "reclassify"
        and str(decision.get("recommended_action") or "") == current_action
    ):
        blockers.append(
            _preview_blocker(
                "recommended_action_unchanged",
                f"feedback {feedback_id} already has the requested recommended_action.",
            )
        )
    item_for_would_apply = dict(source_item)
    item_for_would_apply["action_cohort"] = action_cohort
    return {
        "feedback_id": feedback_id,
        "state": "ready" if not blockers else "blocked",
        "selected_action": selected_action,
        "action_description": FEEDBACK_DECISION_ACTION_DESCRIPTIONS.get(
            selected_action, ""
        ),
        "message_id": str(source_item.get("message_id") or ""),
        "outcome": str(source_item.get("outcome") or ""),
        "status": str(source_item.get("status") or ""),
        "current_cohort": str(action_cohort.get("id") or ""),
        "current_recommended_action": current_action,
        "new_recommended_action": str(decision.get("recommended_action") or ""),
        "source_context_state": source_state,
        "source_context_fingerprint": current_fingerprint,
        "submitted_source_context_fingerprint": submitted_fingerprint,
        "rationale": str(decision.get("rationale") or ""),
        "closure_note": str(decision.get("closure_note") or ""),
        "would_apply": _decision_would_apply(
            decision=decision,
            row=item_for_would_apply,
            feedback_action_cohort=feedback_action_cohort,
        ),
        "blockers": blockers,
    }


def build_feedback_decision_preview_report(
    *,
    db_path: Path,
    decision_path: Path | None = None,
    outcome: str | None = "fail",
    cohort: str | None = "grounding_source_verification",
    limit: int = 1,
    source_context_builder: SourceContextBuilder | None = None,
    feedback_status_is_open: FeedbackStatusIsOpen | None = None,
    feedback_action_cohort: FeedbackActionCohort | None = None,
) -> dict[str, Any]:
    resolved_decision_path = (
        decision_path.expanduser()
        if decision_path is not None
        else DEFAULT_FEEDBACK_DECISION_PATH
    )
    blockers: list[dict[str, str]] = []
    decision_payload, load_blockers = _load_decision_payload(resolved_decision_path)
    blockers.extend(load_blockers)
    decisions, decision_blockers = _decision_inputs(decision_payload)
    blockers.extend(decision_blockers)
    actual_source_context_builder = (
        source_context_builder or _default_source_context_builder()
    )
    actual_feedback_status_is_open = (
        feedback_status_is_open or _default_feedback_status_is_open()
    )
    actual_feedback_action_cohort = (
        feedback_action_cohort or _default_feedback_action_cohort()
    )
    source_context_report = actual_source_context_builder(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
    )
    source_items = source_context_report.get("items")
    if not isinstance(source_items, list):
        source_items = []
    source_items_by_feedback_id = {
        _int_value(item.get("feedback_id")): item
        for item in source_items
        if isinstance(item, dict)
    }
    if source_context_report.get("state") == "error":
        blockers.append(
            _preview_blocker(
                "source_context_report_error",
                "source-context report returned error.",
            )
        )
    items = [
        _preview_item(
            decision=decision,
            source_item=source_items_by_feedback_id.get(
                _int_value(decision.get("feedback_id"))
            ),
            feedback_status_is_open=actual_feedback_status_is_open,
            feedback_action_cohort=actual_feedback_action_cohort,
        )
        for decision in decisions
    ]
    ready_feedback = sum(1 for item in items if item.get("state") == "ready")
    item_blockers = [
        blocker
        for item in items
        if isinstance(item.get("blockers"), list)
        for blocker in item["blockers"]
        if isinstance(blocker, dict)
    ]
    all_blockers = [*blockers, *item_blockers]
    state = "ok" if decisions and not all_blockers else "blocked"
    return {
        "schema_version": FEEDBACK_DECISION_PREVIEW_SCHEMA_VERSION,
        "state": state,
        "mode": "preview",
        "manual_evals_db": source_context_report.get("manual_evals_db", {}),
        "decision": {
            "path": str(resolved_decision_path),
            "exists": resolved_decision_path.is_file(),
        },
        "filters": source_context_report.get("filters", {}),
        "counts": {
            "planned_feedback": len(decisions),
            "ready_feedback": ready_feedback,
            "blocked_feedback": len(items) - ready_feedback,
            "decision_blockers": len(blockers),
            "item_blockers": len(item_blockers),
            "source_context_rows": len(source_items),
        },
        "allowed_actions": [
            {
                "id": action_id,
                "description": FEEDBACK_DECISION_ACTION_DESCRIPTIONS[action_id],
            }
            for action_id in FEEDBACK_DECISION_ACTIONS
        ],
        "source_context_schema_version": source_context_report.get(
            "schema_version", ""
        ),
        "mutation_boundary": _preview_mutation_boundary(),
        "items": items,
        "blockers": all_blockers,
        "warnings": [],
    }


def format_feedback_decision_preview_report(report: dict[str, Any]) -> str:
    decision = report.get("decision")
    if not isinstance(decision, dict):
        decision = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    decision_path = Path(str(decision.get("path") or "")).name
    lines = [
        "manual eval feedback decision preview: "
        f"state={report.get('state') or 'unknown'} "
        f"mode={report.get('mode') or 'unknown'} "
        f"planned={_int_value(counts.get('planned_feedback'))} "
        f"ready={_int_value(counts.get('ready_feedback'))} "
        f"blocked={_int_value(counts.get('blocked_feedback'))} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"warehouse_mutation={mutation.get('manual_evals_db') or 'unknown'} "
        f"decision_path={decision_path or 'none'}",
    ]
    items = report.get("items")
    if not isinstance(items, list) or not items:
        lines.append("items: none")
    else:
        lines.append("feedback_decisions:")
        for item in items:
            if not isinstance(item, dict):
                continue
            would_apply = item.get("would_apply")
            if not isinstance(would_apply, dict):
                would_apply = {}
            lines.append(
                "- "
                f"feedback={_int_value(item.get('feedback_id'))} "
                f"state={item.get('state') or 'unknown'} "
                f"decision={item.get('selected_action') or 'unknown'} "
                f"from={item.get('current_cohort') or 'unknown'} "
                f"to={would_apply.get('cohort_after') or 'unknown'} "
                f"source_state={item.get('source_context_state') or 'unknown'} "
                f"future_gate={would_apply.get('future_gate') or 'none'} "
                f"mutation={would_apply.get('mutation') or 'none'}"
            )
            if item.get("source_context_fingerprint"):
                lines.append(
                    "  "
                    f"source_context_fingerprint={item.get('source_context_fingerprint')}"
                )
            rationale = _display_text(item.get("rationale"))
            lines.append(f"  rationale={rationale}")
            blockers = item.get("blockers")
            if isinstance(blockers, list) and blockers:
                for blocker in blockers:
                    if not isinstance(blocker, dict):
                        continue
                    lines.append(
                        "  blocker="
                        f"{blocker.get('code') or 'unknown'} "
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
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)


def format_feedback_decision_draft_report(report: dict[str, Any]) -> str:
    manual_db = report.get("manual_evals_db")
    if not isinstance(manual_db, dict):
        manual_db = {}
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    filters = report.get("filters")
    if not isinstance(filters, dict):
        filters = {}
    output = report.get("output")
    if not isinstance(output, dict):
        output = {}
    next_commands = report.get("next_commands")
    if not isinstance(next_commands, dict):
        next_commands = {}

    lines = [
        "manual eval feedback decision draft: "
        f"state={report.get('state') or 'unknown'} "
        f"rows={_int_value(counts.get('returned_rows'))}/"
        f"{_int_value(counts.get('total_rows'))} "
        f"decisions={_int_value(counts.get('draft_decisions'))} "
        f"source_messages_found={_int_value(counts.get('source_messages_found'))} "
        f"context_messages={_int_value(counts.get('context_messages'))} "
        f"blockers={_int_value(counts.get('blockers'))} "
        f"preview_only={'yes' if counts.get('preview_only') else 'no'} "
        f"force={'yes' if output.get('force') else 'no'} "
        f"overwritten={'yes' if output.get('overwritten') else 'no'} "
        f"local_only={'yes' if output.get('local_only') else 'no'} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')} "
        f"output={output.get('path') or 'none'}",
    ]
    preview_command = str(next_commands.get("preview") or "")
    if preview_command:
        lines.append(f"next_preview={preview_command}")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)
