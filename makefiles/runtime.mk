# Operator lifecycle, runtime, and local machine targets.
.PHONY: chat venv env gate start end eod end-preflight end-git-check git-prune-stale-refs end-stop rituals
.PHONY: localhost server server-daemon server-daemon-stop server-daemon-status session-status
.PHONY: docs docs-open open-api-docs open-api-docs-browser viz viz-open open-viz
.PHONY: openai-account-summary openai-costs openai-usage openai-limits
.PHONY: open-limits open-usage open-billing open-cost-console
.PHONY: caffeinate caffeinate-on caffeinate-status caffeinate-off caffeinate-off-all decaffeinate decaffeinate-status
.PHONY: privacy-local-on privacy-local-status privacy-local-off

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

localhost server:
	$(PYTHON) -m uvicorn $(ASGI_APP) --host "$(DEV_HOST)" --port "$(DEV_BACKEND_PORT)" --reload

server-daemon:
	@$(SERVER_DAEMON_ENV) bash "$(SERVER_DAEMON_SCRIPT)" start

server-daemon-stop:
	@$(SERVER_DAEMON_ENV) bash "$(SERVER_DAEMON_SCRIPT)" stop

server-daemon-status:
	@$(SERVER_DAEMON_ENV) bash "$(SERVER_DAEMON_SCRIPT)" status

open-api-docs: server-daemon
	@set -eu; \
	URL="$(DEV_API_DOCS_URL)"; \
	case "$(LOCAL_BROWSER_LAUNCH)" in none|system) ;; \
		*) echo "Invalid LOCAL_BROWSER_LAUNCH='$(LOCAL_BROWSER_LAUNCH)' (expected none or system)."; exit 2 ;; \
	esac; \
	echo "API docs URL: $$URL"
ifeq ($(LOCAL_BROWSER_LAUNCH),system)
	@set -eu; \
	URL="$(DEV_API_DOCS_URL)"; \
	bash "$(LOCAL_URL_LAUNCHER_SCRIPT)" "$$URL"
endif

docs: open-api-docs

docs-open open-api-docs-browser: server-daemon
	@set -eu; \
	URL="$(DEV_API_DOCS_URL)"; \
	bash "$(LOCAL_URL_LAUNCHER_SCRIPT)" "$$URL"; \
	echo "API docs URL: $$URL"

openai-account-summary:
	@$(OPENAI_ACCOUNT_ENV) "$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" summary

openai-costs:
	@$(OPENAI_ACCOUNT_ENV) "$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" costs

openai-usage:
	@$(OPENAI_ACCOUNT_ENV) "$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" usage

openai-limits:
	@$(OPENAI_ACCOUNT_ENV) "$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" limits

open-limits: openai-limits

open-usage: openai-usage

open-billing: openai-costs

open-cost-console: openai-account-summary

viz: server-daemon
	@set -eu; \
	URL="$(DEV_VIZ_URL)"; \
	case "$(LOCAL_BROWSER_LAUNCH)" in none|system) ;; \
		*) echo "Invalid LOCAL_BROWSER_LAUNCH='$(LOCAL_BROWSER_LAUNCH)' (expected none or system)."; exit 2 ;; \
	esac; \
	echo "PASS/FAIL viz URL: $$URL"
ifeq ($(LOCAL_BROWSER_LAUNCH),system)
	@set -eu; \
	URL="$(DEV_VIZ_URL)"; \
	bash "$(LOCAL_URL_LAUNCHER_SCRIPT)" "$$URL"
endif

viz-open open-viz: server-daemon
	@set -eu; \
	URL="$(DEV_VIZ_URL)"; \
	bash "$(LOCAL_URL_LAUNCHER_SCRIPT)" "$$URL"; \
	echo "PASS/FAIL viz URL: $$URL"

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

caffeinate:
	@$(CAFFEINATE_ENV) bash "$(CAFFEINATE_SCRIPT)" start

caffeinate-on: caffeinate

caffeinate-off: decaffeinate

caffeinate-off-all:
	@$(CAFFEINATE_ENV) bash "$(CAFFEINATE_SCRIPT)" stop-all

decaffeinate:
	@$(CAFFEINATE_ENV) bash "$(CAFFEINATE_SCRIPT)" stop

caffeinate-status:
	@$(CAFFEINATE_ENV) bash "$(CAFFEINATE_SCRIPT)" status

decaffeinate-status: caffeinate-status

privacy-local-on:
	bash tools/local_privacy_guard.sh apply

privacy-local-status:
	bash tools/local_privacy_guard.sh status

privacy-local-off:
	bash tools/local_privacy_guard.sh clear
