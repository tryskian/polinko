# Base tool configuration shared by every target family.
VENV ?= .venv
PYTHON ?= $(shell VENV="$(VENV)" . ./tools/python_runtime.sh; polinko_default_python_bin)
