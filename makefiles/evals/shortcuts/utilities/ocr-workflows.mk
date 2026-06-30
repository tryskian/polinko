# OCR data and notebook workflow shortcuts.
.PHONY: ocr-data ocr-notebook-workflow

ocr-data:
	@CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		CGPT_EXPORT_ROOT_DEFAULT="$(CGPT_EXPORT_ROOT_DEFAULT)" \
		bash "$(OCR_WORKFLOW_SCRIPT)" ocr-data

ocr-notebook-workflow:
	@CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		CGPT_EXPORT_ROOT_DEFAULT="$(CGPT_EXPORT_ROOT_DEFAULT)" \
		bash "$(OCR_WORKFLOW_SCRIPT)" ocr-notebook-workflow
