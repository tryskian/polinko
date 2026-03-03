PYTHON ?= ./polinko-repositioning-system/bin/python
NPM ?= npm
DOCKER ?= docker
DOCKER_IMAGE ?= polinko:dev
DOCKER_PORT ?= 8000
ENV_FILE ?= .env
GATE_PORT ?= 8066
GATE_BASE_URL ?= http://127.0.0.1:$(GATE_PORT)
GATE_SESSION_DB ?= /tmp/polinko-quality-gate-sessions.db
GATE_VECTOR_DB ?= /tmp/polinko-quality-gate-vector.db
WORKBENCH_PORT ?= 8020
HALLUCINATION_EVAL_MODE ?= judge

.PHONY: chat server test doctor-env eval-retrieval eval-retrieval-report eval-file-search eval-file-search-report eval-hallucination eval-hallucination-deterministic eval-hallucination-report eval-style eval-style-report eval-ocr eval-ocr-report eval-reports quality-gate quality-gate-deterministic evidence-index ui-install ui-dev ui-build docker-build docker-run dev workbench

chat:
	$(PYTHON) app.py

server:
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

doctor-env:
	$(PYTHON) tools/doctor_env.py

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
	$(PYTHON) tools/eval_hallucination.py

eval-hallucination-deterministic:
	$(PYTHON) tools/eval_hallucination.py --evaluation-mode deterministic

eval-hallucination-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) tools/eval_hallucination.py --run-id $$RUN_ID --report-json "eval_reports/hallucination-$$RUN_ID.json"

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

eval-reports:
	@$(MAKE) eval-retrieval-report
	@$(MAKE) eval-file-search-report
	@$(MAKE) eval-ocr-report
	@$(MAKE) eval-style-report
	@$(MAKE) eval-hallucination-report

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
	$(PYTHON) tools/eval_hallucination.py --base-url "$$BASE_URL" --strict --evaluation-mode "$(HALLUCINATION_EVAL_MODE)"; \
	echo "Quality gate passed."

quality-gate-deterministic:
	@$(MAKE) quality-gate HALLUCINATION_EVAL_MODE=deterministic

evidence-index:
	$(PYTHON) tools/build_evidence_index.py

ui-dev:
	cd frontend && $(NPM) run dev

ui-install:
	cd frontend && $(NPM) install

ui-build:
	cd frontend && $(NPM) run build

dev:
	@echo "Starting backend (8000) and frontend (5173). Press Ctrl+C to stop both."
	@set -e; \
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload & \
	SERVER_PID=$$!; \
	cd frontend && $(NPM) run dev & \
	UI_PID=$$!; \
	trap 'kill $$SERVER_PID $$UI_PID 2>/dev/null || true' EXIT INT TERM; \
	wait $$SERVER_PID $$UI_PID

workbench:
	@echo "Starting portfolio workbench on http://127.0.0.1:$(WORKBENCH_PORT)/workbench.html"
	$(PYTHON) tools/workbench_server.py --port $(WORKBENCH_PORT)

docker-build:
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run:
	$(DOCKER) run --rm -p $(DOCKER_PORT):8000 --env-file $(ENV_FILE) $(DOCKER_IMAGE)
