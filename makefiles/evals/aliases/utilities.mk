# Small eval/runtime utility aliases.
.PHONY: nulls runtime-null-audit ocr-inventory ocr-inventory-json
.PHONY: ocr-data ocr-notebook-workflow

nulls: runtime-null-audit

runtime-null-audit:
	$(PYTHON) -m tools.audit_runtime_nulls

ocr-inventory:
	@$(PYTHON) "$(OCR_LANE_INVENTORY_SCRIPT)" $(strip $(OCR_LANE_INVENTORY_ARGS)) $(if $(strip $(OCR_LANE_INVENTORY_FRESHNESS_DAYS)),--freshness-days "$(OCR_LANE_INVENTORY_FRESHNESS_DAYS)")

ocr-inventory-json: OCR_LANE_INVENTORY_ARGS = --json
ocr-inventory-json: ocr-inventory

ocr-data:
	@CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		CGPT_EXPORT_ROOT_DEFAULT="$(CGPT_EXPORT_ROOT_DEFAULT)" \
		bash "$(OCR_WORKFLOW_SCRIPT)" ocr-data

ocr-notebook-workflow:
	@CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		CGPT_EXPORT_ROOT_DEFAULT="$(CGPT_EXPORT_ROOT_DEFAULT)" \
		bash "$(OCR_WORKFLOW_SCRIPT)" ocr-notebook-workflow
