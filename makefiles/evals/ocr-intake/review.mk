# OCR intake review and transcript-delta targets.
.PHONY: ocr-generalization-review ocr-transcript-delta

ocr-generalization-review:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" generalization-review

ocr-transcript-delta:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" transcript-delta
