# OCR transcript lane benchmark stability runners.
.PHONY: eval-ocr-transcript-stability-handwriting-benchmark
.PHONY: eval-ocr-transcript-stability-typed-benchmark
.PHONY: eval-ocr-transcript-stability-illustration-benchmark

eval-ocr-transcript-stability-handwriting-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" stability handwriting-benchmark

eval-ocr-transcript-stability-typed-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" stability typed-benchmark

eval-ocr-transcript-stability-illustration-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" stability illustration-benchmark
