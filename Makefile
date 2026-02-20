PYTHON ?= ./polinko-repositioning-system/bin/python

.PHONY: eval chat server test

eval:
	$(PYTHON) -m tools.eval_regression

chat:
	$(PYTHON) app.py

server:
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"
