PYTHON ?= ./polinko-repositioning-system/bin/python
NPM ?= npm

.PHONY: chat server test ui-install ui-dev ui-build

chat:
	$(PYTHON) app.py

server:
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

ui-dev:
	cd frontend && $(NPM) run dev

ui-install:
	cd frontend && $(NPM) install

ui-build:
	cd frontend && $(NPM) run build
