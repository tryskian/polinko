#!/usr/bin/env sh
set -eu

usage() {
	echo "Usage: run_ocr_growth_case_workflow.sh <eval|batched>" >&2
}

if [ "$#" -ne 1 ]; then
	usage
	exit 2
fi

suite=$1
case "$suite" in
eval|batched)
	;;
*)
	echo "Unknown OCR growth case workflow suite: $suite" >&2
	exit 2
	;;
esac

common_script=${OCR_WORKFLOW_COMMON_SCRIPT:-./tools/ocr_workflow_common.sh}
growth_eval_runner_script=${OCR_GROWTH_EVAL_RUNNER_SCRIPT:-./tools/run_eval_ocr_growth_cases.sh}
growth_batch_runner_script=${OCR_GROWTH_BATCH_RUNNER_SCRIPT:-./tools/run_eval_ocr_growth_batched.sh}

cases_path=${OCR_TRANSCRIPT_CASES_GROWTH:-.local/eval_cases/ocr_transcript_cases_growth.json}
eval_timeout=${OCR_EVAL_TIMEOUT:-90}
growth_eval_offset=${OCR_GROWTH_EVAL_OFFSET:-0}
growth_eval_max_cases=${OCR_GROWTH_EVAL_MAX_CASES:-0}
eval_ocr_retries=${OCR_EVAL_OCR_RETRIES:-2}
eval_ocr_retry_delay_ms=${OCR_EVAL_OCR_RETRY_DELAY_MS:-750}
max_consecutive_rate_limit_errors=${OCR_MAX_CONSEC_RATE_LIMIT_ERRORS:-3}
growth_batch_size=${OCR_GROWTH_BATCH_SIZE:-40}
growth_ocr_retries=${OCR_GROWTH_OCR_RETRIES:-2}
growth_ocr_retry_delay_ms=${OCR_GROWTH_OCR_RETRY_DELAY_MS:-750}
growth_batch_report_dir=${OCR_GROWTH_BATCH_REPORT_DIR:-.local/eval_reports/ocr_growth_batched_runs}
growth_batch_summary_json=${OCR_GROWTH_BATCH_SUMMARY_JSON:-.local/eval_reports/ocr_growth_batched_summary.json}
growth_batch_summary_md=${OCR_GROWTH_BATCH_SUMMARY_MD:-.local/eval_reports/ocr_growth_batched_summary.md}

# shellcheck source=./tools/ocr_workflow_common.sh
. "$common_script"
ocr_workflow_use_eval_case_guard
eval_case_guard_or_exit \
	"$cases_path" \
	"Transcript OCR growth cases not found" \
	"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
	"No transcript OCR growth cases available yet; skipping eval."

case "$suite" in
eval)
	exec bash "$growth_eval_runner_script" \
		"$cases_path" \
		"$eval_timeout" \
		"$growth_eval_offset" \
		"$growth_eval_max_cases" \
		"$eval_ocr_retries" \
		"$eval_ocr_retry_delay_ms" \
		"$max_consecutive_rate_limit_errors"
	;;
batched)
	exec bash "$growth_batch_runner_script" \
		"$cases_path" \
		"$growth_batch_size" \
		"$growth_ocr_retries" \
		"$growth_ocr_retry_delay_ms" \
		"$growth_eval_offset" \
		"$growth_eval_max_cases" \
		"$growth_batch_report_dir" \
		"$growth_batch_summary_json" \
		"$growth_batch_summary_md"
	;;
esac
