PYTHON ?= ./polinko-repositioning-system/bin/python
NPM ?= npm
DOCKER ?= docker
DOCKER_IMAGE ?= polinko:dev
DOCKER_PORT ?= 8000
ENV_FILE ?= .env

.PHONY: chat server test eval-retrieval eval-hallucination ui-install ui-dev ui-build docker-build docker-run dev

chat:
	$(PYTHON) app.py

server:
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

eval-retrieval:
	$(PYTHON) tools/eval_retrieval.py

eval-hallucination:
	$(PYTHON) tools/eval_hallucination.py

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
