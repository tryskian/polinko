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

python_bin=$(default_python_bin)
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
