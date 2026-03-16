"""Backfill eval trace artifacts from UI eval submissions JSONL.

This is tooling-only and safe to re-run:
- reads submission rows from append-only inbox log
- writes trace rows compatible with polinko.eval_trace.v1
- skips submissions already written (idempotent via submission_key)
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Mapping

try:
    from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
    from tools.eval_trace_artifacts import append_eval_trace
    from tools.eval_trace_artifacts import build_eval_trace
except ModuleNotFoundError:
    from eval_trace_artifacts import DEFAULT_TRACE_JSONL
    from eval_trace_artifacts import append_eval_trace
    from eval_trace_artifacts import build_eval_trace

DEFAULT_SUBMISSIONS_JSONL = Path(
    "docs/portfolio/raw_evidence/INBOX/eval_submissions.jsonl"
)


def _parse_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value or "").strip().lower()
    return normalized in {"1", "true", "yes", "y", "on"}


def _stable_id(prefix: str, seed: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _as_str(value: Any) -> str:
    return str(value or "").strip()


def _as_tags(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    tags: list[str] = []
    seen: set[str] = set()
    for item in value:
        tag = _as_str(item)
        if not tag or tag in seen:
            continue
        seen.add(tag)
        tags.append(tag)
    return tags


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


def _submission_key(submission: Mapping[str, Any]) -> str:
    session_id = _as_str(submission.get("session_id"))
    message_id = _as_str(submission.get("message_id"))
    timestamp_ms = int(submission.get("timestamp_ms", 0) or 0)
    return f"{session_id}|{message_id}|{timestamp_ms}"


def _existing_submission_keys(trace_rows: list[dict[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for row in trace_rows:
        metadata = row.get("metadata")
        if not isinstance(metadata, Mapping):
            continue
        submission_key = _as_str(metadata.get("submission_key"))
        if submission_key:
            keys.add(submission_key)
    return keys


def _build_gate_outcomes(submission: Mapping[str, Any]) -> list[dict[str, Any]]:
    outcome = _as_str(submission.get("outcome")).lower()
    positive_tags = _as_tags(submission.get("positive_tags"))
    negative_tags = _as_tags(submission.get("negative_tags"))

    outcomes: list[dict[str, Any]] = [
        {
            "name": "submission_outcome_pass",
            "passed": outcome == "pass",
            "detail": f"outcome={outcome or 'unknown'}",
        }
    ]
    outcomes.extend(
        {
            "name": f"positive_tag:{tag}",
            "passed": True,
            "detail": "human positive tag",
        }
        for tag in positive_tags
    )
    outcomes.extend(
        {
            "name": f"negative_tag:{tag}",
            "passed": False,
            "detail": "human negative tag",
        }
        for tag in negative_tags
    )
    return outcomes


def _build_summary(submission: Mapping[str, Any]) -> dict[str, Any]:
    outcome = _as_str(submission.get("outcome")).lower()
    status = _as_str(submission.get("status")).lower()
    positive_count = len(_as_tags(submission.get("positive_tags")))
    negative_count = len(_as_tags(submission.get("negative_tags")))
    pass_count = positive_count + (1 if outcome == "pass" else 0)
    fail_count = negative_count + (0 if outcome == "pass" else 1)
    return {
        "outcome": outcome,
        "status": status,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "total": pass_count + fail_count,
        "passed": pass_count,
        "failed": fail_count,
    }


@dataclass(frozen=True)
class BackfillResult:
    enabled: bool
    source_count: int
    written_count: int
    skipped_existing: int
    source_path: Path
    trace_path: Path


def run_backfill(
    *,
    submissions_jsonl: Path,
    trace_jsonl: Path,
    enabled: bool,
    limit: int | None = None,
) -> BackfillResult:
    submissions = _read_jsonl(submissions_jsonl)
    submissions.sort(key=lambda item: int(item.get("timestamp_ms", 0) or 0))
    if limit is not None and limit >= 0:
        submissions = submissions[-limit:]

    if not enabled:
        return BackfillResult(
            enabled=False,
            source_count=len(submissions),
            written_count=0,
            skipped_existing=0,
            source_path=submissions_jsonl,
            trace_path=trace_jsonl,
        )

    existing_keys = _existing_submission_keys(_read_jsonl(trace_jsonl))
    written = 0
    skipped = 0

    for submission in submissions:
        submission_key = _submission_key(submission)
        if submission_key in existing_keys:
            skipped += 1
            continue

        timestamp_ms = int(submission.get("timestamp_ms", 0) or 0)
        run_id = _stable_id("eval_submission", submission_key)
        source_artifacts = {
            "submissions_jsonl": str(submissions_jsonl),
            "submission_key": submission_key,
        }
        metadata = {
            "submission_key": submission_key,
            "session_id": _as_str(submission.get("session_id")),
            "message_id": _as_str(submission.get("message_id")),
            "chat_title": _as_str(submission.get("chat_title")),
            "status": _as_str(submission.get("status")).lower(),
            "note": _as_str(submission.get("note")),
            "recommended_action": _as_str(submission.get("recommended_action")),
            "action_taken": _as_str(submission.get("action_taken")),
        }
        trace_payload = build_eval_trace(
            run_id=run_id,
            tool_name="ui/eval_submission",
            source_artifacts=source_artifacts,
            gate_outcomes=_build_gate_outcomes(submission),
            summary=_build_summary(submission),
            metadata=metadata,
        )
        if timestamp_ms > 0:
            trace_payload["generated_at"] = timestamp_ms // 1000
        trace_payload["trace_type"] = "ui_eval_submission"
        trace_payload["trace_id"] = _stable_id("trace", submission_key)

        append_eval_trace(trace_payload=trace_payload, trace_jsonl_path=trace_jsonl)
        existing_keys.add(submission_key)
        written += 1

    return BackfillResult(
        enabled=True,
        source_count=len(submissions),
        written_count=written,
        skipped_existing=skipped,
        source_path=submissions_jsonl,
        trace_path=trace_jsonl,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Backfill eval trace artifacts from UI eval submission logs."
    )
    parser.add_argument(
        "--submissions-jsonl",
        default=str(DEFAULT_SUBMISSIONS_JSONL),
        help="Eval submissions JSONL source path.",
    )
    parser.add_argument(
        "--trace-jsonl",
        default=str(DEFAULT_TRACE_JSONL),
        help="Eval trace JSONL output path.",
    )
    parser.add_argument(
        "--enabled",
        default="true",
        help="Enable writes (true/false).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional max number of latest source rows to process.",
    )
    args = parser.parse_args()

    result = run_backfill(
        submissions_jsonl=Path(args.submissions_jsonl),
        trace_jsonl=Path(args.trace_jsonl),
        enabled=_parse_bool(args.enabled),
        limit=args.limit,
    )
    if not result.enabled:
        print("SKIPPED")
        print("Backfill disabled.")
        print(f"Source rows available: {result.source_count}")
        return 0

    print("OK")
    print(f"Source: {result.source_path}")
    print(f"Trace output: {result.trace_path}")
    print(f"Source rows: {result.source_count}")
    print(f"Written rows: {result.written_count}")
    print(f"Skipped existing: {result.skipped_existing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
