# Python and Node security check targets.
.PHONY: python-security-check node-security-check security-checks

python-security-check:
	@$(call repo_activity,make python-security-check,python-security-check)
	$(PYTHON) -m pip_audit -r "$(REQUIREMENTS_LOCK)" $(PIP_AUDIT_ARGS)

node-security-check:
	@$(call repo_activity,make node-security-check,node-security-check)
	npm audit --audit-level=moderate

security-checks: python-security-check node-security-check
