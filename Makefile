PYTHON ?= $(shell \
	if [ -x ./polinko-repositioning-system/bin/python ] && ./polinko-repositioning-system/bin/python -V >/dev/null 2>&1; then \
		echo ./polinko-repositioning-system/bin/python; \
	elif [ -x ./venv/bin/python ] && ./venv/bin/python -V >/dev/null 2>&1; then \
		echo ./venv/bin/python; \
	else \
		echo python3; \
	fi)
NPM ?= npm
DOCKER ?= docker
DOCKER_IMAGE ?= polinko:dev
DOCKER_PORT ?= 8000
DEV_HOST ?= 127.0.0.1
DEV_BACKEND_PORT ?= 8000
DEV_FRONTEND_PORT ?= 5173
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

.PHONY: chat server test doctor-env precommit-install precommit-run act-list act-ci k6-chat-smoke trivy-fs trivy-image eval-retrieval eval-retrieval-report eval-file-search eval-file-search-report eval-hallucination eval-hallucination-deterministic eval-hallucination-braintrust eval-hallucination-report eval-style eval-style-report eval-ocr eval-ocr-report eval-ocr-recovery eval-ocr-recovery-report eval-clip-ab eval-clip-ab-report eval-clip-ab-readiness eval-inbox eval-cleanup eval-reports calibrate-hallucination-threshold hallucination-gate quality-gate quality-gate-deterministic evidence-index evidence-refresh portfolio-metadata-audit ui-install ui-dev ui-build ui-e2e-install ui-e2e docker-build docker-run dev dev-stop workbench

chat:
	$(PYTHON) app.py

server:
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

doctor-env:
	$(PYTHON) tools/doctor_env.py

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
	$(PYTHON) tools/eval_retrieval.py

eval-retrieval-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) tools/eval_retrieval.py --run-id $$RUN_ID --report-json "eval_reports/retrieval-$$RUN_ID.json"

eval-file-search:
	$(PYTHON) tools/eval_file_search.py

eval-file-search-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) tools/eval_file_search.py --run-id $$RUN_ID --report-json "eval_reports/file-search-$$RUN_ID.json"

eval-hallucination:
	$(PYTHON) tools/eval_hallucination.py --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-deterministic:
	$(PYTHON) tools/eval_hallucination.py --evaluation-mode deterministic --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

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
	$(PYTHON) tools/eval_hallucination.py --evaluation-mode judge --judge-api-key-env BRAINTRUST_API_KEY --judge-base-url "$$BASE_URL" --judge-model "$(HALLUCINATION_JUDGE_MODEL)" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) tools/eval_hallucination.py --run-id $$RUN_ID --report-json "eval_reports/hallucination-$$RUN_ID.json" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

calibrate-hallucination-threshold:
	$(PYTHON) tools/calibrate_hallucination_threshold.py

eval-style:
	$(PYTHON) tools/eval_style.py

eval-style-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) tools/eval_style.py --run-id $$RUN_ID --report-json "eval_reports/style-$$RUN_ID.json"

eval-ocr:
	$(PYTHON) tools/eval_ocr.py

eval-ocr-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) tools/eval_ocr.py --run-id $$RUN_ID --report-json "eval_reports/ocr-$$RUN_ID.json"

eval-ocr-recovery:
	$(PYTHON) tools/eval_ocr_recovery.py

eval-ocr-recovery-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) tools/eval_ocr_recovery.py --run-id $$RUN_ID --report-json "eval_reports/ocr-recovery-$$RUN_ID.json"

eval-clip-ab:
	$(PYTHON) tools/eval_clip_ab.py --source-types "$(CLIP_AB_SOURCE_TYPES)"

eval-clip-ab-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) tools/eval_clip_ab.py --source-types "$(CLIP_AB_SOURCE_TYPES)" --run-id $$RUN_ID --report-json "eval_reports/clip-ab-$$RUN_ID.json"

eval-clip-ab-readiness:
	$(PYTHON) tools/eval_clip_ab_readiness.py

eval-inbox:
	$(PYTHON) tools/eval_inbox.py --new --limit 30

eval-cleanup:
	$(PYTHON) tools/cleanup_eval_chats.py

