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
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES)" ]; then \
		echo "Transcript OCR cases not found: $(OCR_TRANSCRIPT_CASES)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	$(OCR_EVAL_RUNNER_ENV) bash "$(OCR_EVAL_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES)"

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
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES)" ]; then \
		echo "Transcript OCR cases not found: $(OCR_TRANSCRIPT_CASES)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	OCR_STABILITY_PYTHONUNBUFFERED=1 $(OCR_STABILITY_RUNNER_ENV) bash "$(OCR_STABILITY_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES)" "$(OCR_STABILITY_RUNS)" "$(OCR_STABILITY_OCR_RETRIES)" "$(OCR_STABILITY_OCR_RETRY_DELAY_MS)" "$(OCR_STABILITY_CASE_DELAY_MS)" "$(OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS)" "$(OCR_STABILITY_REPORT_DIR)" "$(OCR_STABILITY_OUTPUT)"

eval-ocr-transcript-growth:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_GROWTH)" ]; then \
		echo "Transcript OCR growth cases not found: $(OCR_TRANSCRIPT_CASES_GROWTH)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	if [ ! -d "$(OCR_GROWTH_STABILITY_REPORT_DIR)" ]; then \
		echo "OCR growth runs dir not found: $(OCR_GROWTH_STABILITY_REPORT_DIR)"; \
		echo "Run: make ocrstablegrowth"; \
		exit 1; \
	fi; \
	$(OCR_REPORT_BUILDER_ENV) bash "$(OCR_REPORT_BUILDER_SCRIPT)" growth-metrics

eval-ocr-growth-fail-cohort:
	@set -eu; \
	if [ ! -f "$(OCR_GROWTH_STABILITY_OUTPUT)" ]; then \
		echo "OCR growth stability report not found: $(OCR_GROWTH_STABILITY_OUTPUT)"; \
		echo "Run: make ocrstablegrowth"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_GROWTH)" ]; then \
		echo "Transcript OCR growth cases not found: $(OCR_TRANSCRIPT_CASES_GROWTH)"; \
		echo "Run: make ocrmine"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		echo "Transcript OCR review report not found: $(OCR_TRANSCRIPT_REVIEW)"; \
		echo "Run: make ocrmine"; \
		exit 1; \
	fi; \
	$(OCR_REPORT_BUILDER_ENV) bash "$(OCR_REPORT_BUILDER_SCRIPT)" growth-fail-cohort

eval-ocr-focus-cases:
	@set -eu; \
	if [ ! -f "$(OCR_GROWTH_FAIL_COHORT_JSON)" ]; then \
		echo "OCR growth fail cohort not found: $(OCR_GROWTH_FAIL_COHORT_JSON)"; \
		echo "Run: make ocrfails"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_GROWTH)" ]; then \
		echo "Transcript OCR growth cases not found: $(OCR_TRANSCRIPT_CASES_GROWTH)"; \
		echo "Run: make ocrmine"; \
		exit 1; \
	fi; \
	$(OCR_REPORT_BUILDER_ENV) bash "$(OCR_REPORT_BUILDER_SCRIPT)" focus-cases

