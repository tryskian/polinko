# OCR intake lane shortcuts.
.PHONY: ocrminehand ocrminetype ocrmineillu

ocrminehand: OCR_CASES_FROM_EXPORT_ARGS = --include-lanes handwriting
ocrminehand: ocr-cases-from-export

ocrminetype: OCR_CASES_FROM_EXPORT_ARGS = --include-lanes typed
ocrminetype: ocr-cases-from-export

ocrmineillu: OCR_CASES_FROM_EXPORT_ARGS = --include-lanes illustration
ocrmineillu: ocr-cases-from-export
