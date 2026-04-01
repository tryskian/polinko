"""Build a reusable fail cohort from OCR growth-lane stability outputs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any


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


def _normalise_reason(raw: str) -> str:
    cleaned = " ".join(str(raw).split()).strip()
    if not cleaned:
        return ""
    if len(cleaned) <= 140:
        return cleaned
    return f"{cleaned[:137]}..."


def build_fail_cohort(
    *,
    stability_payload: dict[str, Any],
    growth_case_map: dict[str, dict[str, Any]],
    metrics_map: dict[str, dict[str, Any]],
    min_runs: int,
    include_unstable: bool,
) -> dict[str, Any]:
    raw_cases = stability_payload.get("cases")
    if not isinstance(raw_cases, list):
        raise RuntimeError("Expected 'cases' list in stability payload")

    selected: list[dict[str, Any]] = []
    lane_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()

    for row in raw_cases:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        if not case_id:
            continue

        observed_runs = int(row.get("observed_runs", 0) or 0)
        pass_runs = int(row.get("pass_runs", 0) or 0)
        fail_runs = int(row.get("fail_runs", 0) or 0)
        decision_stable = bool(row.get("decision_stable", False))
        always_fail = bool(row.get("always_fail", False))

        if observed_runs < min_runs:
            continue
        if pass_runs > 0 or fail_runs <= 0:
            continue
        if include_unstable:
            if not (fail_runs > 0 and pass_runs == 0):
                continue
        else:
            if not (decision_stable and always_fail):
                continue

        growth_case = growth_case_map.get(case_id, {})
        lane = str(growth_case.get("lane", "unknown")).strip() or "unknown"
        source_name = str(growth_case.get("source_name", "")).strip() or case_id
        image_path = str(growth_case.get("image_path", "")).strip()

        metrics = metrics_map.get(case_id, {})
        unresolved_fail_age_hours = metrics.get("unresolved_fail_age_hours")
        age_hours = float(unresolved_fail_age_hours or 0.0)

        sample_reasons_raw = row.get("sample_reasons")
        sample_reasons = (
            [str(item).strip() for item in sample_reasons_raw if str(item).strip()]
            if isinstance(sample_reasons_raw, list)
            else []
        )

        for reason in sample_reasons:
            reason_key = _normalise_reason(reason)
            if reason_key:
                reason_counts[reason_key] += 1

        selected_row = {
            "id": case_id,
            "lane": lane,
            "source_name": source_name,
            "image_path": image_path,
            "observed_runs": observed_runs,
            "pass_runs": pass_runs,
            "fail_runs": fail_runs,
            "error_runs": int(row.get("error_runs", 0) or 0),
            "pass_rate": float(row.get("pass_rate", 0.0) or 0.0),
            "decision_stable": decision_stable,
            "always_fail": always_fail,
            "statuses": row.get("statuses") if isinstance(row.get("statuses"), list) else [],
            "sample_reasons": sample_reasons,
            "text_variant_count": int(row.get("text_variant_count", 0) or 0),
            "char_count_span": int(row.get("char_count_span", 0) or 0),
            "must_contain_any": growth_case.get("must_contain_any", []),
            "must_appear_in_order": growth_case.get("must_appear_in_order", []),
            "unresolved_fail_age_hours": round(age_hours, 3),
        }
        selected.append(selected_row)
        lane_counts[lane] += 1

    selected.sort(
        key=lambda item: (
            item["lane"],
            -float(item.get("unresolved_fail_age_hours", 0.0) or 0.0),
            item["id"],
        )
    )

    summary = {
        "cases_total": len(raw_cases),
        "selected_fail_cases": len(selected),
        "min_runs": min_runs,
        "include_unstable": include_unstable,
        "lane_counts": dict(sorted(lane_counts.items())),
        "top_reasons": [
            {"reason": reason, "count": count}
            for reason, count in reason_counts.most_common(10)
        ],
    }

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": summary,
        "cases": selected,
    }


def _render_markdown(*, report: dict[str, Any], stability_report: Path, growth_cases: Path) -> str:
    summary = report["summary"]
    selected = report["cases"]
    top_reasons = summary.get("top_reasons") if isinstance(summary.get("top_reasons"), list) else []

    lines: list[str] = []
    lines.append("# OCR Growth Fail Cohort")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Stability report: `{stability_report}`")
    lines.append(f"Growth cases: `{growth_cases}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    lines.append(f"| cases_total | {summary['cases_total']} |")
    lines.append(f"| selected_fail_cases | {summary['selected_fail_cases']} |")
    lines.append(f"| min_runs | {summary['min_runs']} |")
    lines.append(f"| include_unstable | {summary['include_unstable']} |")
    lines.append("")

    lane_counts = summary.get("lane_counts")
    if isinstance(lane_counts, dict) and lane_counts:
        lines.append("## Lane Counts")
        lines.append("")
        lines.append("| lane | selected_fail_cases |")
        lines.append("|---|---:|")
        for lane, count in lane_counts.items():
            lines.append(f"| {lane} | {count} |")
        lines.append("")

    if top_reasons:
        lines.append("## Top Failure Reasons")
        lines.append("")
        lines.append("| reason | count |")
        lines.append("|---|---:|")
        for row in top_reasons:
            reason = str(row.get("reason", "")).replace("|", "\\|")
            count = int(row.get("count", 0) or 0)
            lines.append(f"| {reason} | {count} |")
        lines.append("")

    if selected:
        lines.append("## Selected Cases")
        lines.append("")
        lines.append(
            "| case_id | lane | fail_runs | observed_runs | age_hours | source_name | image_path |"
        )
        lines.append("|---|---|---:|---:|---:|---|---|")
        for row in selected:
            case_id = str(row.get("id", ""))
            lane = str(row.get("lane", ""))
            fail_runs = int(row.get("fail_runs", 0) or 0)
            observed = int(row.get("observed_runs", 0) or 0)
            age_hours = float(row.get("unresolved_fail_age_hours", 0.0) or 0.0)
            source_name = str(row.get("source_name", "")).replace("|", "\\|")
            image_path = str(row.get("image_path", "")).replace("|", "\\|")
            lines.append(
                f"| {case_id} | {lane} | {fail_runs} | {observed} | {age_hours:.3f} | "
                f"{source_name} | {image_path} |"
            )
        lines.append("")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a fail cohort from OCR growth-lane stability outputs."
    )
    parser.add_argument(
        "--stability-report",
        default=".local/eval_reports/ocr_growth_stability.json",
        help="Path to OCR growth stability summary JSON.",
    )
    parser.add_argument(
        "--cases",
        default=".local/eval_cases/ocr_transcript_cases_growth.json",
        help="Path to OCR growth cases JSON.",
    )
    parser.add_argument(
        "--metrics",
        default=".local/eval_reports/ocr_growth_metrics.json",
        help="Optional path to OCR growth metrics JSON (for fail-age enrichment).",
    )
    parser.add_argument(
        "--output-json",
        default=".local/eval_cases/ocr_growth_fail_cohort.json",
        help="Output path for fail cohort JSON.",
    )
    parser.add_argument(
        "--output-markdown",
        default=".local/eval_reports/ocr_growth_fail_cohort.md",
        help="Output path for fail cohort markdown report.",
    )
    parser.add_argument(
        "--min-runs",
        type=int,
        default=3,
        help="Minimum observed runs required before selecting a fail case.",
    )
    parser.add_argument(
        "--include-unstable",
        action="store_true",
        help="Include persistent fail cases even when decision_stable is false.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.min_runs < 1:
        print("min-runs must be >= 1")
        return 2

    stability_path = Path(args.stability_report).expanduser()
    cases_path = Path(args.cases).expanduser()
    metrics_path = Path(args.metrics).expanduser()
    output_json = Path(args.output_json).expanduser()
    output_markdown = Path(args.output_markdown).expanduser()

    if not stability_path.is_file():
        print(f"stability report not found: {stability_path}")
        return 2
    if not cases_path.is_file():
        print(f"growth cases not found: {cases_path}")
        return 2

    stability_payload = _load_json_object(stability_path)
    growth_case_map = _load_case_map(cases_path)

    metrics_map: dict[str, dict[str, Any]] = {}
    if metrics_path.is_file():
        metrics_payload = _load_json_object(metrics_path)
        raw_metrics_cases = metrics_payload.get("cases")
        if isinstance(raw_metrics_cases, list):
            for row in raw_metrics_cases:
                if not isinstance(row, dict):
                    continue
                case_id = str(row.get("id", "")).strip()
                if case_id:
                    metrics_map[case_id] = row

    report = build_fail_cohort(
        stability_payload=stability_payload,
        growth_case_map=growth_case_map,
        metrics_map=metrics_map,
        min_runs=int(args.min_runs),
        include_unstable=bool(args.include_unstable),
    )
    report["stability_report"] = str(stability_path)
    report["cases_path"] = str(cases_path)
    report["metrics_path"] = str(metrics_path)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    markdown = _render_markdown(
        report=report,
        stability_report=stability_path,
        growth_cases=cases_path,
    )
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.write_text(markdown, encoding="utf-8")

    summary = report["summary"]
    print("OCR growth fail cohort")
    print(f"  selected_fail_cases: {summary['selected_fail_cases']}")
    print(f"  cases_total: {summary['cases_total']}")
    print(f"  min_runs: {summary['min_runs']}")
    print(f"  include_unstable: {summary['include_unstable']}")
    print(f"  json: {output_json}")
    print(f"  markdown: {output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
