# Operator lifecycle, runtime, and local machine targets.
.PHONY: chat venv env gate start end eod end-preflight end-git-check eod-stop rituals
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
	bash ./tools/start_of_day_routine.sh

end:
	bash ./tools/end_of_day_routine.sh

eod: end

end-preflight:
	END_SKIP_GIT_CHECK=1 END_SKIP_STOP=1 bash ./tools/end_of_day_routine.sh

end-git-check:
	bash ./tools/check_end_git_clean.sh

eod-stop: server-daemon-stop caffeinate-off-all session-status

rituals:
	@cat docs/runtime/START_END_REFERENCE.md

localhost server:
	$(PYTHON) -m uvicorn $(ASGI_APP) --host "$(DEV_HOST)" --port "$(DEV_BACKEND_PORT)" --reload

server-daemon:
	@$(SERVER_DAEMON_ENV) bash "$(SERVER_DAEMON_SCRIPT)"

server-daemon-stop:
	@set -eu; \
	if [ ! -f "$(SERVER_PID_FILE)" ]; then \
		echo "No server-daemon PID file found."; \
		exit 0; \
	fi; \
	PID=$$(cat "$(SERVER_PID_FILE)" 2>/dev/null || true); \
	if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
		kill "$$PID"; \
		echo "server-daemon stopped (PID $$PID)."; \
	else \
		echo "Stale server-daemon PID file; cleaning up."; \
	fi; \
	rm -f "$(SERVER_PID_FILE)"

server-daemon-status:
	@set -eu; \
	if [ -f "$(SERVER_PID_FILE)" ]; then \
		PID=$$(cat "$(SERVER_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "server-daemon: RUNNING (PID $$PID)."; \
			exit 0; \
		fi; \
		echo "server-daemon: STALE PID file."; \
		exit 1; \
	fi; \
	echo "server-daemon: OFF."

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
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi
endif

docs: open-api-docs

docs-open open-api-docs-browser: server-daemon
	@set -eu; \
	URL="$(DEV_API_DOCS_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
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
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi
endif

viz-open open-viz: server-daemon
	@set -eu; \
	URL="$(DEV_VIZ_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "PASS/FAIL viz URL: $$URL"

session-status:
	@echo "== Server =="
	@$(MAKE) --no-print-directory server-daemon-status || true
	@echo ""
	@echo "== Keep-awake =="
	@$(MAKE) --no-print-directory caffeinate-status || true

caffeinate:
	@$(CAFFEINATE_ENV) bash "$(CAFFEINATE_SCRIPT)" start

caffeinate-on: caffeinate

caffeinate-off: decaffeinate

caffeinate-off-all: caffeinate-off
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
