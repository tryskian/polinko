# GitHub repository health helper targets.
.PHONY: github-health

github-health:
	@$(call repo_activity,make github-health,github-health)
	$(PYTHON) -m tools.github_health --gh "$(GH)" --run-limit "$(GITHUB_HEALTH_RUN_LIMIT)" --pr-limit "$(GITHUB_HEALTH_PR_LIMIT)" $(if $(strip $(GITHUB_HEALTH_REPO)),--repo "$(GITHUB_HEALTH_REPO)",)
