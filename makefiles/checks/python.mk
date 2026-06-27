# Python static-analysis and compile targets.
.PHONY: pycheck type-check pyright-check ruff-check ruff-format-check

pycheck:
	@set -eu; \
	if [ -z "$(FILES)" ]; then \
		echo 'Usage: make pycheck FILES="tools/check_shell_scripts.py tools/check_runtime_risk_scan.py"'; \
		exit 2; \
	fi; \
	$(PYTHON) -m py_compile $(FILES)

type-check:
	@$(call repo_activity,make type-check,type-check)
	$(PYTHON) -m mypy --config-file mypy.ini

pyright-check:
	@$(call repo_activity,make pyright-check,pyright-check)
	npm run typecheck:pyright

ruff-check:
	@$(call repo_activity,make ruff-check,ruff-check)
	$(PYTHON) -m ruff check .

ruff-format-check:
	@$(call repo_activity,make ruff-format-check,ruff-format-check)
	$(PYTHON) -m ruff format --check .
