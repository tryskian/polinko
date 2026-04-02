"""Rate-limit backoff guard for OCR replay commands."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any


def _parse_generated_at(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    raw = str(value or "").strip()
    if not raw:
        return 0
    if raw.isdigit():
        return int(raw)
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return 0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _has_rate_limit_abort(payload: dict[str, Any]) -> bool:
    summary = payload.get("summary")
    if isinstance(summary, dict):
        abort_runs = summary.get("rate_limit_abort_runs")
        if isinstance(abort_runs, (int, float)) and abort_runs > 0:
            return True
        rate_limited_cases = summary.get("rate_limited_cases")
        if isinstance(rate_limited_cases, (int, float)) and rate_limited_cases > 0:
            return True

    runs = payload.get("runs")
    if not isinstance(runs, list):
        return False
    for row in runs:
        if not isinstance(row, dict):
            continue
        summary = row.get("summary")
        if not isinstance(summary, dict):
            continue
        if bool(summary.get("aborted_due_to_rate_limit", False)):
            return True
    return False


def should_skip(
    *,
    payload: dict[str, Any],
    backoff_seconds: int,
    now_epoch: int,
) -> bool:
    if backoff_seconds <= 0:
        return False
    if not _has_rate_limit_abort(payload):
        return False
    generated_at = _parse_generated_at(payload.get("generated_at"))
    if generated_at <= 0:
        return False
    return (now_epoch - generated_at) < backoff_seconds


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Return 1 when OCR run should be skipped due to rate-limit backoff."
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Path to OCR stability report JSON.",
    )
    parser.add_argument(
        "--backoff-seconds",
        type=int,
        default=900,
        help="Backoff window in seconds.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.backoff_seconds < 0:
        print("0")
        return 0

    report_path = Path(args.report).expanduser()
    if not report_path.is_file():
        print("0")
        return 0
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        print("0")
        return 0
    if not isinstance(payload, dict):
        print("0")
        return 0

    skip = should_skip(
        payload=payload,
        backoff_seconds=int(args.backoff_seconds),
        now_epoch=int(time.time()),
    )
    print("1" if skip else "0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
