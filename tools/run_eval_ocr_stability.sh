#!/usr/bin/env sh
set -eu

if [ "$#" -ne 8 ]; then
	echo "Usage: run_eval_ocr_stability.sh <cases-json> <runs> <ocr-retries> <ocr-retry-delay-ms> <case-delay-ms> <rate-limit-cooldown-ms> <report-dir> <output-json>" >&2
	exit 2
fi

cases_path=$1
runs=$2
ocr_retries=$3
ocr_retry_delay_ms=$4
case_delay_ms=$5
rate_limit_cooldown_ms=$6
report_dir=$7
output_json=$8

python_bin=${PYTHON:-python3}
server_daemon_script=${EVAL_SERVER_DAEMON_SCRIPT:-./tools/ensure_eval_server_daemon.sh}
timeout_seconds=${OCR_EVAL_TIMEOUT:-90}
max_consecutive_rate_limit_errors=${OCR_MAX_CONSEC_RATE_LIMIT_ERRORS:-3}

if [ "${OCR_STABILITY_PYTHONUNBUFFERED:-}" = "1" ]; then
	export PYTHONUNBUFFERED=1
fi

bash "$server_daemon_script"
exec "$python_bin" -m tools.eval_ocr_stability \
	--base-url "http://127.0.0.1:8000" \
	--cases "$cases_path" \
	--runs "$runs" \
	--timeout "$timeout_seconds" \
	--ocr-retries "$ocr_retries" \
	--ocr-retry-delay-ms "$ocr_retry_delay_ms" \
	--case-delay-ms "$case_delay_ms" \
	--rate-limit-cooldown-ms "$rate_limit_cooldown_ms" \
	--max-consecutive-rate-limit-errors "$max_consecutive_rate_limit_errors" \
	--stop-on-rate-limit-abort \
	--strict \
	--report-dir "$report_dir" \
	--output-json "$output_json"
