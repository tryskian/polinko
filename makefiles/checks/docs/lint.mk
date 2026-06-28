# Documentation lint check.
.PHONY: lint-docs

lint-docs:
	@$(call repo_activity,make lint-docs,lint-docs)
	npm run lint:docs
