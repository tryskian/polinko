# OCR kernel workflow alias.
.PHONY: ocrkernel

ocrkernel:
	@CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		CGPT_EXPORT_ROOT_DEFAULT="$(CGPT_EXPORT_ROOT_DEFAULT)" \
		bash "$(OCR_WORKFLOW_SCRIPT)" ocrkernel
