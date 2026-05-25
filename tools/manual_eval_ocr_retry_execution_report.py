from __future__ import annotations

from pathlib import Path
from typing import Any


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


def format_ocr_retry_execution_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    output = report.get("output")
    if not isinstance(output, dict):
        output = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}

    lines = [
        "manual eval OCR retry execution: "
        f"state={report.get('state', 'unknown')} "
        f"readiness={report.get('readiness_state', 'unknown')} "
        f"provider={report.get('ocr_provider') or 'unknown'} "
        f"model={report.get('ocr_model') or 'unknown'} "
        f"readiness_items={_int_value(counts.get('readiness_items'))} "
        f"executable={_int_value(counts.get('executable_items'))} "
        f"requests={_int_value(counts.get('requests'))} "
        f"responses={_int_value(counts.get('responses'))} "
        f"succeeded={_int_value(counts.get('succeeded'))} "
        f"failed={_int_value(counts.get('failed'))} "
        f"context_only_skipped={_int_value(counts.get('context_only_skipped'))} "
        f"warehouse_mutation={mutation.get('manual_eval_warehouse') or 'none'} "
        f"output={output.get('run_dir') or 'none'}",
    ]
    stop_reason = str(report.get("stop_reason") or "")
    if stop_reason:
        lines.append(f"stop_reason: {stop_reason}")
    blockers = report.get("execution_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("execution_blockers:")
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


def format_ocr_retry_execution_bundle_report(report: dict[str, Any]) -> str:
    counts = report.get("counts")
    if not isinstance(counts, dict):
        counts = {}
    mutation = report.get("mutation_boundary")
    if not isinstance(mutation, dict):
        mutation = {}
    files_available = _int_value(counts.get("files_available"))
    files_expected = _int_value(counts.get("files_expected"))
    run_dir_name = Path(str(report.get("run_dir") or "none")).name or "none"

    lines = [
        "manual eval OCR retry execution bundle: "
        f"state={report.get('state', 'unknown')} "
        f"run={report.get('run_id') or 'unknown'} "
        f"execution={report.get('execution_state') or 'unknown'} "
        f"readiness={report.get('readiness_state') or 'unknown'} "
        f"provider={report.get('ocr_provider') or 'unknown'} "
        f"model={report.get('ocr_model') or 'unknown'} "
        f"requests={_int_value(counts.get('requests'))} "
        f"responses={_int_value(counts.get('responses'))} "
        f"succeeded={_int_value(counts.get('succeeded'))} "
        f"failed={_int_value(counts.get('failed'))} "
        f"skipped={_int_value(counts.get('skipped_after_stop'))} "
        f"warehouse_mutation={mutation.get('manual_eval_warehouse') or 'none'} "
        f"files={files_available}/{files_expected} "
        f"dir={run_dir_name}",
    ]
    blockers = report.get("inspection_blockers")
    if isinstance(blockers, list) and blockers:
        lines.append("inspection_blockers:")
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
