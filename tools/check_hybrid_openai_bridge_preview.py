"""Validate Hybrid OpenAI dry-run bridge preview artifact quality.

Tooling-only checker:
- validates JSONL structure and required fields
- enforces minimum row count
- returns non-zero on validation failure
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Mapping


DEFAULT_PREVIEW_JSONL = Path(
    "docs/portfolio/raw_evidence/INBOX/openai_trace_bridge_preview.jsonl"
)


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    row_count: int
    errors: list[str]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Line {line_no}: invalid JSON ({exc.msg})") from exc
        if not isinstance(parsed, Mapping):
            raise ValueError(f"Line {line_no}: row must be JSON object")
        rows.append(dict(parsed))
    return rows


def _require_non_empty_str(value: Any, field: str, row_index: int, errors: list[str]) -> str:
    text = str(value or "").strip()
    if not text:
        errors.append(f"row {row_index}: missing {field}")
    return text


def _require_mapping(
    value: Any, field: str, row_index: int, errors: list[str]
) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"row {row_index}: {field} must be object")
        return {}
    return dict(value)


def _require_list(value: Any, field: str, row_index: int, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"row {row_index}: {field} must be list")
        return []
    return value


def validate_preview(
    *, preview_jsonl: Path, min_rows: int = 1, max_errors: int = 50
) -> CheckResult:
    errors: list[str] = []
    try:
        rows = _read_jsonl(preview_jsonl)
    except ValueError as exc:
        return CheckResult(ok=False, row_count=0, errors=[str(exc)])

    if len(rows) < min_rows:
        errors.append(
            f"preview has {len(rows)} row(s); requires at least {min_rows} row(s)"
        )
        return CheckResult(ok=False, row_count=len(rows), errors=errors)

    for i, row in enumerate(rows, start=1):
        schema = _require_non_empty_str(row.get("schema_version"), "schema_version", i, errors)
        if schema and schema != "polinko.hybrid_openai_trace_bridge.v1":
            errors.append(f"row {i}: unexpected schema_version={schema}")

        mode = _require_non_empty_str(row.get("bridge_mode"), "bridge_mode", i, errors)
        if mode and mode != "dry_run":
            errors.append(f"row {i}: bridge_mode must be dry_run")

        source_trace_id = _require_non_empty_str(
            row.get("source_trace_id"), "source_trace_id", i, errors
        )

        openai_trace = _require_mapping(row.get("openai_trace"), "openai_trace", i, errors)
        openai_grader = _require_mapping(
            row.get("openai_grader_preview"), "openai_grader_preview", i, errors
        )

        trace_id = _require_non_empty_str(
            openai_trace.get("trace_id"), "openai_trace.trace_id", i, errors
        )
        _require_non_empty_str(openai_trace.get("name"), "openai_trace.name", i, errors)
        _require_list(openai_trace.get("gate_outcomes"), "openai_trace.gate_outcomes", i, errors)
        gate_summary = _require_mapping(
            openai_trace.get("gate_summary"), "openai_trace.gate_summary", i, errors
        )

        eval_id = _require_non_empty_str(
            openai_grader.get("evaluation_id"),
            "openai_grader_preview.evaluation_id",
            i,
            errors,
        )
        _require_non_empty_str(
            openai_grader.get("sample_id"), "openai_grader_preview.sample_id", i, errors
        )
        _require_non_empty_str(
            openai_grader.get("task"), "openai_grader_preview.task", i, errors
        )
        _require_list(openai_grader.get("labels"), "openai_grader_preview.labels", i, errors)
        metrics = _require_mapping(openai_grader.get("metrics"), "openai_grader_preview.metrics", i, errors)
        source_trace_ref = _require_non_empty_str(
            openai_grader.get("source_trace_ref"),
            "openai_grader_preview.source_trace_ref",
            i,
            errors,
        )

        if source_trace_id and not source_trace_id.startswith("trace"):
            errors.append(f"row {i}: source_trace_id should start with trace*")
        if trace_id and source_trace_ref and trace_id != source_trace_ref:
            errors.append(f"row {i}: source_trace_ref must match openai_trace.trace_id")
        if eval_id and not eval_id.startswith("oa_eval_"):
            errors.append(f"row {i}: evaluation_id should start with oa_eval_")
        if gate_summary and metrics and gate_summary != metrics:
            errors.append(f"row {i}: gate_summary must match grader metrics")

        for key in ("total", "passed", "failed", "pass_rate"):
            if key not in gate_summary:
                errors.append(f"row {i}: gate_summary missing {key}")
            if key not in metrics:
                errors.append(f"row {i}: metrics missing {key}")

        if len(errors) >= max_errors:
            errors.append(f"stopped after {max_errors} errors")
            break

    return CheckResult(ok=not errors, row_count=len(rows), errors=errors)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Hybrid OpenAI dry-run bridge preview JSONL quality."
    )
    parser.add_argument(
        "--preview-jsonl",
        default=str(DEFAULT_PREVIEW_JSONL),
        help="Bridge preview JSONL path.",
    )
    parser.add_argument(
        "--min-rows",
        type=int,
        default=1,
        help="Minimum required preview rows.",
    )
    args = parser.parse_args()

    result = validate_preview(
        preview_jsonl=Path(args.preview_jsonl),
        min_rows=max(args.min_rows, 0),
    )
    if not result.ok:
        print("NOT_OK")
        print(f"Preview rows: {result.row_count}")
        for err in result.errors:
            print(f"- {err}")
        return 1

    print("OK")
    print(f"Preview rows: {result.row_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
