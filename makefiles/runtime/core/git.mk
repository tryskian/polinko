# Git hygiene targets.
.PHONY: end-git-check git-prune-stale-refs

end-git-check:
	@$(call repo_activity,make end-git-check,end-git-check)
	bash ./tools/check_end_git_clean.sh

git-prune-stale-refs:
	@$(call repo_activity,make git-prune-stale-refs,git-prune-stale-refs)
	git remote prune origin
