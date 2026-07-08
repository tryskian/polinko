# Closeout documentation freshness check.
.PHONY: end-docs-check

end-docs-check: path-leak-check
	@$(call repo_activity,make end-docs-check,end-docs-check)
	$(PYTHON) -m tools.check_end_docs
