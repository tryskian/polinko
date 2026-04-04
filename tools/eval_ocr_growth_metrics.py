"""Compute pass-from-fail growth metrics from OCR eval run history."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from statistics import median
from typing import Any


PASS = "PASS"
FAIL = "FAIL"
ERROR = "ERROR"


@dataclass(frozen=True)
class CaseMetadata:
    case_id: str
    lane: str
    source_name: str
    image_path: str


@dataclass(frozen=True)
class RunReport:
    run_id: str
    timestamp: int
    case_statuses: dict[str, str]


def _normalise_status(raw: Any) -> str:
    status = str(raw or "").strip().upper()
    if status == PASS:
        return PASS
    if status == FAIL:
        return FAIL
    return ERROR


def _format_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 4)


def _canonical_eval_path(raw_path: str, *, cwd: Path) -> str:
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = cwd / candidate
    return str(candidate.resolve())


def _load_cases(path: Path) -> dict[str, CaseMetadata]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list):
        raise RuntimeError(f"Expected 'cases' list in: {path}")

    case_map: dict[str, CaseMetadata] = {}
    for row in raw_cases:
        if not isinstance(row, dict):
            continue
        case_id = str(row.get("id", "")).strip()
        if not case_id:
            continue
        lane = str(row.get("lane", "unknown")).strip() or "unknown"
        source_name = str(row.get("source_name", "")).strip() or case_id
        image_path = str(row.get("image_path", "")).strip()
        case_map[case_id] = CaseMetadata(
            case_id=case_id,
            lane=lane,
            source_name=source_name,
            image_path=image_path,
        )
    return case_map


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _collect_run_reports(
    *,
    runs_dir: Path,
    expected_cases_path: Path,
) -> list[RunReport]:
    cwd = Path.cwd()
    expected_path = str(expected_cases_path.resolve())
    collected: list[tuple[int, str, RunReport]] = []
    for candidate in runs_dir.glob("*.json"):
        payload = _read_json_object(candidate)
        if payload is None:
            continue
        raw_cases_path = str(payload.get("cases_path", "")).strip()
        if not raw_cases_path:
            continue
        report_cases_path = _canonical_eval_path(raw_cases_path, cwd=cwd)
        if report_cases_path != expected_path:
            continue
        run_id = str(payload.get("run_id", candidate.stem)).strip() or candidate.stem
        timestamp = int(payload.get("generated_at", 0) or 0)
        if timestamp <= 0:
            timestamp = int(candidate.stat().st_mtime)
        case_statuses: dict[str, str] = {}
        raw_cases = payload.get("cases")
        if isinstance(raw_cases, list):
            for row in raw_cases:
                if not isinstance(row, dict):
                    continue
                case_id = str(row.get("id", "")).strip()
                if not case_id:
                    continue
                case_statuses[case_id] = _normalise_status(row.get("status"))
        collected.append(
            (
                timestamp,
                candidate.name,
                RunReport(
                    run_id=run_id,
                    timestamp=timestamp,
                    case_statuses=case_statuses,
                ),
            )
        )
    collected.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in collected]


def _run_metrics_for_cases(
    *,
    summaries: list[dict[str, Any]],
    now_epoch: int,
) -> dict[str, Any]:
    total_cases = len(summaries)
    first_decision_cases = 0
    first_fail_cases = 0
    first_error_cases = 0
    fail_first_cases = 0
    fail_to_pass_cases = 0
    runs_to_pass_values: list[int] = []
    unresolved_ages_hours: list[float] = []
    observed_status_total = 0
    pass_status_total = 0
    fail_status_total = 0
    error_status_total = 0

    for row in summaries:
        first_status = str(row.get("first_status", "")).upper()
        observed_runs = int(row.get("observed_runs", 0) or 0)
        pass_runs = int(row.get("pass_runs", 0) or 0)
        fail_runs = int(row.get("fail_runs", 0) or 0)
        error_runs = int(row.get("error_runs", 0) or 0)
        observed_status_total += observed_runs
        pass_status_total += pass_runs
        fail_status_total += fail_runs
        error_status_total += error_runs
        if first_status in {PASS, FAIL}:
            first_decision_cases += 1
            if first_status == FAIL:
                first_fail_cases += 1
                fail_first_cases += 1
                if bool(row.get("fail_to_pass_converted", False)):
                    fail_to_pass_cases += 1
        else:
            first_error_cases += 1
        runs_to_first_pass = row.get("runs_to_first_pass")
        if isinstance(runs_to_first_pass, int):
            runs_to_pass_values.append(runs_to_first_pass)
        first_fail_epoch = row.get("first_fail_epoch")
        has_pass = bool(row.get("ever_pass", False))
        has_fail = bool(row.get("ever_fail", False))
        if not has_fail or has_pass or not isinstance(first_fail_epoch, int):
            continue
        age_hours = max(0.0, (now_epoch - first_fail_epoch) / 3600.0)
        unresolved_ages_hours.append(age_hours)

    unresolved_oldest = max(unresolved_ages_hours) if unresolved_ages_hours else 0.0
    unresolved_median = median(unresolved_ages_hours) if unresolved_ages_hours else 0.0
    median_runs_to_pass = float(median(runs_to_pass_values)) if runs_to_pass_values else 0.0
    decision_status_total = pass_status_total + fail_status_total

    return {
        "cases": total_cases,
        "first_decision_cases": first_decision_cases,
        "first_fail_cases": first_fail_cases,
        "first_error_cases": first_error_cases,
        "decision_coverage_rate": _format_rate(first_decision_cases, total_cases),
        "observed_status_total": observed_status_total,
        "decision_run_rate": _format_rate(decision_status_total, observed_status_total),
        "pass_run_rate": _format_rate(pass_status_total, observed_status_total),
        "fail_run_rate": _format_rate(fail_status_total, observed_status_total),
        "error_run_rate": _format_rate(error_status_total, observed_status_total),
        "first_error_rate": _format_rate(first_error_cases, total_cases),
        "first_pass_fail_rate": _format_rate(first_fail_cases, first_decision_cases),
        "fail_first_cases": fail_first_cases,
        "fail_to_pass_cases": fail_to_pass_cases,
        "fail_to_pass_conversion_rate": _format_rate(fail_to_pass_cases, fail_first_cases),
        "median_runs_to_pass": round(median_runs_to_pass, 3),
        "unresolved_fail_cases": len(unresolved_ages_hours),
        "unresolved_fail_age": round(unresolved_oldest, 3),
        "unresolved_fail_age_median": round(unresolved_median, 3),
        "unresolved_fail_age_unit": "hours",
    }


def build_growth_report(
    *,
    case_map: dict[str, CaseMetadata],
    run_reports: list[RunReport],
    now_epoch: int,
) -> dict[str, Any]:
    case_summaries: list[dict[str, Any]] = []
    run_count = len(run_reports)

    for case_id in sorted(case_map.keys()):
        metadata = case_map[case_id]
        first_status = ""
        latest_status = ""
        first_fail_epoch: int | None = None
        first_pass_run_index: int | None = None
        first_fail_run_index: int | None = None
        ever_pass = False
        ever_fail = False
        pass_runs = 0
        fail_runs = 0
        error_runs = 0
        observed_runs = 0
        decision_attempts = 0
        runs_to_first_pass: int | None = None

        for index, run in enumerate(run_reports, start=1):
            status = run.case_statuses.get(case_id)
            if status is None:
                continue
            observed_runs += 1
            latest_status = status
            if not first_status:
                first_status = status
            if status == PASS:
                ever_pass = True
                pass_runs += 1
                decision_attempts += 1
                if first_pass_run_index is None:
                    first_pass_run_index = index
                    runs_to_first_pass = decision_attempts
            elif status == FAIL:
                ever_fail = True
                fail_runs += 1
                decision_attempts += 1
                if first_fail_run_index is None:
                    first_fail_run_index = index
                    first_fail_epoch = run.timestamp
            else:
                error_runs += 1

        fail_to_pass_converted = bool(
            first_fail_run_index is not None
            and first_pass_run_index is not None
            and first_pass_run_index > first_fail_run_index
        )

        unresolved_fail_age_hours = 0.0
        if ever_fail and not ever_pass and isinstance(first_fail_epoch, int):
            unresolved_fail_age_hours = max(0.0, (now_epoch - first_fail_epoch) / 3600.0)

        case_summaries.append(
            {
                "id": case_id,
                "lane": metadata.lane,
                "source_name": metadata.source_name,
                "image_path": metadata.image_path,
                "observed_runs": observed_runs,
                "run_count": run_count,
                "first_status": first_status or ERROR,
                "latest_status": latest_status or ERROR,
                "ever_pass": ever_pass,
                "ever_fail": ever_fail,
                "pass_runs": pass_runs,
                "fail_runs": fail_runs,
                "error_runs": error_runs,
                "first_pass_run_index": first_pass_run_index,
                "first_fail_run_index": first_fail_run_index,
                "runs_to_first_pass": runs_to_first_pass,
                "fail_to_pass_converted": fail_to_pass_converted,
                "first_fail_epoch": first_fail_epoch,
                "unresolved_fail_age_hours": round(unresolved_fail_age_hours, 3),
            }
        )

    global_metrics = _run_metrics_for_cases(summaries=case_summaries, now_epoch=now_epoch)

    lane_metrics: dict[str, dict[str, Any]] = {}
    for lane in sorted({row["lane"] for row in case_summaries}):
        lane_rows = [row for row in case_summaries if row["lane"] == lane]
        lane_metrics[lane] = _run_metrics_for_cases(summaries=lane_rows, now_epoch=now_epoch)

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "runs_total": run_count,
        "cases_total": len(case_summaries),
        "metrics": global_metrics,
        "lane_metrics": lane_metrics,
        "cases": case_summaries,
    }


def _render_markdown(
    *,
    report: dict[str, Any],
    cases_path: Path,
    runs_dir: Path,
) -> str:
    lines: list[str] = []
    metrics = report["metrics"]
    lane_metrics: dict[str, dict[str, Any]] = report["lane_metrics"]
    cases: list[dict[str, Any]] = report["cases"]

    lines.append("# OCR Growth Metrics")
    lines.append("")
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Cases path: `{cases_path}`")
    lines.append(f"Runs dir: `{runs_dir}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    lines.append(f"| runs_total | {report['runs_total']} |")
    lines.append(f"| cases_total | {report['cases_total']} |")
    lines.append(f"| decision_coverage_rate | {metrics['decision_coverage_rate']:.4f} |")
    lines.append(f"| decision_run_rate | {metrics['decision_run_rate']:.4f} |")
    lines.append(f"| pass_run_rate | {metrics['pass_run_rate']:.4f} |")
    lines.append(f"| fail_run_rate | {metrics['fail_run_rate']:.4f} |")
    lines.append(f"| error_run_rate | {metrics['error_run_rate']:.4f} |")
    lines.append(f"| first_error_rate | {metrics['first_error_rate']:.4f} |")
    lines.append(f"| first_pass_fail_rate | {metrics['first_pass_fail_rate']:.4f} |")
    lines.append(f"| fail_to_pass_conversion_rate | {metrics['fail_to_pass_conversion_rate']:.4f} |")
    lines.append(f"| median_runs_to_pass | {metrics['median_runs_to_pass']} |")
    lines.append(
        f"| unresolved_fail_age ({metrics['unresolved_fail_age_unit']}) | {metrics['unresolved_fail_age']} |"
    )
    lines.append(f"| unresolved_fail_cases | {metrics['unresolved_fail_cases']} |")
    lines.append("")
    lines.append("## Per Lane")
    lines.append("")
    lines.append("| lane | cases | decision_coverage_rate | decision_run_rate | pass_run_rate | fail_run_rate | error_run_rate | first_error_rate | first_pass_fail_rate | fail_to_pass_conversion_rate | median_runs_to_pass | unresolved_fail_age (hours) |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for lane in sorted(lane_metrics.keys()):
        item = lane_metrics[lane]
        lines.append(
            f"| {lane} | {item['cases']} | {item['decision_coverage_rate']:.4f} | "
            f"{item['decision_run_rate']:.4f} | {item['pass_run_rate']:.4f} | "
            f"{item['fail_run_rate']:.4f} | {item['error_run_rate']:.4f} | "
            f"{item['first_error_rate']:.4f} | {item['first_pass_fail_rate']:.4f} | "
            f"{item['fail_to_pass_conversion_rate']:.4f} | {item['median_runs_to_pass']} | "
            f"{item['unresolved_fail_age']} |"
        )
    lines.append("")

    unresolved = [
        row
        for row in cases
        if bool(row.get("ever_fail", False)) and not bool(row.get("ever_pass", False))
    ]
    if unresolved:
        unresolved.sort(key=lambda row: float(row.get("unresolved_fail_age_hours", 0.0)), reverse=True)
        lines.append("## Unresolved Fails")
        lines.append("")
        lines.append("| case_id | lane | age_hours | source_name | image_path |")
        lines.append("|---|---|---:|---|---|")
        for row in unresolved:
            lines.append(
                f"| {row['id']} | {row['lane']} | {row['unresolved_fail_age_hours']} | "
                f"{row['source_name']} | {row['image_path']} |"
            )
        lines.append("")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute pass-from-fail growth metrics from OCR run history."
    )
    parser.add_argument(
        "--cases",
        default=".local/eval_cases/ocr_transcript_cases_all.json",
        help="Path to OCR cases JSON (growth lane).",
    )
    parser.add_argument(
        "--runs-dir",
        default=".local/eval_reports/ocr_stability_runs",
        help="Directory containing per-run OCR report JSON files.",
    )
    parser.add_argument(
        "--output-json",
        default=".local/eval_reports/ocr_growth_metrics.json",
        help="Output path for growth metrics JSON report.",
    )
    parser.add_argument(
        "--output-markdown",
        default=".local/eval_reports/ocr_growth_metrics.md",
        help="Output path for growth metrics markdown report.",
    )
    parser.add_argument(
        "--limit-runs",
        type=int,
        default=0,
        help="Optional cap on most recent runs (0 = all).",
    )
    parser.add_argument(
        "--now-epoch",
        type=int,
        default=0,
        help="Override current epoch for deterministic tests.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cases_path = Path(args.cases).expanduser()
    runs_dir = Path(args.runs_dir).expanduser()
    output_json = Path(args.output_json).expanduser()
    output_markdown = Path(args.output_markdown).expanduser()

    if not cases_path.is_file():
        print(f"cases file not found: {cases_path}")
        return 2
    if not runs_dir.is_dir():
        print(f"runs dir not found: {runs_dir}")
        return 2

    case_map = _load_cases(cases_path)
    run_reports = _collect_run_reports(
        runs_dir=runs_dir,
        expected_cases_path=cases_path.resolve(),
    )
    if args.limit_runs > 0:
        run_reports = run_reports[-args.limit_runs :]
    if not run_reports:
        print(f"no matching run reports found for cases: {cases_path}")
        return 2

    now_epoch = args.now_epoch if args.now_epoch > 0 else int(time.time())
    report = build_growth_report(
        case_map=case_map,
        run_reports=run_reports,
        now_epoch=now_epoch,
    )
    report["cases_path"] = str(cases_path)
    report["runs_dir"] = str(runs_dir)
    report["limit_runs"] = int(args.limit_runs)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown = _render_markdown(report=report, cases_path=cases_path, runs_dir=runs_dir)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.write_text(markdown, encoding="utf-8")

    metrics = report["metrics"]
    print("OCR growth metrics")
    print(f"  runs_total: {report['runs_total']}")
    print(f"  cases_total: {report['cases_total']}")
    print(f"  decision_coverage_rate: {metrics['decision_coverage_rate']:.4f}")
    print(f"  first_error_rate: {metrics['first_error_rate']:.4f}")
    print(f"  first_pass_fail_rate: {metrics['first_pass_fail_rate']:.4f}")
    print(f"  fail_to_pass_conversion_rate: {metrics['fail_to_pass_conversion_rate']:.4f}")
    print(f"  median_runs_to_pass: {metrics['median_runs_to_pass']}")
    print(
        f"  unresolved_fail_age ({metrics['unresolved_fail_age_unit']}): "
        f"{metrics['unresolved_fail_age']}"
    )
    print(f"  json: {output_json}")
    print(f"  markdown: {output_markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
