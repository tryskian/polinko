# Response-behaviour eval targets and reports.
.PHONY: eval-response-behaviour eval-response-behaviour-report

eval-response-behaviour:
	$(PYTHON) -m tools.eval_response_behaviour

eval-response-behaviour-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" response-behaviour
