#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
# shellcheck source=tools/python_runtime.sh
. "$script_dir/python_runtime.sh"
# shellcheck source=tools/ocr_workflow_common.sh
. "$script_dir/ocr_workflow_common.sh"

usage() {
	echo "Usage: run_ocr_intake_workflow.sh <export-index|cases-from-export-build|benchmark|generalization-review|transcript-delta> [lane|extra args...]" >&2
}

if [ "$#" -lt 1 ]; then
	usage
	exit 2
fi

suite=$1
shift

python_bin=$(polinko_default_python_bin)
export_output_dir=${CGPT_EXPORT_OUTPUT_DIR:-.local/eval_cases}
transcript_cases_all=${OCR_TRANSCRIPT_CASES_ALL:-.local/eval_cases/ocr_transcript_cases_all.json}
transcript_cases_growth=${OCR_TRANSCRIPT_CASES_GROWTH:-.local/eval_cases/ocr_transcript_cases_growth.json}
transcript_cases_handwriting=${OCR_TRANSCRIPT_CASES_HANDWRITING:-.local/eval_cases/ocr_handwriting_from_transcripts.json}
transcript_cases_typed=${OCR_TRANSCRIPT_CASES_TYPED:-.local/eval_cases/ocr_typed_from_transcripts.json}
transcript_cases_illustration=${OCR_TRANSCRIPT_CASES_ILLUSTRATION:-.local/eval_cases/ocr_illustration_from_transcripts.json}
transcript_cases_handwriting_benchmark=${OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK:-.local/eval_cases/ocr_handwriting_benchmark_cases.json}
transcript_cases_typed_benchmark=${OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK:-.local/eval_cases/ocr_typed_benchmark_cases.json}
transcript_cases_illustration_benchmark=${OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK:-.local/eval_cases/ocr_illustration_benchmark_cases.json}
transcript_review=${OCR_TRANSCRIPT_REVIEW:-.local/eval_cases/ocr_transcript_cases_review.json}
transcript_review_prev=${OCR_TRANSCRIPT_REVIEW_PREV:-.local/eval_cases/ocr_transcript_cases_review_prev.json}
transcript_delta_md=${OCR_TRANSCRIPT_DELTA_MD:-.local/eval_cases/ocr_transcript_cases_delta.md}
transcript_delta_json=${OCR_TRANSCRIPT_DELTA_JSON:-.local/eval_cases/ocr_transcript_cases_delta.json}
generalization_candidates=${OCR_GENERALIZATION_CANDIDATES:-.local/eval_cases/ocr_generalization_candidates.json}
generalization_review=${OCR_GENERALIZATION_REVIEW:-.local/eval_cases/ocr_generalization_review.json}
generalization_review_max_cases=${OCR_GENERALIZATION_REVIEW_MAX_CASES:-24}
generalization_review_max_per_conversation=${OCR_GENERALIZATION_REVIEW_MAX_PER_CONVERSATION:-2}
generalization_review_include_ids=${OCR_GENERALIZATION_REVIEW_INCLUDE_IDS:-}
growth_max_cases=${OCR_GROWTH_MAX_CASES:-600}
handwriting_benchmark_top_k=${OCR_HANDWRITING_BENCHMARK_TOP_K:-6}
handwriting_benchmark_min_anchors=${OCR_HANDWRITING_BENCHMARK_MIN_ANCHORS:-3}
typed_benchmark_top_k=${OCR_TYPED_BENCHMARK_TOP_K:-8}
typed_benchmark_min_anchors=${OCR_TYPED_BENCHMARK_MIN_ANCHORS:-3}
illustration_benchmark_top_k=${OCR_ILLUSTRATION_BENCHMARK_TOP_K:-6}
illustration_benchmark_min_anchors=${OCR_ILLUSTRATION_BENCHMARK_MIN_ANCHORS:-2}

require_file() {
	path=$1
	message=$2

	if [ ! -f "$path" ]; then
		echo "$message: $path"
		exit 1
	fi
}

