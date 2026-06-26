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

if [ "$#" -ne 12 ]; then
	echo "Usage: run_eval_ocr_growth_stability.sh <cases-json> <runs> <offset> <max-cases> <timeout> <ocr-retries> <ocr-retry-delay-ms> <case-delay-ms> <rate-limit-cooldown-ms> <max-consecutive-rate-limit-errors> <report-dir> <output-json>" >&2
	exit 2
fi

cases_path=$1
runs=$2
offset=$3
max_cases=$4
timeout_seconds=$5
ocr_retries=$6
ocr_retry_delay_ms=$7
case_delay_ms=$8
rate_limit_cooldown_ms=$9
max_consecutive_rate_limit_errors=${10}
report_dir=${11}
output_json=${12}

python_bin=$(default_python_bin)
server_daemon_script=${EVAL_SERVER_DAEMON_SCRIPT:-./tools/ensure_eval_server_daemon.sh}

export PYTHONUNBUFFERED=1

bash "$server_daemon_script"
exec "$python_bin" -m tools.eval_ocr_stability \
	--base-url "http://127.0.0.1:8000" \
	--cases "$cases_path" \
	--runs "$runs" \
	--offset "$offset" \
	--max-cases "$max_cases" \
	--timeout "$timeout_seconds" \
	--ocr-retries "$ocr_retries" \
	--ocr-retry-delay-ms "$ocr_retry_delay_ms" \
	--case-delay-ms "$case_delay_ms" \
	--rate-limit-cooldown-ms "$rate_limit_cooldown_ms" \
	--max-consecutive-rate-limit-errors "$max_consecutive_rate_limit_errors" \
	--stop-on-rate-limit-abort \
	--report-dir "$report_dir" \
	--output-json "$output_json"
