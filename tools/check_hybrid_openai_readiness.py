"""Check readiness for hybrid OpenAI tooling adoption using eval artifacts.

This checker is intentionally non-runtime: it only inspects report artifacts.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.eval_trace_artifacts import DEFAULT_TRACE_JSONL
from tools.eval_trace_artifacts import append_eval_trace
from tools.eval_trace_artifacts import build_eval_trace


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    detail: str


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_report(reports_dir: Path, pattern: str) -> Path:
    matches = sorted(reports_dir.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No reports found for pattern: {pattern}")
    return matches[-1]


def _evaluate_style(report_path: Path) -> GateResult:
    payload = _load_json(report_path)
    summary = payload.get("summary", {})
    total = int(summary.get("total", 0))
    passed = int(summary.get("passed", 0))
    failed = int(summary.get("failed", 0))
    ok = total > 0 and passed == total and failed == 0
    detail = (
        f"{report_path.name}: passed={passed}/{total}, failed={failed}"
        if total > 0
        else f"{report_path.name}: invalid summary payload"
    )
    return GateResult(name="style_strict", passed=ok, detail=detail)


def _evaluate_file_search(report_path: Path) -> GateResult:
    payload = _load_json(report_path)
    summary = payload.get("summary", {})
    total = int(summary.get("total", 0))
    passed = int(summary.get("passed", 0))
    failed = int(summary.get("failed", 0))
    errors = int(summary.get("errors", 0))
    skipped = int(summary.get("skipped", 0))
    ok = total > 0 and passed == total and failed == 0 and errors == 0 and skipped == 0
    detail = (
        f"{report_path.name}: passed={passed}/{total}, failed={failed}, "
        f"errors={errors}, skipped={skipped}"
    )
    return GateResult(name="file_search", passed=ok, detail=detail)


def _evaluate_clip_report(
    report_path: Path,
    min_cases: int,
    min_any_rate: float,
    min_delta: float,
) -> GateResult:
    payload = _load_json(report_path)
    cases_count = int(payload.get("cases_count", 0))
    delta = float(payload.get("any_rate_delta_proxy_minus_baseline", 0.0))

    summary = payload.get("summary", {})
    proxy = summary.get("clip_proxy_image_only", {})
    baseline = summary.get("baseline_mixed", {})

    proxy_any = float(proxy.get("any_rate", 0.0))
    baseline_errors = int(baseline.get("errors", 0))
    baseline_skipped = int(baseline.get("skipped", 0))
    proxy_errors = int(proxy.get("errors", 0))
    proxy_skipped = int(proxy.get("skipped", 0))

    ok = (
        cases_count >= min_cases
        and proxy_any >= min_any_rate
        and delta >= min_delta
        and baseline_errors == 0
        and baseline_skipped == 0
        and proxy_errors == 0
        and proxy_skipped == 0
    )
    detail = (
        f"{report_path.name}: cases={cases_count}, proxy_any_rate={proxy_any:.3f}, "
        f"delta={delta:+.3f}, baseline_errors={baseline_errors}, "
        f"baseline_skipped={baseline_skipped}, proxy_errors={proxy_errors}, "
        f"proxy_skipped={proxy_skipped}"
    )
    return GateResult(name="clip_readiness_report", passed=ok, detail=detail)


def _evaluate_clip_sequence(
    reports_dir: Path,
    required_consecutive: int,
    min_cases: int,
    min_any_rate: float,
    min_delta: float,
) -> GateResult:
    reports = sorted(reports_dir.glob("clip-ab-*.json"))
    if len(reports) < required_consecutive:
        return GateResult(
            name="clip_readiness_sequence",
            passed=False,
            detail=(
                f"Need {required_consecutive} clip-ab reports; found {len(reports)} "
                f"in {reports_dir}"
            ),
        )

    latest = reports[-required_consecutive:]
    checks = [
        _evaluate_clip_report(
            report_path=path,
            min_cases=min_cases,
            min_any_rate=min_any_rate,
            min_delta=min_delta,
        )
        for path in latest
    ]
    failed = [item for item in checks if not item.passed]
    if failed:
        return GateResult(
            name="clip_readiness_sequence",
            passed=False,
            detail="; ".join(item.detail for item in failed),
        )
    return GateResult(
        name="clip_readiness_sequence",
        passed=True,
        detail="; ".join(item.detail for item in checks),
    )


def _run(
    reports_dir: Path,
    required_consecutive: int,
    min_cases: int,
    min_any_rate: float,
    min_delta: float,
) -> tuple[bool, list[GateResult]]:
    style_report = _latest_report(reports_dir, "style-strict-*.json")
    file_search_report = _latest_report(reports_dir, "file-search-*.json")
    gates = [
        _evaluate_style(style_report),
        _evaluate_file_search(file_search_report),
        _evaluate_clip_sequence(
            reports_dir=reports_dir,
            required_consecutive=required_consecutive,
            min_cases=min_cases,
            min_any_rate=min_any_rate,
            min_delta=min_delta,
        ),
    ]
    overall = all(item.passed for item in gates)
    return overall, gates


def _latest_clip_reports(reports_dir: Path, required_consecutive: int) -> list[Path]:
    reports = sorted(reports_dir.glob("clip-ab-*.json"))
    if len(reports) < required_consecutive:
        return []
    return reports[-required_consecutive:]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check report-level readiness for hybrid OpenAI tooling adoption "
            "without changing runtime behavior."
        )
    )
    parser.add_argument(
        "--reports-dir",
        default="eval_reports",
        help="Directory containing eval report artifacts.",
    )
    parser.add_argument(
        "--required-consecutive",
        type=int,
        default=2,
        help="Number of latest clip-ab reports that must pass readiness.",
    )
    parser.add_argument(
        "--min-cases",
        type=int,
        default=4,
        help="Minimum cases_count for each clip-ab report.",
    )
    parser.add_argument(
        "--min-proxy-any-rate",
        type=float,
        default=0.90,
        help="Minimum clip proxy any_rate required per clip-ab report.",
    )
    parser.add_argument(
        "--min-delta",
        type=float,
        default=0.50,
        help="Minimum any_rate delta (proxy - baseline) per clip-ab report.",
    )
    parser.add_argument(
        "--trace-jsonl",
        default=str(DEFAULT_TRACE_JSONL),
        help="Append-only JSONL trace artifact path (set empty string to disable).",
    )
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    if not reports_dir.exists():
        raise SystemExit(f"Reports directory not found: {reports_dir}")

    overall, results = _run(
        reports_dir=reports_dir,
        required_consecutive=args.required_consecutive,
        min_cases=args.min_cases,
        min_any_rate=args.min_proxy_any_rate,
        min_delta=args.min_delta,
    )

    if overall:
        print("READY")
    else:
        print("NOT_READY")
    print(
        "Hybrid adoption gate (reports-only): strict style + file-search + "
        f"{args.required_consecutive}x clip readiness."
    )
    for item in results:
        status = "PASS" if item.passed else "FAIL"
        print(f"- [{status}] {item.name}: {item.detail}")

    trace_jsonl = str(args.trace_jsonl or "").strip()
    if trace_jsonl:
        style_report = _latest_report(reports_dir, "style-strict-*.json")
        file_search_report = _latest_report(reports_dir, "file-search-*.json")
        clip_reports = _latest_clip_reports(reports_dir, args.required_consecutive)
        trace_payload = build_eval_trace(
            run_id=f"hybrid-openai-readiness-{int(Path(style_report).stat().st_mtime)}",
            tool_name="tools/check_hybrid_openai_readiness.py",
            source_artifacts={
                "reports_dir": str(reports_dir),
                "style_report": str(style_report),
                "file_search_report": str(file_search_report),
                "clip_reports": [str(path) for path in clip_reports],
            },
            gate_outcomes=[
                {
                    "name": item.name,
                    "passed": item.passed,
                    "detail": item.detail,
                }
                for item in results
            ],
            summary={
                "overall_ready": overall,
                "required_consecutive": args.required_consecutive,
                "min_cases": args.min_cases,
                "min_proxy_any_rate": args.min_proxy_any_rate,
                "min_delta": args.min_delta,
            },
            metadata={
                "reports_dir": str(reports_dir),
            },
        )
        trace_path = append_eval_trace(
            trace_payload=trace_payload,
            trace_jsonl_path=Path(trace_jsonl),
        )
        print(f"Trace written: {trace_path}")

    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
