# GitHub repository health helper targets.
.PHONY: github-health github-pr-create

github-health:
	@$(call repo_activity,make github-health,github-health)
	$(PYTHON) -m tools.github_health --gh "$(GH)" --run-limit "$(GITHUB_HEALTH_RUN_LIMIT)" --pr-limit "$(GITHUB_HEALTH_PR_LIMIT)" $(if $(strip $(GITHUB_HEALTH_REPO)),--repo "$(GITHUB_HEALTH_REPO)",)

github-pr-create:
	@$(call repo_activity,make github-pr-create,github-pr-create)
	./tools/github_pr_create.sh --gh "$(GH)" --base "$(GITHUB_PR_BASE)" --head "$(GITHUB_PR_HEAD)" --title "$(GITHUB_PR_TITLE)" --body-file "$(GITHUB_PR_BODY_FILE)"
