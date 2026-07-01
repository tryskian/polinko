# OCR safety eval targets and reports.
.PHONY: eval-ocr-safety eval-ocr-safety-report

eval-ocr-safety: server-daemon
	$(PYTHON) -m tools.eval_response_behaviour --suite-id ocr_safety --cases "$(OCR_SAFETY_CASES)" --session-prefix ocr-safety-eval

eval-ocr-safety-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" ocr-safety
