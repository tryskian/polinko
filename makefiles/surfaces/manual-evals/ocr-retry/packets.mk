# Manual eval OCR retry read-only packet targets.
.PHONY: manual-evals-ocr-retry-candidates
.PHONY: manual-evals-ocr-retry-source-verification
.PHONY: manual-evals-ocr-retry-source-provenance
.PHONY: manual-evals-ocr-retry-input-packet
.PHONY: manual-evals-ocr-retry-rerun-manifest

manual-evals-ocr-retry-candidates:
	$(call manual_evals_db_health,--ocr-retry-candidates,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-source-verification:
	$(call manual_evals_db_health,--ocr-retry-source-verification,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-source-provenance:
	$(call manual_evals_db_health,--ocr-retry-source-provenance,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-input-packet:
	$(call manual_evals_db_health,--ocr-retry-input-packet,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-rerun-manifest:
	$(call manual_evals_db_health,--ocr-retry-rerun-manifest,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))
