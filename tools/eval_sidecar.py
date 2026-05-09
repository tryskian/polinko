"""Run and inspect long-lived eval sidecar loops."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

DEFAULT_TARGET = "quality-gate-deterministic"
DEFAULT_MIN_SECONDS = 3600
DEFAULT_RUNS_DIR = Path(".local/eval_runs")
DEFAULT_PID_FILE = Path("/tmp/polinko-eval-sidecar.pid")
DEFAULT_LOG_FILE = Path("/tmp/polinko-eval-sidecar.log")
DEFAULT_CURRENT_FILE = DEFAULT_RUNS_DIR / "eval_sidecar_current.txt"
STATUS_FILE_NAME = "status.json"
SUMMARY_FILE_NAME = "summary.log"
STOP_FILE_NAME = "stop_requested.flag"
START_SNAPSHOT_NAME = "operator_burden_rows_summary.start.json"
END_SNAPSHOT_NAME = "operator_burden_rows_summary.end.json"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_iso() -> str:
    return _utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _append_line(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{line}\n")


def _extract_failure_signals(text: str) -> list[str]:
    signals: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("[FAIL] "):
            continue
        parts = line.split()
        if len(parts) >= 2:
            signals.append(parts[1])
    return signals


def _failure_counter(failure_texts: list[str]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for text in failure_texts:
        counts.update(_extract_failure_signals(text))
    return [
        {"signal": signal_name, "count": count}
        for signal_name, count in counts.most_common()
    ]


def _tail_text(path: Path, max_lines: int) -> str:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines) + ("\n" if lines else "")
    return "\n".join(lines[-max_lines:]) + "\n"


def _write_operator_burden_snapshot(path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.report_operator_burden_rows"],
        check=True,
        capture_output=True,
        text=True,
    )
    path.write_text(result.stdout, encoding="utf-8")


def _load_current_run_dir(current_file: Path) -> Path:
    if not current_file.exists():
        raise RuntimeError(f"No current eval sidecar file: {current_file}")
    run_dir = Path(current_file.read_text(encoding="utf-8").strip())
    if not run_dir:
        raise RuntimeError(f"Eval sidecar current file is empty: {current_file}")
    return run_dir


def _status_path(run_dir: Path) -> Path:
    return run_dir / STATUS_FILE_NAME


def _render_status(status: dict[str, Any], pid_file: Path) -> str:
    lines = [
        f"eval-sidecar: {status.get('state', 'unknown').upper()}",
        f"run_id: {status.get('run_id', '')}",
        f"target: {status.get('target', '')}",
        f"run_dir: {status.get('run_dir', '')}",
        f"started_at: {status.get('started_at', '')}",
        f"elapsed_seconds: {status.get('elapsed_seconds', 0)}",
        f"min_seconds: {status.get('min_seconds', 0)}",
        f"cycles_completed: {status.get('cycles_completed', 0)}",
        f"pass_cycles: {status.get('pass_cycles', 0)}",
        f"fail_cycles: {status.get('fail_cycles', 0)}",
        f"current_cycle: {status.get('current_cycle', 0)}",
        f"last_cycle_status: {status.get('last_cycle_status', 'n/a')}",
        f"stop_requested: {status.get('stop_requested', False)}",
    ]
    pid_text = ""
    if pid_file.exists():
        pid_text = pid_file.read_text(encoding="utf-8").strip()
    if pid_text:
        lines.append(f"pid: {pid_text}")
    signals = status.get("recent_failure_signals", [])
    if signals:
        lines.append("recent_failure_signals:")
        for item in signals:
            lines.append(f"- {item['signal']}: {item['count']}")
    return "\n".join(lines)


def run_sidecar(args: argparse.Namespace) -> int:
    run_id = _utc_now().strftime("%Y%m%d-%H%M%S")
    run_dir = args.runs_dir / f"eval-sidecar-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_log = run_dir / SUMMARY_FILE_NAME
    stop_file = run_dir / STOP_FILE_NAME
    current_file = args.current_file
    current_file.parent.mkdir(parents=True, exist_ok=True)
    current_file.write_text(str(run_dir), encoding="utf-8")
    args.pid_file.write_text(str(os.getpid()), encoding="utf-8")

    start_snapshot = run_dir / START_SNAPSHOT_NAME
    end_snapshot = run_dir / END_SNAPSHOT_NAME
    _write_operator_burden_snapshot(start_snapshot)

    started_at = _utc_now()
    cycles_completed = 0
    pass_cycles = 0
    fail_cycles = 0
    current_cycle = 0
    last_cycle_status = "n/a"
    failure_texts: list[str] = []
    state = "running"

    def write_status() -> None:
        payload = {
            "run_id": run_id,
            "state": state,
            "target": args.target,
            "run_dir": str(run_dir),
            "pid": os.getpid(),
            "started_at": started_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": _utc_iso(),
            "completed_at": _utc_iso() if state in {"completed", "failed", "stopped"} else None,
            "elapsed_seconds": int(time.time() - started_at.timestamp()),
            "min_seconds": args.min_seconds,
            "cycles_completed": cycles_completed,
            "pass_cycles": pass_cycles,
            "fail_cycles": fail_cycles,
            "current_cycle": current_cycle,
            "last_cycle_status": last_cycle_status,
            "stop_requested": stop_file.exists(),
            "recent_failure_signals": _failure_counter(failure_texts),
            "summary_log": str(summary_log),
        }
        _write_json(_status_path(run_dir), payload)

    def handle_term(signum: int, _frame: Any) -> None:
        stop_file.write_text(f"signal={signum}\n", encoding="utf-8")

    signal.signal(signal.SIGTERM, handle_term)
    signal.signal(signal.SIGINT, handle_term)

    write_status()

    while True:
        elapsed = int(time.time() - started_at.timestamp())
        if stop_file.exists() and cycles_completed > 0:
            state = "stopped"
            break
        if elapsed >= args.min_seconds and cycles_completed > 0:
            state = "completed"
            break

        current_cycle += 1
        cycle_dir = run_dir / f"cycle-{current_cycle}"
        cycle_dir.mkdir(parents=True, exist_ok=True)
        _append_line(summary_log, f"=== cycle {current_cycle} start {_utc_iso()} elapsed={elapsed}s ===")
        write_status()
        cycle_started = time.time()
        log_path = cycle_dir / "command.log"
        with log_path.open("w", encoding="utf-8") as handle:
            result = subprocess.run(
                ["make", args.target],
                stdout=handle,
                stderr=subprocess.STDOUT,
                text=True,
            )
        cycle_seconds = int(time.time() - cycle_started)
        cycles_completed += 1
        if result.returncode == 0:
            pass_cycles += 1
            last_cycle_status = "pass"
        else:
            fail_cycles += 1
            last_cycle_status = "fail"
            failure_tail = _tail_text(log_path, max_lines=120)
            failure_tail_path = cycle_dir / "failure-tail.log"
            failure_tail_path.write_text(failure_tail, encoding="utf-8")
            failure_texts.append(failure_tail)
        total_seconds = int(time.time() - started_at.timestamp())
        _append_line(
            summary_log,
            (
                f"cycle={current_cycle} status={last_cycle_status} cycle_seconds={cycle_seconds} "
                f"total_seconds={total_seconds} finished={_utc_iso()} "
                f"pass_cycles={pass_cycles} fail_cycles={fail_cycles}"
            ),
        )
        write_status()

    _write_operator_burden_snapshot(end_snapshot)
    total_seconds = int(time.time() - started_at.timestamp())
    _append_line(
        summary_log,
        (
            f"completed iter={current_cycle} total_seconds={total_seconds} "
            f"pass_cycles={pass_cycles} fail_cycles={fail_cycles} run_dir={run_dir}"
        ),
    )
    write_status()
    if args.pid_file.exists():
        try:
            if args.pid_file.read_text(encoding="utf-8").strip() == str(os.getpid()):
                args.pid_file.unlink()
        except OSError:
            pass
    return 0


def status_sidecar(args: argparse.Namespace) -> int:
    run_dir = _load_current_run_dir(args.current_file)
    status = _read_json(_status_path(run_dir))
    print(_render_status(status, args.pid_file))
    return 0


def stop_sidecar(args: argparse.Namespace) -> int:
    run_dir = _load_current_run_dir(args.current_file)
    stop_file = run_dir / STOP_FILE_NAME
    stop_file.write_text(_utc_iso(), encoding="utf-8")
    pid = ""
    if args.pid_file.exists():
        pid = args.pid_file.read_text(encoding="utf-8").strip()
    if pid:
        print(f"eval-sidecar stop requested (PID {pid}).")
    else:
        print("eval-sidecar stop requested.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the eval sidecar loop.")
    run_parser.add_argument("--target", default=DEFAULT_TARGET)
    run_parser.add_argument("--min-seconds", type=int, default=DEFAULT_MIN_SECONDS)
    run_parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    run_parser.add_argument("--pid-file", type=Path, default=DEFAULT_PID_FILE)
    run_parser.add_argument("--current-file", type=Path, default=DEFAULT_CURRENT_FILE)
    run_parser.set_defaults(func=run_sidecar)

    status_parser = subparsers.add_parser("status", help="Show current eval sidecar status.")
    status_parser.add_argument("--current-file", type=Path, default=DEFAULT_CURRENT_FILE)
    status_parser.add_argument("--pid-file", type=Path, default=DEFAULT_PID_FILE)
    status_parser.set_defaults(func=status_sidecar)

    stop_parser = subparsers.add_parser("stop", help="Request that the current eval sidecar stop.")
    stop_parser.add_argument("--current-file", type=Path, default=DEFAULT_CURRENT_FILE)
    stop_parser.add_argument("--pid-file", type=Path, default=DEFAULT_PID_FILE)
    stop_parser.set_defaults(func=stop_sidecar)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
