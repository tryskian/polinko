#!/bin/zsh
set -u
REPO_ROOT="/Users/tryskian/Github/polinko"
cd "$REPO_ROOT" || exit 1
RUNNER_PID="$1"
SECS_TO_NOON="$2"
STOP_LOG=".local/logs/noon_stop.log"
DIGEST_TS=$(date +%Y%m%d_%H%M%S)
DIGEST_MD=".local/logs/noon_digest_${DIGEST_TS}.md"
DIGEST_LOG=".local/logs/noon_digest_${DIGEST_TS}.log"

echo "[watchdog-start] $(date -u +%Y-%m-%dT%H:%M:%SZ) runner=$RUNNER_PID secs_to_noon=$SECS_TO_NOON" >> "$STOP_LOG"
sleep "$SECS_TO_NOON"

if [ -n "$RUNNER_PID" ] && ps -p "$RUNNER_PID" >/dev/null 2>&1; then
  kill "$RUNNER_PID" || true
  sleep 1
fi
pkill -f "make ocrkernel CGPT_EXPORT_ROOT=/Users/tryskian/Library/CloudStorage/Dropbox/CGPT-DATA-EXPORT" || true
pkill -f "tools.eval_ocr --cases .local/eval_cases/ocr_transcript_cases_growth.json" || true

echo "[watchdog-stop] $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$STOP_LOG"

{
  echo "# Noon Kernel Digest"
  echo
  echo "generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  make ocrgrowth
  make ocrfails
  make ocrfocuscases
  make eval-ocr-focus-stability OCR_FOCUS_RUNS=2 OCR_FOCUS_MAX_CASES=12 OCR_FOCUS_OCR_RETRIES=0 OCR_MAX_CONSEC_RATE_LIMIT_ERRORS=1 || true
  make ocrfocusreport
  echo
  echo "## Quick Summary"
  ./venv/bin/python - <<'PY'
import json
from pathlib import Path

def load(path):
    p=Path(path)
    return json.loads(p.read_text()) if p.exists() else {}

growth=load('.local/eval_reports/ocr_growth_metrics.json')
cohort=load('.local/eval_cases/ocr_growth_fail_cohort.json')
focus=load('.local/eval_reports/ocr_focus_fail_patterns.json')

print(f"- growth cases_total: {growth.get('summary',{}).get('cases_total','n/a')}")
print(f"- growth first_pass_fail_rate: {growth.get('summary',{}).get('first_pass_fail_rate','n/a')}")
print(f"- fail cohort selected_fail_cases: {cohort.get('summary',{}).get('selected_fail_cases','n/a')}")
fs=focus.get('summary',{})
print(f"- focus failing_cases: {fs.get('failing_cases','n/a')}")
print(f"- focus rate_limit_pressure: {fs.get('rate_limit_pressure','n/a')}")
print(f"- focus recommended bucket: {(focus.get('recommended_next_kernel') or fs.get('recommended_next_kernel') or {}).get('bucket','n/a')}")
PY
} > "$DIGEST_MD" 2> "$DIGEST_LOG"

echo "$DIGEST_MD" > .local/logs/noon_digest.current
