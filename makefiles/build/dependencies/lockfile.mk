# Dependency lockfile targets.
.PHONY: deps-lock deps-lock-check

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
