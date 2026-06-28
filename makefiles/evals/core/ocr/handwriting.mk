# OCR handwriting eval targets and reports.
.PHONY: eval-ocr-handwriting eval-ocr-handwriting-report

eval-ocr-handwriting:
	@$(OCR_HANDWRITING_EVAL_RUNNER_ENV) bash "$(OCR_HANDWRITING_EVAL_RUNNER_SCRIPT)" run

eval-ocr-handwriting-report:
	@$(OCR_HANDWRITING_EVAL_RUNNER_ENV) bash "$(OCR_HANDWRITING_EVAL_RUNNER_SCRIPT)" report
