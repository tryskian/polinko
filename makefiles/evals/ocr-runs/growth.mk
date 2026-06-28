# OCR growth case and stability runners.
.PHONY: eval-ocr-transcript-cases-growth eval-ocr-transcript-cases-growth-batched
.PHONY: eval-ocr-transcript-stability-growth

eval-ocr-transcript-cases-growth:
	@$(OCR_GROWTH_CASE_WORKFLOW_ENV) bash "$(OCR_GROWTH_CASE_WORKFLOW_SCRIPT)" eval

eval-ocr-transcript-cases-growth-batched:
	@$(OCR_GROWTH_CASE_WORKFLOW_ENV) bash "$(OCR_GROWTH_CASE_WORKFLOW_SCRIPT)" batched

eval-ocr-transcript-stability-growth:
	@$(OCR_GROWTH_STABILITY_WORKFLOW_ENV) bash "$(OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT)"
