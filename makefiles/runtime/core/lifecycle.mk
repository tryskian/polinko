# Startup, closeout, and lifecycle aliases.
.PHONY: gate start end eod end-preflight end-stop rituals

gate: quality-gate-deterministic

start:
	@$(call repo_activity,make start,start)
	bash ./tools/start_of_day_routine.sh

end:
	@$(call repo_activity,make end,end)
	bash ./tools/end_of_day_routine.sh

eod: end

end-preflight:
	@$(call repo_activity,make end-preflight,end-preflight)
	END_SKIP_GIT_CHECK=1 END_SKIP_STOP=1 bash ./tools/end_of_day_routine.sh

end-stop: eval-sidecar-stop portfolio-mockups-stop server-daemon-stop caffeinate-off-all session-status

rituals:
	@cat docs/runtime/START_END_REFERENCE.md
