PYTHON ?= $(shell \
	if [ -x ./polinko-repositioning-system/bin/python ] && ./polinko-repositioning-system/bin/python -V >/dev/null 2>&1; then \
		echo ./polinko-repositioning-system/bin/python; \
	elif [ -x ./venv/bin/python ] && ./venv/bin/python -V >/dev/null 2>&1; then \
		echo ./venv/bin/python; \
	else \
		echo python3; \
	fi)
DOCKER ?= docker
DOCKER_IMAGE ?= polinko:dev
DOCKER_PORT ?= 8000
DEV_HOST ?= 127.0.0.1
DEV_BACKEND_PORT ?= 8000
DEV_AUTOKILL ?= 1
ENV_FILE ?= .env
K6_BASE_URL ?= http://127.0.0.1:8000
K6_API_KEY ?= test-server-key
K6_VUS ?= 3
K6_DURATION ?= 10s
TRIVY_SEVERITY ?= HIGH,CRITICAL
GATE_PORT ?= 8066
GATE_BASE_URL ?= http://127.0.0.1:$(GATE_PORT)
GATE_SESSION_DB ?= /tmp/polinko-quality-gate-sessions.db
GATE_VECTOR_DB ?= /tmp/polinko-quality-gate-vector.db
WORKBENCH_PORT ?= 8020
HALLUCINATION_EVAL_MODE ?= judge
HALLUCINATION_JUDGE_MODEL ?= gpt-4.1-mini
HALLUCINATION_JUDGE_API_KEY_ENV ?= OPENAI_API_KEY
BRAINTRUST_OPENAI_BASE_URL ?=
HALLUCINATION_JUDGE_BASE_URL ?=
HALLUCINATION_MIN_ACCEPTABLE_SCORE ?= 5
CLIP_AB_SOURCE_TYPES ?= image
CAFFEINATE_PID_FILE ?= /tmp/polinko-caffeinate.pid
CAFFEINATE_LOG ?= /tmp/polinko-caffeinate.log
CAFFEINATE_CMD ?= /usr/bin/caffeinate -d -i -m
SERVER_PID_FILE ?= /tmp/polinko-server.pid
SERVER_LOG ?= /tmp/polinko-server.log

.PHONY: chat server server-daemon server-daemon-stop server-daemon-status session-status test lint-docs doctor-env build-audit backend-gate caffeinate-on caffeinate-off caffeinate-status decaffeinate privacy-local-on privacy-local-status privacy-local-off precommit-install precommit-run act-list act-ci k6-chat-smoke trivy-fs trivy-image eval-retrieval eval-retrieval-report eval-file-search eval-file-search-report eval-hallucination eval-hallucination-deterministic eval-hallucination-braintrust eval-hallucination-report eval-style eval-style-report eval-ocr eval-ocr-report eval-ocr-recovery eval-ocr-recovery-report eval-clip-ab eval-clip-ab-report eval-clip-ab-readiness eval-cleanup eval-reports eval-reports-parallel calibrate-hallucination-threshold backfill-eval-traces hallucination-gate quality-gate quality-gate-deterministic evidence-index evidence-refresh portfolio-metadata-audit reference-graph db-visuals db-reset db-archive docker-build docker-run dev dev-stop

chat:
	$(PYTHON) app.py

server:
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

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
		EXISTING_PID=$$(lsof -nP -iTCP:"$(DEV_BACKEND_PORT)" -sTCP:LISTEN -t 2>/dev/null | head -n 1 || true); \
		if [ -n "$$EXISTING_PID" ]; then \
			EXISTING_CMD=$$(ps -o command= -p "$$EXISTING_PID" 2>/dev/null || true); \
			if echo "$$EXISTING_CMD" | grep -q "uvicorn server:app"; then \
				EXISTING_PY=$$(printf '%s\n' "$$EXISTING_CMD" | awk '{print $$1}'); \
				EXISTING_PY_REAL="$$( "$$EXISTING_PY" -c 'import os,sys; print(os.path.realpath(sys.executable))' 2>/dev/null || true )"; \
				if [ "$$EXISTING_PY_REAL" = "$$EXPECTED_PY" ]; then \
					echo "$$EXISTING_PID" >"$(SERVER_PID_FILE)"; \
					echo "server-daemon already active on port $(DEV_BACKEND_PORT); adopted PID $$EXISTING_PID ($$EXISTING_PY_REAL)."; \
					exit 0; \
				fi; \
				echo "server-daemon found polinko server on port $(DEV_BACKEND_PORT) with interpreter mismatch."; \
				echo "expected: $$EXPECTED_PY"; \
				echo "found:    $$EXISTING_PY_REAL"; \
				echo "Restarting server-daemon with expected interpreter."; \
				kill "$$EXISTING_PID"; \
				sleep 0.2; \
			fi; \
			echo "Port $(DEV_BACKEND_PORT) is in use by a non-polinko process."; \
			echo "PID $$EXISTING_PID: $$EXISTING_CMD"; \
			exit 1; \
		fi; \
	fi; \
	nohup $(PYTHON) -m uvicorn server:app --host "$(DEV_HOST)" --port "$(DEV_BACKEND_PORT)" --reload >"$(SERVER_LOG)" 2>&1 & \
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

