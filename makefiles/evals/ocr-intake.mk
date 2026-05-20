# OCR intake, mining, and benchmark case builders.
.PHONY: cgpt-export-index ocr-cases-from-export ocr-cases-from-export-build
.PHONY: ocr-handwriting-benchmark-cases ocr-typed-benchmark-cases ocr-illustration-benchmark-cases
.PHONY: ocr-generalization-review ocr-transcript-delta

cgpt-export-index:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" export-index

ocr-cases-from-export: ocr-cases-from-export-build ocr-handwriting-benchmark-cases ocr-typed-benchmark-cases ocr-illustration-benchmark-cases ocr-transcript-delta

ocr-cases-from-export-build:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" cases-from-export-build $(OCR_CASES_FROM_EXPORT_ARGS)

ocr-handwriting-benchmark-cases:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" benchmark handwriting

ocr-generalization-review:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" generalization-review

ocr-typed-benchmark-cases:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" benchmark typed

ocr-illustration-benchmark-cases:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" benchmark illustration

ocr-transcript-delta:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" transcript-delta
