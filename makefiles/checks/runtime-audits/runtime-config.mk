# Runtime config, risk, and alias audit targets.
.PHONY: local-runtime-config-check risk-scan operator-alias-check

local-runtime-config-check:
	@$(call repo_activity,make local-runtime-config-check,local-runtime-config-check)
	$(PYTHON) -m tools.check_local_runtime_config

risk-scan:
	@$(call repo_activity,make risk-scan,risk-scan)
	$(PYTHON) -m tools.check_runtime_risk_scan

operator-alias-check:
	@$(call repo_activity,make operator-alias-check,operator-alias-check)
	$(PYTHON) -m tools.check_operator_aliases
