# Notebook surface targets.
.PHONY: notebook-setup notebook nb notes

notebook-setup:
	@$(call repo_activity,make notebook-setup,notebook-setup)
	@test -f requirements.notebook.txt || { echo "notebook helper: missing requirements file: requirements.notebook.txt" >&2; exit 1; }
	$(PYTHON) -m pip install -r requirements.notebook.txt

notebook nb notes:
	@$(call repo_activity,make $@,$@)
	@$(PYTHON) -c 'import importlib.util, sys; sys.exit(0 if importlib.util.find_spec("jupyter") else 1)' || { echo "notebook helper: missing Python module: jupyter (run make notebook-setup)" >&2; exit 1; }
	@mkdir -p "$(NOTEBOOK_DIR_ABS)"; \
	if [ -f "$(NOTEBOOK_START_PATH_ABS)" ]; then \
		$(PYTHON) -m jupyter lab --notebook-dir="$(NOTEBOOK_DIR_ABS)" "$(NOTEBOOK_START_PATH_ABS)"; \
	else \
		$(PYTHON) -m jupyter lab --notebook-dir="$(NOTEBOOK_DIR_ABS)" "$(NOTEBOOK_DIR_ABS)"; \
	fi
