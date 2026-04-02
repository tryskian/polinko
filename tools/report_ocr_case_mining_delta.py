"""Generate a before/after delta report for mined OCR transcript episodes."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SIGNAL_STRENGTH_LEVELS = ("high", "medium", "low")
ACTIONABLE_EMIT_STATUSES = (
    "skipped_unstable_source",
    "skipped_insufficient_anchor_terms",
    "skipped_low_confidence",
)
EMIT_STATUS_PRIORITY = {
    "skipped_unstable_source": 0,
    "skipped_insufficient_anchor_terms": 1,
    "skipped_low_confidence": 2,
}
SIGNAL_STRENGTH_PRIORITY = {"high": 0, "medium": 1, "low": 2}


def _load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _empty_payload() -> dict[str, Any]:
    return {"summary": {}, "episodes": []}


def _count_signal_strength(payload: dict[str, Any]) -> dict[str, int]:
    counts = {level: 0 for level in SIGNAL_STRENGTH_LEVELS}
    episodes = payload.get("episodes")
    if not isinstance(episodes, list):
        return counts
    for row in episodes:
        if not isinstance(row, dict):
            continue
        signal_strength = str(row.get("signal_strength", row.get("confidence", ""))).strip().lower()
        if signal_strength in counts:
            counts[signal_strength] += 1
    return counts


def _count_lane_signal_strength(payload: dict[str, Any]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    episodes = payload.get("episodes")
    if not isinstance(episodes, list):
        return counts
    for row in episodes:
        if not isinstance(row, dict):
            continue
        lane = str(row.get("lane", "unknown")).strip() or "unknown"
        signal_strength = str(row.get("signal_strength", row.get("confidence", ""))).strip().lower()
        if signal_strength not in SIGNAL_STRENGTH_LEVELS:
            continue
        bucket = counts.setdefault(lane, {level: 0 for level in SIGNAL_STRENGTH_LEVELS})
        bucket[signal_strength] += 1
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


def _single_line(value: Any, *, max_chars: int = 110) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def _md_cell(value: Any) -> str:
    text = str(value or "")
    return text.replace("|", r"\|").replace("\n", " ")


def _extract_actionable_backlog(payload: dict[str, Any], *, max_items: int) -> list[dict[str, Any]]:
    episodes = payload.get("episodes")
    if not isinstance(episodes, list):
        return []
    rows: list[dict[str, Any]] = []
    for row in episodes:
        if not isinstance(row, dict):
            continue
        emit_status = str(row.get("emit_status", "")).strip()
        if emit_status not in ACTIONABLE_EMIT_STATUSES:
            continue
        if emit_status == "skipped_low_confidence":
            has_ocr_signal = bool(
                row.get("ocr_literal_intent_signal")
                or row.get("ocr_framing_signal")
                or row.get("correction_signal")
                or row.get("correction_overlap_signal")
                or row.get("transcription_phrases")
            )
            if not has_ocr_signal:
                continue
        signal_strength = str(row.get("signal_strength", row.get("confidence", "low"))).strip().lower()
        if signal_strength not in SIGNAL_STRENGTH_LEVELS:
            signal_strength = "low"
        anchor_terms = row.get("anchor_terms")
        anchor_count = len(anchor_terms) if isinstance(anchor_terms, list) else int(row.get("anchor_terms_count", 0) or 0)
        chosen_phrases = row.get("chosen_phrases")
        chosen_preview = ""
        if isinstance(chosen_phrases, list) and chosen_phrases:
            chosen_preview = _single_line(" | ".join(str(item) for item in chosen_phrases[:3]), max_chars=140)
        image_path = str(row.get("image_path", "")).strip()
        source_name = str(row.get("source_name", "")).strip() or Path(image_path).name
        rows.append(
            {
                "emit_status": emit_status,
                "conversation_id": str(row.get("conversation_id", "")).strip(),
                "conversation_title": _single_line(row.get("conversation_title", ""), max_chars=70),
                "lane": str(row.get("lane", "unknown")).strip() or "unknown",
                "signal_strength": signal_strength,
                "anchor_terms_count": anchor_count,
                "source_name": _single_line(source_name, max_chars=70),
                "image_path": image_path,
                "ask_excerpt": _single_line(row.get("ask_text", ""), max_chars=140),
                "chosen_preview": chosen_preview,
            }
        )
    rows.sort(
        key=lambda item: (
            EMIT_STATUS_PRIORITY.get(item["emit_status"], 99),
            SIGNAL_STRENGTH_PRIORITY.get(str(item["signal_strength"]), 99),
            -int(item["anchor_terms_count"]),
            item["lane"],
            item["conversation_title"].lower(),
        )
    )
    return rows[:max_items]


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
    lines.append("## Signal Strength")
    lines.append("")
    lines.append("| signal_strength | before | after | delta |")
    lines.append("|---|---:|---:|---:|")
    for level in SIGNAL_STRENGTH_LEVELS:
        before = int(report["signal_strength"]["before"].get(level, 0))
        after = int(report["signal_strength"]["after"].get(level, 0))
        delta = after - before
        lines.append(f"| {level} | {before} | {after} | {delta:+d} |")
    lines.append("")
    lines.append("## Lane by Signal Strength")
    lines.append("")
    lines.append("| lane | high (before) | high (after) | delta | medium (before) | medium (after) | delta | low (before) | low (after) | delta |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for lane in report["lanes"]:
        before_bucket = report["lane_signal_strength"]["before"].get(lane, {level: 0 for level in SIGNAL_STRENGTH_LEVELS})
        after_bucket = report["lane_signal_strength"]["after"].get(lane, {level: 0 for level in SIGNAL_STRENGTH_LEVELS})
        hb, ha = int(before_bucket["high"]), int(after_bucket["high"])
        mb, ma = int(before_bucket["medium"]), int(after_bucket["medium"])
        lb, la = int(before_bucket["low"]), int(after_bucket["low"])
        lines.append(
            f"| {lane} | {hb} | {ha} | {ha-hb:+d} | {mb} | {ma} | {ma-mb:+d} | {lb} | {la} | {la-lb:+d} |"
        )
    lines.append("")
    backlog_rows = report.get("actionable_backlog")
    if isinstance(backlog_rows, list) and backlog_rows:
        lines.append("## Actionable Skipped Episodes")
        lines.append("")
        lines.append("| rank | status | lane | signal_strength | anchors | source | image_path | ask excerpt | chosen preview |")
        lines.append("|---:|---|---|---|---:|---|---|---|---|")
        for idx, row in enumerate(backlog_rows, start=1):
            lines.append(
                "| "
                + f"{idx} | {_md_cell(row['emit_status'])} | {_md_cell(row['lane'])} | {_md_cell(row['signal_strength'])} | "
                + f"{row['anchor_terms_count']} | {_md_cell(row['source_name'])} | {_md_cell(row['image_path'])} | "
                + f"{_md_cell(row['ask_excerpt'])} | {_md_cell(row['chosen_preview'])} |"
            )
        lines.append("")
    return "\n".join(lines)


def build_delta_report(
    *,
    current_review_path: Path,
    previous_review_path: Path | None,
    output_markdown_path: Path,
    output_json_path: Path,
    max_actionable_items: int = 12,
) -> dict[str, Any]:
    current_payload = _load_payload(current_review_path)
    previous_payload = _empty_payload()
    if previous_review_path is not None and previous_review_path.is_file():
        previous_payload = _load_payload(previous_review_path)

    before_signal_strength = _count_signal_strength(previous_payload)
    after_signal_strength = _count_signal_strength(current_payload)
    before_lane_signal_strength = _count_lane_signal_strength(previous_payload)
    after_lane_signal_strength = _count_lane_signal_strength(current_payload)
    lanes = sorted(set(before_lane_signal_strength.keys()) | set(after_lane_signal_strength.keys()))
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
        "signal_strength": {
            "before": before_signal_strength,
            "after": after_signal_strength,
        },
        "lane_signal_strength": {
            "before": before_lane_signal_strength,
            "after": after_lane_signal_strength,
        },
        "lanes": lanes,
        "actionable_backlog": _extract_actionable_backlog(
            current_payload,
            max_items=max_actionable_items,
        ),
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
    parser.add_argument(
        "--max-actionable-items",
        type=int,
        default=12,
        help="Maximum actionable skipped episodes to include in report.",
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
        max_actionable_items=max(1, int(args.max_actionable_items)),
    )
    before = report["totals"]["before"]
    after = report["totals"]["after"]
    print(f"episodes_before={before['episodes']}")
    print(f"episodes_after={after['episodes']}")
    print(f"emitted_before={before['emitted_cases']}")
    print(f"emitted_after={after['emitted_cases']}")
    print(f"actionable_backlog={len(report.get('actionable_backlog', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
