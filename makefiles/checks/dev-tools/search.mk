# Local repository search helper targets.
.PHONY: repo-search repo-search-full

repo-search:
	@set -eu; \
	if [ -z "$(Q)" ]; then \
		echo 'Usage: make repo-search Q="pattern"'; \
		exit 2; \
	fi
	@$(call repo_activity,make repo-search,repo-search)
	$(PYTHON) -m tools.repo_search --query "$(Q)"

repo-search-full:
	@set -eu; \
	if [ -z "$(Q)" ]; then \
		echo 'Usage: make repo-search-full Q="pattern"'; \
		exit 2; \
	fi
	@$(call repo_activity,make repo-search-full,repo-search-full)
	$(PYTHON) -m tools.repo_search --mode full --query "$(Q)"
