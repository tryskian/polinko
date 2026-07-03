# Local GitHub Actions runner helper targets.
.PHONY: act-list act-ci

act-list:
	@$(call repo_activity,make act-list,act-list)
	@$(PYTHON) -m tools.require_command --command "$(ACT)" --label "act helper"
	$(ACT) -l

act-ci:
	@$(call repo_activity,make act-ci,act-ci)
	@$(PYTHON) -m tools.require_command --command "$(ACT)" --label "act helper"
	$(ACT) -W .github/workflows/ci.yml
