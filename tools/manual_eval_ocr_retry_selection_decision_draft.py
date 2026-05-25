from __future__ import annotations

import hashlib
import json
import shlex
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.manual_eval_ocr_retry_selection_review import (
    OCR_RETRY_SELECTION_ALLOWED_ACTIONS,
)
from tools.manual_eval_ocr_retry_selection_template import (
    build_ocr_retry_selection_template_report,
)
from tools.manual_eval_ocr_retry_selection_validation import (
    OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION,
)


OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_decision_draft.v1"
)
OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION = (
    "polinko.manual_eval_ocr_retry_selection_apply_preview.v1"
)
DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH = Path(
    ".local/manual_eval_decisions/ocr_retry_selection_draft.json"
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


def _json_fingerprint(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()


def _json_safe_copy(payload: object) -> object:
    return json.loads(json.dumps(payload, ensure_ascii=True, sort_keys=True))


def _ocr_retry_selection_draft_template(
    template_report: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    raw_template = template_report.get("selection_template")
    if not isinstance(raw_template, dict):
        raw_template = {}
    template = _json_safe_copy(raw_template)
    if not isinstance(template, dict):
        template = {}
    items = template.get("items")
    if not isinstance(items, list):
        items = []
        template["items"] = items
    for item in items:
        if isinstance(item, dict):
            item["template_item_fingerprint"] = _json_fingerprint(
                {
                    "selection_template_schema_version": template_report.get(
                        "schema_version", ""
                    ),
                    "item": item,
                }
            )
    template_fingerprint = _json_fingerprint(
        {
            "selection_template_schema_version": template_report.get(
                "schema_version", ""
            ),
            "filters": template_report.get("filters", {}),
            "selection_template": template,
        }
    )
    template["template_fingerprint"] = template_fingerprint
    return template, template_fingerprint


def build_ocr_retry_selection_decision_draft_payload(
    *,
    db_path: Path,
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
    template, template_fingerprint = _ocr_retry_selection_draft_template(
        template_report
    )
    template_counts = template_report.get("counts")
    if not isinstance(template_counts, dict):
        template_counts = {}
    template_filters = template_report.get("filters")
    if not isinstance(template_filters, dict):
        template_filters = {}
    draft_items = template.get("items")
    if not isinstance(draft_items, list):
        draft_items = []
    payload: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION,
        "selection_template_schema_version": template_report.get("schema_version", ""),
        "state": template_report.get("state", "unknown"),
        "manual_evals_db": template_report.get("manual_evals_db", {}),
        "filters": {
            "status": template_filters.get("status") or "open",
            "outcome": template_filters.get("outcome") or "",
            "cohort": template_filters.get("cohort") or "",
            "limit": _int_value(template_filters.get("limit")),
            "packet_basis": "selection_template_local_decision_draft",
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
            "shortlist_items": _int_value(template_counts.get("shortlist_items")),
            "draft_items": len(draft_items),
            "candidate_artifacts": _int_value(
                template_counts.get("candidate_artifacts")
            ),
            "collapsed_duplicate_source_artifacts": _int_value(
                template_counts.get("collapsed_duplicate_source_artifacts")
            ),
            "default_undecided_items": _int_value(
                template_counts.get("default_undecided_items")
            ),
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
        "template_fingerprint": template_fingerprint,
        "draft_contract": {
            "mutation": "none",
            "execution": "none",
            "local_only": True,
            "requires_validation": True,
            "next_validation_schema_version": (
                OCR_RETRY_SELECTION_VALIDATION_SCHEMA_VERSION
            ),
            "next_apply_preview_schema_version": (
                OCR_RETRY_SELECTION_APPLY_PREVIEW_SCHEMA_VERSION
            ),
            "allowed_actions": list(OCR_RETRY_SELECTION_ALLOWED_ACTIONS),
        },
        "selection_template": template,
    }
    warnings = template_report.get("warnings")
    if isinstance(warnings, list) and warnings:
        payload["warnings"] = warnings
    return payload


def write_ocr_retry_selection_decision_draft(
    *,
    db_path: Path,
    output_path: Path | None = None,
    force: bool = False,
    outcome: str | None = "partial",
    cohort: str | None = "ocr_retry_evidence",
    limit: int = 100,
    artifact_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    payload = build_ocr_retry_selection_decision_draft_payload(
        db_path=db_path,
        outcome=outcome,
        cohort=cohort,
        limit=limit,
        artifact_ids=artifact_ids,
    )
    resolved_path = (output_path or DEFAULT_OCR_RETRY_SELECTION_DRAFT_PATH).expanduser()
    quoted_output_path = shlex.quote(str(resolved_path))
    counts = payload.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    report: dict[str, Any] = {
        "schema_version": OCR_RETRY_SELECTION_DECISION_DRAFT_SCHEMA_VERSION,
        "selection_template_schema_version": payload.get(
            "selection_template_schema_version", ""
        ),
        "state": "pending",
        "manual_evals_db": payload.get("manual_evals_db", {}),
        "filters": payload.get("filters", {}),
        "counts": counts,
        "template_fingerprint": payload.get("template_fingerprint", ""),
        "output": {
            "path": str(resolved_path),
            "force": force,
            "overwritten": False,
            "local_only": True,
        },
        "next_commands": {
            "validate": (
                "make manual-evals-ocr-retry-selection-validate "
                f"SELECTION_PATH={quoted_output_path}"
            ),
            "apply_preview": (
                "make manual-evals-ocr-retry-selection-apply-preview "
                f"SELECTION_PATH={quoted_output_path}"
            ),
        },
    }
    if resolved_path.exists() and resolved_path.is_dir():
        report["state"] = "blocked"
        report.setdefault("warnings", []).append(
            f"OCR retry selection draft output path is a directory: {resolved_path}"
        )
        return report
    if resolved_path.exists() and not force:
        report["state"] = "blocked"
        report.setdefault("warnings", []).append(
            "OCR retry selection draft already exists; pass --force to overwrite: "
            f"{resolved_path}"
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


def format_ocr_retry_selection_decision_draft_report(report: dict[str, Any]) -> str:
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
        "manual eval OCR retry selection decision draft: "
        f"state={report.get('state', 'unknown')} "
        "rows="
        f"{_int_value(counts.get('returned_feedback_rows'))}/"
        f"{_int_value(counts.get('total_feedback_rows'))} "
        f"items={_int_value(counts.get('draft_items'))} "
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
        f"force={'yes' if output.get('force') else 'no'} "
        f"overwritten={'yes' if output.get('overwritten') else 'no'} "
        f"local_only={'yes' if output.get('local_only') else 'no'} "
        f"outcome={filters.get('outcome') or 'all'} "
        f"cohort={filters.get('cohort') or 'all'} "
        f"limit={_int_value(filters.get('limit'))} "
        f"basis={filters.get('packet_basis') or 'unknown'} "
        f"path={manual_db.get('path', 'unknown')} "
        f"output={output.get('path') or 'none'} "
        f"fingerprint={report.get('template_fingerprint') or 'none'}",
    ]
    validate_command = str(next_commands.get("validate") or "")
    apply_preview_command = str(next_commands.get("apply_preview") or "")
    if validate_command:
        lines.append(f"next_validate={validate_command}")
    if apply_preview_command:
        lines.append(f"next_apply_preview={apply_preview_command}")
    warnings = report.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings:")
        lines.extend(f"- {str(item)}" for item in warnings)
    return "\n".join(lines)
