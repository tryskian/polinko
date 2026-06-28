# Eval smoke targets.
.PHONY: api-smoke eval-smoke

api-smoke:
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" api-smoke

eval-smoke:
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" eval-smoke
