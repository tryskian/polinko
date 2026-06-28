# OCR focus and stability aliases.
.PHONY: ocrstable ocrstablegrowth ocrgrowth ocrfails ocrfocus
.PHONY: ocrfocuscases ocrfocusreport

ocrstable: eval-ocr-transcript-stability

ocrstablegrowth: eval-ocr-transcript-stability-growth

ocrgrowth: eval-ocr-transcript-growth

ocrfails: eval-ocr-growth-fail-cohort

ocrfocuscases: eval-ocr-focus-cases

ocrfocusreport: eval-ocr-focus-fail-patterns

ocrfocus: ocrgrowth ocrfails ocrfocuscases eval-ocr-focus-stability ocrfocusreport
