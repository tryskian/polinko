# OCR transcript lane case and benchmark stability runners.
.PHONY: eval-ocr-transcript-cases-handwriting eval-ocr-transcript-cases-handwriting-benchmark
.PHONY: eval-ocr-transcript-cases-typed eval-ocr-transcript-cases-typed-benchmark
.PHONY: eval-ocr-transcript-cases-illustration eval-ocr-transcript-cases-illustration-benchmark
.PHONY: eval-ocr-transcript-stability-handwriting-benchmark
.PHONY: eval-ocr-transcript-stability-typed-benchmark
.PHONY: eval-ocr-transcript-stability-illustration-benchmark

eval-ocr-transcript-cases-handwriting:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" case handwriting

eval-ocr-transcript-cases-handwriting-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" case handwriting-benchmark

eval-ocr-transcript-cases-typed:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" case typed

eval-ocr-transcript-cases-typed-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" case typed-benchmark

eval-ocr-transcript-cases-illustration:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" case illustration

eval-ocr-transcript-cases-illustration-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" case illustration-benchmark

eval-ocr-transcript-stability-handwriting-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" stability handwriting-benchmark

eval-ocr-transcript-stability-typed-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" stability typed-benchmark

eval-ocr-transcript-stability-illustration-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" stability illustration-benchmark
