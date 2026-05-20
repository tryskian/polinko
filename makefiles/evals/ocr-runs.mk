# OCR transcript eval, growth, focus, and stability runners.
.PHONY: eval-ocr-transcript-cases eval-ocr-transcript-cases-growth
.PHONY: eval-ocr-transcript-cases-growth-batched eval-ocr-growth-fail-cohort
.PHONY: eval-ocr-focus-cases eval-ocr-focus-stability eval-ocr-focus-fail-patterns
.PHONY: eval-ocr-transcript-cases-handwriting eval-ocr-transcript-cases-handwriting-benchmark
.PHONY: eval-ocr-transcript-cases-typed eval-ocr-transcript-cases-typed-benchmark
.PHONY: eval-ocr-transcript-cases-illustration eval-ocr-transcript-cases-illustration-benchmark
.PHONY: eval-ocr-transcript-stability eval-ocr-transcript-stability-growth eval-ocr-transcript-growth
.PHONY: eval-ocr-transcript-stability-handwriting-benchmark
.PHONY: eval-ocr-transcript-stability-typed-benchmark
.PHONY: eval-ocr-transcript-stability-illustration-benchmark

eval-ocr-transcript-cases:
	@$(OCR_BASE_TRANSCRIPT_WORKFLOW_ENV) bash "$(OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT)" cases

eval-ocr-transcript-cases-growth:
	@$(OCR_GROWTH_CASE_WORKFLOW_ENV) bash "$(OCR_GROWTH_CASE_WORKFLOW_SCRIPT)" eval

eval-ocr-transcript-cases-growth-batched:
	@$(OCR_GROWTH_CASE_WORKFLOW_ENV) bash "$(OCR_GROWTH_CASE_WORKFLOW_SCRIPT)" batched

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

eval-ocr-transcript-stability:
	@$(OCR_BASE_TRANSCRIPT_WORKFLOW_ENV) bash "$(OCR_BASE_TRANSCRIPT_WORKFLOW_SCRIPT)" stability

eval-ocr-transcript-growth:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" growth-metrics

eval-ocr-growth-fail-cohort:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" growth-fail-cohort

eval-ocr-focus-cases:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" focus-cases

eval-ocr-focus-stability:
	@$(OCR_FOCUS_STABILITY_WORKFLOW_ENV) bash "$(OCR_FOCUS_STABILITY_WORKFLOW_SCRIPT)"

eval-ocr-focus-fail-patterns:
	@$(OCR_REPORT_WORKFLOW_ENV) bash "$(OCR_REPORT_WORKFLOW_SCRIPT)" focus-fail-patterns

eval-ocr-transcript-stability-growth:
	@$(OCR_GROWTH_STABILITY_WORKFLOW_ENV) bash "$(OCR_GROWTH_STABILITY_WORKFLOW_SCRIPT)"

eval-ocr-transcript-stability-handwriting-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" stability handwriting-benchmark

eval-ocr-transcript-stability-typed-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" stability typed-benchmark

eval-ocr-transcript-stability-illustration-benchmark:
	@$(OCR_TRANSCRIPT_LANE_WORKFLOW_ENV) bash "$(OCR_TRANSCRIPT_LANE_WORKFLOW_SCRIPT)" stability illustration-benchmark
