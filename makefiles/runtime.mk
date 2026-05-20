# Operator lifecycle, runtime, and local machine targets.
.PHONY: chat venv env gate start end eod end-preflight end-git-check eod-stop rituals
.PHONY: localhost server server-daemon server-daemon-stop server-daemon-status session-status
.PHONY: docs open-api-docs open-limits open-usage open-billing open-cost-console viz
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

eod end-preflight: end

end-git-check:
	bash ./tools/check_end_git_clean.sh

eod-stop: server-daemon-stop caffeinate-off-all session-status

rituals:
	@cat docs/runtime/START_END_REFERENCE.md

localhost server:
	$(PYTHON) -m uvicorn $(ASGI_APP) --host "$(DEV_HOST)" --port "$(DEV_BACKEND_PORT)" --reload

server-daemon:
	@set -eu; \
	EXPECTED_PY="$$( $(PYTHON) -c 'import os,sys; print(os.path.realpath(sys.executable))' 2>/dev/null || true )"; \
	if [ -z "$$EXPECTED_PY" ]; then \
		echo "Unable to resolve expected Python interpreter from $(PYTHON)."; \
		exit 1; \
	fi; \
	if [ -f "$(SERVER_PID_FILE)" ]; then \
		PID=$$(cat "$(SERVER_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "server-daemon already running (PID $$PID)."; \
			exit 0; \
		fi; \
		rm -f "$(SERVER_PID_FILE)"; \
	fi; \
	if command -v lsof >/dev/null 2>&1; then \
		EXISTING_PIDS=$$(lsof -nP -iTCP:"$(DEV_BACKEND_PORT)" -sTCP:LISTEN -t 2>/dev/null | tr '\n' ' ' || true); \
		if [ -n "$$EXISTING_PIDS" ]; then \
			POLINKO_PID=""; \
			POLINKO_CMD=""; \
			for CANDIDATE_PID in $$EXISTING_PIDS; do \
				CANDIDATE_CMD=$$(ps -o command= -p "$$CANDIDATE_PID" 2>/dev/null || true); \
				CHECK_PID="$$CANDIDATE_PID"; \
				CHECK_CMD="$$CANDIDATE_CMD"; \
				if ! echo "$$CHECK_CMD" | grep -Fq "uvicorn $(ASGI_APP)"; then \
					PARENT_PID=$$(ps -o ppid= -p "$$CANDIDATE_PID" 2>/dev/null | tr -d ' ' || true); \
					if [ -n "$$PARENT_PID" ]; then \
						PARENT_CMD=$$(ps -o command= -p "$$PARENT_PID" 2>/dev/null || true); \
						if echo "$$PARENT_CMD" | grep -Fq "uvicorn $(ASGI_APP)"; then \
							CHECK_PID="$$PARENT_PID"; \
							CHECK_CMD="$$PARENT_CMD"; \
						fi; \
					fi; \
				fi; \
				if echo "$$CHECK_CMD" | grep -Fq "uvicorn $(ASGI_APP)"; then \
					POLINKO_PID="$$CHECK_PID"; \
					POLINKO_CMD="$$CHECK_CMD"; \
					break; \
				fi; \
			done; \
			if [ -n "$$POLINKO_PID" ]; then \
				EXISTING_PY=$$(printf '%s\n' "$$POLINKO_CMD" | awk '{print $$1}'); \
				EXISTING_PY_REAL="$$( "$$EXISTING_PY" -c 'import os,sys; print(os.path.realpath(sys.executable))' 2>/dev/null || true )"; \
				if [ "$$EXISTING_PY_REAL" = "$$EXPECTED_PY" ]; then \
					echo "$$POLINKO_PID" >"$(SERVER_PID_FILE)"; \
					echo "server-daemon already active on port $(DEV_BACKEND_PORT); adopted PID $$POLINKO_PID ($$EXISTING_PY_REAL)."; \
					exit 0; \
				fi; \
				echo "server-daemon found polinko server on port $(DEV_BACKEND_PORT) with interpreter mismatch."; \
				echo "expected: $$EXPECTED_PY"; \
				echo "found:    $$EXISTING_PY_REAL"; \
				echo "Restarting server-daemon with expected interpreter."; \
				kill "$$POLINKO_PID"; \
				sleep 0.2; \
			else \
				FIRST_PID=$$(printf '%s\n' "$$EXISTING_PIDS" | awk '{print $$1}'); \
				FIRST_CMD=$$(ps -o command= -p "$$FIRST_PID" 2>/dev/null || true); \
				echo "Port $(DEV_BACKEND_PORT) is in use by a non-polinko process."; \
				echo "PID $$FIRST_PID: $$FIRST_CMD"; \
				exit 1; \
			fi; \
		fi; \
	fi; \
	nohup $(PYTHON) -m uvicorn $(ASGI_APP) --host "$(DEV_HOST)" --port "$(DEV_BACKEND_PORT)" --reload >"$(SERVER_LOG)" 2>&1 & \
	PID=$$!; \
	echo "$$PID" >"$(SERVER_PID_FILE)"; \
	sleep 0.2; \
	if kill -0 "$$PID" 2>/dev/null; then \
		echo "server-daemon started (PID $$PID, log: $(SERVER_LOG))."; \
	else \
		rm -f "$(SERVER_PID_FILE)"; \
		echo "Failed to start server-daemon. Check $(SERVER_LOG)."; \
		exit 1; \
	fi

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
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "API docs URL: $$URL"

docs: open-api-docs

open-limits:
	@set -eu; \
	URL="$(OPENAI_LIMITS_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "OpenAI limits URL: $$URL"

open-usage:
	@set -eu; \
	URL="$(OPENAI_USAGE_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "OpenAI usage URL: $$URL"

open-billing:
	@set -eu; \
	URL="$(OPENAI_BILLING_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "OpenAI billing URL: $$URL"

open-cost-console: open-limits open-usage open-billing

viz: server-daemon
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
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate is macOS-only; skipping."; \
		exit 0; \
	fi; \
	if [ -f "$(CAFFEINATE_PID_FILE)" ]; then \
		PID=$$(cat "$(CAFFEINATE_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "caffeinate already running (PID $$PID)."; \
			exit 0; \
		fi; \
		rm -f "$(CAFFEINATE_PID_FILE)"; \
	fi; \
	nohup $(CAFFEINATE_CMD) >"$(CAFFEINATE_LOG)" 2>&1 & \
	PID=$$!; \
	echo "$$PID" >"$(CAFFEINATE_PID_FILE)"; \
	sleep 0.1; \
	if kill -0 "$$PID" 2>/dev/null; then \
		echo "caffeinate started (PID $$PID)."; \
	else \
		rm -f "$(CAFFEINATE_PID_FILE)"; \
		echo "Failed to start caffeinate."; \
		exit 1; \
	fi

caffeinate-on: caffeinate

caffeinate-off: decaffeinate

caffeinate-off-all: caffeinate-off
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate is macOS-only; skipping."; \
		exit 0; \
	fi; \
	PIDS=$$(pgrep -f "^/usr/bin/caffeinate -d -i -m( |$$)" || true); \
	if [ -n "$$PIDS" ]; then \
		for PID in $$PIDS; do \
			kill "$$PID" 2>/dev/null || true; \
		done; \
		sleep 0.1; \
		echo "Stopped matching caffeinate processes: $$PIDS"; \
	else \
		echo "No matching caffeinate processes running."; \
	fi; \
	rm -f "$(CAFFEINATE_PID_FILE)"

decaffeinate:
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate is macOS-only; skipping."; \
		exit 0; \
	fi; \
	if [ ! -f "$(CAFFEINATE_PID_FILE)" ]; then \
		echo "No managed caffeinate PID file found."; \
		exit 0; \
	fi; \
	PID=$$(cat "$(CAFFEINATE_PID_FILE)" 2>/dev/null || true); \
	if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
		kill "$$PID"; \
		sleep 0.1; \
		echo "caffeinate stopped (PID $$PID)."; \
	else \
		echo "Stale PID file found; cleaning up."; \
	fi; \
	rm -f "$(CAFFEINATE_PID_FILE)"

caffeinate-status:
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate status is only available on macOS."; \
		exit 0; \
	fi; \
	if [ -f "$(CAFFEINATE_PID_FILE)" ]; then \
		PID=$$(cat "$(CAFFEINATE_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "Managed caffeinate: RUNNING (PID $$PID)."; \
		else \
			echo "Managed caffeinate: STALE PID file."; \
		fi; \
	else \
		echo "Managed caffeinate: OFF."; \
		EXISTING_PID=$$(pgrep -f "^/usr/bin/caffeinate -d -i -m( |$$)" | head -n 1 || true); \
		if [ -n "$$EXISTING_PID" ]; then \
			echo "Unmanaged caffeinate detected (PID $$EXISTING_PID); not owned by this repo."; \
		fi; \
	fi; \
	if command -v rg >/dev/null 2>&1; then \
		/usr/bin/pmset -g assertions | rg -n "PreventUserIdleDisplaySleep|PreventUserIdleSystemSleep|PreventDiskIdle|caffeinate" || true; \
	else \
		/usr/bin/pmset -g assertions | grep -nE "PreventUserIdleDisplaySleep|PreventUserIdleSystemSleep|PreventDiskIdle|caffeinate" || true; \
	fi

decaffeinate-status: caffeinate-status

privacy-local-on:
	bash tools/local_privacy_guard.sh apply

privacy-local-status:
	bash tools/local_privacy_guard.sh status

privacy-local-off:
	bash tools/local_privacy_guard.sh clear
