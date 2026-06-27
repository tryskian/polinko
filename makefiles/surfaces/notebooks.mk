# Notebook surface targets.
.PHONY: notebook-setup notebook nb notes

notebook-setup:
	$(PYTHON) -m pip install -r requirements.notebook.txt

notebook nb notes:
	@mkdir -p "$(NOTEBOOK_DIR_ABS)"; \
	if [ -f "$(NOTEBOOK_START_PATH_ABS)" ]; then \
		$(PYTHON) -m jupyter lab --notebook-dir="$(NOTEBOOK_DIR_ABS)" "$(NOTEBOOK_START_PATH_ABS)"; \
	else \
		$(PYTHON) -m jupyter lab --notebook-dir="$(NOTEBOOK_DIR_ABS)" "$(NOTEBOOK_DIR_ABS)"; \
	fi
