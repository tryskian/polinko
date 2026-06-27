# Direct OCR eval targets and reports.
.PHONY: eval-ocr-safety eval-ocr-safety-report
.PHONY: eval-ocr eval-ocr-report
.PHONY: eval-ocr-handwriting eval-ocr-handwriting-report
.PHONY: eval-ocr-recovery eval-ocr-recovery-report

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
