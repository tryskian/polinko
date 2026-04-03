"""Summarize OCR focus stability failures into operator-readable patterns."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

MISSING_ORDERED_PHRASE_RX = re.compile(
    r"missing ordered phrase: '([^']+)'(?: after offset (\d+))?",
    flags=re.IGNORECASE,
)


def _load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _load_case_map(path: Path) -> dict[str, dict[str, Any]]:
    payload = _load_json_object(path)
    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list):
        raise RuntimeError(f"Expected 'cases' list in: {path}")
    out: dict[str, dict[str, Any]] = {}
    for row in raw_cases:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        if not case_id:
            continue
        out[case_id] = row
    return out


def _extract_missing_ordered_phrase(reason: str) -> tuple[str | None, int | None]:
    match = MISSING_ORDERED_PHRASE_RX.search(reason)
    if not match:
        return (None, None)
    phrase = str(match.group(1)).strip().lower()
    offset_raw = match.group(2)
    offset: int | None = None
    if offset_raw is not None:
        try:
            offset = int(offset_raw)
        except ValueError:
            offset = None
    return (phrase or None, offset)


def _missing_offset_bucket(offset: int | None) -> str:
    if offset is None:
        return "unknown"
    if offset <= 0:
        return "at_start"
    if offset < 200:
        return "mid_sequence"
    return "late_sequence"


def _preview_order(ordered_terms: list[str], *, limit: int = 4) -> str:
    if not ordered_terms:
        return "-"
    clean = [str(term).strip() for term in ordered_terms if str(term).strip()]
    if not clean:
        return "-"
    head = clean[:limit]
    preview = " -> ".join(head)
    if len(clean) > limit:
        preview = f"{preview} (+{len(clean) - limit})"
    return preview


def _sequence_position_bucket(
    *,
    missing_phrase: str | None,
    ordered_terms: list[str],
) -> tuple[str, int | None]:
    if not missing_phrase or not ordered_terms:
        return ("unknown", None)
    lowered = [str(term).strip().lower() for term in ordered_terms if str(term).strip()]
    if not lowered:
        return ("unknown", None)
    try:
        index = lowered.index(missing_phrase.lower())
    except ValueError:
        return ("unknown", None)
    if index == 0:
        return ("head", index)
    if index == len(lowered) - 1:
        return ("tail", index)
    return ("mid", index)


def build_report(
    *,
    stability_payload: dict[str, Any],
    focus_case_map: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    raw_cases = stability_payload.get("cases")
    if not isinstance(raw_cases, list):
        raise RuntimeError("Expected 'cases' list in stability payload.")

    total_cases = len(raw_cases)
    failing_case_rows: list[dict[str, Any]] = []
    lane_total_counts: Counter[str] = Counter()
    lane_fail_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    missing_phrase_counts: Counter[str] = Counter()
    missing_offset_buckets: Counter[str] = Counter()
    missing_sequence_position_buckets: Counter[str] = Counter()
    lane_sequence_position_buckets: dict[str, Counter[str]] = {}

    for row in raw_cases:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        if not case_id:
            continue

        focus_case = focus_case_map.get(case_id, {})
        lane = str(focus_case.get("lane", "unknown")).strip() or "unknown"
        lane_total_counts[lane] += 1

        fail_runs = int(row.get("fail_runs", 0) or 0)
        pass_runs = int(row.get("pass_runs", 0) or 0)
        error_runs = int(row.get("error_runs", 0) or 0)
        sample_reasons = row.get("sample_reasons")
        reasons = (
            [str(item).strip() for item in sample_reasons if str(item).strip()]
            if isinstance(sample_reasons, list)
            else []
        )
        top_missing_phrase = ""
        top_missing_offset: int | None = None
        for reason in reasons:
            reason_counts[reason] += 1
            maybe_phrase, maybe_offset = _extract_missing_ordered_phrase(reason)
            if maybe_phrase:
                missing_phrase_counts[maybe_phrase] += 1
                missing_offset_buckets[_missing_offset_bucket(maybe_offset)] += 1
                if not top_missing_phrase:
                    top_missing_phrase = maybe_phrase
                    top_missing_offset = maybe_offset

        if fail_runs <= 0:
            continue

        lane_fail_counts[lane] += 1
        ordered_terms = (
            [
                str(term).strip()
                for term in focus_case.get("must_appear_in_order", [])
                if str(term).strip()
            ]
            if isinstance(focus_case.get("must_appear_in_order"), list)
            else []
        )
        sequence_bucket, sequence_index = _sequence_position_bucket(
            missing_phrase=top_missing_phrase or None,
            ordered_terms=ordered_terms,
        )
        missing_sequence_position_buckets[sequence_bucket] += 1
        lane_bucket = lane_sequence_position_buckets.setdefault(lane, Counter())
        lane_bucket[sequence_bucket] += 1

        failing_case_rows.append(
            {
                "id": case_id,
                "lane": lane,
                "fail_runs": fail_runs,
                "pass_runs": pass_runs,
                "error_runs": error_runs,
                "pass_rate": float(row.get("pass_rate", 0.0) or 0.0),
                "text_variant_count": int(row.get("text_variant_count", 0) or 0),
                "char_count_span": int(row.get("char_count_span", 0) or 0),
                "focus_source": str(focus_case.get("focus_source", "")).strip() or "unknown",
                "source_name": str(focus_case.get("source_name", "")).strip(),
                "image_path": str(focus_case.get("image_path", "")).strip(),
                "order_preview": _preview_order(ordered_terms),
                "top_reason": reasons[0] if reasons else "",
                "top_missing_phrase": top_missing_phrase,
                "top_missing_offset": top_missing_offset,
                "top_missing_offset_bucket": _missing_offset_bucket(top_missing_offset),
                "top_missing_sequence_position_bucket": sequence_bucket,
                "top_missing_sequence_index": sequence_index,
            }
        )

    failing_case_rows.sort(
        key=lambda item: (
            -int(item.get("fail_runs", 0) or 0),
            -int(item.get("error_runs", 0) or 0),
            str(item.get("id", "")),
        )
    )
    lane_summary: dict[str, dict[str, Any]] = {}
    for lane, total in sorted(lane_total_counts.items()):
        fails = int(lane_fail_counts.get(lane, 0))
        lane_summary[lane] = {
            "total_cases": int(total),
            "failing_cases": fails,
            "fail_case_rate": round((fails / total) if total else 0.0, 4),
        }

    summary = {
        "cases_total": total_cases,
        "failing_cases": len(failing_case_rows),
        "failing_case_rate": round((len(failing_case_rows) / total_cases) if total_cases else 0.0, 4),
        "lane_summary": lane_summary,
        "top_missing_ordered_phrases": [
            {"phrase": phrase, "count": count}
            for phrase, count in missing_phrase_counts.most_common(20)
        ],
        "missing_order_offset_buckets": {
            "at_start": int(missing_offset_buckets.get("at_start", 0)),
            "mid_sequence": int(missing_offset_buckets.get("mid_sequence", 0)),
            "late_sequence": int(missing_offset_buckets.get("late_sequence", 0)),
            "unknown": int(missing_offset_buckets.get("unknown", 0)),
        },
        "missing_order_sequence_position_buckets": {
            "head": int(missing_sequence_position_buckets.get("head", 0)),
            "mid": int(missing_sequence_position_buckets.get("mid", 0)),
            "tail": int(missing_sequence_position_buckets.get("tail", 0)),
            "unknown": int(missing_sequence_position_buckets.get("unknown", 0)),
        },
        "lane_missing_order_sequence_position_buckets": {
            lane: {
                "head": int(bucket.get("head", 0)),
                "mid": int(bucket.get("mid", 0)),
                "tail": int(bucket.get("tail", 0)),
                "unknown": int(bucket.get("unknown", 0)),
            }
            for lane, bucket in sorted(lane_sequence_position_buckets.items())
        },
        "lane_sequence_hotspots": [
            {
                "lane": lane,
                "bucket": bucket_name,
                "count": int(count),
            }
            for lane, bucket_name, count in sorted(
                (
                    (lane, bucket_name, int(bucket.get(bucket_name, 0)))
                    for lane, bucket in lane_sequence_position_buckets.items()
                    for bucket_name in ("head", "mid", "tail", "unknown")
                    if int(bucket.get(bucket_name, 0)) > 0
                ),
                key=lambda item: (-item[2], item[0], item[1]),
            )
        ],
        "top_reasons": [
            {"reason": reason, "count": count}
            for reason, count in reason_counts.most_common(20)
        ],
    }
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": summary,
        "failing_cases": failing_case_rows,
    }


def _render_markdown(*, report: dict[str, Any], stability_report: Path, focus_cases: Path) -> str:
    summary = report["summary"]
    lane_summary = summary.get("lane_summary") if isinstance(summary.get("lane_summary"), dict) else {}
    top_missing = (
        summary.get("top_missing_ordered_phrases")
        if isinstance(summary.get("top_missing_ordered_phrases"), list)
        else []
    )
    top_reasons = summary.get("top_reasons") if isinstance(summary.get("top_reasons"), list) else []
    failing_cases = report.get("failing_cases") if isinstance(report.get("failing_cases"), list) else []

    lines: list[str] = []
    lines.append("# OCR Focus Fail Patterns")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Focus stability report: `{stability_report}`")
    lines.append(f"Focus case map: `{focus_cases}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    lines.append(f"| cases_total | {summary['cases_total']} |")
    lines.append(f"| failing_cases | {summary['failing_cases']} |")
    lines.append(f"| failing_case_rate | {summary['failing_case_rate']:.4f} |")
    lines.append("")

    if lane_summary:
        lines.append("## Lane Failure Rate")
        lines.append("")
        lines.append("| lane | total_cases | failing_cases | fail_case_rate |")
        lines.append("|---|---:|---:|---:|")
        for lane, lane_row in lane_summary.items():
            lines.append(
                f"| {lane} | {int(lane_row.get('total_cases', 0))} | {int(lane_row.get('failing_cases', 0))} | "
                f"{float(lane_row.get('fail_case_rate', 0.0)):.4f} |"
            )
        lines.append("")

    if top_missing:
        lines.append("## Top Missing Ordered Phrases")
        lines.append("")
        lines.append("| phrase | count |")
        lines.append("|---|---:|")
        for row in top_missing:
            phrase = str(row.get("phrase", "")).replace("|", "\\|")
            count = int(row.get("count", 0) or 0)
            lines.append(f"| {phrase} | {count} |")
        lines.append("")

    offset_buckets = (
        summary.get("missing_order_offset_buckets")
        if isinstance(summary.get("missing_order_offset_buckets"), dict)
        else {}
    )
    if offset_buckets:
        lines.append("## Missing Ordered Phrase Offset Buckets")
        lines.append("")
        lines.append("| bucket | count |")
        lines.append("|---|---:|")
        for bucket in ("at_start", "mid_sequence", "late_sequence", "unknown"):
            lines.append(f"| {bucket} | {int(offset_buckets.get(bucket, 0) or 0)} |")
        lines.append("")

    sequence_buckets = (
        summary.get("missing_order_sequence_position_buckets")
        if isinstance(summary.get("missing_order_sequence_position_buckets"), dict)
        else {}
    )
    if sequence_buckets:
        lines.append("## Missing Ordered Phrase Sequence Position Buckets")
        lines.append("")
        lines.append("| bucket | count |")
        lines.append("|---|---:|")
        for bucket in ("head", "mid", "tail", "unknown"):
            lines.append(f"| {bucket} | {int(sequence_buckets.get(bucket, 0) or 0)} |")
        lines.append("")

    lane_sequence_buckets = (
        summary.get("lane_missing_order_sequence_position_buckets")
        if isinstance(summary.get("lane_missing_order_sequence_position_buckets"), dict)
        else {}
    )
    if lane_sequence_buckets:
        lines.append("## Lane Missing Ordered Sequence Position Buckets")
        lines.append("")
        lines.append("| lane | head | mid | tail | unknown |")
        lines.append("|---|---:|---:|---:|---:|")
        for lane, bucket in lane_sequence_buckets.items():
            if not isinstance(bucket, dict):
                continue
            lines.append(
                f"| {str(lane).replace('|', '\\|')} | "
                f"{int(bucket.get('head', 0) or 0)} | "
                f"{int(bucket.get('mid', 0) or 0)} | "
                f"{int(bucket.get('tail', 0) or 0)} | "
                f"{int(bucket.get('unknown', 0) or 0)} |"
            )
        lines.append("")

    lane_hotspots = (
        summary.get("lane_sequence_hotspots")
        if isinstance(summary.get("lane_sequence_hotspots"), list)
        else []
    )
    if lane_hotspots:
        lines.append("## Lane Sequence Hotspots")
        lines.append("")
        lines.append("| lane | bucket | count |")
        lines.append("|---|---|---:|")
        for row in lane_hotspots:
            lane = str(row.get("lane", "")).replace("|", "\\|")
            bucket = str(row.get("bucket", "")).replace("|", "\\|")
            count = int(row.get("count", 0) or 0)
            lines.append(f"| {lane} | {bucket} | {count} |")
        lines.append("")

    if top_reasons:
        lines.append("## Top Fail Reasons")
        lines.append("")
        lines.append("| reason | count |")
        lines.append("|---|---:|")
        for row in top_reasons:
            reason = str(row.get("reason", "")).replace("|", "\\|")
            count = int(row.get("count", 0) or 0)
            lines.append(f"| {reason} | {count} |")
        lines.append("")

    if failing_cases:
        lines.append("## Failing Cases")
        lines.append("")
        lines.append(
            "| case_id | lane | source_name | image_path | fail_runs | pass_runs | pass_rate | order_preview | missing_phrase | missing_offset | missing_offset_bucket | missing_sequence_bucket | missing_sequence_index | top_reason |"
        )
        lines.append("|---|---|---|---|---:|---:|---:|---|---|---:|---|---|---:|---|")
        for row in failing_cases:
            case_id = str(row.get("id", ""))
            lane = str(row.get("lane", ""))
            source_name = str(row.get("source_name", "")).replace("|", "\\|")
            image_path = str(row.get("image_path", "")).replace("|", "\\|")
            fail_runs = int(row.get("fail_runs", 0) or 0)
            pass_runs = int(row.get("pass_runs", 0) or 0)
            pass_rate = float(row.get("pass_rate", 0.0) or 0.0)
            order_preview = str(row.get("order_preview", "-")).replace("|", "\\|")
            missing_phrase = str(row.get("top_missing_phrase", "")).replace("|", "\\|")
            missing_offset = row.get("top_missing_offset")
            missing_offset_value = (
                str(int(missing_offset))
                if isinstance(missing_offset, int)
                else "-"
            )
            missing_offset_bucket = str(row.get("top_missing_offset_bucket", "unknown")).replace("|", "\\|")
            missing_sequence_bucket = str(
                row.get("top_missing_sequence_position_bucket", "unknown")
            ).replace("|", "\\|")
            missing_sequence_index = row.get("top_missing_sequence_index")
            missing_sequence_index_value = (
                str(int(missing_sequence_index))
                if isinstance(missing_sequence_index, int)
                else "-"
            )
            top_reason = str(row.get("top_reason", "")).replace("|", "\\|")
            lines.append(
                f"| {case_id} | {lane} | {source_name} | {image_path} | {fail_runs} | {pass_runs} | {pass_rate:.4f} | "
                f"{order_preview} | {missing_phrase} | {missing_offset_value} | {missing_offset_bucket} | "
                f"{missing_sequence_bucket} | {missing_sequence_index_value} | {top_reason} |"
            )
        lines.append("")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize OCR focus fail patterns.")
    parser.add_argument(
        "--stability-report",
        default=".local/eval_reports/ocr_focus_stability.json",
        help="Path to OCR focus stability JSON report.",
    )
    parser.add_argument(
        "--focus-cases",
        default=".local/eval_cases/ocr_growth_focus_cases.json",
        help="Path to focused OCR case map JSON.",
    )
    parser.add_argument(
        "--output-json",
        default=".local/eval_reports/ocr_focus_fail_patterns.json",
        help="Output path for fail-pattern summary JSON.",
    )
    parser.add_argument(
        "--output-markdown",
        default=".local/eval_reports/ocr_focus_fail_patterns.md",
        help="Output path for fail-pattern summary markdown.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    stability_report = Path(args.stability_report).expanduser()
    focus_cases = Path(args.focus_cases).expanduser()
    output_json = Path(args.output_json).expanduser()
    output_markdown = Path(args.output_markdown).expanduser()

    if not stability_report.is_file():
        print(f"focus stability report not found: {stability_report}")
        return 2
    if not focus_cases.is_file():
        print(f"focus cases file not found: {focus_cases}")
        return 2

    stability_payload = _load_json_object(stability_report)
    focus_case_map = _load_case_map(focus_cases)
    report = build_report(
        stability_payload=stability_payload,
        focus_case_map=focus_case_map,
    )
    report["stability_report"] = str(stability_report)
    report["focus_cases_path"] = str(focus_cases)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    markdown = _render_markdown(
        report=report,
        stability_report=stability_report,
        focus_cases=focus_cases,
    )
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.write_text(markdown, encoding="utf-8")

    summary = report["summary"]
    print("OCR focus fail patterns")
    print(f"  cases_total: {summary['cases_total']}")
    print(f"  failing_cases: {summary['failing_cases']}")
    print(f"  failing_case_rate: {summary['failing_case_rate']:.4f}")
    print(f"  json: {output_json}")
    print(f"  markdown: {output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
