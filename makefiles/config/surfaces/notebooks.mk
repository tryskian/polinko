# Notebook surface configuration.
NOTEBOOK_DIR ?= .local/notebooks
NOTEBOOK_START_PATH ?= $(NOTEBOOK_DIR)/ocr-eval-live-filters-starter.ipynb
NOTEBOOK_START_PATH_ABS := $(abspath $(NOTEBOOK_START_PATH))
NOTEBOOK_DIR_ABS := $(abspath $(NOTEBOOK_DIR))
