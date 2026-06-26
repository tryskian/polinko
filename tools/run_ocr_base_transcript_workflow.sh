#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root

if [ "$#" -ne 1 ]; then
	echo "Usage: run_ocr_base_transcript_workflow.sh <cases|stability>" >&2
	exit 2
fi

suite=$1
common_script=${OCR_WORKFLOW_COMMON_SCRIPT:-./tools/ocr_workflow_common.sh}
cases_path=${OCR_TRANSCRIPT_CASES:-.local/eval_cases/ocr_transcript_cases_all.json}
eval_runner_script=${OCR_EVAL_RUNNER_SCRIPT:-./tools/run_eval_ocr_cases.sh}
stability_runner_script=${OCR_STABILITY_RUNNER_SCRIPT:-./tools/run_eval_ocr_stability.sh}

case "$suite" in
cases|stability)
	;;
*)
	echo "Unknown OCR base transcript workflow suite: $suite" >&2
	exit 2
	;;
esac

case "$suite" in
cases)
	empty_message="No transcript OCR cases available yet; skipping eval."
	;;
stability)
	empty_message="No transcript OCR cases available yet; skipping stability run."
	;;
esac

# shellcheck source=./tools/ocr_workflow_common.sh
. "$common_script"
ocr_workflow_use_eval_case_guard
eval_case_guard_or_exit \
	"$cases_path" \
	"Transcript OCR cases not found" \
	"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
	"$empty_message"

case "$suite" in
cases)
	exec bash "$eval_runner_script" "$cases_path"
	;;
stability)
	OCR_STABILITY_PYTHONUNBUFFERED=1 exec bash "$stability_runner_script" \
		"$cases_path" \
		"${OCR_STABILITY_RUNS:-5}" \
		"${OCR_STABILITY_OCR_RETRIES:-2}" \
		"${OCR_STABILITY_OCR_RETRY_DELAY_MS:-750}" \
		"${OCR_STABILITY_CASE_DELAY_MS:-0}" \
		"${OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS:-0}" \
		"${OCR_STABILITY_REPORT_DIR:-.local/eval_reports/ocr_stability_runs}" \
		"${OCR_STABILITY_OUTPUT:-.local/eval_reports/ocr_transcript_stability.json}"
	;;
esac
