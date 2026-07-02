# Dependency refresh target.
.PHONY: deps-refresh

deps-refresh:
	@$(call repo_activity,make deps-refresh,deps-refresh)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install --upgrade --upgrade-strategy eager -r "$(REQUIREMENTS_LOCK)"
	npm install --no-audit --no-fund
