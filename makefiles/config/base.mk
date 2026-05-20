# Base tool configuration shared by every target family.
VENV ?= .venv
PYTHON ?= $(shell \
	if [ -x ./$(VENV)/bin/python3.14 ] && ./$(VENV)/bin/python3.14 -V >/dev/null 2>&1; then \
		echo ./$(VENV)/bin/python3.14; \
	elif [ -x ./$(VENV)/bin/python ] && ./$(VENV)/bin/python -V >/dev/null 2>&1; then \
		echo ./$(VENV)/bin/python; \
	else \
		echo python3; \
	fi)
