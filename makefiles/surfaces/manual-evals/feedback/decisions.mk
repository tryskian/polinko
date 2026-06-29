# Manual eval feedback decision targets.
.PHONY: manual-evals-feedback-decision-draft
.PHONY: manual-evals-feedback-decision-preview

manual-evals-feedback-decision-draft:
	$(call manual_evals_db_health,--feedback-decision-draft,$(MANUAL_EVALS_FEEDBACK_DECISION_DRAFT_ARGS))

manual-evals-feedback-decision-preview:
	$(call manual_evals_db_health,--feedback-decision-preview,$(MANUAL_EVALS_FEEDBACK_DECISION_ARGS))
