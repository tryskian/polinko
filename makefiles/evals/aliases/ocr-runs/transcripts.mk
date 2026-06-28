# OCR transcript and growth aliases.
.PHONY: ocrall ocrwiden ocrwidensync ocrwidenbatch ocrwidenall

ocrall: eval-ocr-transcript-cases

ocrwiden: eval-ocr-transcript-cases-growth-batched

ocrwidensync: eval-ocr-transcript-cases-growth

ocrwidenbatch: eval-ocr-transcript-cases-growth-batched

ocrwidenall: eval-ocr-transcript-cases-growth-batched
