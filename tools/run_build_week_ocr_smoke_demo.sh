#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
# shellcheck source=tools/make_runtime.sh
source "$script_dir/make_runtime.sh"
# shellcheck source=tools/python_runtime.sh
source "$script_dir/python_runtime.sh"

polinko_cd_repo_root

make_bin=$(polinko_require_make_command "build-week OCR smoke demo")
python_bin=$(polinko_default_python_bin)
server_daemon_script=${EVAL_SERVER_DAEMON_SCRIPT:-./tools/ensure_eval_server_daemon.sh}
cases_path=${BUILD_WEEK_OCR_SMOKE_CASES_PATH:-.local/eval_cases/ocr_transcript_cases_growth.json}
max_cases=${BUILD_WEEK_OCR_SMOKE_CASES:-5}
offset=${BUILD_WEEK_OCR_SMOKE_OFFSET:-0}
run_id=${BUILD_WEEK_OCR_SMOKE_RUN_ID:-build-week-ocr-smoke-$(date +%s)}
report_json=${BUILD_WEEK_OCR_SMOKE_REPORT:-.local/eval_reports/build_week_ocr_smoke_demo.json}
log_path=${BUILD_WEEK_OCR_SMOKE_LOG:-.local/eval_reports/build_week_ocr_smoke_demo.log}

cleanup() {
	"$make_bin" --no-print-directory server-daemon-stop >/dev/null 2>&1 || true
}
trap cleanup EXIT

mkdir -p "$(dirname -- "$report_json")" "$(dirname -- "$log_path")"

echo "== Polinko OCR smoke demo =="
echo "cases=$max_cases"
echo "gate=PASS/FAIL"
echo

bash "$server_daemon_script" >/dev/null

"$python_bin" - "$cases_path" "$max_cases" "$offset" "$run_id" "$report_json" "$log_path" <<'PY'
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

cases_path = sys.argv[1]
max_cases = sys.argv[2]
offset = sys.argv[3]
run_id = sys.argv[4]
report_json = Path(sys.argv[5])
log_path = Path(sys.argv[6])

cmd = [
    sys.executable,
    "-u",
    "-m",
    "tools.eval_ocr",
    "--base-url",
    "http://127.0.0.1:8000",
    "--cases",
    cases_path,
    "--run-id",
    run_id,
    "--session-prefix",
    "build-week-ocr-smoke",
    "--timeout",
    "90",
    "--offset",
    offset,
    "--max-cases",
    max_cases,
    "--ocr-retries",
    "1",
    "--ocr-retry-delay-ms",
    "300",
    "--case-delay-ms",
    "0",
    "--rate-limit-cooldown-ms",
    "1000",
    "--max-consecutive-rate-limit-errors",
    "1",
    "--report-json",
    str(report_json),
    "--trace-jsonl",
    "",
]

status_re = re.compile(r"^\[(PASS|FAIL|ERROR)\]\s+(.+)$")
counts: Counter[str] = Counter()
printed = 0

with log_path.open("w", encoding="utf-8") as log:
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert proc.stdout is not None
    for raw_line in proc.stdout:
        log.write(raw_line)
        line = raw_line.rstrip("\n")
        match = status_re.match(line)
        if match:
            counts[match.group(1)] += 1
            printed += 1
            print(line, flush=True)
    return_code = proc.wait()

if return_code != 0:
    print()
    print(f"[ERROR] eval command exited with code {return_code}")
    print(f"log={log_path}")
    raise SystemExit(return_code)

if report_json.exists():
    payload = json.loads(report_json.read_text(encoding="utf-8"))
    cases = payload.get("cases") if isinstance(payload.get("cases"), list) else []
    counts = Counter(str(case.get("status", "ERROR")) for case in cases)

print()
print(f"[PASS]: {counts.get('PASS', 0)}")
print(f"[FAIL]: {counts.get('FAIL', 0)}")
print(f"[ERROR]: {counts.get('ERROR', 0)}")
print(f"report={report_json}")
print(f"log={log_path}")

if printed == 0:
    print()
    print("[ERROR] no status lines were emitted")
    raise SystemExit(1)
PY
