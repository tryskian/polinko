# Dependency install, refresh, and lockfile targets.
.PHONY: deps-install deps-refresh refresh-deps deps-lock deps-lock-check

deps-install:
	@$(call repo_activity,make deps-install,deps-install)
	$(PYTHON) -m pip install -r "$(REQUIREMENTS_LOCK)"

deps-refresh refresh-deps:
	@$(call repo_activity,make deps-refresh,deps-refresh)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install --upgrade --upgrade-strategy eager -r "$(REQUIREMENTS_LOCK)"
	npm install --no-audit --no-fund
	@if [ -f "$(PORTFOLIO_APP_DIR)/package.json" ]; then \
		npm --prefix "$(PORTFOLIO_APP_DIR)" install --no-audit --no-fund; \
	fi

deps-lock:
	@$(call repo_activity,make deps-lock,deps-lock)
	@set -eu; \
	if ! $(PYTHON) -m piptools --version >/dev/null 2>&1; then \
		$(PYTHON) -m pip install "pip-tools==$(PIP_TOOLS_VERSION)"; \
	fi; \
	$(PYTHON) -m piptools compile \
		--resolver=backtracking \
		--allow-unsafe \
		--strip-extras \
		--output-file "$(REQUIREMENTS_LOCK)" \
		"$(REQUIREMENTS_IN)"

deps-lock-check:
	@$(call repo_activity,make deps-lock-check,deps-lock-check)
	$(PYTHON) -m piptools compile \
		--resolver=backtracking \
		--allow-unsafe \
		--output-file="$(REQUIREMENTS_LOCK)" \
		--strip-extras \
		"$(REQUIREMENTS_IN)"
	git diff --exit-code -- "$(REQUIREMENTS_LOCK)"
