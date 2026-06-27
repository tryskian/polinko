# OCR intake and case-mining aliases.
.PHONY: ocrindex ocrmine ocrminehand ocrminetype ocrmineillu
.PHONY: ocrminehigh ocrminelow ocrminebacklog ocrdelta

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

ocrdelta: ocr-transcript-delta
