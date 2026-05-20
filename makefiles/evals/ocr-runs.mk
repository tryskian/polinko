# OCR transcript eval, growth, focus, and stability runners.
.PHONY: eval-ocr-transcript-cases eval-ocr-transcript-cases-growth
.PHONY: eval-ocr-transcript-cases-growth-batched eval-ocr-growth-fail-cohort
.PHONY: eval-ocr-focus-cases eval-ocr-focus-stability eval-ocr-focus-fail-patterns
.PHONY: eval-ocr-transcript-cases-handwriting eval-ocr-transcript-cases-handwriting-benchmark
.PHONY: eval-ocr-transcript-cases-typed eval-ocr-transcript-cases-typed-benchmark
.PHONY: eval-ocr-transcript-cases-illustration eval-ocr-transcript-cases-illustration-benchmark
.PHONY: eval-ocr-transcript-stability eval-ocr-transcript-stability-growth eval-ocr-transcript-growth
.PHONY: eval-ocr-transcript-stability-handwriting-benchmark
.PHONY: eval-ocr-transcript-stability-typed-benchmark
.PHONY: eval-ocr-transcript-stability-illustration-benchmark

eval-ocr-transcript-cases:
	@$(OCR_BASE_TRANSCRIPT_WORKFLOW_ENV) bash "$(OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT)" cases

eval-ocr-transcript-cases-growth:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_GROWTH_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		"Transcript OCR growth cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript OCR growth cases available yet; skipping eval." \
		-- \
		bash "$(OCR_GROWTH_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_GROWTH)" "$(OCR_EVAL_TIMEOUT)" "$(OCR_GROWTH_EVAL_OFFSET)" "$(OCR_GROWTH_EVAL_MAX_CASES)" "$(OCR_EVAL_OCR_RETRIES)" "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-transcript-cases-growth-batched:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_GROWTH_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		"Transcript OCR growth cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript OCR growth cases available yet; skipping eval." \
		-- \
		bash "$(OCR_GROWTH_BATCH_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_GROWTH)" "$(OCR_GROWTH_BATCH_SIZE)" "$(OCR_GROWTH_OCR_RETRIES)" "$(OCR_GROWTH_OCR_RETRY_DELAY_MS)" "$(OCR_GROWTH_EVAL_OFFSET)" "$(OCR_GROWTH_EVAL_MAX_CASES)" "$(OCR_GROWTH_BATCH_REPORT_DIR)" "$(OCR_GROWTH_BATCH_SUMMARY_JSON)" "$(OCR_GROWTH_BATCH_SUMMARY_MD)"

eval-ocr-transcript-cases-handwriting:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_EVAL_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_HANDWRITING)" \
		"Transcript handwriting OCR cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript handwriting OCR cases available yet; skipping eval." \
		-- \
		bash "$(OCR_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_HANDWRITING)"

eval-ocr-transcript-cases-handwriting-benchmark:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_EVAL_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)" \
		"Transcript handwriting benchmark OCR cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript handwriting benchmark OCR cases available yet; skipping eval." \
		-- \
		bash "$(OCR_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)"

eval-ocr-transcript-cases-typed:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_EVAL_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_TYPED)" \
		"Transcript typed OCR cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript typed OCR cases available yet; skipping eval." \
		-- \
		bash "$(OCR_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_TYPED)"

eval-ocr-transcript-cases-typed-benchmark:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_EVAL_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)" \
		"Transcript typed benchmark OCR cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript typed benchmark OCR cases available yet; skipping eval." \
		-- \
		bash "$(OCR_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)"

eval-ocr-transcript-cases-illustration:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_EVAL_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" \
		"Transcript illustration OCR cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript illustration OCR cases available yet; skipping eval." \
		-- \
		bash "$(OCR_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)"

eval-ocr-transcript-cases-illustration-benchmark:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_EVAL_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)" \
		"Transcript illustration benchmark OCR cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript illustration benchmark OCR cases available yet; skipping eval." \
		-- \
		bash "$(OCR_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)"

eval-ocr-transcript-stability:
	@$(OCR_BASE_TRANSCRIPT_WORKFLOW_ENV) bash "$(OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT)" stability

eval-ocr-transcript-growth:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" growth-metrics

eval-ocr-growth-fail-cohort:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" growth-fail-cohort

eval-ocr-focus-cases:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" focus-cases

eval-ocr-focus-stability:
	@$(OCR_FOCUS_STABILITY_WORKFLOW_ENV) bash "$(OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT)"

eval-ocr-focus-fail-patterns:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" focus-fail-patterns

eval-ocr-transcript-stability-growth:
	@$(OCR_GROWTH_STABILITY_WORKFLOW_ENV) bash "$(OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT)"

eval-ocr-transcript-stability-handwriting-benchmark:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_STABILITY_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)" \
		"Transcript handwriting benchmark OCR cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript handwriting benchmark OCR cases available yet; skipping stability run." \
		-- \
		bash "$(OCR_STABILITY_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)" "$(OCR_STABILITY_RUNS)" "$(OCR_STABILITY_OCR_RETRIES)" "$(OCR_STABILITY_OCR_RETRY_DELAY_MS)" "$(OCR_STABILITY_CASE_DELAY_MS)" "$(OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS)" "$(OCR_STABILITY_HANDWRITING_BENCHMARK_REPORT_DIR)" "$(OCR_STABILITY_HANDWRITING_BENCHMARK_OUTPUT)"

eval-ocr-transcript-stability-typed-benchmark:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_STABILITY_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)" \
		"Transcript typed benchmark OCR cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript typed benchmark OCR cases available yet; skipping stability run." \
		-- \
		bash "$(OCR_STABILITY_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)" "$(OCR_STABILITY_RUNS)" "$(OCR_STABILITY_OCR_RETRIES)" "$(OCR_STABILITY_OCR_RETRY_DELAY_MS)" "$(OCR_STABILITY_CASE_DELAY_MS)" "$(OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS)" "$(OCR_STABILITY_TYPED_BENCHMARK_REPORT_DIR)" "$(OCR_STABILITY_TYPED_BENCHMARK_OUTPUT)"

eval-ocr-transcript-stability-illustration-benchmark:
	@$(OCR_GUARDED_CASE_RUNNER_ENV) \
		$(OCR_STABILITY_RUNNER_ENV) \
		bash "$(OCR_GUARDED_CASE_RUNNER_SCRIPT)" \
		"$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)" \
		"Transcript illustration benchmark OCR cases not found" \
		"Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" \
		"No transcript illustration benchmark OCR cases available yet; skipping stability run." \
		-- \
		bash "$(OCR_STABILITY_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)" "$(OCR_STABILITY_RUNS)" "$(OCR_STABILITY_OCR_RETRIES)" "$(OCR_STABILITY_OCR_RETRY_DELAY_MS)" "$(OCR_STABILITY_CASE_DELAY_MS)" "$(OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS)" "$(OCR_STABILITY_ILLUSTRATION_BENCHMARK_REPORT_DIR)" "$(OCR_STABILITY_ILLUSTRATION_BENCHMARK_OUTPUT)"
