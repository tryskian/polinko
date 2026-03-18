"""Export local eval traces to OpenAI custom-eval JSONL dataset rows.

This tool is tooling-only and deterministic:
- reads local trace artifacts (`polinko.eval_trace.v1`)
- emits JSONL rows shaped for `data_source_config.type=custom`
- emits an accompanying `item_schema` JSON for eval creation
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Mapping

try:
    from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
except ModuleNotFoundError:
    from eval_trace_artifacts import DEFAULT_TRACE_JSONL

DEFAULT_OUTPUT_JSONL = Path(
    "docs/portfolio/raw_evidence/INBOX/openai_eval_dataset.jsonl"
)
DEFAULT_ITEM_SCHEMA_JSON = Path(
    "docs/portfolio/raw_evidence/INBOX/openai_eval_item_schema.json"
)
DATASET_SCHEMA_VERSION = "polinko.openai_eval_dataset.v1"


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _as_list_dict(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    output: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, Mapping):
            output.append(dict(item))
    return output


def _label_slug(value: str) -> str:
    slug = "".join(ch if ch.isalnum() else "_" for ch in value.strip().lower())
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")


def _gate_metrics(gates: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(gates)
    passed = sum(1 for gate in gates if bool(gate.get("passed", False)))
    failed = total - passed
    pass_rate = (passed / total) if total else 0.0
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(pass_rate, 6),
    }


def _build_output_text(
    *, run_id: str, tool_name: str, overall: str, metrics: Mapping[str, Any]
) -> str:
    return (
        f"run_id={run_id or 'unknown'}; "
        f"tool={tool_name or 'unknown'}; "
        f"overall={overall}; "
        f"passed={int(metrics.get('passed', 0) or 0)}/{int(metrics.get('total', 0) or 0)}; "
        f"failed={int(metrics.get('failed', 0) or 0)}; "
        f"pass_rate={float(metrics.get('pass_rate', 0.0) or 0.0):.6f}"
    )


def build_item_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "item": {
                "type": "object",
                "properties": {
                    "trace_id": {"type": "string"},
                    "run_id": {"type": "string"},
                    "trace_type": {"type": "string"},
                    "tool_name": {"type": "string"},
                    "generated_at": {"type": "integer"},
                    "source_artifacts": {"type": "object"},
                    "model_metadata": {"type": "object"},
                    "summary": {"type": "object"},
                    "metadata": {"type": "object"},
                    "gate_outcomes": {"type": "array", "items": {"type": "object"}},
                },
                "required": [
                    "trace_id",
                    "run_id",
                    "tool_name",
                    "generated_at",
                    "gate_outcomes",
                ],
                "additionalProperties": True,
            },
            "sample": {
                "type": "object",
                "properties": {
                    "output_text": {"type": "string"},
                    "overall": {"type": "string", "enum": ["pass", "fail"]},
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "metrics": {
                        "type": "object",
                        "properties": {
                            "total": {"type": "integer"},
                            "passed": {"type": "integer"},
                            "failed": {"type": "integer"},
                            "pass_rate": {"type": "number"},
                        },
                        "required": ["total", "passed", "failed", "pass_rate"],
                        "additionalProperties": True,
                    },
                    "failed_gate_names": {"type": "array", "items": {"type": "string"}},
                    "passed_gate_names": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["output_text", "overall", "labels", "metrics"],
                "additionalProperties": True,
            },
            "schema_version": {"type": "string"},
        },
        "required": ["item", "sample", "schema_version"],
        "additionalProperties": False,
    }


def map_trace_to_dataset_row(trace: Mapping[str, Any]) -> dict[str, Any]:
    trace_id = _as_str(trace.get("trace_id"))
    run_id = _as_str(trace.get("run_id"))
    trace_type = _as_str(trace.get("trace_type"))
    tool_name = _as_str(trace.get("tool_name"))
    generated_at = int(trace.get("generated_at", 0) or 0)

    gate_outcomes = _as_list_dict(trace.get("gate_outcomes"))
    metrics = _gate_metrics(gate_outcomes)
    overall = "pass" if metrics["failed"] == 0 else "fail"

    passed_gate_names: list[str] = []
    failed_gate_names: list[str] = []
    for gate in gate_outcomes:
        name = _as_str(gate.get("name"))
        if not name:
            continue
        if bool(gate.get("passed", False)):
            passed_gate_names.append(name)
        else:
            failed_gate_names.append(name)

    labels: list[str] = []
    labels.append(f"overall:{overall}")
    if tool_name:
        labels.append(f"tool:{_label_slug(tool_name)}")
    labels.extend(f"gate_fail:{_label_slug(name)}" for name in failed_gate_names)
    labels.extend(f"gate_pass:{_label_slug(name)}" for name in passed_gate_names)

    return {
        "schema_version": DATASET_SCHEMA_VERSION,
        "item": {
            "trace_id": trace_id,
            "run_id": run_id,
            "trace_type": trace_type,
            "tool_name": tool_name,
            "generated_at": generated_at,
            "source_artifacts": _as_dict(trace.get("source_artifacts")),
            "model_metadata": _as_dict(trace.get("model_metadata")),
            "summary": _as_dict(trace.get("summary")),
            "metadata": _as_dict(trace.get("metadata")),
            "gate_outcomes": gate_outcomes,
        },
        "sample": {
            "output_text": _build_output_text(
                run_id=run_id,
                tool_name=tool_name,
                overall=overall,
                metrics=metrics,
            ),
            "overall": overall,
            "labels": labels,
            "metrics": metrics,
            "failed_gate_names": failed_gate_names,
            "passed_gate_names": passed_gate_names,
        },
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parsed = json.loads(line)
        if isinstance(parsed, Mapping):
            rows.append(dict(parsed))
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(value), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _select_unique_traces(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest_by_key: dict[str, dict[str, Any]] = {}
    for row in traces:
        trace_id = _as_str(row.get("trace_id"))
        if not trace_id:
            run_id = _as_str(row.get("run_id"))
            tool_name = _as_str(row.get("tool_name"))
            generated_at = int(row.get("generated_at", 0) or 0)
            trace_id = f"fallback:{run_id}|{tool_name}|{generated_at}"
        latest_by_key[trace_id] = row
    unique = list(latest_by_key.values())
    unique.sort(
        key=lambda row: (
            int(row.get("generated_at", 0) or 0),
            _as_str(row.get("trace_id")),
        )
    )
    return unique


@dataclass(frozen=True)
class ExportResult:
    source_count: int
    selected_count: int
    deduped_count: int
    written_count: int
    source_path: Path
    output_jsonl_path: Path
    item_schema_json_path: Path


def run_export(
    *,
    source_jsonl: Path,
    output_jsonl: Path,
    item_schema_json: Path,
    limit: int | None = None,
    include_tools: set[str] | None = None,
) -> ExportResult:
    source_rows = _read_jsonl(source_jsonl)
    selected = _select_unique_traces(source_rows)

    if include_tools:
        selected = [
            row
            for row in selected
            if _as_str(row.get("tool_name")) in include_tools
        ]

    if limit is not None and limit >= 0:
        selected = selected[-limit:]

    rows = [map_trace_to_dataset_row(row) for row in selected]
    _write_jsonl(output_jsonl, rows)
    _write_json(item_schema_json, build_item_schema())

    return ExportResult(
        source_count=len(source_rows),
        selected_count=len(selected),
        deduped_count=len(_select_unique_traces(source_rows)),
        written_count=len(rows),
        source_path=source_jsonl,
        output_jsonl_path=output_jsonl,
        item_schema_json_path=item_schema_json,
    )


def _parse_include_tools(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export local eval trace artifacts into OpenAI custom-eval JSONL "
            "dataset rows and item_schema JSON."
        )
    )
    parser.add_argument(
        "--source-jsonl",
        default=str(DEFAULT_TRACE_JSONL),
        help="Eval trace JSONL source path.",
    )
    parser.add_argument(
        "--output-jsonl",
        default=str(DEFAULT_OUTPUT_JSONL),
        help="Output JSONL path for exported dataset rows.",
    )
    parser.add_argument(
        "--item-schema-json",
        default=str(DEFAULT_ITEM_SCHEMA_JSON),
        help="Output JSON path for data_source_config.item_schema.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max number of latest selected rows to export.",
    )
    parser.add_argument(
        "--include-tools",
        default="",
        help="Optional comma-separated tool_name filter.",
    )
    args = parser.parse_args()

    include_tools = _parse_include_tools(args.include_tools)
    result = run_export(
        source_jsonl=Path(args.source_jsonl),
        output_jsonl=Path(args.output_jsonl),
        item_schema_json=Path(args.item_schema_json),
        limit=args.limit,
        include_tools=include_tools or None,
    )
    print("OK")
    print(f"Source rows: {result.source_count}")
    print(f"Selected rows: {result.selected_count}")
    print(f"Unique rows: {result.deduped_count}")
    print(f"Written dataset rows: {result.written_count}")
    print(f"Dataset JSONL: {result.output_jsonl_path}")
    print(f"Item schema JSON: {result.item_schema_json_path}")
    if include_tools:
        print(f"Tool filter: {sorted(include_tools)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