session-status:
	@echo "== Server =="
	@$(MAKE) --no-print-directory server-daemon-status || true
	@echo ""
	@echo "== Keep-awake =="
	@$(MAKE) --no-print-directory caffeinate-status || true

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

lint-docs:
	npm run lint:docs

doctor-env:
	$(PYTHON) -m tools.doctor_env

build-audit:
	$(PYTHON) -m tools.audit_build_blocks

backend-gate:
	@echo "Running backend gate (doctor + build-audit + tests + deterministic quality gate)..."
	@$(MAKE) doctor-env
	@$(MAKE) build-audit
	@$(MAKE) test
	@$(MAKE) quality-gate-deterministic

caffeinate-on:
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
	EXISTING_PID=$$(pgrep -f "^/usr/bin/caffeinate -d -i -m( |$$)" | head -n 1 || true); \
	if [ -n "$$EXISTING_PID" ]; then \
		echo "$$EXISTING_PID" >"$(CAFFEINATE_PID_FILE)"; \
		echo "caffeinate already active; adopted PID $$EXISTING_PID."; \
		exit 0; \
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

caffeinate-off:
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
			echo "Unmanaged caffeinate detected (PID $$EXISTING_PID); run 'make caffeinate-on' to adopt it."; \
		fi; \
	fi; \
	if command -v rg >/dev/null 2>&1; then \
		/usr/bin/pmset -g assertions | rg -n "PreventUserIdleDisplaySleep|PreventUserIdleSystemSleep|PreventDiskIdle|caffeinate" || true; \
	else \
		/usr/bin/pmset -g assertions | grep -nE "PreventUserIdleDisplaySleep|PreventUserIdleSystemSleep|PreventDiskIdle|caffeinate" || true; \
	fi

decaffeinate: caffeinate-off

privacy-local-on:
	bash tools/local_privacy_guard.sh apply

privacy-local-status:
	bash tools/local_privacy_guard.sh status

privacy-local-off:
	bash tools/local_privacy_guard.sh clear

precommit-install:
	$(PYTHON) -m pip install pre-commit

precommit-run:
	$(PYTHON) -m pre_commit run --all-files

act-list:
	act -l

act-ci:
	act -W .github/workflows/ci.yml

k6-chat-smoke:
	k6 run tests/perf/chat_smoke.js -e BASE_URL="$(K6_BASE_URL)" -e POLINKO_SERVER_API_KEY="$(K6_API_KEY)" -e VUS="$(K6_VUS)" -e DURATION="$(K6_DURATION)"

trivy-fs:
	trivy fs --severity "$(TRIVY_SEVERITY)" --exit-code 1 .

trivy-image:
	$(DOCKER) build -t $(DOCKER_IMAGE) . && trivy image --severity "$(TRIVY_SEVERITY)" --exit-code 1 $(DOCKER_IMAGE)

eval-retrieval:
	$(PYTHON) -m tools.eval_retrieval

eval-retrieval-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_retrieval --run-id $$RUN_ID --report-json "eval_reports/retrieval-$$RUN_ID.json"

eval-file-search:
	$(PYTHON) -m tools.eval_file_search

eval-file-search-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_file_search --run-id $$RUN_ID --report-json "eval_reports/file-search-$$RUN_ID.json"

