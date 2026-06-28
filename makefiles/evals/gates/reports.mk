# Eval operator report targets.
.PHONY: operator-burden-report

operator-burden-report:
	$(PYTHON) -m tools.report_operator_burden_rows
