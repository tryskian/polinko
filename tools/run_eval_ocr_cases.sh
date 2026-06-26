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
	echo "Usage: run_eval_ocr_cases.sh <cases-json>" >&2
	exit 2
fi

cases_path=$1
python_bin=$(default_python_bin)
server_daemon_script=${EVAL_SERVER_DAEMON_SCRIPT:-./tools/ensure_eval_server_daemon.sh}
timeout_seconds=${OCR_EVAL_TIMEOUT:-90}
ocr_retries=${OCR_EVAL_OCR_RETRIES:-2}
ocr_retry_delay_ms=${OCR_EVAL_OCR_RETRY_DELAY_MS:-750}
max_consecutive_rate_limit_errors=${OCR_MAX_CONSEC_RATE_LIMIT_ERRORS:-3}

bash "$server_daemon_script"
exec "$python_bin" -m tools.eval_ocr \
	--timeout "$timeout_seconds" \
	--cases "$cases_path" \
	--strict \
	--show-text \
	--ocr-retries "$ocr_retries" \
	--ocr-retry-delay-ms "$ocr_retry_delay_ms" \
	--max-consecutive-rate-limit-errors "$max_consecutive_rate_limit_errors"
