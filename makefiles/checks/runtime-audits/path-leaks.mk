# Path leak audit targets.
.PHONY: path-leak-check path-leak-audit-local

path-leak-check:
	@$(call repo_activity,make path-leak-check,path-leak-check)
	$(PYTHON) -m tools.path_leak_check --scope tracked

path-leak-audit-local:
	$(PYTHON) -m tools.path_leak_check --scope local-config
	$(MAKE) --no-print-directory local-runtime-config-check
