#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
# shellcheck source=tools/python_runtime.sh
. "$script_dir/python_runtime.sh"

if [ "$#" -ne 7 ]; then
	echo "Usage: run_eval_ocr_growth_cases.sh <cases-json> <timeout> <offset> <max-cases> <ocr-retries> <ocr-retry-delay-ms> <max-consecutive-rate-limit-errors>" >&2
	exit 2
fi

cases_path=$1
timeout_seconds=$2
offset=$3
max_cases=$4
ocr_retries=$5
ocr_retry_delay_ms=$6
max_consecutive_rate_limit_errors=$7

python_bin=$(polinko_default_python_bin)
server_daemon_script=${EVAL_SERVER_DAEMON_SCRIPT:-./tools/ensure_eval_server_daemon.sh}

export PYTHONUNBUFFERED=1

bash "$server_daemon_script"
exec "$python_bin" -m tools.eval_ocr \
	--timeout "$timeout_seconds" \
	--cases "$cases_path" \
	--show-text \
	--offset "$offset" \
	--max-cases "$max_cases" \
	--ocr-retries "$ocr_retries" \
	--ocr-retry-delay-ms "$ocr_retry_delay_ms" \
	--max-consecutive-rate-limit-errors "$max_consecutive_rate_limit_errors"
