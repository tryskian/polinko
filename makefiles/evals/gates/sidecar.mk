# Eval sidecar lifecycle targets.
.PHONY: eval-sidecar-start eval-sidecar-status eval-sidecar-stop

eval-sidecar-start:
	@$(call repo_activity,make eval-sidecar-start,eval-sidecar-start)
	@$(EVAL_SIDECAR_START_ENV) bash "$(EVAL_SIDECAR_START_SCRIPT)" start

eval-sidecar-status:
	@$(EVAL_SIDECAR_START_ENV) bash "$(EVAL_SIDECAR_START_SCRIPT)" status

eval-sidecar-stop:
	@$(call repo_activity,make eval-sidecar-stop,eval-sidecar-stop)
	@$(EVAL_SIDECAR_START_ENV) bash "$(EVAL_SIDECAR_START_SCRIPT)" stop
