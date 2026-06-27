# OCR run, focus, and benchmark aliases.
.PHONY: ocrall ocrwiden ocrwidensync ocrwidenbatch ocrwidenall
.PHONY: ocrhand ocrtype ocrillu ocrstable ocrstablegrowth
.PHONY: ocrgrowth ocrfails ocrfocus ocrfocuscases ocrfocusreport ocrkernel
.PHONY: ocrhandbench ocrtypebench ocrillubench
.PHONY: ocrstablehand ocrstabletype ocrstableillu

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
