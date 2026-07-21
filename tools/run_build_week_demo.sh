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
ocr_smoke_cases_path=${BUILD_WEEK_OCR_SMOKE_CASES_PATH:-.local/eval_cases/ocr_transcript_cases_growth.json}
ocr_smoke_max_cases=${BUILD_WEEK_OCR_SMOKE_CASES:-5}
ocr_smoke_offset=${BUILD_WEEK_OCR_SMOKE_OFFSET:-0}

DEMO_TOTAL_STEPS=7
demo_pause=${BUILD_WEEK_DEMO_PAUSE:-auto}
demo_open_ocr_source=${BUILD_WEEK_DEMO_OPEN_OCR_SOURCE:-auto}
demo_step_number=0
pass_total=0
fail_total=0
error_total=0

demo_should_pause() {
	case "$demo_pause" in
		1 | true | TRUE | yes | YES)
			return 0
			;;
		0 | false | FALSE | no | NO)
			return 1
			;;
		auto | "")
			[ -t 0 ] && [ -t 1 ]
			return
			;;
		*)
			printf '[ERROR] invalid BUILD_WEEK_DEMO_PAUSE value: %s\n' "$demo_pause" >&2
			printf 'Use auto, 1, or 0.\n' >&2
			exit 2
			;;
	esac
}

demo_pause_for_step() {
	local label=$1
	if demo_should_pause; then
		printf '[demo] ready: %s\n' "$label"
		printf '[demo] press Enter to run this step...'
		read -r _ || true
	fi
}

demo_should_open_ocr_source() {
	case "$demo_open_ocr_source" in
		1 | true | TRUE | yes | YES)
			return 0
			;;
		0 | false | FALSE | no | NO)
			return 1
			;;
		auto | "")
			demo_should_pause
			return
			;;
		*)
			printf '[ERROR] invalid BUILD_WEEK_DEMO_OPEN_OCR_SOURCE value: %s\n' "$demo_open_ocr_source" >&2
			printf 'Use auto, 1, or 0.\n' >&2
			exit 2
			;;
	esac
}

step() {
	local label=$1
	demo_step_number=$((demo_step_number + 1))
	printf '\n[demo] %s/%s %s\n' "$demo_step_number" "$DEMO_TOTAL_STEPS" "$label"
	demo_pause_for_step "$label"
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

codex_note() {
	printf '[codex] %s\n' "$1"
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
echo "A visible terminal runbook: preflight -> API smoke -> OCR source -> binary eval -> artifacts."
echo "presenter=codex"
if demo_should_pause; then
	echo "mode=interactive"
	echo "pace=press Enter before each step"
else
	echo "mode=continuous"
fi

step "preflight"
codex_note "First I check the repo state, case packet, and API key."
pass "repo root: $POLINKO_REPO_ROOT"
printf 'branch: %s\n' "$(git branch --show-current)"
git status --short --branch
pass "workspace context printed"

if [ -f "$ocr_smoke_cases_path" ]; then
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
codex_note "Next I smoke-test the local API endpoints used by the eval runner."
run_and_report "api-smoke completed" "$make_bin" --no-print-directory api-smoke

step "OCR source preview"
codex_note "Now I show the source artifact and gate before running OCR."
mkdir -p .local/eval_reports
if "$python_bin" - "$ocr_smoke_cases_path" "$ocr_smoke_max_cases" "$ocr_smoke_offset" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.ocr_export_refs import resolve_export_ref

cases_path = Path(sys.argv[1])
max_cases = int(sys.argv[2])
offset = int(sys.argv[3])
payload = json.loads(cases_path.read_text(encoding="utf-8"))
cases = payload["cases"] if isinstance(payload, dict) else payload
if offset < 0 or offset >= len(cases):
    raise SystemExit(f"offset {offset} is outside case packet length {len(cases)}")

case = cases[offset]
image_path = str(case.get("image_path", "")).strip()
resolved_image = resolve_export_ref(image_path)
preview_path = Path(".local/eval_reports/build_week_demo_ocr_source_path.txt")
preview_path.write_text(str(resolved_image), encoding="utf-8")

case_id = str(case.get("id", "")).strip()
source_name = str(case.get("source_name") or image_path or case_id).strip()
lane = str(case.get("lane", "")).strip()
mode = str(case.get("transcription_mode", "")).strip()
must_contain = [str(item) for item in case.get("must_contain_any", [])]
must_not_contain = [str(item) for item in case.get("must_not_contain_words", [])]

print(f"case={case_id}")
print(f"batch={max_cases} OCR cases from offset {offset}")
print(f"source={source_name}")
print(f"image={resolved_image}")
print(f"lane={lane}")
print(f"mode={mode}")
if must_contain:
    print("pass signal=contains one expected anchor:")
    print("  " + ", ".join(must_contain[:8]))
if must_not_contain:
    print("fail signal=contains blocked words:")
    print("  " + ", ".join(must_not_contain[:8]))
if not resolved_image.is_file():
    raise SystemExit(f"resolved image does not exist: {resolved_image}")
PY
then
	ocr_source_image=$(cat .local/eval_reports/build_week_demo_ocr_source_path.txt)
	pass "OCR source image resolved"
	if demo_should_open_ocr_source; then
		if command -v open >/dev/null 2>&1; then
			open "$ocr_source_image"
			pass "OCR source image opened"
		else
			error "open command unavailable; image path printed above"
		fi
	fi
else
	fail "OCR source preview failed"
	summary
	exit 1
fi

step "OCR binary eval"
codex_note "Now I run the OCR eval. Each case resolves to PASS, FAIL, or ERROR."
run_and_report "OCR smoke completed" "$make_bin" --no-print-directory build-week-ocr-smoke-demo

step "OCR result counts"
codex_note "Now I read the report back into counts so the result is visible at a glance."
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
codex_note "This run produced $ocr_pass passing OCR cases, $ocr_fail failures, and $ocr_error errors."

step "evidence artifacts"
codex_note "Then I check that the run left evidence artifacts, not just terminal output."
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
codex_note "Finally I stop the local server so the demo leaves the machine clean."
if "$make_bin" --no-print-directory server-daemon-stop >/dev/null 2>&1; then
	pass "server stopped"
else
	error "server stop command failed"
fi

summary
