# Python compile helper.
.PHONY: pycheck

pycheck:
	@$(PYTHON) -m tools.validate_make_variable --value "$(FILES)" --usage 'Usage: make pycheck FILES="tools/check_shell_scripts.py tools/check_runtime_risk_scan.py"'
	@$(call repo_activity,make pycheck,pycheck)
	$(PYTHON) -m py_compile $(FILES)
