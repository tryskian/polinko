#!/usr/bin/env sh
set -eu

if [ "$#" -ne 9 ]; then
	echo "Usage: run_eval_ocr_growth_batched.sh <cases-json> <batch-size> <ocr-retries> <ocr-retry-delay-ms> <offset> <max-cases> <report-dir> <output-json> <output-markdown>" >&2
	exit 2
fi

cases_path=$1
batch_size=$2
ocr_retries=$3
ocr_retry_delay_ms=$4
offset=$5
max_cases=$6
report_dir=$7
output_json=$8
output_markdown=$9

python_bin=${PYTHON:-python3}
server_daemon_script=${EVAL_SERVER_DAEMON_SCRIPT:-./tools/ensure_eval_server_daemon.sh}

export PYTHONUNBUFFERED=1

bash "$server_daemon_script"
exec "$python_bin" -m tools.eval_ocr_batched \
	--base-url "http://127.0.0.1:8000" \
	--cases "$cases_path" \
	--batch-size "$batch_size" \
	--ocr-retries "$ocr_retries" \
	--ocr-retry-delay-ms "$ocr_retry_delay_ms" \
	--offset "$offset" \
	--max-cases "$max_cases" \
	--report-dir "$report_dir" \
	--output-json "$output_json" \
	--output-markdown "$output_markdown"
