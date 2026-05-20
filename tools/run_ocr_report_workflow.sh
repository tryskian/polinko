#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
	echo "Usage: run_ocr_report_workflow.sh <suite>" >&2
	exit 2
fi

suite=$1
report_builder_script=${OCR_REPORT_BUILDER_SCRIPT:-./tools/run_ocr_report_builder.sh}

require_file() {
	path=$1
	message=$2
	next_step=$3

	if [ ! -f "$path" ]; then
		echo "$message: $path"
		echo "Run: $next_step"
		exit 1
	fi
}

require_dir() {
	path=$1
	message=$2
	next_step=$3

	if [ ! -d "$path" ]; then
		echo "$message: $path"
		echo "Run: $next_step"
		exit 1
	fi
}

case "$suite" in
growth-metrics)
	require_file \
		"${OCR_TRANSCRIPT_CASES_GROWTH:-.local/eval_cases/ocr_transcript_cases_growth.json}" \
		"Transcript OCR growth cases not found" \
		"make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"
	require_dir \
		"${OCR_GROWTH_STABILITY_REPORT_DIR:-.local/eval_reports/ocr_growth_stability_runs}" \
		"OCR growth runs dir not found" \
		"make ocrstablegrowth"
	;;
growth-fail-cohort)
	require_file \
		"${OCR_GROWTH_STABILITY_OUTPUT:-.local/eval_reports/ocr_growth_stability.json}" \
		"OCR growth stability report not found" \
		"make ocrstablegrowth"
	require_file \
		"${OCR_TRANSCRIPT_CASES_GROWTH:-.local/eval_cases/ocr_transcript_cases_growth.json}" \
		"Transcript OCR growth cases not found" \
		"make ocrmine"
	require_file \
		"${OCR_TRANSCRIPT_REVIEW:-.local/eval_cases/ocr_transcript_cases_review.json}" \
		"Transcript OCR review report not found" \
		"make ocrmine"
	;;
focus-cases)
	require_file \
		"${OCR_GROWTH_FAIL_COHORT_JSON:-.local/eval_cases/ocr_growth_fail_cohort.json}" \
		"OCR growth fail cohort not found" \
		"make ocrfails"
	require_file \
		"${OCR_TRANSCRIPT_CASES_GROWTH:-.local/eval_cases/ocr_transcript_cases_growth.json}" \
		"Transcript OCR growth cases not found" \
		"make ocrmine"
	;;
focus-fail-patterns)
	require_file \
		"${OCR_FOCUS_OUTPUT:-.local/eval_reports/ocr_focus_stability.json}" \
		"OCR focus stability report not found" \
		"make eval-ocr-focus-stability"
	require_file \
		"${OCR_FOCUS_CASES_JSON:-.local/eval_cases/ocr_growth_focus_cases.json}" \
		"OCR focus cases not found" \
		"make ocrfocuscases"
	;;
*)
	echo "Unknown OCR report workflow suite: $suite" >&2
	exit 2
	;;
esac

exec bash "$report_builder_script" "$suite"
