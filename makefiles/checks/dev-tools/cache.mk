# Local cache cleanup helper targets.
.PHONY: cache-clean-preview cache-clean

cache-clean-preview:
	@$(call repo_activity,make cache-clean-preview,cache-clean-preview)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m tools.clean_runtime_caches

cache-clean:
	@$(call repo_activity,make cache-clean,cache-clean)
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m tools.clean_runtime_caches --apply