eval-hallucination:
	$(PYTHON) -m tools.eval_hallucination --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-deterministic:
	$(PYTHON) -m tools.eval_hallucination --evaluation-mode deterministic --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-braintrust:
	@set -eu; \
	BASE_URL="$(HALLUCINATION_JUDGE_BASE_URL)"; \
	if [ -z "$$BASE_URL" ]; then \
		BASE_URL="$(BRAINTRUST_OPENAI_BASE_URL)"; \
	fi; \
	if [ -z "$$BASE_URL" ]; then \
		echo "Missing Braintrust base URL."; \
		echo "Set BRAINTRUST_OPENAI_BASE_URL (recommended: https://api.braintrust.dev/v1/proxy)"; \
		echo "or pass HALLUCINATION_JUDGE_BASE_URL explicitly."; \
		exit 2; \
	fi; \
	if [ -z "$${BRAINTRUST_API_KEY:-}" ]; then \
		echo "Missing BRAINTRUST_API_KEY in environment."; \
		exit 2; \
	fi; \
	$(PYTHON) -m tools.eval_hallucination --evaluation-mode judge --judge-api-key-env BRAINTRUST_API_KEY --judge-base-url "$$BASE_URL" --judge-model "$(HALLUCINATION_JUDGE_MODEL)" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_hallucination --run-id $$RUN_ID --report-json "eval_reports/hallucination-$$RUN_ID.json" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

calibrate-hallucination-threshold:
	$(PYTHON) -m tools.calibrate_hallucination_threshold

eval-style:
	$(PYTHON) -m tools.eval_style

eval-style-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_style --run-id $$RUN_ID --report-json "eval_reports/style-$$RUN_ID.json"

eval-ocr:
	$(PYTHON) -m tools.eval_ocr

eval-ocr-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_ocr --run-id $$RUN_ID --report-json "eval_reports/ocr-$$RUN_ID.json"

eval-ocr-recovery:
	$(PYTHON) -m tools.eval_ocr_recovery

eval-ocr-recovery-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_ocr_recovery --run-id $$RUN_ID --report-json "eval_reports/ocr-recovery-$$RUN_ID.json"

eval-clip-ab:
	$(PYTHON) -m tools.eval_clip_ab --source-types "$(CLIP_AB_SOURCE_TYPES)"

eval-clip-ab-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_clip_ab --source-types "$(CLIP_AB_SOURCE_TYPES)" --run-id $$RUN_ID --report-json "eval_reports/clip-ab-$$RUN_ID.json"

eval-clip-ab-readiness:
	$(PYTHON) -m tools.eval_clip_ab_readiness

backfill-eval-traces:
	$(PYTHON) -m tools.backfill_eval_trace_artifacts

eval-cleanup:
	@set -eu; \
	if [ ! -f "tools/cleanup_eval_chats.py" ]; then \
		echo "tools/cleanup_eval_chats.py is local-only and not tracked in this repo."; \
		echo "Skipping eval cleanup."; \
		exit 0; \
	fi; \
	$(PYTHON) -m tools.cleanup_eval_chats

eval-reports:
	@$(MAKE) eval-retrieval-report
	@$(MAKE) eval-file-search-report
	@$(MAKE) eval-ocr-report
	@$(MAKE) eval-style-report
	@$(MAKE) eval-hallucination-report

eval-reports-parallel:
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_parallel_orchestrator --base-url "$${BASE_URL:-http://127.0.0.1:8000}" --run-id $$RUN_ID --hallucination-mode "$(HALLUCINATION_EVAL_MODE)" --hallucination-min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

hallucination-gate:
	@echo "Running hallucination gate..."
	@set -eu; \
	BASE_URL="$(GATE_BASE_URL)"; \
	rm -f "$(GATE_SESSION_DB)" "$(GATE_VECTOR_DB)"; \
	POLINKO_SESSION_DB_PATH="$(GATE_SESSION_DB)" \
	POLINKO_VECTOR_DB_PATH="$(GATE_VECTOR_DB)" \
	POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK=true \
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port $(GATE_PORT) >/tmp/polinko-hallucination-gate.log 2>&1 & \
	SERVER_PID=$$!; \
	trap 'kill $$SERVER_PID 2>/dev/null || true' EXIT INT TERM; \
	READY=0; \
	for i in $$(seq 1 100); do \
		if curl -fsS "$$BASE_URL/health" >/dev/null 2>&1; then \
			READY=1; \
			break; \
		fi; \
		sleep 0.2; \
	done; \
	if [ "$$READY" -ne 1 ]; then \
		echo "Server failed to start. See /tmp/polinko-hallucination-gate.log"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.eval_hallucination --base-url "$$BASE_URL" --strict --evaluation-mode "$(HALLUCINATION_EVAL_MODE)" --judge-model "$(HALLUCINATION_JUDGE_MODEL)" --judge-api-key-env "$(HALLUCINATION_JUDGE_API_KEY_ENV)" --judge-base-url "$(HALLUCINATION_JUDGE_BASE_URL)" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"; \
	echo "Hallucination gate passed."

