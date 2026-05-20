#!/usr/bin/env sh
set -eu

usage() {
	echo "Usage: run_ocr_transcript_lane_workflow.sh <case|stability> <lane>" >&2
	echo "Lanes: handwriting, handwriting-benchmark, typed, typed-benchmark, illustration, illustration-benchmark" >&2
}

if [ "$#" -ne 2 ]; then
	usage
	exit 2
fi

mode=$1
lane=$2
missing_hint="Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"
guarded_case_runner_script=${OCR_GUARDED_CASE_RUNNER_SCRIPT:-./tools/run_guarded_ocr_case_eval.sh}
eval_runner_script=${OCR_EVAL_RUNNER_SCRIPT:-./tools/run_eval_ocr_cases.sh}
stability_runner_script=${OCR_STABILITY_RUNNER_SCRIPT:-./tools/run_eval_ocr_stability.sh}

case "$mode:$lane" in
case:handwriting)
	cases_path=${OCR_TRANSCRIPT_CASES_HANDWRITING:-.local/eval_cases/ocr_handwriting_from_transcripts.json}
	missing_message="Transcript handwriting OCR cases not found"
	empty_message="No transcript handwriting OCR cases available yet; skipping eval."
	;;
case:handwriting-benchmark)
	cases_path=${OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK:-.local/eval_cases/ocr_handwriting_benchmark_cases.json}
	missing_message="Transcript handwriting benchmark OCR cases not found"
	empty_message="No transcript handwriting benchmark OCR cases available yet; skipping eval."
	;;
case:typed)
	cases_path=${OCR_TRANSCRIPT_CASES_TYPED:-.local/eval_cases/ocr_typed_from_transcripts.json}
	missing_message="Transcript typed OCR cases not found"
	empty_message="No transcript typed OCR cases available yet; skipping eval."
	;;
case:typed-benchmark)
	cases_path=${OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK:-.local/eval_cases/ocr_typed_benchmark_cases.json}
	missing_message="Transcript typed benchmark OCR cases not found"
	empty_message="No transcript typed benchmark OCR cases available yet; skipping eval."
	;;
case:illustration)
	cases_path=${OCR_TRANSCRIPT_CASES_ILLUSTRATION:-.local/eval_cases/ocr_illustration_from_transcripts.json}
	missing_message="Transcript illustration OCR cases not found"
	empty_message="No transcript illustration OCR cases available yet; skipping eval."
	;;
case:illustration-benchmark)
	cases_path=${OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK:-.local/eval_cases/ocr_illustration_benchmark_cases.json}
	missing_message="Transcript illustration benchmark OCR cases not found"
	empty_message="No transcript illustration benchmark OCR cases available yet; skipping eval."
	;;
stability:handwriting-benchmark)
	cases_path=${OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK:-.local/eval_cases/ocr_handwriting_benchmark_cases.json}
	missing_message="Transcript handwriting benchmark OCR cases not found"
	empty_message="No transcript handwriting benchmark OCR cases available yet; skipping stability run."
	stability_report_dir=${OCR_STABILITY_HANDWRITING_BENCHMARK_REPORT_DIR:-.local/eval_reports/ocr_handwriting_benchmark_runs}
	stability_output=${OCR_STABILITY_HANDWRITING_BENCHMARK_OUTPUT:-.local/eval_reports/ocr_handwriting_benchmark_stability.json}
	;;
stability:typed-benchmark)
	cases_path=${OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK:-.local/eval_cases/ocr_typed_benchmark_cases.json}
	missing_message="Transcript typed benchmark OCR cases not found"
	empty_message="No transcript typed benchmark OCR cases available yet; skipping stability run."
	stability_report_dir=${OCR_STABILITY_TYPED_BENCHMARK_REPORT_DIR:-.local/eval_reports/ocr_typed_benchmark_runs}
	stability_output=${OCR_STABILITY_TYPED_BENCHMARK_OUTPUT:-.local/eval_reports/ocr_typed_benchmark_stability.json}
	;;
stability:illustration-benchmark)
	cases_path=${OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK:-.local/eval_cases/ocr_illustration_benchmark_cases.json}
	missing_message="Transcript illustration benchmark OCR cases not found"
	empty_message="No transcript illustration benchmark OCR cases available yet; skipping stability run."
	stability_report_dir=${OCR_STABILITY_ILLUSTRATION_BENCHMARK_REPORT_DIR:-.local/eval_reports/ocr_illustration_benchmark_runs}
	stability_output=${OCR_STABILITY_ILLUSTRATION_BENCHMARK_OUTPUT:-.local/eval_reports/ocr_illustration_benchmark_stability.json}
	;;
*)
	echo "Unknown OCR transcript lane workflow: $mode $lane" >&2
	exit 2
	;;
esac

case "$mode" in
case)
	exec bash "$guarded_case_runner_script" \
		"$cases_path" \
		"$missing_message" \
		"$missing_hint" \
		"$empty_message" \
		-- \
		bash "$eval_runner_script" "$cases_path"
	;;
stability)
	exec bash "$guarded_case_runner_script" \
		"$cases_path" \
		"$missing_message" \
		"$missing_hint" \
		"$empty_message" \
		-- \
		bash "$stability_runner_script" \
			"$cases_path" \
			"${OCR_STABILITY_RUNS:-5}" \
			"${OCR_STABILITY_OCR_RETRIES:-2}" \
			"${OCR_STABILITY_OCR_RETRY_DELAY_MS:-750}" \
			"${OCR_STABILITY_CASE_DELAY_MS:-0}" \
			"${OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS:-0}" \
			"$stability_report_dir" \
			"$stability_output"
	;;
esac
