# Core eval report aggregation targets.
.PHONY: eval-reports eval-reports-parallel build-week-ocr-demo build-week-ocr-notebook-demo build-week-ocr-smoke-demo

eval-reports: eval-retrieval-report eval-file-search-report eval-ocr-report eval-style-report eval-response-behaviour-report eval-ocr-safety-report eval-hallucination-report

eval-reports-parallel:
	@$(EVAL_REPORTS_PARALLEL_RUNNER_ENV) bash "$(EVAL_REPORTS_PARALLEL_RUNNER_SCRIPT)"

build-week-ocr-demo:
	@bash ./tools/run_build_week_ocr_demo.sh

build-week-ocr-notebook-demo:
	@bash ./tools/run_build_week_ocr_notebook_demo.sh

build-week-ocr-smoke-demo:
	@bash ./tools/run_build_week_ocr_smoke_demo.sh
