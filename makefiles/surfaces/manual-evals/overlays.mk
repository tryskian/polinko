# Manual eval overlay comparison and source-index targets.
.PHONY: manual-evals-overlay-comparison-readiness
.PHONY: manual-evals-overlay-source-index-draft
.PHONY: manual-evals-overlay-source-index-validate

manual-evals-overlay-comparison-readiness:
	$(call manual_evals_db_health,--overlay-ocr-comparison-readiness,$(MANUAL_EVALS_OVERLAY_COMPARISON_ARGS))

manual-evals-overlay-source-index-draft:
	$(call manual_evals_db_health,--overlay-source-index-draft,$(MANUAL_EVALS_OVERLAY_SOURCE_INDEX_DRAFT_ARGS))

manual-evals-overlay-source-index-validate:
	$(call manual_evals_db_health,--overlay-source-index-validate,$(MANUAL_EVALS_OVERLAY_SOURCE_INDEX_VALIDATE_ARGS))
