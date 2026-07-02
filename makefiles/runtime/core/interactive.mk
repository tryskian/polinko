# Interactive runtime entrypoints.
.PHONY: chat venv

chat:
	@$(call repo_activity,make chat,chat)
	$(PYTHON) $(CLI_ENTRYPOINT)

venv:
	@$(call repo_activity,make $@,$@)
	@bash ./tools/open_venv_shell.sh
