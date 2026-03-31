"""Generate a before/after delta report for mined OCR transcript episodes."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CONFIDENCE_LEVELS = ("high", "medium", "low")


def _load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _empty_payload() -> dict[str, Any]:
    return {"summary": {}, "episodes": []}


def _count_confidence(payload: dict[str, Any]) -> dict[str, int]:
    counts = {level: 0 for level in CONFIDENCE_LEVELS}
    episodes = payload.get("episodes")
    if not isinstance(episodes, list):
        return counts
    for row in episodes:
        if not isinstance(row, dict):
            continue
        confidence = str(row.get("confidence", "")).strip().lower()
        if confidence in counts:
            counts[confidence] += 1
    return counts


def _count_lane_confidence(payload: dict[str, Any]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    episodes = payload.get("episodes")
    if not isinstance(episodes, list):
        return counts
    for row in episodes:
        if not isinstance(row, dict):
            continue
        lane = str(row.get("lane", "unknown")).strip() or "unknown"
        confidence = str(row.get("confidence", "")).strip().lower()
        if confidence not in CONFIDENCE_LEVELS:
            continue
        bucket = counts.setdefault(lane, {level: 0 for level in CONFIDENCE_LEVELS})
        bucket[confidence] += 1
    return counts


def _summary_metric(payload: dict[str, Any], key: str) -> int:
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        return 0
    return int(summary.get(key, 0) or 0)


def _emit_status_count(payload: dict[str, Any], key: str) -> int:
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        return 0
    emit_status = summary.get("emit_status_counts")
    if not isinstance(emit_status, dict):
        return 0
    return int(emit_status.get(key, 0) or 0)


def _render_markdown(*, report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# OCR Transcript Mining Delta")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    lines.append("| metric | before | after | delta |")
    lines.append("|---|---:|---:|---:|")
    for metric in (
        "episodes",
        "emitted_cases",
        "skipped_low_confidence",
        "skipped_duplicate_image_path",
        "skipped_unstable_source",
    ):
        before = int(report["totals"]["before"].get(metric, 0))
        after = int(report["totals"]["after"].get(metric, 0))
        delta = after - before
        lines.append(f"| {metric} | {before} | {after} | {delta:+d} |")
    lines.append("")
    lines.append("## Confidence")
    lines.append("")
    lines.append("| confidence | before | after | delta |")
    lines.append("|---|---:|---:|---:|")
    for level in CONFIDENCE_LEVELS:
        before = int(report["confidence"]["before"].get(level, 0))
        after = int(report["confidence"]["after"].get(level, 0))
        delta = after - before
        lines.append(f"| {level} | {before} | {after} | {delta:+d} |")
    lines.append("")
    lines.append("## Lane by Confidence")
    lines.append("")
    lines.append("| lane | high (before) | high (after) | delta | medium (before) | medium (after) | delta | low (before) | low (after) | delta |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for lane in report["lanes"]:
        before_bucket = report["lane_confidence"]["before"].get(lane, {level: 0 for level in CONFIDENCE_LEVELS})
        after_bucket = report["lane_confidence"]["after"].get(lane, {level: 0 for level in CONFIDENCE_LEVELS})
        hb, ha = int(before_bucket["high"]), int(after_bucket["high"])
        mb, ma = int(before_bucket["medium"]), int(after_bucket["medium"])
        lb, la = int(before_bucket["low"]), int(after_bucket["low"])
        lines.append(
            f"| {lane} | {hb} | {ha} | {ha-hb:+d} | {mb} | {ma} | {ma-mb:+d} | {lb} | {la} | {la-lb:+d} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_delta_report(
    *,
    current_review_path: Path,
    previous_review_path: Path | None,
    output_markdown_path: Path,
    output_json_path: Path,
) -> dict[str, Any]:
    current_payload = _load_payload(current_review_path)
    previous_payload = _empty_payload()
    if previous_review_path is not None and previous_review_path.is_file():
        previous_payload = _load_payload(previous_review_path)

    before_confidence = _count_confidence(previous_payload)
    after_confidence = _count_confidence(current_payload)
    before_lane_confidence = _count_lane_confidence(previous_payload)
    after_lane_confidence = _count_lane_confidence(current_payload)
    lanes = sorted(set(before_lane_confidence.keys()) | set(after_lane_confidence.keys()))
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    report = {
        "generated_at": generated_at,
        "current_review_path": str(current_review_path),
        "previous_review_path": str(previous_review_path) if previous_review_path else "",
        "totals": {
            "before": {
                "episodes": _summary_metric(previous_payload, "episodes"),
                "emitted_cases": _emit_status_count(previous_payload, "emitted"),
                "skipped_low_confidence": _emit_status_count(previous_payload, "skipped_low_confidence"),
                "skipped_duplicate_image_path": _emit_status_count(previous_payload, "skipped_duplicate_image_path"),
                "skipped_unstable_source": _emit_status_count(previous_payload, "skipped_unstable_source"),
            },
            "after": {
                "episodes": _summary_metric(current_payload, "episodes"),
                "emitted_cases": _emit_status_count(current_payload, "emitted"),
                "skipped_low_confidence": _emit_status_count(current_payload, "skipped_low_confidence"),
                "skipped_duplicate_image_path": _emit_status_count(current_payload, "skipped_duplicate_image_path"),
                "skipped_unstable_source": _emit_status_count(current_payload, "skipped_unstable_source"),
            },
        },
        "confidence": {
            "before": before_confidence,
            "after": after_confidence,
        },
        "lane_confidence": {
            "before": before_lane_confidence,
            "after": after_lane_confidence,
        },
        "lanes": lanes,
    }

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown = _render_markdown(report=report)
    output_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    output_markdown_path.write_text(markdown, encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate OCR transcript miner delta summary for before/after daily review."
    )
    parser.add_argument(
        "--current-review",
        default=".local/eval_cases/ocr_transcript_cases_review.json",
        help="Path to current review JSON.",
    )
    parser.add_argument(
        "--previous-review",
        default=".local/eval_cases/ocr_transcript_cases_review_prev.json",
        help="Path to previous review JSON (optional).",
    )
    parser.add_argument(
        "--output-markdown",
        default=".local/eval_cases/ocr_transcript_cases_delta.md",
        help="Path to output markdown delta report.",
    )
    parser.add_argument(
        "--output-json",
        default=".local/eval_cases/ocr_transcript_cases_delta.json",
        help="Path to output JSON delta report.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    resolved_previous_path = Path(args.previous_review).expanduser().resolve()
    previous_path: Path | None = resolved_previous_path if resolved_previous_path.is_file() else None
    report = build_delta_report(
        current_review_path=Path(args.current_review).expanduser().resolve(),
        previous_review_path=previous_path,
        output_markdown_path=Path(args.output_markdown).expanduser().resolve(),
        output_json_path=Path(args.output_json).expanduser().resolve(),
    )
    before = report["totals"]["before"]
    after = report["totals"]["after"]
    print(f"episodes_before={before['episodes']}")
    print(f"episodes_after={after['episodes']}")
    print(f"emitted_before={before['emitted_cases']}")
    print(f"emitted_after={after['emitted_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
