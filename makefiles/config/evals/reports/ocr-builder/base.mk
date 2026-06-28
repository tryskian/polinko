# OCR report builder base configuration.
OCR_REPORT_BUILDER_SCRIPT ?= ./tools/run_ocr_report_builder.sh
OCR_REPORT_BUILDER_ENV = \
	PYTHON="$(PYTHON)" \
	OCR_TRANSCRIPT_CASES_GROWTH="$(OCR_TRANSCRIPT_CASES_GROWTH)"
