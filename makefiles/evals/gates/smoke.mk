# Eval smoke targets.
.PHONY: api-smoke eval-smoke

api-smoke:
	@$(call repo_activity,make api-smoke,api-smoke)
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" api-smoke

eval-smoke:
	@$(call repo_activity,make eval-smoke,eval-smoke)
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" eval-smoke
