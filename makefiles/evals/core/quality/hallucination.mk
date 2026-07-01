# Hallucination eval targets and threshold calibration.
.PHONY: eval-hallucination eval-hallucination-deterministic
.PHONY: eval-hallucination-report calibrate-hallucination-threshold

eval-hallucination: server-daemon
	$(PYTHON) -m tools.eval_hallucination --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-deterministic: server-daemon
	$(PYTHON) -m tools.eval_hallucination --evaluation-mode deterministic --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" hallucination

calibrate-hallucination-threshold:
	$(PYTHON) -m tools.calibrate_hallucination_threshold
