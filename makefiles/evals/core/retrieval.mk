# Retrieval and file-search eval targets.
.PHONY: eval-retrieval eval-retrieval-report
.PHONY: eval-file-search eval-file-search-report

eval-retrieval:
	$(PYTHON) -m tools.eval_retrieval \
		--request-retries "$(RETRIEVAL_REQUEST_RETRIES)" \
		--request-retry-delay-ms "$(RETRIEVAL_REQUEST_RETRY_DELAY_MS)"

eval-retrieval-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" retrieval

eval-file-search:
	$(PYTHON) -m tools.eval_file_search

eval-file-search-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" file-search
