# Core eval suites and report aggregation.
.PHONY: eval-retrieval eval-retrieval-report eval-file-search eval-file-search-report
.PHONY: eval-hallucination eval-hallucination-deterministic eval-hallucination-report
.PHONY: eval-style eval-style-report eval-response-behaviour eval-response-behaviour-report
.PHONY: eval-ocr-safety eval-ocr-safety-report eval-ocr eval-ocr-report
.PHONY: eval-ocr-handwriting eval-ocr-handwriting-report eval-ocr-recovery eval-ocr-recovery-report
.PHONY: eval-clip-ab eval-clip-ab-report eval-clip-ab-readiness eval-reports eval-reports-parallel
.PHONY: calibrate-hallucination-threshold backfill-eval-traces

eval-retrieval:
	$(PYTHON) -m tools.eval_retrieval \
		--request-retries "$(RETRIEVAL_REQUEST_RETRIES)" \
		--request-retry-delay-ms "$(RETRIEVAL_REQUEST_RETRY_DELAY_MS)"

eval-retrieval-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" retrieval

eval-file-search:
	$(PYTHON) -m tools.eval_file_search

eval-file-search-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" file-search

eval-hallucination:
	$(PYTHON) -m tools.eval_hallucination --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-deterministic:
	$(PYTHON) -m tools.eval_hallucination --evaluation-mode deterministic --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" hallucination

calibrate-hallucination-threshold:
	$(PYTHON) -m tools.calibrate_hallucination_threshold

eval-style:
	$(PYTHON) -m tools.eval_style --case-attempts "$(STYLE_CASE_ATTEMPTS)" --min-pass-attempts "$(STYLE_MIN_PASS_ATTEMPTS)"

eval-style-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" style

eval-response-behaviour:
	$(PYTHON) -m tools.eval_response_behaviour

eval-response-behaviour-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" response-behaviour

eval-ocr-safety:
	$(PYTHON) -m tools.eval_response_behaviour --suite-id ocr_safety --cases "$(OCR_SAFETY_CASES)" --session-prefix ocr-safety-eval

eval-ocr-safety-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" ocr-safety

eval-ocr:
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" ocr

eval-ocr-handwriting:
	@$(OCR_HANDWRITING_EVAL_RUNNER_ENV) bash "$(OCR_HANDWRITING_EVAL_RUNNER_SCRIPT)" run

eval-ocr-handwriting-report:
	@$(OCR_HANDWRITING_EVAL_RUNNER_ENV) bash "$(OCR_HANDWRITING_EVAL_RUNNER_SCRIPT)" report

eval-ocr-recovery:
	$(PYTHON) -m tools.eval_ocr_recovery

eval-ocr-recovery-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" ocr-recovery

eval-clip-ab:
	$(PYTHON) -m tools.eval_clip_ab --source-types "$(CLIP_AB_SOURCE_TYPES)"

eval-clip-ab-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" clip-ab

eval-clip-ab-readiness:
	$(PYTHON) -m tools.eval_clip_ab_readiness

backfill-eval-traces:
	$(PYTHON) -m tools.backfill_eval_trace_artifacts

eval-reports: eval-retrieval-report eval-file-search-report eval-ocr-report eval-style-report eval-response-behaviour-report eval-ocr-safety-report eval-hallucination-report

eval-reports-parallel:
	@$(EVAL_REPORTS_PARALLEL_RUNNER_ENV) bash "$(EVAL_REPORTS_PARALLEL_RUNNER_SCRIPT)"
