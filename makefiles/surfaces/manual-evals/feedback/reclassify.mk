# Manual eval feedback reclassification targets.
.PHONY: manual-evals-no-context-reclassify-preview
.PHONY: manual-evals-no-context-reclassify-apply
.PHONY: manual-evals-feedback-reclassify-preview
.PHONY: manual-evals-feedback-reclassify-apply

manual-evals-no-context-reclassify-preview:
	$(call manual_evals_db_health,--no-context-feedback-reclassify-preview,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-no-context-reclassify-apply:
	$(call manual_evals_db_health,--no-context-feedback-reclassify-apply,$(MANUAL_EVALS_NO_CONTEXT_RECLASSIFY_ARGS))

manual-evals-feedback-reclassify-preview:
	$(call manual_evals_db_health,--feedback-reclassify-preview,$(MANUAL_EVALS_FEEDBACK_RECLASSIFY_ARGS))

manual-evals-feedback-reclassify-apply:
	$(call manual_evals_db_health,--feedback-reclassify-apply,$(MANUAL_EVALS_FEEDBACK_RECLASSIFY_APPLY_ARGS))
