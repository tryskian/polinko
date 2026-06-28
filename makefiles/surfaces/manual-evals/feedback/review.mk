# Manual eval feedback review targets.
.PHONY: manual-evals-feedback-actionables manualdb-feedback-actionables
.PHONY: manual-evals-feedback-cohorts manualdb-feedback-cohorts
.PHONY: manual-evals-feedback-source-context manualdb-feedback-source-context

manual-evals-feedback-actionables manualdb-feedback-actionables:
	$(call manual_evals_db_health,--open-feedback-actionables,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-feedback-cohorts manualdb-feedback-cohorts:
	$(call manual_evals_db_health,--open-feedback-cohorts,$(MANUAL_EVALS_FEEDBACK_FILTER_ARGS))

manual-evals-feedback-source-context manualdb-feedback-source-context:
	$(call manual_evals_db_health,--feedback-source-context,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))
