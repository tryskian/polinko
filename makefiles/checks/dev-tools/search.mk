# Local repository search helper targets.
.PHONY: repo-search repo-search-full

repo-search:
	@$(PYTHON) -m tools.repo_search --check-query --make-target repo-search --query "$(Q)"
	@$(call repo_activity,make repo-search,repo-search)
	$(PYTHON) -m tools.repo_search --query "$(Q)"

repo-search-full:
	@$(PYTHON) -m tools.repo_search --check-query --make-target repo-search-full --query "$(Q)"
	@$(call repo_activity,make repo-search-full,repo-search-full)
	$(PYTHON) -m tools.repo_search --mode full --query "$(Q)"
