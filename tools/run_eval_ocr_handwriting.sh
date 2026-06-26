#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root

default_python_bin() {
	if [ -n "${PYTHON:-}" ]; then
		printf "%s\n" "$PYTHON"
		return
	fi
	for candidate in ./.venv/bin/python3.14 ./.venv/bin/python ./.venv/bin/python3; do
		if [ -x "$candidate" ] && "$candidate" -V >/dev/null 2>&1; then
			printf "%s\n" "$candidate"
			return
		fi
	done
	printf "%s\n" python3
}

if [ "$#" -ne 1 ]; then
	echo "Usage: run_eval_ocr_handwriting.sh <run|report>" >&2
	exit 2
fi

mode=$1
python_bin=$(default_python_bin)
cases_path=${OCR_HANDWRITING_CASES:-.local/eval_cases/ocr_handwriting_eval_cases.json}
timeout_seconds=${OCR_EVAL_TIMEOUT:-90}
ocr_retries=${OCR_EVAL_OCR_RETRIES:-2}
ocr_retry_delay_ms=${OCR_EVAL_OCR_RETRY_DELAY_MS:-750}
max_consecutive_rate_limit_errors=${OCR_MAX_CONSEC_RATE_LIMIT_ERRORS:-3}
report_dir=${EVAL_REPORTS_DIR:-eval_reports}
run_id=${EVAL_REPORT_RUN_ID:-$(date +%Y%m%d-%H%M%S)}

case "$mode" in
run|report)
	;;
*)
	echo "Unknown OCR handwriting eval mode: $mode" >&2
	exit 2
	;;
esac

if [ ! -f "$cases_path" ]; then
	echo "Handwriting cases file not found: $cases_path"
	echo "Create it with image_path entries (see docs/runtime/RUNBOOK.md)."
	exit 1
fi

case "$mode" in
run)
	exec "$python_bin" -m tools.eval_ocr \
		--timeout "$timeout_seconds" \
		--cases "$cases_path" \
		--strict \
		--show-text \
		--ocr-retries "$ocr_retries" \
		--ocr-retry-delay-ms "$ocr_retry_delay_ms" \
		--max-consecutive-rate-limit-errors "$max_consecutive_rate_limit_errors"
	;;
report)
	mkdir -p "$report_dir"
	exec "$python_bin" -m tools.eval_ocr \
		--timeout "$timeout_seconds" \
		--cases "$cases_path" \
		--strict \
		--show-text \
		--ocr-retries "$ocr_retries" \
		--ocr-retry-delay-ms "$ocr_retry_delay_ms" \
		--max-consecutive-rate-limit-errors "$max_consecutive_rate_limit_errors" \
		--run-id "$run_id" \
		--report-json "$report_dir/ocr-handwriting-$run_id.json"
	;;
esac
