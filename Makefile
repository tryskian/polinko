PYTHON ?= python3

.PHONY: test run

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

run:
	$(PYTHON) -m nautorus.app
