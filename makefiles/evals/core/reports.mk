# Core eval report aggregation targets.
.PHONY: eval-reports eval-reports-parallel

eval-reports: eval-retrieval-report eval-file-search-report eval-ocr-report eval-style-report eval-response-behaviour-report eval-ocr-safety-report eval-hallucination-report

eval-reports-parallel:
	@$(EVAL_REPORTS_PARALLEL_RUNNER_ENV) bash "$(EVAL_REPORTS_PARALLEL_RUNNER_SCRIPT)"
