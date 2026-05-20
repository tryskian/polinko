#!/usr/bin/env sh
set -eu

python_bin=${PYTHON:-python3}
guard_script=${EVAL_CASE_GUARD_SCRIPT:-./tools/eval_case_guard.sh}
stability_runner_script=${OCR_STABILITY_RUNNER_SCRIPT:-./tools/run_eval_ocr_stability.sh}

focus_cases_json=${OCR_FOCUS_CASES_JSON:-.local/eval_cases/ocr_growth_focus_cases.json}
focus_runs=${OCR_FOCUS_RUNS:-3}
focus_ocr_retries=${OCR_FOCUS_OCR_RETRIES:-3}
focus_ocr_retry_delay_ms=${OCR_FOCUS_OCR_RETRY_DELAY_MS:-1000}
focus_case_delay_ms=${OCR_FOCUS_CASE_DELAY_MS:-1200}
focus_rate_limit_cooldown_ms=${OCR_FOCUS_RATE_LIMIT_COOLDOWN_MS:-12000}
focus_report_dir=${OCR_FOCUS_REPORT_DIR:-.local/eval_reports/ocr_focus_runs}
focus_output=${OCR_FOCUS_OUTPUT:-.local/eval_reports/ocr_focus_stability.json}
focus_skip_recent_rate_limit=${OCR_FOCUS_SKIP_RECENT_RATE_LIMIT:-true}
focus_rate_limit_backoff_seconds=${OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS:-900}
growth_fail_cohort_json=${OCR_GROWTH_FAIL_COHORT_JSON:-.local/eval_cases/ocr_growth_fail_cohort.json}

export PYTHON="$python_bin"

. "$guard_script"
eval_case_guard_or_exit \
	"$focus_cases_json" \
	"OCR focus cases not found" \
	"Run: make ocrfocuscases" \
	"No OCR focus cases available; skipping focus stability run."

if [ "$focus_skip_recent_rate_limit" = "true" ] && [ -f "$focus_output" ]; then
	skip=$("$python_bin" -m tools.should_skip_ocr_run \
		--report "$focus_output" \
		--backoff-seconds "$focus_rate_limit_backoff_seconds")
	if [ "$skip" = "1" ]; then
		echo "Skipping focus stability replay: recent rate-limit abort is still within backoff window (${focus_rate_limit_backoff_seconds}s)."
		exit 0
	fi
fi

if [ "$focus_skip_recent_rate_limit" = "true" ] && [ -f "$growth_fail_cohort_json" ]; then
	skip=$("$python_bin" -m tools.should_skip_ocr_run \
		--report "$growth_fail_cohort_json" \
		--backoff-seconds "$focus_rate_limit_backoff_seconds")
	if [ "$skip" = "1" ]; then
		echo "Skipping focus stability replay: recent growth fail cohort shows active rate-limit pressure (backoff ${focus_rate_limit_backoff_seconds}s)."
		exit 0
	fi
fi

exec bash "$stability_runner_script" \
	"$focus_cases_json" \
	"$focus_runs" \
	"$focus_ocr_retries" \
	"$focus_ocr_retry_delay_ms" \
	"$focus_case_delay_ms" \
	"$focus_rate_limit_cooldown_ms" \
	"$focus_report_dir" \
	"$focus_output"
