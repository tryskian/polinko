# Runtime config, risk, tool-reference, and operator command audit targets.
.PHONY: local-runtime-config-check risk-scan runtime-tool-reference-check operator-command-check

local-runtime-config-check:
	@$(call repo_activity,make local-runtime-config-check,local-runtime-config-check)
	$(PYTHON) -m tools.check_local_runtime_config

risk-scan:
	@$(call repo_activity,make risk-scan,risk-scan)
	$(PYTHON) -m tools.check_runtime_risk_scan

runtime-tool-reference-check:
	@$(call repo_activity,make runtime-tool-reference-check,runtime-tool-reference-check)
	$(PYTHON) -m unittest tests.test_runtime_tool_reference_coverage

operator-command-check:
	@$(call repo_activity,make operator-command-check,operator-command-check)
	$(PYTHON) -m tools.check_operator_commands
