# GitHub repository health helper targets.
.PHONY: github-health

github-health:
	@$(call repo_activity,make github-health,github-health)
	$(PYTHON) -m tools.github_health --gh "$(GH)"