eval-reports:
	@$(MAKE) eval-retrieval-report
	@$(MAKE) eval-file-search-report
	@$(MAKE) eval-ocr-report
	@$(MAKE) eval-style-report
	@$(MAKE) eval-hallucination-report

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
	$(PYTHON) tools/eval_hallucination.py --base-url "$$BASE_URL" --strict --evaluation-mode "$(HALLUCINATION_EVAL_MODE)" --judge-model "$(HALLUCINATION_JUDGE_MODEL)" --judge-api-key-env "$(HALLUCINATION_JUDGE_API_KEY_ENV)" --judge-base-url "$(HALLUCINATION_JUDGE_BASE_URL)" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"; \
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
	$(PYTHON) tools/eval_retrieval.py --base-url "$$BASE_URL"; \
	$(PYTHON) tools/eval_file_search.py --base-url "$$BASE_URL"; \
	$(PYTHON) tools/eval_ocr.py --base-url "$$BASE_URL" --strict; \
	$(PYTHON) tools/eval_style.py --base-url "$$BASE_URL" --strict; \
	$(PYTHON) tools/eval_hallucination.py --base-url "$$BASE_URL" --strict --evaluation-mode "$(HALLUCINATION_EVAL_MODE)" --judge-model "$(HALLUCINATION_JUDGE_MODEL)" --judge-api-key-env "$(HALLUCINATION_JUDGE_API_KEY_ENV)" --judge-base-url "$(HALLUCINATION_JUDGE_BASE_URL)" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"; \
	echo "Quality gate passed."

quality-gate-deterministic:
	@$(MAKE) quality-gate HALLUCINATION_EVAL_MODE=deterministic

evidence-index:
	$(PYTHON) tools/build_evidence_index.py

evidence-refresh:
	@set -eu; \
	OVERRIDES="docs/portfolio/raw_evidence/triage_overrides.json"; \
	TEMPLATE="docs/portfolio/raw_evidence/triage_overrides.example.json"; \
	if [ ! -f "$$OVERRIDES" ] && [ -f "$$TEMPLATE" ]; then \
		cp "$$TEMPLATE" "$$OVERRIDES"; \
		echo "Initialized $$OVERRIDES from template."; \
	fi; \
	$(MAKE) evidence-index; \
	$(MAKE) portfolio-metadata-audit; \
	INDEX_JSON="docs/portfolio/raw_evidence/index.json"; \
	if [ -f "$$INDEX_JSON" ]; then \
		TOTAL=$$(rg -o '"evidence_id"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
		OPEN=$$(rg -o '"status": "OPEN"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
		CLOSED=$$(rg -o '"status": "CLOSED"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
		echo "Evidence refresh summary: total=$$TOTAL open=$$OPEN closed=$$CLOSED"; \
	fi

portfolio-metadata-audit:
	$(PYTHON) tools/audit_portfolio_metadata.py --strict

ui-dev:
	cd frontend && $(NPM) run dev

ui-install:
	cd frontend && $(NPM) install

ui-build:
	cd frontend && $(NPM) run build

ui-e2e-install:
	cd frontend && npx playwright install

ui-e2e:
	cd frontend && $(NPM) run test:e2e

dev:
	@PYTHON_BIN="$(PYTHON)" NPM_BIN="$(NPM)" DEV_HOST="$(DEV_HOST)" DEV_BACKEND_PORT="$(DEV_BACKEND_PORT)" DEV_FRONTEND_PORT="$(DEV_FRONTEND_PORT)" DEV_AUTOKILL="$(DEV_AUTOKILL)" bash tools/dev_run.sh

dev-stop:
	@DEV_BACKEND_PORT="$(DEV_BACKEND_PORT)" DEV_FRONTEND_PORT="$(DEV_FRONTEND_PORT)" DEV_AUTOKILL="$(DEV_AUTOKILL)" DEV_STOP_ONLY=1 bash tools/dev_run.sh

workbench:
	@echo "Starting portfolio workbench on http://127.0.0.1:$(WORKBENCH_PORT)/workbench.html"
	$(PYTHON) tools/workbench_server.py --port $(WORKBENCH_PORT)

docker-build:
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run:
	$(DOCKER) run --rm -p $(DOCKER_PORT):8000 --env-file $(ENV_FILE) $(DOCKER_IMAGE)
