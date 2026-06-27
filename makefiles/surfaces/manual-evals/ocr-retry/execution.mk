# Manual eval OCR retry execution and report targets.
.PHONY: manual-evals-ocr-retry-execute manualdb-ocr-retry-execute
.PHONY: manual-evals-ocr-retry-execution-report manualdb-ocr-retry-execution-report

manual-evals-ocr-retry-execute manualdb-ocr-retry-execute:
	$(call manual_evals_db_health,--ocr-retry-execute,$(MANUAL_EVALS_OCR_RETRY_EXECUTE_ARGS))

manual-evals-ocr-retry-execution-report manualdb-ocr-retry-execution-report:
	$(call manual_evals_db_health,--ocr-retry-execution-report,$(MANUAL_EVALS_OCR_RETRY_EXECUTION_REPORT_ARGS))
