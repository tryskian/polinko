# OCR focus stability runner.
.PHONY: eval-ocr-focus-stability

eval-ocr-focus-stability:
	@$(OCR_FOCUS_STABILITY_WORKFLOW_ENV) bash "$(OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT)"
