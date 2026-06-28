# OCR intake export and case-mining targets.
.PHONY: cgpt-export-index ocr-cases-from-export ocr-cases-from-export-build

cgpt-export-index:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" export-index

ocr-cases-from-export: ocr-cases-from-export-build ocr-handwriting-benchmark-cases ocr-typed-benchmark-cases ocr-illustration-benchmark-cases ocr-transcript-delta

ocr-cases-from-export-build:
	@$(OCR_INTAKE_WORKFLOW_ENV) bash "$(OCR_INTAKE_WORKFLOW_SCRIPT)" cases-from-export-build $(OCR_CASES_FROM_EXPORT_ARGS)
