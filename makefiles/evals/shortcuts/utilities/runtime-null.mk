# Runtime null audit shortcuts.
.PHONY: nulls runtime-null-audit

nulls: runtime-null-audit

runtime-null-audit:
	$(PYTHON) -m tools.audit_runtime_nulls
