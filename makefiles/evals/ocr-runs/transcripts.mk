# OCR base transcript case and stability runners.
.PHONY: eval-ocr-transcript-cases eval-ocr-transcript-stability

eval-ocr-transcript-cases:
	@$(OCR_BASE_TRANSCRIPT_WORKFLOW_ENV) bash "$(OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT)" cases

eval-ocr-transcript-stability:
	@$(OCR_BASE_TRANSCRIPT_WORKFLOW_ENV) bash "$(OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT)" stability
