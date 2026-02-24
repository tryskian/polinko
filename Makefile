PYTHON ?= ./polinko-repositioning-system/bin/python
NPM ?= npm
DOCKER ?= docker
DOCKER_IMAGE ?= polinko:dev
DOCKER_PORT ?= 8000
ENV_FILE ?= .env
GATE_PORT ?= 8066
GATE_BASE_URL ?= http://127.0.0.1:$(GATE_PORT)

.PHONY: chat server test eval-retrieval eval-file-search eval-hallucination quality-gate ui-install ui-dev ui-build docker-build docker-run dev

chat:
	$(PYTHON) app.py

server:
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

eval-retrieval:
	$(PYTHON) tools/eval_retrieval.py

eval-file-search:
	$(PYTHON) tools/eval_file_search.py

eval-hallucination:
	$(PYTHON) tools/eval_hallucination.py

quality-gate:
	@echo "Running quality gate (tests + retrieval eval + hallucination eval)..."
	@set -eu; \
	BASE_URL="$(GATE_BASE_URL)"; \
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
	$(PYTHON) tools/eval_hallucination.py --base-url "$$BASE_URL" --strict; \
	echo "Quality gate passed."

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

docker-build:
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run:
	$(DOCKER) run --rm -p $(DOCKER_PORT):8000 --env-file $(ENV_FILE) $(DOCKER_IMAGE)
