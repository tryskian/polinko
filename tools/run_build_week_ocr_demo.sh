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

make_bin=$(polinko_require_make_command "build-week OCR demo")
python_bin=$(polinko_default_python_bin)
summary_path=${BUILD_WEEK_OCR_DEMO_SUMMARY:-.local/eval_reports/build_week_ocr_demo_summary.md}
stability_path=${BUILD_WEEK_OCR_DEMO_STABILITY:-.local/eval_reports/ocr_growth_stability.slice-offset0-max1.json}
run_id_path=${BUILD_WEEK_OCR_DEMO_RUN_ID_PATH:-.local/eval_reports/build_week_ocr_demo_run_id.txt}
cases_path=${BUILD_WEEK_OCR_DEMO_CASES:-.local/eval_cases/ocr_transcript_cases_growth.json}

cleanup() {
	"$make_bin" --no-print-directory server-daemon-stop >/dev/null 2>&1 || true
}
trap cleanup EXIT

mkdir -p "$(dirname -- "$summary_path")"

echo "== Polinko Build Week OCR demo =="
echo "A one-case OCR eval run, shown as source evidence -> binary gate -> report."
echo
echo "1. Current manual-eval warehouse"
"$make_bin" --no-print-directory manual-evals-db-status
echo

echo "2. What is being evaluated"
"$python_bin" - "$cases_path" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

cases_path = Path(sys.argv[1])
payload = json.loads(cases_path.read_text(encoding="utf-8"))
cases = payload.get("cases") if isinstance(payload.get("cases"), list) else []
case = cases[0] if cases else {}

def joined(value: object) -> str:
    if isinstance(value, list):
        return " | ".join(str(item) for item in value if str(item).strip())
    return str(value or "").strip()

print(f"case_id: {case.get('id', '')}")
print(f"source_image: {case.get('source_name') or case.get('image_path') or ''}")
print(f"transcription_mode: {case.get('transcription_mode', '')}")
print("task: read the image and return OCR text for this one source case")
print("binary_gate:")
must_contain_any = joined(case.get("must_contain_any"))
if must_contain_any:
    print(f"  PASS requires any signal: {must_contain_any}")
must_not_contain_words = joined(case.get("must_not_contain_words"))
if must_not_contain_words:
    print(f"  FAIL if output uses uncertainty words: {must_not_contain_words}")
min_chars = case.get("min_chars")
if min_chars not in ("", None):
    print(f"  PASS requires at least {min_chars} extracted characters")
print(f"case_packet: {cases_path}")
PY
echo

echo "3. How the eval runs"
cat <<'EOF'
command:
  make eval-ocr-transcript-stability-growth \
    OCR_GROWTH_STABILITY_RUNS=1 \
    OCR_GROWTH_EVAL_MAX_CASES=1 \
    OCR_GROWTH_OCR_RETRIES=1

scope:
  runs: 1
  cases: 1
  output: local JSON report plus stability summary
EOF
echo

echo "4. Live OCR binary gate"
"$make_bin" --no-print-directory eval-ocr-transcript-stability-growth \
	OCR_GROWTH_STABILITY_RUNS=1 \
	OCR_GROWTH_EVAL_MAX_CASES=1 \
	OCR_GROWTH_OCR_RETRIES=1 \
	OCR_GROWTH_OCR_RETRY_DELAY_MS=300 \
	OCR_GROWTH_CASE_DELAY_MS=0 \
	OCR_GROWTH_RATE_LIMIT_COOLDOWN_MS=1000 \
	OCR_MAX_CONSEC_RATE_LIMIT_ERRORS=1
echo

"$python_bin" - "$stability_path" "$run_id_path" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

stability_path = Path(sys.argv[1])
run_id_path = Path(sys.argv[2])
payload = json.loads(stability_path.read_text(encoding="utf-8"))
run_id = str(payload.get("run_id", "")).strip()
run_id_path.write_text(run_id + "\n", encoding="utf-8")
case = (payload.get("cases") or [{}])[0]
summary = payload.get("summary") or {}
status = (case.get("statuses") or [""])[0]
print("5. Binary result")
print(f"run_id={run_id}")
print(f"case_id={case.get('id', '')}")
print(f"signal={status}")
print(f"stable_decision_cases={summary.get('stable_decision_cases', 0)}")
print(f"decision_flaky_cases={summary.get('decision_flaky_cases', 0)}")
print(f"always_pass_cases={summary.get('always_pass_cases', 0)}")
print(f"always_fail_cases={summary.get('always_fail_cases', 0)}")
print(f"output_variant_cases={summary.get('output_variant_cases', 0)}")
PY
echo

