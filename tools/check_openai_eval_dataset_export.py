"""Validate exported OpenAI custom-eval dataset artifacts."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Mapping

from tools.export_openai_eval_dataset import DATASET_SCHEMA_VERSION
from tools.export_openai_eval_dataset import DEFAULT_ITEM_SCHEMA_JSON
from tools.export_openai_eval_dataset import DEFAULT_OUTPUT_JSONL


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_no}: invalid JSON ({exc.msg})") from exc
        if not isinstance(parsed, Mapping):
            raise ValueError(f"line {line_no}: row must be object")
        rows.append(dict(parsed))
    return rows


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, Mapping):
        raise ValueError("item schema JSON must be an object")
    return dict(parsed)


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


def _require_str(value: Any, field: str, row_index: int, errors: list[str]) -> str:
    text = str(value or "").strip()
    if not text:
        errors.append(f"row {row_index}: {field} must be non-empty string")
    return text


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    row_count: int
    errors: list[str]


def validate_export(
    *, dataset_jsonl: Path, item_schema_json: Path, min_rows: int = 1
) -> CheckResult:
    errors: list[str] = []

    try:
        rows = _read_jsonl(dataset_jsonl)
    except ValueError as exc:
        return CheckResult(ok=False, row_count=0, errors=[str(exc)])

    try:
        item_schema = _read_json(item_schema_json)
    except ValueError as exc:
        return CheckResult(ok=False, row_count=len(rows), errors=[str(exc)])

    if len(rows) < min_rows:
        errors.append(
            f"dataset has {len(rows)} row(s); requires at least {min_rows} row(s)"
        )
        return CheckResult(ok=False, row_count=len(rows), errors=errors)

    required_top = item_schema.get("required")
    if not isinstance(required_top, list) or not {"item", "sample"}.issubset(required_top):
        errors.append("item schema must require top-level item and sample fields")

    for i, row in enumerate(rows, start=1):
        schema_version = _require_str(row.get("schema_version"), "schema_version", i, errors)
        if schema_version and schema_version != DATASET_SCHEMA_VERSION:
            errors.append(f"row {i}: unexpected schema_version={schema_version}")

        item = _require_mapping(row.get("item"), "item", i, errors)
        sample = _require_mapping(row.get("sample"), "sample", i, errors)

        gate_outcomes = _require_list(item.get("gate_outcomes"), "item.gate_outcomes", i, errors)
        _require_str(item.get("trace_id"), "item.trace_id", i, errors)
        _require_str(item.get("run_id"), "item.run_id", i, errors)
        _require_str(item.get("tool_name"), "item.tool_name", i, errors)
        if not isinstance(item.get("generated_at"), int):
            errors.append(f"row {i}: item.generated_at must be integer")

        _require_str(sample.get("output_text"), "sample.output_text", i, errors)
        overall = _require_str(sample.get("overall"), "sample.overall", i, errors)
        if overall and overall not in {"pass", "fail"}:
            errors.append(f"row {i}: sample.overall must be pass or fail")
        _require_list(sample.get("labels"), "sample.labels", i, errors)
        metrics = _require_mapping(sample.get("metrics"), "sample.metrics", i, errors)

        for key in ("total", "passed", "failed"):
            if not isinstance(metrics.get(key), int):
                errors.append(f"row {i}: sample.metrics.{key} must be integer")
        pass_rate = metrics.get("pass_rate")
        if not isinstance(pass_rate, (int, float)):
            errors.append(f"row {i}: sample.metrics.pass_rate must be numeric")

        if isinstance(metrics.get("total"), int):
            if metrics["total"] != len(gate_outcomes):
                errors.append(f"row {i}: sample.metrics.total must equal gate_outcomes length")

    return CheckResult(ok=not errors, row_count=len(rows), errors=errors)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate exported OpenAI custom-eval dataset artifacts."
    )
    parser.add_argument(
        "--dataset-jsonl",
        default=str(DEFAULT_OUTPUT_JSONL),
        help="Exported dataset JSONL path.",
    )
    parser.add_argument(
        "--item-schema-json",
        default=str(DEFAULT_ITEM_SCHEMA_JSON),
        help="Exported item schema JSON path.",
    )
    parser.add_argument(
        "--min-rows",
        type=int,
        default=1,
        help="Minimum required dataset rows.",
    )
    args = parser.parse_args()

    result = validate_export(
        dataset_jsonl=Path(args.dataset_jsonl),
        item_schema_json=Path(args.item_schema_json),
        min_rows=max(args.min_rows, 0),
    )
    if not result.ok:
        print("NOT_OK")
        print(f"Dataset rows: {result.row_count}")
        for error in result.errors:
            print(f"- {error}")
        return 1

    print("OK")
    print(f"Dataset rows: {result.row_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
