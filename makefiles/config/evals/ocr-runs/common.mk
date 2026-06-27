# OCR run helper scripts shared across workflow families.
EVAL_SERVER_DAEMON_SCRIPT ?= ./tools/ensure_eval_server_daemon.sh
EVAL_CASE_GUARD_SCRIPT ?= ./tools/eval_case_guard.sh
OCR_WORKFLOW_COMMON_SCRIPT ?= ./tools/ocr_workflow_common.sh
OCR_GUARDED_CASE_RUNNER_SCRIPT ?= ./tools/run_guarded_ocr_case_eval.sh
OCR_GUARDED_CASE_RUNNER_ENV = \
	PYTHON="$(PYTHON)" \
	OCR_WORKFLOW_COMMON_SCRIPT="$(OCR_WORKFLOW_COMMON_SCRIPT)" \
	EVAL_CASE_GUARD_SCRIPT="$(EVAL_CASE_GUARD_SCRIPT)"
