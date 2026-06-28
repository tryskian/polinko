# OCR workflow script entrypoints and base runtime environment.
OCR_WORKFLOW_SCRIPT ?= ./tools/run_ocr_workflow.sh
OCR_INTAKE_WORKFLOW_SCRIPT ?= ./tools/run_ocr_intake_workflow.sh
OCR_INTAKE_WORKFLOW_ENV = \
	PYTHON="$(PYTHON)"
