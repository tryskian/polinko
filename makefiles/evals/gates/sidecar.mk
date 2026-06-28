# Eval sidecar lifecycle targets.
.PHONY: eval-sidecar-start eval-sidecar-status eval-sidecar-stop

eval-sidecar-start:
	@$(EVAL_SIDECAR_START_ENV) bash "$(EVAL_SIDECAR_START_SCRIPT)" start

eval-sidecar-status:
	@$(EVAL_SIDECAR_START_ENV) bash "$(EVAL_SIDECAR_START_SCRIPT)" status

eval-sidecar-stop:
	@$(EVAL_SIDECAR_START_ENV) bash "$(EVAL_SIDECAR_START_SCRIPT)" stop
