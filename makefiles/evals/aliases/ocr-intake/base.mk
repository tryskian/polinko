# OCR intake base aliases.
.PHONY: ocrindex ocrmine ocrdelta

ocrindex: cgpt-export-index

ocrmine: ocr-cases-from-export

ocrdelta: ocr-transcript-delta