run_benchmark() {
	if [ "$#" -ne 1 ]; then
		echo "Usage: run_ocr_intake_workflow.sh benchmark <handwriting|typed|illustration>" >&2
		exit 2
	fi

	lane=$1
	case "$lane" in
	handwriting)
		lane_cases=$transcript_cases_handwriting
		output_cases=$transcript_cases_handwriting_benchmark
		top_k=$handwriting_benchmark_top_k
		min_anchors=$handwriting_benchmark_min_anchors
		missing_message="Transcript handwriting OCR cases not found"
		;;
	typed)
		lane_cases=$transcript_cases_typed
		output_cases=$transcript_cases_typed_benchmark
		top_k=$typed_benchmark_top_k
		min_anchors=$typed_benchmark_min_anchors
		missing_message="Transcript typed OCR cases not found"
		;;
	illustration)
		lane_cases=$transcript_cases_illustration
		output_cases=$transcript_cases_illustration_benchmark
		top_k=$illustration_benchmark_top_k
		min_anchors=$illustration_benchmark_min_anchors
		missing_message="Transcript illustration OCR cases not found"
		;;
	*)
		echo "Unknown OCR intake benchmark lane: $lane" >&2
		exit 2
		;;
	esac

	require_file "$transcript_review" "Transcript OCR review not found"
	require_file "$lane_cases" "$missing_message"

	exec "$python_bin" -m tools.build_handwriting_benchmark_cases \
		--review "$transcript_review" \
		--lane "$lane" \
		--lane-cases "$lane_cases" \
		--output-cases "$output_cases" \
		--top-k "$top_k" \
		--min-anchor-terms "$min_anchors"
}

case "$suite" in
export-index)
	if [ "$#" -ne 0 ]; then
		usage
		exit 2
	fi
	ocr_workflow_require_export_root "cgpt-export-index"
	exec "$python_bin" -m tools.index_cgpt_export \
		--export-root "$OCR_WORKFLOW_EXPORT_ROOT" \
		--output-dir "$export_output_dir"
	;;
cases-from-export-build)
	ocr_workflow_require_export_root "ocr-cases-from-export"
	if [ -f "$transcript_review" ]; then
		cp "$transcript_review" "$transcript_review_prev"
	fi
	exec "$python_bin" -m tools.build_ocr_cases_from_export \
		--export-root "$OCR_WORKFLOW_EXPORT_ROOT" \
		--output-cases "$transcript_cases_all" \
		--output-cases-growth "$transcript_cases_growth" \
		--output-cases-handwriting "$transcript_cases_handwriting" \
		--output-cases-typed "$transcript_cases_typed" \
		--output-cases-illustration "$transcript_cases_illustration" \
		--output-review "$transcript_review" \
		--output-generalization-candidates "$generalization_candidates" \
		--max-growth-cases "$growth_max_cases" \
		"$@"
	;;
benchmark)
	run_benchmark "$@"
	;;
generalization-review)
	if [ "$#" -ne 0 ]; then
		usage
		exit 2
	fi
	if [ ! -f "$generalization_candidates" ]; then
		echo "OCR generalization candidates not found: $generalization_candidates"
		echo "Run: make ocrmine CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"
		exit 1
	fi
	exec "$python_bin" -m tools.build_ocr_generalization_review \
		--candidates "$generalization_candidates" \
		--output-review "$generalization_review" \
		--max-cases "$generalization_review_max_cases" \
		--max-per-conversation "$generalization_review_max_per_conversation" \
		--include-candidate-ids "$generalization_review_include_ids"
	;;
transcript-delta)
	if [ "$#" -ne 0 ]; then
		usage
		exit 2
	fi
	"$python_bin" -m tools.report_ocr_case_mining_delta \
		--current-review "$transcript_review" \
		--previous-review "$transcript_review_prev" \
		--output-markdown "$transcript_delta_md" \
		--output-json "$transcript_delta_json"
	echo "OCR transcript delta report: $transcript_delta_md"
	;;
*)
	echo "Unknown OCR intake workflow suite: $suite" >&2
	exit 2
	;;
esac