quality-gate:
	@echo "Running quality gate (tests + retrieval eval + file-search eval + OCR eval + style eval + hallucination eval)..."
	@set -eu; \
	BASE_URL="$(GATE_BASE_URL)"; \
	rm -f "$(GATE_SESSION_DB)" "$(GATE_VECTOR_DB)"; \
	POLINKO_SESSION_DB_PATH="$(GATE_SESSION_DB)" \
	POLINKO_VECTOR_DB_PATH="$(GATE_VECTOR_DB)" \
	POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK=true \
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port $(GATE_PORT) >/tmp/polinko-quality-gate.log 2>&1 & \
	SERVER_PID=$$!; \
	trap 'kill $$SERVER_PID 2>/dev/null || true' EXIT INT TERM; \
	READY=0; \
	for i in $$(seq 1 100); do \
		if curl -fsS "$$BASE_URL/health" >/dev/null 2>&1; then \
			READY=1; \
			break; \
		fi; \
		sleep 0.2; \
	done; \
	if [ "$$READY" -ne 1 ]; then \
		echo "Server failed to start. See /tmp/polinko-quality-gate.log"; \
		exit 1; \
	fi; \
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"; \
	$(PYTHON) -m tools.eval_retrieval --base-url "$$BASE_URL"; \
	$(PYTHON) -m tools.eval_file_search --base-url "$$BASE_URL"; \
	$(PYTHON) -m tools.eval_ocr --base-url "$$BASE_URL" --strict; \
	$(PYTHON) -m tools.eval_style --base-url "$$BASE_URL" --strict; \
	$(PYTHON) -m tools.eval_hallucination --base-url "$$BASE_URL" --strict --evaluation-mode "$(HALLUCINATION_EVAL_MODE)" --judge-model "$(HALLUCINATION_JUDGE_MODEL)" --judge-api-key-env "$(HALLUCINATION_JUDGE_API_KEY_ENV)" --judge-base-url "$(HALLUCINATION_JUDGE_BASE_URL)" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"; \
	echo "Quality gate passed."

quality-gate-deterministic:
	@$(MAKE) quality-gate HALLUCINATION_EVAL_MODE=deterministic

evidence-index:
	$(PYTHON) -m tools.build_evidence_index

evidence-refresh:
	@set -eu; \
	$(MAKE) evidence-index; \
	$(MAKE) portfolio-metadata-audit; \
	INDEX_JSON="docs/portfolio/raw_evidence/index.json"; \
	if [ -f "$$INDEX_JSON" ]; then \
		if command -v rg >/dev/null 2>&1; then \
			TOTAL=$$(rg -o '"evidence_id"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
			OPEN=$$(rg -o '"status": "OPEN"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
			CLOSED=$$(rg -o '"status": "CLOSED"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
		else \
			TOTAL=$$(grep -o '"evidence_id"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
			OPEN=$$(grep -o '"status": "OPEN"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
			CLOSED=$$(grep -o '"status": "CLOSED"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
		fi; \
		echo "Evidence refresh summary: total=$$TOTAL open=$$OPEN closed=$$CLOSED"; \
	fi

portfolio-metadata-audit:
	$(PYTHON) -m tools.audit_portfolio_metadata --strict

reference-graph:
	$(PYTHON) -m tools.build_reference_graph

dev:
	@PYTHON_BIN="$(PYTHON)" DEV_HOST="$(DEV_HOST)" DEV_BACKEND_PORT="$(DEV_BACKEND_PORT)" DEV_AUTOKILL="$(DEV_AUTOKILL)" bash tools/dev_run.sh

dev-stop:
	@DEV_BACKEND_PORT="$(DEV_BACKEND_PORT)" DEV_AUTOKILL="$(DEV_AUTOKILL)" DEV_STOP_ONLY=1 bash tools/dev_run.sh

docker-build:
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run:
	$(DOCKER) run --rm -p $(DOCKER_PORT):8000 --env-file $(ENV_FILE) $(DOCKER_IMAGE)
