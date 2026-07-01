# OCR recovery eval targets and reports.
.PHONY: eval-ocr-recovery eval-ocr-recovery-report

eval-ocr-recovery: server-daemon
	$(PYTHON) -m tools.eval_ocr_recovery

eval-ocr-recovery-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" ocr-recovery
