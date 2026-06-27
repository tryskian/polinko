# Manual eval OCR retry selection and readiness targets.
.PHONY: manual-evals-ocr-retry-rerun-plan manualdb-ocr-retry-rerun-plan
.PHONY: manual-evals-ocr-retry-selection-review manualdb-ocr-retry-selection-review
.PHONY: manual-evals-ocr-retry-selection-template manualdb-ocr-retry-selection-template
.PHONY: manual-evals-ocr-retry-selection-draft manualdb-ocr-retry-selection-draft
.PHONY: manual-evals-ocr-retry-selection-validate manualdb-ocr-retry-selection-validate
.PHONY: manual-evals-ocr-retry-selection-apply-preview manualdb-ocr-retry-selection-apply-preview
.PHONY: manual-evals-ocr-retry-execution-readiness manualdb-ocr-retry-execution-readiness

manual-evals-ocr-retry-rerun-plan manualdb-ocr-retry-rerun-plan:
	$(call manual_evals_db_health,--ocr-retry-rerun-plan,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS))

manual-evals-ocr-retry-selection-review manualdb-ocr-retry-selection-review:
	$(call manual_evals_db_health,--ocr-retry-selection-review,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS))

manual-evals-ocr-retry-selection-template manualdb-ocr-retry-selection-template:
	$(call manual_evals_db_health,--ocr-retry-selection-template,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS))

manual-evals-ocr-retry-selection-draft manualdb-ocr-retry-selection-draft:
	$(call manual_evals_db_health,--ocr-retry-selection-draft,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS) $(MANUAL_EVALS_OCR_RETRY_SELECTION_DRAFT_ARGS))

manual-evals-ocr-retry-selection-validate manualdb-ocr-retry-selection-validate:
	$(call manual_evals_db_health,--ocr-retry-selection-validate,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS) $(MANUAL_EVALS_OCR_RETRY_SELECTION_VALIDATE_ARGS))

manual-evals-ocr-retry-selection-apply-preview manualdb-ocr-retry-selection-apply-preview:
	$(call manual_evals_db_health,--ocr-retry-selection-apply-preview,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS) $(MANUAL_EVALS_OCR_RETRY_SELECTION_VALIDATE_ARGS))

manual-evals-ocr-retry-execution-readiness manualdb-ocr-retry-execution-readiness:
	$(call manual_evals_db_health,--ocr-retry-execution-readiness,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS) $(MANUAL_EVALS_OCR_RETRY_SELECTION_VALIDATE_ARGS))
