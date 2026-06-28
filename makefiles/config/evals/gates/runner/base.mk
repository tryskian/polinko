# Local eval gate runner base environment.
LOCAL_EVAL_GATE_RUNNER_SCRIPT ?= ./tools/run_local_eval_gate.sh
LOCAL_EVAL_GATE_RUNNER_ENV = \
	PYTHON="$(PYTHON)" \
	ASGI_APP="$(ASGI_APP)"
