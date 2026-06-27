# Manual eval OCR retry feedback-closure targets.
.PHONY: manual-evals-ocr-retry-feedback-closure-preview manualdb-ocr-retry-feedback-closure-preview
.PHONY: manual-evals-ocr-retry-feedback-closure-apply manualdb-ocr-retry-feedback-closure-apply
.PHONY: manual-evals-ocr-retry-feedback-closure-apply-report manualdb-ocr-retry-feedback-closure-apply-report
.PHONY: manual-evals-ocr-retry-feedback-closure-restore-preview manualdb-ocr-retry-feedback-closure-restore-preview
.PHONY: manual-evals-ocr-retry-feedback-closure-restore manualdb-ocr-retry-feedback-closure-restore

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
