"""Dry-run bridge from local eval traces to OpenAI-compatible metadata payloads.

This tool is intentionally tooling-only:
- no runtime /chat behavior changes
- no provider upload calls
- deterministic transformation from local JSONL traces
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Mapping

from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL

DEFAULT_BRIDGE_OUTPUT = Path(
    "docs/portfolio/raw_evidence/INBOX/openai_trace_bridge_preview.jsonl"
)


def _parse_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value or "").strip().lower()
    return normalized in {"1", "true", "yes", "y", "on"}


def _stable_id(prefix: str, seed: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _as_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    output: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, Mapping):
            output.append(dict(item))
    return output


def _gate_summary(gate_outcomes: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(gate_outcomes)
    passed = sum(1 for item in gate_outcomes if bool(item.get("passed", False)))
    failed = total - passed
    pass_rate = (passed / total) if total else 0.0
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(pass_rate, 6),
    }


def map_trace_to_openai_preview(source: Mapping[str, Any]) -> dict[str, Any]:
    source_trace_id = str(source.get("trace_id", ""))
    run_id = str(source.get("run_id", ""))
    tool_name = str(source.get("tool_name", ""))
    generated_at = int(source.get("generated_at", 0) or 0)

    gate_outcomes = _as_list(source.get("gate_outcomes"))
    gate_names = [str(item.get("name", "")) for item in gate_outcomes if item.get("name")]
    gate_stats = _gate_summary(gate_outcomes)

    if not source_trace_id:
        source_trace_id = _stable_id(
            "trace",
            f"{run_id}|{tool_name}|{generated_at}|{json.dumps(gate_names, sort_keys=True)}",
        )
    trace_seed = (
        f"{source_trace_id}|{run_id}|{tool_name}|{generated_at}|"
        f"{json.dumps(gate_stats, sort_keys=True)}"
    )

    openai_trace_id = _stable_id("oa_trace", trace_seed)
    openai_eval_id = _stable_id("oa_eval", trace_seed)

    return {
        "schema_version": "polinko.hybrid_openai_trace_bridge.v1",
        "bridge_mode": "dry_run",
        "source_trace_id": source_trace_id,
        "openai_trace": {
            "trace_id": openai_trace_id,
            "group_id": run_id,
            "name": tool_name or "eval_tool",
            "created_at": generated_at,
            "metadata": {
                "run_id": run_id,
                "tool_name": tool_name,
                "model_metadata": _as_dict(source.get("model_metadata")),
                "source_artifacts": _as_dict(source.get("source_artifacts")),
                "summary": _as_dict(source.get("summary")),
                "metadata": _as_dict(source.get("metadata")),
            },
            "gate_outcomes": gate_outcomes,
            "gate_summary": gate_stats,
        },
        "openai_grader_preview": {
            "evaluation_id": openai_eval_id,
            "sample_id": run_id or source_trace_id,
            "task": tool_name or "eval_tool",
            "labels": gate_names,
            "metrics": gate_stats,
            "source_trace_ref": openai_trace_id,
        },
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parsed = json.loads(line)
        if isinstance(parsed, Mapping):
            rows.append(dict(parsed))
    return rows


def _append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


@dataclass(frozen=True)
class BridgeResult:
    enabled: bool
    source_count: int
    written_count: int
    source_path: Path
    output_path: Path


def run_bridge(
    *,
    source_jsonl: Path,
    output_jsonl: Path,
    enabled: bool,
    limit: int | None = None,
) -> BridgeResult:
    source_rows = _read_jsonl(source_jsonl)
    if limit is not None and limit >= 0:
        source_rows = source_rows[-limit:]

    if not enabled:
        return BridgeResult(
            enabled=False,
            source_count=len(source_rows),
            written_count=0,
            source_path=source_jsonl,
            output_path=output_jsonl,
        )

    transformed = [map_trace_to_openai_preview(row) for row in source_rows]
    _append_jsonl(output_jsonl, transformed)
    return BridgeResult(
        enabled=True,
        source_count=len(source_rows),
        written_count=len(transformed),
        source_path=source_jsonl,
        output_path=output_jsonl,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Dry-run bridge from local eval traces to OpenAI-compatible "
            "trace/grader metadata payload shape."
        )
    )
    parser.add_argument(
        "--source-jsonl",
        default=str(DEFAULT_TRACE_JSONL),
        help="Local eval trace JSONL source path.",
    )
    parser.add_argument(
        "--output-jsonl",
        default=str(DEFAULT_BRIDGE_OUTPUT),
        help="Append-only dry-run preview output JSONL path.",
    )
    parser.add_argument(
        "--enabled",
        default=os.getenv("POLINKO_HYBRID_OPENAI_PILOT_ENABLED", "false"),
        help=(
            "Enable dry-run bridge writes (true/false). Defaults to "
            "POLINKO_HYBRID_OPENAI_PILOT_ENABLED."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max number of latest source rows to transform.",
    )
    args = parser.parse_args()

    enabled = _parse_bool(args.enabled)
    result = run_bridge(
        source_jsonl=Path(args.source_jsonl),
        output_jsonl=Path(args.output_jsonl),
        enabled=enabled,
        limit=args.limit,
    )

    if not result.enabled:
        print("SKIPPED")
        print(
            "Hybrid OpenAI pilot bridge disabled "
            "(POLINKO_HYBRID_OPENAI_PILOT_ENABLED=false)."
        )
        print(f"Source rows available: {result.source_count}")
        return 0

    print("OK")
    print(f"Source: {result.source_path}")
    print(f"Output: {result.output_path}")
    print(f"Transformed rows: {result.written_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
