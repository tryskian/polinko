"""Run OCR eval cases in bounded batches and aggregate summary artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.eval_ocr import _load_cases


@dataclass(frozen=True)
class BatchPlan:
    offset: int
    max_cases: int


def _plan_batches(*, total_cases: int, offset: int, max_cases: int, batch_size: int) -> list[BatchPlan]:
    if total_cases < 0:
        raise RuntimeError("total_cases must be >= 0.")
    if offset < 0:
        raise RuntimeError("offset must be >= 0.")
    if max_cases < 0:
        raise RuntimeError("max_cases must be >= 0.")
    if batch_size <= 0:
        raise RuntimeError("batch_size must be > 0.")

    available = max(0, total_cases - offset)
    if max_cases > 0:
        available = min(available, max_cases)
    if available <= 0:
        return []

    batches: list[BatchPlan] = []
    cursor = offset
    remaining = available
    while remaining > 0:
        size = min(batch_size, remaining)
        batches.append(BatchPlan(offset=cursor, max_cases=size))
        cursor += size
        remaining -= size
    return batches


def _build_markdown_summary(payload: dict[str, Any]) -> str:
    summary = payload.get("summary", {})
    lines = [
        "# OCR Growth Batched Summary",
        "",
        f"- generated_at: {payload.get('generated_at')}",
        f"- base_url: {payload.get('base_url')}",
        f"- cases_path: {payload.get('cases_path')}",
        f"- total_cases_file: {payload.get('cases_total')}",
        (
            "- selected_window: "
            f"offset={payload.get('offset')} max_cases={payload.get('max_cases')} "
            f"batch_size={payload.get('batch_size')}"
        ),
        "",
        "## Aggregate",
        "",
        f"- batches_total: {summary.get('batches_total')}",
        f"- batches_completed: {summary.get('batches_completed')}",
        f"- batches_failed: {summary.get('batches_failed')}",
        f"- total_selected: {summary.get('total_selected')}",
        f"- passed: {summary.get('passed')}",
        f"- failed: {summary.get('failed')}",
        f"- errors: {summary.get('errors')}",
        "",
        "## Batches",
        "",
        "| # | offset | max_cases | return_code | report |",
        "|---|---:|---:|---:|---|",
    ]
    for row in payload.get("batches", []):
        lines.append(
            f"| {row.get('index')} | {row.get('offset')} | {row.get('max_cases')} | "
            f"{row.get('return_code')} | {row.get('report_json')} |"
        )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run OCR eval in deterministic batches.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Polinko API base URL.")
    parser.add_argument(
        "--cases",
        default=".local/eval_cases/ocr_transcript_cases_growth.json",
        help="Path to OCR cases JSON file.",
    )
    parser.add_argument("--batch-size", type=int, default=40, help="Cases per batch.")
    parser.add_argument("--offset", type=int, default=0, help="Global offset into cases.")
    parser.add_argument("--max-cases", type=int, default=0, help="Global case cap (0 = all).")
    parser.add_argument(
        "--report-dir",
        default=".local/eval_reports/ocr_growth_batched_runs",
        help="Directory for per-batch report JSON files.",
    )
    parser.add_argument(
        "--output-json",
        default=".local/eval_reports/ocr_growth_batched_summary.json",
        help="Path for aggregate summary JSON.",
    )
    parser.add_argument(
        "--output-markdown",
        default=".local/eval_reports/ocr_growth_batched_summary.md",
        help="Path for aggregate summary markdown.",
    )
    parser.add_argument("--session-prefix", default="ocr-growth-batch", help="Session prefix for eval_ocr.")
    parser.add_argument("--timeout", type=int, default=90, help="HTTP timeout passed to eval_ocr.")
    parser.add_argument("--show-text", action="store_true", help="Forward --show-text to eval_ocr.")
    parser.add_argument("--keep-chats", action="store_true", help="Forward --keep-chats to eval_ocr.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any case fails.")
    return parser


def _run_batch(
    *,
    python_exec: str,
    base_url: str,
    cases_path: Path,
    session_prefix: str,
    timeout: int,
    plan: BatchPlan,
    run_id: str,
    report_path: Path,
    show_text: bool,
    keep_chats: bool,
) -> tuple[int, str]:
    command = [
        python_exec,
        "-m",
        "tools.eval_ocr",
        "--base-url",
        base_url,
        "--cases",
        str(cases_path),
        "--session-prefix",
        session_prefix,
        "--timeout",
        str(timeout),
        "--offset",
        str(plan.offset),
        "--max-cases",
        str(plan.max_cases),
        "--run-id",
        run_id,
        "--report-json",
        str(report_path),
    ]
    if show_text:
        command.append("--show-text")
    if keep_chats:
        command.append("--keep-chats")

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.stderr:
        print(completed.stderr.rstrip(), file=sys.stderr)
    return completed.returncode, " ".join(command)


def main() -> int:
    args = build_parser().parse_args()
    cases_path = Path(args.cases).expanduser()
    if not cases_path.exists():
        raise SystemExit(f"Cases file not found: {cases_path}")

    cases = _load_cases(cases_path)
    batches = _plan_batches(
        total_cases=len(cases),
        offset=int(args.offset),
        max_cases=int(args.max_cases),
        batch_size=int(args.batch_size),
    )
    if not batches:
        raise SystemExit(
            f"No batches planned (cases={len(cases)} offset={args.offset} max_cases={args.max_cases} batch_size={args.batch_size})."
        )

    report_dir = Path(args.report_dir).expanduser()
    report_dir.mkdir(parents=True, exist_ok=True)
    output_json = Path(args.output_json).expanduser()
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown = Path(args.output_markdown).expanduser()
    output_markdown.parent.mkdir(parents=True, exist_ok=True)

    base_run_id = f"batch-{int(time.time())}"
    batch_rows: list[dict[str, Any]] = []
    passed_total = 0
    failed_total = 0
    errors_total = 0
    selected_total = 0
    failed_batches = 0
    completed_batches = 0

    for index, plan in enumerate(batches, start=1):
        run_id = f"{base_run_id}-b{index:03d}"
        report_path = report_dir / f"ocr-{run_id}.json"
        print(
            f"[batch {index}/{len(batches)}] offset={plan.offset} max_cases={plan.max_cases} run_id={run_id}"
        )
        return_code, command_str = _run_batch(
            python_exec=sys.executable,
            base_url=str(args.base_url),
            cases_path=cases_path,
            session_prefix=str(args.session_prefix),
            timeout=int(args.timeout),
            plan=plan,
            run_id=run_id,
            report_path=report_path,
            show_text=bool(args.show_text),
            keep_chats=bool(args.keep_chats),
        )

        row: dict[str, Any] = {
            "index": index,
            "offset": plan.offset,
            "max_cases": plan.max_cases,
            "run_id": run_id,
            "command": command_str,
            "report_json": str(report_path),
            "return_code": return_code,
        }

        if report_path.exists():
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            summary = payload.get("summary") if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                batch_total = int(summary.get("total", 0) or 0)
                batch_passed = int(summary.get("passed", 0) or 0)
                batch_failed = int(summary.get("failed", 0) or 0)
                batch_errors = int(summary.get("errors", 0) or 0)
                selected_total += batch_total
                passed_total += batch_passed
                failed_total += batch_failed
                errors_total += batch_errors
                row["summary"] = {
                    "total": batch_total,
                    "passed": batch_passed,
                    "failed": batch_failed,
                    "errors": batch_errors,
                }
                completed_batches += 1
        if return_code != 0:
            failed_batches += 1
        batch_rows.append(row)

    summary_payload = {
        "generated_at": int(time.time()),
        "base_url": args.base_url,
        "cases_path": str(cases_path.resolve()),
        "cases_total": len(cases),
        "offset": int(args.offset),
        "max_cases": int(args.max_cases),
        "batch_size": int(args.batch_size),
        "summary": {
            "batches_total": len(batches),
            "batches_completed": completed_batches,
            "batches_failed": failed_batches,
            "total_selected": selected_total,
            "passed": passed_total,
            "failed": failed_total,
            "errors": errors_total,
        },
        "batches": batch_rows,
    }

    output_json.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    output_markdown.write_text(_build_markdown_summary(summary_payload), encoding="utf-8")

    print("\nBatched OCR summary")
    print(f"  Batches: {completed_batches}/{len(batches)} completed")
    print(f"  Selected: {selected_total}")
    print(f"  Passed: {passed_total}")
    print(f"  Failed: {failed_total}")
    print(f"  Errors: {errors_total}")
    print(f"  Summary JSON: {output_json}")
    print(f"  Summary MD: {output_markdown}")

    if failed_batches > 0:
        return 2
    if args.strict and (failed_total > 0 or errors_total > 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
