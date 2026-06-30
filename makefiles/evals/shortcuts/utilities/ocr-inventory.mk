# OCR inventory shortcuts.
.PHONY: ocr-inventory ocr-inventory-json

ocr-inventory:
	@$(PYTHON) "$(OCR_LANE_INVENTORY_SCRIPT)" $(strip $(OCR_LANE_INVENTORY_ARGS)) $(if $(strip $(OCR_LANE_INVENTORY_FRESHNESS_DAYS)),--freshness-days "$(OCR_LANE_INVENTORY_FRESHNESS_DAYS)")

ocr-inventory-json: OCR_LANE_INVENTORY_ARGS = --json
ocr-inventory-json: ocr-inventory
