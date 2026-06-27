# Manual eval OCR retry bundle helper targets.
.PHONY: manual-evals-ocr-retry-candidates manualdb-ocr-retry-candidates
.PHONY: manual-evals-ocr-retry-source-verification manualdb-ocr-retry-source-verification
.PHONY: manual-evals-ocr-retry-source-provenance manualdb-ocr-retry-source-provenance
.PHONY: manual-evals-ocr-retry-input-packet manualdb-ocr-retry-input-packet
.PHONY: manual-evals-ocr-retry-rerun-manifest manualdb-ocr-retry-rerun-manifest
.PHONY: manual-evals-ocr-retry-rerun-plan manualdb-ocr-retry-rerun-plan
.PHONY: manual-evals-ocr-retry-selection-review manualdb-ocr-retry-selection-review
.PHONY: manual-evals-ocr-retry-selection-template manualdb-ocr-retry-selection-template
.PHONY: manual-evals-ocr-retry-selection-draft manualdb-ocr-retry-selection-draft
.PHONY: manual-evals-ocr-retry-selection-validate manualdb-ocr-retry-selection-validate
.PHONY: manual-evals-ocr-retry-selection-apply-preview manualdb-ocr-retry-selection-apply-preview
.PHONY: manual-evals-ocr-retry-execution-readiness manualdb-ocr-retry-execution-readiness
.PHONY: manual-evals-ocr-retry-execute manualdb-ocr-retry-execute
.PHONY: manual-evals-ocr-retry-execution-report manualdb-ocr-retry-execution-report
.PHONY: manual-evals-ocr-retry-feedback-closure-preview manualdb-ocr-retry-feedback-closure-preview
.PHONY: manual-evals-ocr-retry-feedback-closure-apply manualdb-ocr-retry-feedback-closure-apply
.PHONY: manual-evals-ocr-retry-feedback-closure-apply-report manualdb-ocr-retry-feedback-closure-apply-report
.PHONY: manual-evals-ocr-retry-feedback-closure-restore-preview manualdb-ocr-retry-feedback-closure-restore-preview
.PHONY: manual-evals-ocr-retry-feedback-closure-restore manualdb-ocr-retry-feedback-closure-restore

manual-evals-ocr-retry-candidates manualdb-ocr-retry-candidates:
	$(call manual_evals_db_health,--ocr-retry-candidates,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-source-verification manualdb-ocr-retry-source-verification:
	$(call manual_evals_db_health,--ocr-retry-source-verification,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-source-provenance manualdb-ocr-retry-source-provenance:
	$(call manual_evals_db_health,--ocr-retry-source-provenance,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-input-packet manualdb-ocr-retry-input-packet:
	$(call manual_evals_db_health,--ocr-retry-input-packet,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-rerun-manifest manualdb-ocr-retry-rerun-manifest:
	$(call manual_evals_db_health,--ocr-retry-rerun-manifest,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

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

manual-evals-ocr-retry-execute manualdb-ocr-retry-execute:
	$(call manual_evals_db_health,--ocr-retry-execute,$(MANUAL_EVALS_OCR_RETRY_EXECUTE_ARGS))

manual-evals-ocr-retry-execution-report manualdb-ocr-retry-execution-report:
	$(call manual_evals_db_health,--ocr-retry-execution-report,$(MANUAL_EVALS_OCR_RETRY_EXECUTION_REPORT_ARGS))

manual-evals-ocr-retry-feedback-closure-preview manualdb-ocr-retry-feedback-closure-preview:
	$(call manual_evals_db_health,--ocr-retry-feedback-closure-preview,$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_ARGS))

manual-evals-ocr-retry-feedback-closure-apply manualdb-ocr-retry-feedback-closure-apply:
	$(call manual_evals_db_health,--ocr-retry-feedback-closure-apply,$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_APPLY_ARGS))

manual-evals-ocr-retry-feedback-closure-apply-report manualdb-ocr-retry-feedback-closure-apply-report:
	$(call manual_evals_db_health,--ocr-retry-feedback-closure-apply-report,$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_ARGS))

manual-evals-ocr-retry-feedback-closure-restore-preview manualdb-ocr-retry-feedback-closure-restore-preview:
	$(call manual_evals_db_health,--ocr-retry-feedback-closure-restore-preview,$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_ARGS))

manual-evals-ocr-retry-feedback-closure-restore manualdb-ocr-retry-feedback-closure-restore:
	$(call manual_evals_db_health,--ocr-retry-feedback-closure-restore,$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_APPLY_ARGS))
