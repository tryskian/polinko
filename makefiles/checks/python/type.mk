# Python type-check targets.
.PHONY: type-check pyright-check

type-check:
	@$(call repo_activity,make type-check,type-check)
	$(PYTHON) -m mypy --config-file mypy.ini

pyright-check:
	@$(call repo_activity,make pyright-check,pyright-check)
	npm run typecheck:pyright
