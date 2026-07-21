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

make_bin=$(polinko_require_make_command "build-week demo")
python_bin=$(polinko_default_python_bin)

DEMO_TOTAL_STEPS=6
demo_step_number=0
pass_total=0
fail_total=0
error_total=0

step() {
	demo_step_number=$((demo_step_number + 1))
	printf '\n[demo] %s/%s %s\n' "$demo_step_number" "$DEMO_TOTAL_STEPS" "$1"
}

pass() {
	pass_total=$((pass_total + 1))
	printf '[PASS] %s\n' "$1"
}

fail() {
	fail_total=$((fail_total + 1))
	printf '[FAIL] %s\n' "$1"
}

error() {
	error_total=$((error_total + 1))
	printf '[ERROR] %s\n' "$1"
}

summary() {
	printf '\nSummary\n'
	printf '[PASS]: %s\n' "$pass_total"
	printf '[FAIL]: %s\n' "$fail_total"
	printf '[ERROR]: %s\n' "$error_total"
}

cleanup() {
	"$make_bin" --no-print-directory server-daemon-stop >/dev/null 2>&1 || true
}
trap cleanup EXIT

run_and_report() {
	local label=$1
	shift
	printf 'running: %s\n' "$*"
	if "$@"; then
		pass "$label"
	else
		fail "$label"
		summary
		exit 1
	fi
}

echo "== Polinko Build Week demo =="
echo "A visible terminal runbook: preflight -> API smoke -> OCR binary eval -> artifacts."

step "preflight"
pass "repo root: $POLINKO_REPO_ROOT"
printf 'branch: %s\n' "$(git branch --show-current)"
git status --short --branch
pass "workspace context printed"

if [ -f ".local/eval_cases/ocr_transcript_cases_growth.json" ]; then
	pass "OCR growth case packet present"
else
	fail "OCR growth case packet missing"
	summary
	exit 1
fi

if "$python_bin" - <<'PY'
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
raise SystemExit(0 if os.environ.get("OPENAI_API_KEY") else 1)
PY
then
	pass "OpenAI API key visible"
else
	fail "OpenAI API key missing"
	summary
	exit 1
fi

step "API smoke"
run_and_report "api-smoke completed" "$make_bin" --no-print-directory api-smoke

step "OCR binary eval"
run_and_report "OCR smoke completed" "$make_bin" --no-print-directory build-week-ocr-smoke-demo

step "OCR result counts"
"$python_bin" - <<'PY' > .local/eval_reports/build_week_demo_ocr_counts.env
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

path = Path(".local/eval_reports/build_week_ocr_smoke_demo.json")
payload = json.loads(path.read_text(encoding="utf-8"))
counts = Counter(str(case.get("status", "ERROR")) for case in payload.get("cases", []))
print(f"ocr_pass={counts.get('PASS', 0)}")
print(f"ocr_fail={counts.get('FAIL', 0)}")
print(f"ocr_error={counts.get('ERROR', 0)}")
PY
# shellcheck source=/dev/null
. .local/eval_reports/build_week_demo_ocr_counts.env
pass_total=$((pass_total + ocr_pass))
fail_total=$((fail_total + ocr_fail))
error_total=$((error_total + ocr_error))
printf '[PASS] OCR cases: %s\n' "$ocr_pass"
if [ "$ocr_fail" -eq 0 ]; then
	pass "OCR failed cases: 0"
else
	printf '[FAIL] OCR failed cases: %s\n' "$ocr_fail"
fi
if [ "$ocr_error" -eq 0 ]; then
	pass "OCR error cases: 0"
else
	printf '[ERROR] OCR error cases: %s\n' "$ocr_error"
fi

step "evidence artifacts"
for artifact in \
	".local/eval_reports/build_week_ocr_smoke_demo.json" \
	".local/eval_reports/build_week_ocr_smoke_demo.log"; do
	if [ -s "$artifact" ]; then
		pass "$artifact"
	else
		fail "$artifact"
	fi
done

step "cleanup"
if "$make_bin" --no-print-directory server-daemon-stop >/dev/null 2>&1; then
	pass "server stopped"
else
	error "server stop command failed"
fi

summary