eval-ocr-focus-stability:
	@set -eu; \
	PYTHON="$(PYTHON)"; \
	. "$(EVAL_CASE_GUARD_SCRIPT)"; \
	eval_case_guard_or_exit "$(OCR_FOCUS_CASES_JSON)" "OCR focus cases not found" "Run: make ocrfocuscases" "No OCR focus cases available; skipping focus stability run."; \
	if [ "$(OCR_FOCUS_SKIP_RECENT_RATE_LIMIT)" = "true" ] && [ -f "$(OCR_FOCUS_OUTPUT)" ]; then \
		SKIP=$$($(PYTHON) -m tools.should_skip_ocr_run --report "$(OCR_FOCUS_OUTPUT)" --backoff-seconds "$(OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS)"); \
		if [ "$$SKIP" = "1" ]; then \
			echo "Skipping focus stability replay: recent rate-limit abort is still within backoff window ($(OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS)s)."; \
			exit 0; \
		fi; \
	fi; \
	if [ "$(OCR_FOCUS_SKIP_RECENT_RATE_LIMIT)" = "true" ] && [ -f "$(OCR_GROWTH_FAIL_COHORT_JSON)" ]; then \
		SKIP=$$($(PYTHON) -m tools.should_skip_ocr_run --report "$(OCR_GROWTH_FAIL_COHORT_JSON)" --backoff-seconds "$(OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS)"); \
		if [ "$$SKIP" = "1" ]; then \
			echo "Skipping focus stability replay: recent growth fail cohort shows active rate-limit pressure (backoff $(OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS)s)."; \
			exit 0; \
		fi; \
	fi; \
	$(OCR_STABILITY_RUNNER_ENV) bash "$(OCR_STABILITY_RUNNER_SCRIPT)" "$(OCR_FOCUS_CASES_JSON)" "$(OCR_FOCUS_RUNS)" "$(OCR_FOCUS_OCR_RETRIES)" "$(OCR_FOCUS_OCR_RETRY_DELAY_MS)" "$(OCR_FOCUS_CASE_DELAY_MS)" "$(OCR_FOCUS_RATE_LIMIT_COOLDOWN_MS)" "$(OCR_FOCUS_REPORT_DIR)" "$(OCR_FOCUS_OUTPUT)"

eval-ocr-focus-fail-patterns:
	@set -eu; \
	if [ ! -f "$(OCR_FOCUS_OUTPUT)" ]; then \
		echo "OCR focus stability report not found: $(OCR_FOCUS_OUTPUT)"; \
		echo "Run: make eval-ocr-focus-stability"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_FOCUS_CASES_JSON)" ]; then \
		echo "OCR focus cases not found: $(OCR_FOCUS_CASES_JSON)"; \
		echo "Run: make ocrfocuscases"; \
		exit 1; \
	fi; \
	$(OCR_REPORT_BUILDER_ENV) bash "$(OCR_REPORT_BUILDER_SCRIPT)" focus-fail-patterns

eval-ocr-transcript-stability-growth:
	@set -eu; \
	PYTHON="$(PYTHON)"; \
	. "$(EVAL_CASE_GUARD_SCRIPT)"; \
	eval_case_guard_or_exit "$(OCR_TRANSCRIPT_CASES_GROWTH)" "Transcript OCR growth cases not found" "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export" "No transcript OCR growth cases available yet; skipping stability run."; \
	OUTPUT_JSON="$(OCR_GROWTH_STABILITY_OUTPUT)"; \
	if [ "$(OCR_GROWTH_EVAL_OFFSET)" -gt 0 ] || [ "$(OCR_GROWTH_EVAL_MAX_CASES)" -gt 0 ]; then \
		OUTPUT_JSON=".local/eval_reports/ocr_growth_stability.slice-offset$(OCR_GROWTH_EVAL_OFFSET)-max$(OCR_GROWTH_EVAL_MAX_CASES).json"; \
		echo "Using sliced growth stability output: $$OUTPUT_JSON"; \
	fi; \
	$(OCR_GROWTH_RUNNER_ENV) bash "$(OCR_GROWTH_STABILITY_RUNNER_SCRIPT)" "$(OCR_TRANSCRIPT_CASES_GROWTH)" "$(OCR_GROWTH_STABILITY_RUNS)" "$(OCR_GROWTH_EVAL_OFFSET)" "$(OCR_GROWTH_EVAL_MAX_CASES)" "$(OCR_EVAL_TIMEOUT)" "$(OCR_GROWTH_OCR_RETRIES)" "$(OCR_GROWTH_OCR_RETRY_DELAY_MS)" "$(OCR_GROWTH_CASE_DELAY_MS)" "$(OCR_GROWTH_RATE_LIMIT_COOLDOWN_MS)" "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)" "$(OCR_GROWTH_STABILITY_REPORT_DIR)" "$$OUTPUT_JSON"

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
