# Hallucination, style, and response-behaviour eval targets.
.PHONY: eval-hallucination eval-hallucination-deterministic
.PHONY: eval-hallucination-report calibrate-hallucination-threshold
.PHONY: eval-style eval-style-report
.PHONY: eval-response-behaviour eval-response-behaviour-report

eval-hallucination:
	$(PYTHON) -m tools.eval_hallucination --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-deterministic:
	$(PYTHON) -m tools.eval_hallucination --evaluation-mode deterministic --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" hallucination

calibrate-hallucination-threshold:
	$(PYTHON) -m tools.calibrate_hallucination_threshold

eval-style:
	$(PYTHON) -m tools.eval_style --case-attempts "$(STYLE_CASE_ATTEMPTS)" --min-pass-attempts "$(STYLE_MIN_PASS_ATTEMPTS)"

eval-style-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" style

eval-response-behaviour:
	$(PYTHON) -m tools.eval_response_behaviour

eval-response-behaviour-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" response-behaviour
