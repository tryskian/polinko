#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
# shellcheck source=tools/process_lifecycle_common.sh
. "$script_dir/process_lifecycle_common.sh"

polinko_cd_repo_root

common_script=${OCR_WORKFLOW_COMMON_SCRIPT:-./tools/ocr_workflow_common.sh}
growth_stability_runner_script=${OCR_GROWTH_STABILITY_RUNNER_SCRIPT:-./tools/run_eval_ocr_growth_stability.sh}

cases_path=${OCR_TRANSCRIPT_CASES_GROWTH:-.local/eval_cases/ocr_transcript_cases_growth.json}
growth_stability_runs=${OCR_GROWTH_STABILITY_RUNS:-5}
growth_eval_offset=${OCR_GROWTH_EVAL_OFFSET:-0}
growth_eval_max_cases=${OCR_GROWTH_EVAL_MAX_CASES:-0}
eval_timeout=${OCR_EVAL_TIMEOUT:-90}
growth_ocr_retries=${OCR_GROWTH_OCR_RETRIES:-2}
growth_ocr_retry_delay_ms=${OCR_GROWTH_OCR_RETRY_DELAY_MS:-750}
growth_case_delay_ms=${OCR_GROWTH_CASE_DELAY_MS:-0}
growth_rate_limit_cooldown_ms=${OCR_GROWTH_RATE_LIMIT_COOLDOWN_MS:-0}
max_consecutive_rate_limit_errors=${OCR_MAX_CONSEC_RATE_LIMIT_ERRORS:-3}
growth_stability_report_dir=${OCR_GROWTH_STABILITY_REPORT_DIR:-.local/eval_reports/ocr_growth_stability_runs}
growth_stability_output=${OCR_GROWTH_STABILITY_OUTPUT:-.local/eval_reports/ocr_growth_stability.json}

# shellcheck source=./tools/ocr_workflow_common.sh
. "$common_script"
ocr_workflow_use_eval_case_guard
eval_case_guard_or_exit \
	"$cases_path" \
	"Transcript OCR growth cases not found" \
	"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
	"No transcript OCR growth cases available yet; skipping stability run."

polinko_require_non_negative_integer \
	"OCR_GROWTH_EVAL_OFFSET" \
	"$growth_eval_offset" \
	"OCR growth stability workflow"
polinko_require_non_negative_integer \
	"OCR_GROWTH_EVAL_MAX_CASES" \
	"$growth_eval_max_cases" \
	"OCR growth stability workflow"

output_json=$growth_stability_output
if [ "$growth_eval_offset" -gt 0 ] || [ "$growth_eval_max_cases" -gt 0 ]; then
	output_json=".local/eval_reports/ocr_growth_stability.slice-offset${growth_eval_offset}-max${growth_eval_max_cases}.json"
	echo "Using sliced growth stability output: $output_json"
fi

exec bash "$growth_stability_runner_script" \
	"$cases_path" \
	"$growth_stability_runs" \
	"$growth_eval_offset" \
	"$growth_eval_max_cases" \
	"$eval_timeout" \
	"$growth_ocr_retries" \
	"$growth_ocr_retry_delay_ms" \
	"$growth_case_delay_ms" \
	"$growth_rate_limit_cooldown_ms" \
	"$max_consecutive_rate_limit_errors" \
	"$growth_stability_report_dir" \
	"$output_json"
