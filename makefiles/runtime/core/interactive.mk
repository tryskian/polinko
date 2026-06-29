# Interactive runtime entrypoints.
.PHONY: chat venv env

chat:
	@$(call repo_activity,make chat,chat)
	$(PYTHON) $(CLI_ENTRYPOINT)

venv env:
	@$(call repo_activity,make $@,$@)
	@set -eu; \
	if [ -f ./.venv/bin/activate ]; then \
		ACTIVATE_PATH="./.venv/bin/activate"; \
	else \
		echo "No local activation script found (checked ./.venv/bin/activate)."; \
		exit 1; \
	fi; \
	echo "Opening shell with virtual environment: $$ACTIVATE_PATH"; \
	. "$$ACTIVATE_PATH"; \
	echo "VIRTUAL_ENV=$$VIRTUAL_ENV"; \
	exec "$$SHELL" -i
