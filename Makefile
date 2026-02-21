PYTHON ?= ./polinko-repositioning-system/bin/python
LEDGER_INPUT ?= transcript_turns.csv

.PHONY: eval chat server test build-eval-seed build-memory-facts

eval:
	$(PYTHON) -m tools.eval_regression

chat:
	$(PYTHON) app.py

server:
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

build-eval-seed:
	$(PYTHON) -m tools.build_eval_seed $(LEDGER_INPUT) --output configs/eval_seed.json

build-memory-facts:
	$(PYTHON) -m tools.build_memory_facts $(LEDGER_INPUT) --output configs/memory_facts.json
