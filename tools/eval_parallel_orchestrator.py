import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from pathlib import Path
from typing import Any


DEFAULT_SUITES = (
    "retrieval",
    "file_search",
    "ocr",
    "style",
    "response_behaviour",
    "hallucination",
)


def _suite_module(suite: str) -> str:
    modules = {
        "retrieval": "tools.eval_retrieval",
        "file_search": "tools.eval_file_search",
        "ocr": "tools.eval_ocr",
        "style": "tools.eval_style",
        "response_behaviour": "tools.eval_response_behaviour",
        "hallucination": "tools.eval_hallucination",
    }
    return modules[suite]


def _suite_report_path(suite: str, run_id: str) -> Path:
    names = {
        "retrieval": "retrieval",
        "file_search": "file-search",
        "ocr": "ocr",
        "style": "style",
        "response_behaviour": "response-behaviour",
        "hallucination": "hallucination",
    }
    return Path("eval_reports") / f"{names[suite]}-{run_id}.json"


def _suite_log_path(suite: str, run_id: str) -> Path:
    return Path("eval_reports") / f"{suite.replace('_', '-')}-{run_id}.log"


def _parse_suites(raw: str) -> list[str]:
    values = [item.strip().lower() for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError("At least one suite is required.")
    unknown = [item for item in values if item not in DEFAULT_SUITES]
    if unknown:
        raise ValueError(f"Unsupported suite(s): {', '.join(unknown)}")
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def _load_summary(report_path: Path) -> dict[str, Any]:
    if not report_path.exists():
        return {}
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if not isinstance(payload, dict):
        return {}
    summary = payload.get("summary")
    if isinstance(summary, dict):
        return summary
    fallback_keys = (
        "total_cases",
        "passed",
        "failed",
        "risk_counts",
        "strict",
    )
    fallback = {key: payload.get(key) for key in fallback_keys if key in payload}
    return fallback if isinstance(fallback, dict) else {}


def _run_suite(
    *,
    suite: str,
    run_id: str,
    base_url: str,
    timeout: int,
    hallucination_mode: str,
    hallucination_min_acceptable_score: int,
) -> dict[str, Any]:
    report_path = _suite_report_path(suite, run_id)
    log_path = _suite_log_path(suite, run_id)

    cmd = [
        sys.executable,
        "-m",
        _suite_module(suite),
        "--base-url",
        base_url,
        "--run-id",
        run_id,
        "--report-json",
        str(report_path),
    ]
    if suite == "hallucination":
        cmd.extend(
            [
                "--evaluation-mode",
                hallucination_mode,
                "--min-acceptable-score",
                str(hallucination_min_acceptable_score),
            ]
        )

    started = time.time()
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    elapsed_seconds = round(time.time() - started, 2)
    output = f"$ {' '.join(cmd)}\n\n{completed.stdout}\n{completed.stderr}".strip()
    log_path.write_text(output + "\n", encoding="utf-8")

    return {
        "suite": suite,
        "command": cmd,
        "exit_code": int(completed.returncode),
        "elapsed_seconds": elapsed_seconds,
        "report_json": str(report_path),
        "log_path": str(log_path),
        "summary": _load_summary(report_path),
        "passed": completed.returncode == 0,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run eval report suites in parallel and write a consolidated summary "
            "artifact while preserving per-suite logs/reports."
        ),
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Polinko API base URL.",
    )
    parser.add_argument(
        "--run-id",
        default="",
        help="Run id for all suite artifacts (defaults to timestamp).",
    )
    parser.add_argument(
        "--suites",
        default=",".join(DEFAULT_SUITES),
        help=(
            "Comma-separated suites. Supported: "
            "retrieval,file_search,ocr,style,response_behaviour,hallucination"
        ),
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=len(DEFAULT_SUITES),
        help="Maximum parallel workers.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1200,
        help="Per-suite subprocess timeout in seconds.",
    )
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional path for consolidated report JSON.",
    )
    parser.add_argument(
        "--hallucination-mode",
        choices=("judge", "deterministic", "auto"),
        default="judge",
        help="Evaluation mode passed to hallucination suite.",
    )
    parser.add_argument(
        "--hallucination-min-acceptable-score",
        type=int,
        default=5,
        help="Minimum acceptable hallucination score.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run_id = args.run_id.strip() or time.strftime("%Y%m%d-%H%M%S")
    suites = _parse_suites(args.suites)
    worker_count = max(1, min(int(args.max_workers), len(suites)))
    output_path = (
        Path(args.output_json)
        if str(args.output_json).strip()
        else Path("eval_reports") / f"parallel-{run_id}.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Running parallel eval orchestration on {args.base_url}")
    print(f"Suites: {', '.join(suites)} | run_id={run_id} | workers={worker_count}")

    started = time.time()
    suite_results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_by_suite = {
            executor.submit(
                _run_suite,
                suite=suite,
                run_id=run_id,
                base_url=args.base_url,
                timeout=args.timeout,
                hallucination_mode=args.hallucination_mode,
                hallucination_min_acceptable_score=args.hallucination_min_acceptable_score,
            ): suite
            for suite in suites
        }
        for future in as_completed(future_by_suite):
            suite = future_by_suite[future]
            try:
                suite_results.append(future.result())
            except subprocess.TimeoutExpired as exc:
                suite_results.append(
                    {
                        "suite": suite,
                        "command": [],
                        "exit_code": 124,
                        "elapsed_seconds": args.timeout,
                        "report_json": "",
                        "log_path": "",
                        "summary": {},
                        "passed": False,
                        "error": f"timeout after {args.timeout}s: {exc}",
                    }
                )
            except Exception as exc:  # pragma: no cover - operational CLI guard
                suite_results.append(
                    {
                        "suite": suite,
                        "command": [],
                        "exit_code": 1,
                        "elapsed_seconds": 0,
                        "report_json": "",
                        "log_path": "",
                        "summary": {},
                        "passed": False,
                        "error": str(exc),
                    }
                )

    ordered = sorted(suite_results, key=lambda item: suites.index(str(item.get("suite", ""))))
    overall_pass = all(bool(item.get("passed")) for item in ordered)
    elapsed_seconds = round(time.time() - started, 2)

    print("\nSuite results")
    for item in ordered:
        status = "PASS" if item.get("passed") else "FAIL"
        suite = str(item.get("suite", "unknown"))
        summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
        report_json = str(item.get("report_json", "")).strip()
        log_path = str(item.get("log_path", "")).strip()
        print(
            f"  [{status}] {suite} exit={item.get('exit_code')} "
            f"elapsed={item.get('elapsed_seconds')}s"
        )
        if summary:
            print(f"    summary={summary}")
        if report_json:
            print(f"    report={report_json}")
        if log_path:
            print(f"    log={log_path}")
        error = str(item.get("error", "")).strip()
        if error:
            print(f"    error={error}")

    payload = {
        "run_id": run_id,
        "base_url": args.base_url,
        "suites": suites,
        "workers": worker_count,
        "elapsed_seconds": elapsed_seconds,
        "overall_pass": overall_pass,
        "suite_results": ordered,
        "generated_at_unix": int(time.time()),
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nConsolidated report: {output_path}")
    print(f"Overall: {'PASS' if overall_pass else 'FAIL'}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
