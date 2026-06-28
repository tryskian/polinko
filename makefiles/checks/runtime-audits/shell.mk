# Shell helper audit target.
.PHONY: scripts-check

scripts-check:
	@$(call repo_activity,make scripts-check,scripts-check)
	$(PYTHON) -m tools.check_shell_scripts
