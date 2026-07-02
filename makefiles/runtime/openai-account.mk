# OpenAI account summary targets.
.PHONY: openai-account-summary openai-costs openai-usage openai-limits

openai-account-summary:
	@$(call repo_activity,make openai-account-summary,openai-account-summary)
	@$(OPENAI_ACCOUNT_ENV) "$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" summary

openai-costs:
	@$(call repo_activity,make openai-costs,openai-costs)
	@$(OPENAI_ACCOUNT_ENV) "$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" costs

openai-usage:
	@$(call repo_activity,make openai-usage,openai-usage)
	@$(OPENAI_ACCOUNT_ENV) "$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" usage

openai-limits:
	@$(call repo_activity,make openai-limits,openai-limits)
	@$(OPENAI_ACCOUNT_ENV) "$(PYTHON)" "$(OPENAI_ACCOUNT_SCRIPT)" limits
