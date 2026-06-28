# OCR intake filter aliases.
.PHONY: ocrminehigh ocrminelow ocrminebacklog

ocrminehigh: OCR_CASES_FROM_EXPORT_ARGS = --include-signal-strengths high
ocrminehigh: ocr-cases-from-export

ocrminelow: OCR_CASES_FROM_EXPORT_ARGS = --include-signal-strengths low
ocrminelow: ocr-cases-from-export

ocrminebacklog: OCR_CASES_FROM_EXPORT_ARGS = --include-emit-statuses skipped_low_confidence
ocrminebacklog: ocr-cases-from-export
