#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
	echo "Usage: run_ocr_report_builder.sh <suite>" >&2
	exit 2
fi

suite=$1
python_bin=${PYTHON:-python3}

case "$suite" in
growth-metrics|growth-fail-cohort|focus-cases|focus-fail-patterns)
	;;
*)
	echo "Unknown OCR report-builder suite: $suite" >&2
	exit 2
	;;
esac

case "$suite" in
growth-metrics)
	exec "$python_bin" -m tools.eval_ocr_growth_metrics \
		--cases "${OCR_TRANSCRIPT_CASES_GROWTH:-.local/eval_cases/ocr_transcript_cases_growth.json}" \
		--runs-dir "${OCR_GROWTH_STABILITY_REPORT_DIR:-.local/eval_reports/ocr_growth_stability_runs}" \
		--output-json "${OCR_GROWTH_METRICS_OUTPUT:-.local/eval_reports/ocr_growth_metrics.json}" \
		--output-markdown "${OCR_GROWTH_METRICS_MARKDOWN:-.local/eval_reports/ocr_growth_metrics.md}" \
		--limit-runs "${OCR_GROWTH_LIMIT_RUNS:-0}"
	;;
growth-fail-cohort)
	set -- "$python_bin" -m tools.build_ocr_growth_fail_cohort \
		--stability-report "${OCR_GROWTH_STABILITY_OUTPUT:-.local/eval_reports/ocr_growth_stability.json}" \
		--cases "${OCR_TRANSCRIPT_CASES_GROWTH:-.local/eval_cases/ocr_transcript_cases_growth.json}" \
		--metrics "${OCR_GROWTH_METRICS_OUTPUT:-.local/eval_reports/ocr_growth_metrics.json}" \
		--review "${OCR_TRANSCRIPT_REVIEW:-.local/eval_cases/ocr_transcript_cases_review.json}" \
		--output-json "${OCR_GROWTH_FAIL_COHORT_JSON:-.local/eval_cases/ocr_growth_fail_cohort.json}" \
		--output-markdown "${OCR_GROWTH_FAIL_COHORT_MARKDOWN:-.local/eval_reports/ocr_growth_fail_cohort.md}" \
		--min-runs "${OCR_FAIL_COHORT_MIN_RUNS:-1}"
	if [ "${OCR_FAIL_COHORT_INCLUDE_UNSTABLE:-true}" = "true" ]; then
		set -- "$@" --include-unstable
	fi
	if [ "${OCR_FAIL_COHORT_REQUIRE_OCR_FRAMING:-true}" = "true" ]; then
		set -- "$@" --require-ocr-framing
	fi
	if [ "${OCR_FAIL_COHORT_INCLUDE_EXPLORATORY:-true}" = "true" ]; then
		set -- "$@" --include-exploratory
	fi
	set -- "$@" --exploratory-max-cases "${OCR_FAIL_COHORT_EXPLORATORY_MAX_CASES:-18}"
	exec "$@"
	;;
focus-cases)
	set -- "$python_bin" -m tools.build_ocr_focus_cases \
		--cohort "${OCR_GROWTH_FAIL_COHORT_JSON:-.local/eval_cases/ocr_growth_fail_cohort.json}" \
		--source-cases "${OCR_TRANSCRIPT_CASES_GROWTH:-.local/eval_cases/ocr_transcript_cases_growth.json}" \
		--output-cases "${OCR_FOCUS_CASES_JSON:-.local/eval_cases/ocr_growth_focus_cases.json}" \
		--max-cases "${OCR_FOCUS_MAX_CASES:-40}"
	if [ "${OCR_FOCUS_INCLUDE_FAIL_HISTORY:-true}" = "false" ]; then
		set -- "$@" --exclude-fail-history
	fi
	if [ "${OCR_FOCUS_INCLUDE_EXPLORATORY:-true}" = "false" ]; then
		set -- "$@" --exclude-exploratory
	fi
	exec "$@"
	;;
focus-fail-patterns)
	exec "$python_bin" -m tools.report_ocr_focus_fail_patterns \
		--stability-report "${OCR_FOCUS_OUTPUT:-.local/eval_reports/ocr_focus_stability.json}" \
		--focus-cases "${OCR_FOCUS_CASES_JSON:-.local/eval_cases/ocr_growth_focus_cases.json}" \
		--output-json "${OCR_FOCUS_FAIL_PATTERNS_JSON:-.local/eval_reports/ocr_focus_fail_patterns.json}" \
		--output-markdown "${OCR_FOCUS_FAIL_PATTERNS_MD:-.local/eval_reports/ocr_focus_fail_patterns.md}"
	;;
esac
