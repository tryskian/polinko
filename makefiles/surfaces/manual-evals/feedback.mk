# Manual eval feedback review and reclassification targets.
.PHONY: manual-evals-feedback-actionables manualdb-feedback-actionables
.PHONY: manual-evals-feedback-cohorts manualdb-feedback-cohorts
.PHONY: manual-evals-feedback-source-context manualdb-feedback-source-context
.PHONY: manual-evals-feedback-decision-draft manualdb-feedback-decision-draft
.PHONY: manual-evals-feedback-decision-preview manualdb-feedback-decision-preview
.PHONY: manual-evals-no-context-reclassify-preview manualdb-no-context-reclassify-preview
.PHONY: manual-evals-no-context-reclassify-apply manualdb-no-context-reclassify-apply
.PHONY: manual-evals-feedback-reclassify-preview manualdb-feedback-reclassify-preview
.PHONY: manual-evals-feedback-reclassify-apply manualdb-feedback-reclassify-apply

manual-evals-feedback-actionables manualdb-feedback-actionables:
	$(call manual_evals_db_health,--open-feedback-actionables,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-feedback-cohorts manualdb-feedback-cohorts:
	$(call manual_evals_db_health,--open-feedback-cohorts,$(MANUAL_EVALS_FEEDBACK_FILTER_ARGS))

manual-evals-feedback-source-context manualdb-feedback-source-context:
	$(call manual_evals_db_health,--feedback-source-context,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-feedback-decision-draft manualdb-feedback-decision-draft:
	$(call manual_evals_db_health,--feedback-decision-draft,$(MANUAL_EVALS_FEEDBACK_DECISION_DRAFT_ARGS))

manual-evals-feedback-decision-preview manualdb-feedback-decision-preview:
	$(call manual_evals_db_health,--feedback-decision-preview,$(MANUAL_EVALS_FEEDBACK_DECISION_ARGS))

manual-evals-no-context-reclassify-preview manualdb-no-context-reclassify-preview:
	$(call manual_evals_db_health,--no-context-feedback-reclassify-preview,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-no-context-reclassify-apply manualdb-no-context-reclassify-apply:
	$(call manual_evals_db_health,--no-context-feedback-reclassify-apply,$(MANUAL_EVALS_NO_CONTEXT_RECLASSIFY_ARGS))

manual-evals-feedback-reclassify-preview manualdb-feedback-reclassify-preview:
	$(call manual_evals_db_health,--feedback-reclassify-preview,$(MANUAL_EVALS_FEEDBACK_RECLASSIFY_ARGS))

manual-evals-feedback-reclassify-apply manualdb-feedback-reclassify-apply:
	$(call manual_evals_db_health,--feedback-reclassify-apply,$(MANUAL_EVALS_FEEDBACK_RECLASSIFY_APPLY_ARGS))
