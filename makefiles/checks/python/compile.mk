# Python compile helper.
.PHONY: pycheck

pycheck:
	@set -eu; \
	if [ -z "$(FILES)" ]; then \
		echo 'Usage: make pycheck FILES="tools/check_shell_scripts.py tools/check_runtime_risk_scan.py"'; \
		exit 2; \
	fi; \
	$(call repo_activity,make pycheck,pycheck); \
	$(PYTHON) -m py_compile $(FILES)
