#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
# shellcheck source=tools/python_runtime.sh
. "$script_dir/python_runtime.sh"

if [ "$#" -ne 1 ]; then
	echo "Usage: run_eval_report.sh <suite>" >&2
	exit 2
fi

suite=$1
python_bin=$(polinko_default_python_bin)
server_daemon_script=${EVAL_SERVER_DAEMON_SCRIPT:-./tools/ensure_eval_server_daemon.sh}
report_dir=${EVAL_REPORTS_DIR:-eval_reports}
run_id=${EVAL_REPORT_RUN_ID:-$(date +%Y%m%d-%H%M%S)}

case "$suite" in
retrieval|file-search|hallucination|style|response-behaviour|ocr-safety|ocr|ocr-recovery|clip-ab)
	;;
*)
	echo "Unknown eval report suite: $suite" >&2
	exit 2
	;;
esac

prepare_report_dir() {
	if ! mkdir -p "$report_dir" 2>/dev/null; then
		echo "eval-report failed to prepare report directory: $report_dir" >&2
		return 1
	fi
}

if ! prepare_report_dir; then
	exit 1
fi
if ! bash "$server_daemon_script"; then
	echo "eval-report failed to start eval server daemon: $server_daemon_script" >&2
	exit 1
fi

case "$suite" in
retrieval)
	exec "$python_bin" -m tools.eval_retrieval \
		--run-id "$run_id" \
		--request-retries "${RETRIEVAL_REQUEST_RETRIES:-2}" \
		--request-retry-delay-ms "${RETRIEVAL_REQUEST_RETRY_DELAY_MS:-750}" \
		--report-json "$report_dir/retrieval-$run_id.json"
	;;
file-search)
	exec "$python_bin" -m tools.eval_file_search \
		--run-id "$run_id" \
		--report-json "$report_dir/file-search-$run_id.json"
	;;
hallucination)
	exec "$python_bin" -m tools.eval_hallucination \
		--run-id "$run_id" \
		--report-json "$report_dir/hallucination-$run_id.json" \
		--min-acceptable-score "${HALLUCINATION_MIN_ACCEPTABLE_SCORE:-5}"
	;;
style)
	exec "$python_bin" -m tools.eval_style \
		--run-id "$run_id" \
		--report-json "$report_dir/style-$run_id.json" \
		--case-attempts "${STYLE_CASE_ATTEMPTS:-1}" \
		--min-pass-attempts "${STYLE_MIN_PASS_ATTEMPTS:-1}"
	;;
response-behaviour)
	exec "$python_bin" -m tools.eval_response_behaviour \
		--run-id "$run_id" \
		--report-json "$report_dir/response-behaviour-$run_id.json"
	;;
ocr-safety)
	exec "$python_bin" -m tools.eval_response_behaviour \
		--suite-id ocr_safety \
		--cases "${OCR_SAFETY_CASES:-docs/eval/beta_2_0/ocr_safety_eval_cases.json}" \
		--session-prefix ocr-safety-eval \
		--run-id "$run_id" \
		--report-json "$report_dir/ocr-safety-$run_id.json"
	;;
ocr)
	exec "$python_bin" -m tools.eval_ocr \
		--timeout "${OCR_EVAL_TIMEOUT:-90}" \
		--ocr-retries "${OCR_EVAL_OCR_RETRIES:-2}" \
		--ocr-retry-delay-ms "${OCR_EVAL_OCR_RETRY_DELAY_MS:-750}" \
		--max-consecutive-rate-limit-errors "${OCR_MAX_CONSEC_RATE_LIMIT_ERRORS:-3}" \
		--run-id "$run_id" \
		--report-json "$report_dir/ocr-$run_id.json"
	;;
ocr-recovery)
	exec "$python_bin" -m tools.eval_ocr_recovery \
		--run-id "$run_id" \
		--report-json "$report_dir/ocr-recovery-$run_id.json"
	;;
clip-ab)
	exec "$python_bin" -m tools.eval_clip_ab \
		--source-types "${CLIP_AB_SOURCE_TYPES:-image}" \
		--run-id "$run_id" \
		--report-json "$report_dir/clip-ab-$run_id.json"
	;;
esac
