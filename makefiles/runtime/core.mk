# Core operator lifecycle targets.
.PHONY: chat venv env gate start end eod end-preflight end-git-check git-prune-stale-refs end-stop rituals session-status

chat:
	$(PYTHON) $(CLI_ENTRYPOINT)

venv env:
	@set -eu; \
	if [ -f ./.venv/bin/activate ]; then \
		ACTIVATE_PATH="./.venv/bin/activate"; \
	else \
		echo "No local activation script found (checked ./.venv/bin/activate)."; \
		exit 1; \
	fi; \
	echo "Opening shell with virtual environment: $$ACTIVATE_PATH"; \
	. "$$ACTIVATE_PATH"; \
	echo "VIRTUAL_ENV=$$VIRTUAL_ENV"; \
	exec "$$SHELL" -i

gate: quality-gate-deterministic

start:
	@$(call repo_activity,make start,start)
	bash ./tools/start_of_day_routine.sh

end:
	bash ./tools/end_of_day_routine.sh

eod: end

end-preflight:
	@$(call repo_activity,make end-preflight,end-preflight)
	END_SKIP_GIT_CHECK=1 END_SKIP_STOP=1 bash ./tools/end_of_day_routine.sh

end-git-check:
	@$(call repo_activity,make end-git-check,end-git-check)
	bash ./tools/check_end_git_clean.sh

git-prune-stale-refs:
	@$(call repo_activity,make git-prune-stale-refs,git-prune-stale-refs)
	git remote prune origin

end-stop: eval-sidecar-stop portfolio-mockups-stop server-daemon-stop caffeinate-off-all session-status

rituals:
	@cat docs/runtime/START_END_REFERENCE.md

session-status:
	@echo "== Server =="
	@$(MAKE) --no-print-directory server-daemon-status || true
	@echo ""
	@echo "== Eval sidecar =="
	@$(MAKE) --no-print-directory eval-sidecar-status || true
	@echo ""
	@echo "== Portfolio mockups =="
	@$(MAKE) --no-print-directory portfolio-mockups-status || true
	@echo ""
	@echo "== Keep-awake =="
	@$(MAKE) --no-print-directory caffeinate-status || true
