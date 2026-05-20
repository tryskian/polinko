# Smoke, sidecar, and quality-gate eval targets.
.PHONY: api-smoke eval-smoke eval-sidecar-start eval-sidecar-status eval-sidecar-stop operator-burden-report
.PHONY: hallucination-gate quality-gate quality-gate-deterministic

api-smoke:
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" api-smoke

eval-smoke:
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" eval-smoke

eval-sidecar-start:
	@set -eu; \
	if [ -f "$(EVAL_SIDECAR_PID_FILE)" ]; then \
		PID=$$(cat "$(EVAL_SIDECAR_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "eval-sidecar already running (PID $$PID)."; \
			exit 0; \
		fi; \
		rm -f "$(EVAL_SIDECAR_PID_FILE)"; \
	fi; \
	nohup $(PYTHON) -m tools.eval_sidecar run --target "$(EVAL_SIDECAR_TARGET)" --min-seconds "$(EVAL_SIDECAR_MIN_SECONDS)" --runs-dir "$(EVAL_SIDECAR_RUNS_DIR)" --pid-file "$(EVAL_SIDECAR_PID_FILE)" --current-file "$(EVAL_SIDECAR_CURRENT_FILE)" >"$(EVAL_SIDECAR_LOG)" 2>&1 & \
	PID=$$!; \
	sleep 0.2; \
	if kill -0 "$$PID" 2>/dev/null; then \
		echo "eval-sidecar started (PID $$PID, log: $(EVAL_SIDECAR_LOG))."; \
	else \
		echo "Failed to start eval-sidecar. Check $(EVAL_SIDECAR_LOG)."; \
		exit 1; \
	fi

eval-sidecar-status:
	$(PYTHON) -m tools.eval_sidecar status --current-file "$(EVAL_SIDECAR_CURRENT_FILE)" --pid-file "$(EVAL_SIDECAR_PID_FILE)"

eval-sidecar-stop:
	$(PYTHON) -m tools.eval_sidecar stop --current-file "$(EVAL_SIDECAR_CURRENT_FILE)" --pid-file "$(EVAL_SIDECAR_PID_FILE)"

operator-burden-report:
	$(PYTHON) -m tools.report_operator_burden_rows

hallucination-gate:
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" hallucination-gate

quality-gate:
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" quality-gate

quality-gate-deterministic: HALLUCINATION_EVAL_MODE = deterministic
quality-gate-deterministic: STYLE_CASE_ATTEMPTS = 3
quality-gate-deterministic: STYLE_MIN_PASS_ATTEMPTS = 2
quality-gate-deterministic: quality-gate
