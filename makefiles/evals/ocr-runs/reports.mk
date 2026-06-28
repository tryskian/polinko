# OCR report-derived metric and cohort targets.
.PHONY: eval-ocr-transcript-growth eval-ocr-growth-fail-cohort
.PHONY: eval-ocr-focus-cases eval-ocr-focus-fail-patterns

eval-ocr-transcript-growth:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" growth-metrics

eval-ocr-growth-fail-cohort:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" growth-fail-cohort

eval-ocr-focus-cases:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" focus-cases

eval-ocr-focus-fail-patterns:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" focus-fail-patterns
