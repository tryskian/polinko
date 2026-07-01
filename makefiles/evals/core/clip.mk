# CLIP A/B eval targets.
.PHONY: eval-clip-ab eval-clip-ab-report eval-clip-ab-readiness

eval-clip-ab: server-daemon
	$(PYTHON) -m tools.eval_clip_ab --source-types "$(CLIP_AB_SOURCE_TYPES)"

eval-clip-ab-report:
	@$(EVAL_REPORT_RUNNER_ENV) bash "$(EVAL_REPORT_RUNNER_SCRIPT)" clip-ab

eval-clip-ab-readiness:
	$(PYTHON) -m tools.eval_clip_ab_readiness
