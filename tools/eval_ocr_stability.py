from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def _normalise_text(raw: str) -> str:
    return " ".join(str(raw).split()).strip()


def _float_percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def _load_report(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _summarise_reports(
    *,
    reports: list[dict[str, Any]],
    expected_runs: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    case_ids: set[str] = set()
    report_case_maps: list[dict[str, dict[str, Any]]] = []
    for report in reports:
        case_map: dict[str, dict[str, Any]] = {}
        for case in report.get("cases", []):
            if not isinstance(case, dict):
                continue
            case_id = str(case.get("id", "")).strip()
            if not case_id:
                continue
            case_map[case_id] = case
            case_ids.add(case_id)
        report_case_maps.append(case_map)

    case_summaries: list[dict[str, Any]] = []
    for case_id in sorted(case_ids):
        statuses: list[str] = []
        reasons: list[str] = []
        chars: list[int] = []
        variants: set[str] = set()
        pass_runs = 0
        fail_runs = 0
        error_runs = 0
        observed_runs = 0

        for case_map in report_case_maps:
            row = case_map.get(case_id)
            if row is None:
                continue
            observed_runs += 1
            status = str(row.get("status", "")).strip().upper()
            statuses.append(status)
            if status == "PASS":
                pass_runs += 1
            elif status == "FAIL":
                fail_runs += 1
            else:
                error_runs += 1
            chars.append(int(row.get("char_count", 0) or 0))
            text = _normalise_text(str(row.get("extracted_text", "")))
            if text:
                variants.add(text)
            row_reasons = row.get("reasons")
            if isinstance(row_reasons, list):
                reasons.extend(str(item) for item in row_reasons if str(item).strip())

        decision_stable = observed_runs == expected_runs and (
            (pass_runs == expected_runs and fail_runs == 0 and error_runs == 0)
            or (fail_runs == expected_runs and pass_runs == 0 and error_runs == 0)
        )
        always_pass = pass_runs == expected_runs and fail_runs == 0 and error_runs == 0
        always_fail = fail_runs == expected_runs and pass_runs == 0 and error_runs == 0
        text_variant_count = len(variants)

        case_summaries.append(
            {
                "id": case_id,
                "expected_runs": expected_runs,
                "observed_runs": observed_runs,
                "pass_runs": pass_runs,
                "fail_runs": fail_runs,
                "error_runs": error_runs,
                "pass_rate": _float_percent(pass_runs, expected_runs),
                "decision_stable": decision_stable,
                "always_pass": always_pass,
                "always_fail": always_fail,
                "statuses": statuses,
                "text_variant_count": text_variant_count,
                "text_variants": sorted(variants)[:5],
                "char_count_min": min(chars) if chars else 0,
                "char_count_max": max(chars) if chars else 0,
                "char_count_span": (max(chars) - min(chars)) if chars else 0,
                "sample_reasons": sorted(set(reasons))[:5],
            }
        )

    stable_decision_cases = sum(1 for item in case_summaries if item["decision_stable"])
    decision_flaky_cases = len(case_summaries) - stable_decision_cases
    output_variant_cases = sum(
        1 for item in case_summaries if item["text_variant_count"] > 1
    )
    always_pass_cases = sum(1 for item in case_summaries if item["always_pass"])
    always_fail_cases = sum(1 for item in case_summaries if item["always_fail"])

    summary = {
        "cases_total": len(case_summaries),
        "stable_decision_cases": stable_decision_cases,
        "decision_flaky_cases": decision_flaky_cases,
        "always_pass_cases": always_pass_cases,
        "always_fail_cases": always_fail_cases,
        "output_variant_cases": output_variant_cases,
    }
    return summary, case_summaries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run OCR eval repeatedly and summarise case-level stability."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--cases", required=True, help="Path to OCR eval cases JSON.")
    parser.add_argument(
        "--runs", type=int, default=5, help="How many repeated runs to execute."
    )
    parser.add_argument(
        "--run-id", default="", help="Run id prefix (default: unix timestamp)."
    )
    parser.add_argument("--session-prefix", default="ocr-stability")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Start index into the cases list (applies to each run).",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=0,
        help="Maximum number of cases to evaluate per run (0 = all).",
    )
    parser.add_argument(
        "--ocr-retries",
        type=int,
        default=0,
        help="Transient OCR retry count passed through to tools.eval_ocr.",
    )
    parser.add_argument(
        "--ocr-retry-delay-ms",
        type=int,
        default=0,
        help="Delay between transient OCR retries, in milliseconds.",
    )
    parser.add_argument(
        "--case-delay-ms",
        type=int,
        default=0,
        help="Delay between child OCR cases, in milliseconds.",
    )
    parser.add_argument(
        "--rate-limit-cooldown-ms",
        type=int,
        default=0,
        help=(
            "Additional cooldown in milliseconds after a rate-limit error in "
            "child OCR eval."
        ),
    )
    parser.add_argument(
        "--max-consecutive-rate-limit-errors",
        type=int,
        default=0,
        help=(
            "Abort each child tools.eval_ocr run early after N consecutive OCR "
            "rate-limit errors (0 disables early abort)."
        ),
    )
    parser.add_argument(
        "--stop-on-rate-limit-abort",
        action="store_true",
        help=(
            "Stop remaining runs when a child OCR eval report signals "
            "aborted_due_to_rate_limit."
        ),
    )
    parser.add_argument(
        "--strict", action="store_true", help="Pass --strict to tools.eval_ocr."
    )
    parser.add_argument(
        "--report-dir",
        default=".local/eval_reports/ocr_stability_runs",
        help="Directory for per-run OCR reports.",
    )
    parser.add_argument(
        "--output-json",
        default=".local/eval_reports/ocr_transcript_stability.json",
        help="Output summary report path.",
    )
    parser.add_argument(
        "--fail-on-decision-flaky",
        action="store_true",
        help="Exit non-zero when any case has mixed run outcomes.",
    )
    parser.add_argument(
        "--fail-on-run-error",
        action="store_true",
        help="Exit non-zero when any run fails to produce a readable report.",
    )
    parser.add_argument(
        "--capture-child-output",
        action="store_true",
        help="Capture child eval stdout/stderr instead of streaming live progress.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.runs < 1:
        print("runs must be >= 1")
        return 2
    if args.offset < 0:
        print("offset must be >= 0")
        return 2
    if args.max_cases < 0:
        print("max-cases must be >= 0")
        return 2
    if args.ocr_retries < 0:
        print("ocr-retries must be >= 0")
        return 2
    if args.ocr_retry_delay_ms < 0:
        print("ocr-retry-delay-ms must be >= 0")
        return 2
    if args.case_delay_ms < 0:
        print("case-delay-ms must be >= 0")
        return 2
    if args.rate_limit_cooldown_ms < 0:
        print("rate-limit-cooldown-ms must be >= 0")
        return 2
    if args.max_consecutive_rate_limit_errors < 0:
        print("max-consecutive-rate-limit-errors must be >= 0")
        return 2

    run_id = args.run_id.strip() or str(int(time.time()))
    cases_path = Path(args.cases).expanduser()
    if not cases_path.is_file():
        print(f"cases file not found: {cases_path}")
        return 2

    report_dir = Path(args.report_dir).expanduser()
    report_dir.mkdir(parents=True, exist_ok=True)
    output_json = Path(args.output_json).expanduser()
    output_json.parent.mkdir(parents=True, exist_ok=True)

    run_reports: list[dict[str, Any]] = []
    run_statuses: list[dict[str, Any]] = []
    runs_executed = 0

    for index in range(1, args.runs + 1):
        runs_executed += 1
        run_tag = f"{run_id}-r{index:02d}"
        run_report = report_dir / f"ocr-{run_tag}.json"
        cmd = [
            sys.executable,
            "-u",
            "-m",
            "tools.eval_ocr",
            "--base-url",
            args.base_url,
            "--cases",
            str(cases_path),
            "--run-id",
            run_tag,
            "--session-prefix",
            f"{args.session_prefix}-r{index:02d}",
            "--timeout",
            str(args.timeout),
            "--offset",
            str(args.offset),
            "--max-cases",
            str(args.max_cases),
            "--ocr-retries",
            str(args.ocr_retries),
            "--ocr-retry-delay-ms",
            str(args.ocr_retry_delay_ms),
            "--case-delay-ms",
            str(args.case_delay_ms),
            "--rate-limit-cooldown-ms",
            str(args.rate_limit_cooldown_ms),
            "--max-consecutive-rate-limit-errors",
            str(args.max_consecutive_rate_limit_errors),
            "--report-json",
            str(run_report),
        ]
        if args.strict:
            cmd.append("--strict")

        if args.capture_child_output:
            proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
            stdout_tail = proc.stdout[-1000:]
            stderr_tail = proc.stderr[-1000:]
        else:
            proc = subprocess.run(cmd, check=False, text=True)
            stdout_tail = ""
            stderr_tail = ""
        payload = _load_report(run_report)
        if payload is None:
            run_statuses.append(
                {
                    "run_index": index,
                    "run_id": run_tag,
                    "exit_code": proc.returncode,
                    "report_json": str(run_report),
                    "report_loaded": False,
                    "stdout_tail": stdout_tail,
                    "stderr_tail": stderr_tail,
                }
            )
            print(
                f"[{index}/{args.runs}] run_id={run_tag} report load failed (exit={proc.returncode})"
            )
            continue

        run_reports.append(payload)
        raw_summary = payload.get("summary")
        summary: dict[str, Any] = raw_summary if isinstance(raw_summary, dict) else {}
        aborted_due_to_rate_limit = bool(summary.get("aborted_due_to_rate_limit", False))
        total = int(summary.get("total", 0) or 0)
        passed = int(summary.get("passed", 0) or 0)
        failed = int(summary.get("failed", 0) or 0)
        errors = int(summary.get("errors", 0) or 0)
        run_statuses.append(
            {
                "run_index": index,
                "run_id": str(payload.get("run_id", run_tag)),
                "exit_code": proc.returncode,
                "report_json": str(run_report),
                "report_loaded": True,
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "aborted_due_to_rate_limit": aborted_due_to_rate_limit,
                },
            }
        )
        print(
            f"[{index}/{args.runs}] run_id={payload.get('run_id', run_tag)} "
            f"passed={passed}/{total} failed={failed} errors={errors}"
        )
        if args.stop_on_rate_limit_abort and aborted_due_to_rate_limit:
            print(
                f"  STOP after run {index}: child report aborted due to sustained OCR "
                "rate limits."
            )
            break

    expected_runs = runs_executed if runs_executed > 0 else args.runs
    aggregate_summary, case_summaries = _summarise_reports(
        reports=run_reports,
        expected_runs=expected_runs,
    )

    run_error_count = sum(1 for item in run_statuses if not item.get("report_loaded"))
    result = {
        "run_id": run_id,
        "base_url": args.base_url,
        "cases_path": str(cases_path),
        "offset": args.offset,
        "max_cases": args.max_cases,
        "ocr_retries": args.ocr_retries,
        "ocr_retry_delay_ms": args.ocr_retry_delay_ms,
        "case_delay_ms": args.case_delay_ms,
        "rate_limit_cooldown_ms": args.rate_limit_cooldown_ms,
        "max_consecutive_rate_limit_errors": args.max_consecutive_rate_limit_errors,
        "stop_on_rate_limit_abort": args.stop_on_rate_limit_abort,
        "runs_requested": args.runs,
        "runs_executed": runs_executed,
        "runs_expected_for_stability": expected_runs,
        "runs_with_report": len(run_reports),
        "run_error_count": run_error_count,
        "summary": aggregate_summary,
        "runs": run_statuses,
        "cases": sorted(
            case_summaries,
            key=lambda item: (
                item["decision_stable"],
                item["always_pass"],
                -item["error_runs"],
                -item["text_variant_count"],
                item["id"],
            ),
        ),
        "generated_at": int(time.time()),
    }
    output_json.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\nStability summary")
    print(f"  Runs executed: {runs_executed}/{args.runs}")
    print(f"  Runs with report: {len(run_reports)}/{runs_executed}")
    print(f"  Run errors: {run_error_count}")
    print(f"  Cases: {aggregate_summary['cases_total']}")
    print(
        "  Decision stability: "
        f"stable={aggregate_summary['stable_decision_cases']} "
        f"flaky={aggregate_summary['decision_flaky_cases']}"
    )
    print(
        "  Output variability: "
        f"variant_cases={aggregate_summary['output_variant_cases']}"
    )
    print(f"  Report: {output_json}")

    if args.fail_on_run_error and run_error_count > 0:
        return 1
    if args.fail_on_decision_flaky and aggregate_summary["decision_flaky_cases"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
