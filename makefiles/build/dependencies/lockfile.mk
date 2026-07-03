# Dependency lockfile targets.
.PHONY: deps-lock deps-lock-check

deps-lock:
	@$(call repo_activity,make deps-lock,deps-lock)
	$(PYTHON) -m tools.run_dependency_lock --python "$(PYTHON)" --requirements-in "$(REQUIREMENTS_IN)" --requirements-lock "$(REQUIREMENTS_LOCK)" --pip-tools-version "$(PIP_TOOLS_VERSION)" --ensure-pip-tools

deps-lock-check:
	@$(call repo_activity,make deps-lock-check,deps-lock-check)
	$(PYTHON) -m tools.run_dependency_lock --python "$(PYTHON)" --requirements-in "$(REQUIREMENTS_IN)" --requirements-lock "$(REQUIREMENTS_LOCK)" --check-lockfile
