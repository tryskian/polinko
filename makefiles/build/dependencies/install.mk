# Dependency install target.
.PHONY: deps-install

deps-install:
	@$(call repo_activity,make deps-install,deps-install)
	$(PYTHON) -m pip install -r "$(REQUIREMENTS_LOCK)"
