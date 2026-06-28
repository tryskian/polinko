# OCR intake benchmark case-builder targets.
.PHONY: ocr-handwriting-benchmark-cases ocr-typed-benchmark-cases
.PHONY: ocr-illustration-benchmark-cases

ocr-handwriting-benchmark-cases:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" benchmark handwriting

ocr-typed-benchmark-cases:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" benchmark typed

ocr-illustration-benchmark-cases:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" benchmark illustration
