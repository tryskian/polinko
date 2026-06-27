# Local developer helper targets.
.PHONY: repo-search repo-search-full precommit-install precommit-run act-list act-ci

repo-search:
	@set -eu; \
	if [ -z "$(Q)" ]; then \
		echo 'Usage: make repo-search Q="pattern"'; \
		exit 2; \
	fi; \
	$(PYTHON) -m tools.repo_search --query "$(Q)"

repo-search-full:
	@set -eu; \
	if [ -z "$(Q)" ]; then \
		echo 'Usage: make repo-search-full Q="pattern"'; \
		exit 2; \
	fi; \
	$(PYTHON) -m tools.repo_search --mode full --query "$(Q)"

precommit-install:
	@$(call repo_activity,make precommit-install,precommit-install)
	$(PYTHON) -m pre_commit install --install-hooks --hook-type pre-commit

precommit-run:
	@$(call repo_activity,make precommit-run,precommit-run)
	$(PYTHON) -m pre_commit run --all-files

act-list:
	$(ACT) -l

act-ci:
	$(ACT) -W .github/workflows/ci.yml
