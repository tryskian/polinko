from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any
from typing import Mapping
from typing import Sequence

TRACE_SCHEMA_VERSION = "polinko.eval_trace.v1"
DEFAULT_TRACE_JSONL = Path(
    "docs/portfolio/raw_evidence/archive/eval-trace-records/eval_trace_artifacts.jsonl"
)


def build_eval_trace(
    *,
    run_id: str,
    tool_name: str,
    source_artifacts: Mapping[str, Any] | None,
    gate_outcomes: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    model_metadata: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "trace_id": f"trace-{uuid.uuid4().hex[:12]}",
        "trace_type": "eval_run",
        "generated_at": int(time.time()),
        "run_id": run_id,
        "tool_name": tool_name,
        "model_metadata": dict(model_metadata or {}),
        "source_artifacts": dict(source_artifacts or {}),
        "gate_outcomes": [dict(item) for item in gate_outcomes],
        "summary": dict(summary),
        "metadata": dict(metadata or {}),
    }


def append_eval_trace(
    *,
    trace_payload: Mapping[str, Any],
    trace_jsonl_path: Path | str | None = None,
) -> Path:
    target = Path(trace_jsonl_path) if trace_jsonl_path else DEFAULT_TRACE_JSONL
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(trace_payload), ensure_ascii=False) + "\n")
    return target
