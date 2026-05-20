# OCR aliases and small utility eval targets.
.PHONY: ocrindex ocrmine ocrminehand ocrminetype ocrmineillu ocrminehigh ocrminelow ocrminebacklog
.PHONY: ocrall ocrwiden ocrwidensync ocrwidenbatch ocrwidenall ocrhand ocrtype ocrillu
.PHONY: ocrstable ocrstablegrowth ocrgrowth ocrfails ocrfocus ocrfocuscases ocrfocusreport ocrkernel
.PHONY: ocrhandbench ocrtypebench ocrillubench ocrstablehand ocrstabletype ocrstableillu ocrdelta
.PHONY: nulls runtime-null-audit ocr-data ocr-notebook-workflow

# Short aliases for frequent long-chain commands.
ocrindex: cgpt-export-index

ocrmine: ocr-cases-from-export

ocrminehand: OCR_CASES_FROM_EXPORT_ARGS = --include-lanes handwriting
ocrminehand: ocr-cases-from-export

ocrminetype: OCR_CASES_FROM_EXPORT_ARGS = --include-lanes typed
ocrminetype: ocr-cases-from-export

ocrmineillu: OCR_CASES_FROM_EXPORT_ARGS = --include-lanes illustration
ocrmineillu: ocr-cases-from-export

ocrminehigh: OCR_CASES_FROM_EXPORT_ARGS = --include-signal-strengths high
ocrminehigh: ocr-cases-from-export

ocrminelow: OCR_CASES_FROM_EXPORT_ARGS = --include-signal-strengths low
ocrminelow: ocr-cases-from-export

ocrminebacklog: OCR_CASES_FROM_EXPORT_ARGS = --include-emit-statuses skipped_low_confidence
ocrminebacklog: ocr-cases-from-export

ocrall: eval-ocr-transcript-cases

ocrwiden: eval-ocr-transcript-cases-growth-batched

ocrwidensync: eval-ocr-transcript-cases-growth

ocrwidenbatch: eval-ocr-transcript-cases-growth-batched

ocrwidenall: eval-ocr-transcript-cases-growth-batched

ocrhand: eval-ocr-transcript-cases-handwriting

ocrtype: eval-ocr-transcript-cases-typed

ocrillu: eval-ocr-transcript-cases-illustration

ocrstable: eval-ocr-transcript-stability

ocrstablegrowth: eval-ocr-transcript-stability-growth

ocrgrowth: eval-ocr-transcript-growth

ocrfails: eval-ocr-growth-fail-cohort

ocrfocuscases: eval-ocr-focus-cases

ocrfocusreport: eval-ocr-focus-fail-patterns

ocrfocus: ocrgrowth ocrfails ocrfocuscases eval-ocr-focus-stability ocrfocusreport

ocrkernel:
	@CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		CGPT_EXPORT_ROOT_DEFAULT="$(CGPT_EXPORT_ROOT_DEFAULT)" \
		bash "$(OCR_WORKFLOW_SCRIPT)" ocrkernel

ocrhandbench: eval-ocr-transcript-cases-handwriting-benchmark

ocrtypebench: eval-ocr-transcript-cases-typed-benchmark

ocrillubench: eval-ocr-transcript-cases-illustration-benchmark

ocrstablehand: eval-ocr-transcript-stability-handwriting-benchmark

ocrstabletype: eval-ocr-transcript-stability-typed-benchmark

ocrstableillu: eval-ocr-transcript-stability-illustration-benchmark

ocrdelta: ocr-transcript-delta

nulls: runtime-null-audit

runtime-null-audit:
	$(PYTHON) -m tools.audit_runtime_nulls

ocr-data:
	@CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		CGPT_EXPORT_ROOT_DEFAULT="$(CGPT_EXPORT_ROOT_DEFAULT)" \
		bash "$(OCR_WORKFLOW_SCRIPT)" ocr-data

ocr-notebook-workflow:
	@CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		bash "$(OCR_WORKFLOW_SCRIPT)" ocr-notebook-workflow
