# Backend gate wrapper.
.PHONY: backend-gate backend-gate-start

backend-gate: backend-gate-start doctor-env test quality-gate-deterministic

backend-gate-start:
	@$(call repo_activity,make backend-gate-start,backend-gate-start)
	@echo "Running backend gate (doctor + tests + deterministic quality gate)..."