run_id=$(cat "$run_id_path")
per_run_report=".local/eval_reports/ocr_growth_stability_runs/ocr-${run_id}-r01.json"

echo "6. OCR evidence and report"
"$python_bin" - "$per_run_report" <<'PY'
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

report_path = Path(sys.argv[1])
payload = json.loads(report_path.read_text(encoding="utf-8"))
case = (payload.get("cases") or [{}])[0]
print(f"source_name={case.get('source_name', '')}")
print(f"char_count={case.get('char_count', 0)}")
print("extracted_text_recorded=yes")
print(f"report_json={report_path}")
extracted = str(case.get("extracted_text") or "").strip()
if extracted:
    print("extracted_text_preview:")
    preview = extracted.replace("\r\n", "\n").replace("\r", "\n")
    lines = preview.splitlines()
    visible = "\n".join(lines[:8])
    wrapped = textwrap.shorten(visible, width=900, placeholder="...")
    for line in wrapped.splitlines():
        print(f"  {line}")
PY
echo

echo "7. Existing repeated-run OCR baseline"
"$python_bin" - <<'PY'
from __future__ import annotations

import json
from pathlib import Path

payload = json.loads(Path(".local/eval_reports/ocr_growth_stability.json").read_text(encoding="utf-8"))
summary = payload.get("summary") or {}
print(f"cases_total={summary.get('cases_total', 0)}")
print(f"stable_decision_cases={summary.get('stable_decision_cases', 0)}")
print(f"always_pass_cases={summary.get('always_pass_cases', 0)}")
print(f"decision_flaky_cases={summary.get('decision_flaky_cases', 0)}")
PY
echo

"$python_bin" - "$summary_path" "$stability_path" "$per_run_report" <<'PY'
from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

summary_path = Path(sys.argv[1])
stability_path = Path(sys.argv[2])
per_run_report = Path(sys.argv[3])
stability = json.loads(stability_path.read_text(encoding="utf-8"))
per_run = json.loads(per_run_report.read_text(encoding="utf-8"))
case = (stability.get("cases") or [{}])[0]
run_case = (per_run.get("cases") or [{}])[0]
summary = stability.get("summary") or {}
baseline = json.loads(Path(".local/eval_reports/ocr_growth_stability.json").read_text(encoding="utf-8"))
baseline_summary = baseline.get("summary") or {}
status = (case.get("statuses") or [""])[0]

summary_path.write_text(
	f"""<!-- @format -->

# Build Week OCR Demo Capture

Generated: {datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}

## Live Gate

- run_id: `{stability.get('run_id', '')}`
- case_id: `{case.get('id', '')}`
- source: `{run_case.get('source_name', '')}`
- status: `{status}`
- char_count: `{run_case.get('char_count', 0)}`
- stability report: `{stability_path}`
- per-run report: `{per_run_report}`

## One-Case Summary

- stable_decision_cases: `{summary.get('stable_decision_cases', 0)}`
- decision_flaky_cases: `{summary.get('decision_flaky_cases', 0)}`
- always_pass_cases: `{summary.get('always_pass_cases', 0)}`
- always_fail_cases: `{summary.get('always_fail_cases', 0)}`
- output_variant_cases: `{summary.get('output_variant_cases', 0)}`

## Current OCR Baseline

- cases_total: `{baseline_summary.get('cases_total', 0)}`
- stable_decision_cases: `{baseline_summary.get('stable_decision_cases', 0)}`
- always_pass_cases: `{baseline_summary.get('always_pass_cases', 0)}`
- decision_flaky_cases: `{baseline_summary.get('decision_flaky_cases', 0)}`

## Demo Read

Polinko starts from source evidence, applies a human-defined binary gate, and
keeps the result inspectable as a repo-native report. The live run shows the
gate working on one OCR case. The existing OCR baseline shows the signal across
the mature lane.
""",
	encoding="utf-8",
)
print(f"summary_written={summary_path}")
PY
