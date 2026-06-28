# Ruff lint and format checks.
.PHONY: ruff-check ruff-format-check

ruff-check:
	@$(call repo_activity,make ruff-check,ruff-check)
	$(PYTHON) -m ruff check .

ruff-format-check:
	@$(call repo_activity,make ruff-format-check,ruff-format-check)
	$(PYTHON) -m ruff format --check .
