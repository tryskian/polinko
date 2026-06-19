# Smoke, sidecar, and quality-gate eval targets.
.PHONY: api-smoke eval-smoke eval-sidecar-start eval-sidecar-status eval-sidecar-stop operator-burden-report
.PHONY: hallucination-gate quality-gate quality-gate-deterministic

api-smoke:
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" api-smoke

eval-smoke:
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" eval-smoke

eval-sidecar-start:
	@$(EVAL_SIDECAR_START_ENV) bash "$(EVAL_SIDECAR_START_SCRIPT)" start

eval-sidecar-status:
	@$(EVAL_SIDECAR_START_ENV) bash "$(EVAL_SIDECAR_START_SCRIPT)" status

eval-sidecar-stop:
	@$(EVAL_SIDECAR_START_ENV) bash "$(EVAL_SIDECAR_START_SCRIPT)" stop

operator-burden-report:
	$(PYTHON) -m tools.report_operator_burden_rows

hallucination-gate:
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" hallucination-gate

quality-gate:
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" quality-gate

quality-gate-deterministic: HALLUCINATION_EVAL_MODE = deterministic
quality-gate-deterministic: HALLUCINATION_CHAT_HARNESS_MODE = fixture
quality-gate-deterministic: STYLE_CASE_ATTEMPTS = 3
quality-gate-deterministic: STYLE_MIN_PASS_ATTEMPTS = 2
quality-gate-deterministic: STYLE_EVAL_MODE = deterministic
quality-gate-deterministic: STYLE_CHAT_HARNESS_MODE = fixture
quality-gate-deterministic: RESPONSE_BEHAVIOUR_CHAT_HARNESS_MODE = fixture
quality-gate-deterministic: RETRIEVAL_CHAT_HARNESS_MODE = fixture
quality-gate-deterministic: GATE_VECTOR_EMBEDDING_PROVIDER = local
quality-gate-deterministic: quality-gate
