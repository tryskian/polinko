# Hallucination and quality gate targets.
.PHONY: hallucination-gate quality-gate quality-gate-deterministic

hallucination-gate:
	@$(call repo_activity,make hallucination-gate,hallucination-gate)
	@$(LOCAL_EVAL_GATE_RUNNER_ENV) bash "$(LOCAL_EVAL_GATE_RUNNER_SCRIPT)" hallucination-gate

quality-gate:
	@$(call repo_activity,make quality-gate,quality-gate)
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
