# Environment doctor module execution.
define doctor_env_run
if [ -n "$$ACTIVE_VENV" ]; then \
	POLINKO_DOCTOR_INTERPRETER_SOURCE="$$INTERPRETER_SOURCE" VIRTUAL_ENV="$$ACTIVE_VENV" PATH="$$ACTIVE_VENV/bin:$$PATH" "$$PYTHON_PATH" -m tools.doctor_env; \
else \
	POLINKO_DOCTOR_INTERPRETER_SOURCE="$$INTERPRETER_SOURCE" "$$PYTHON_PATH" -m tools.doctor_env; \
fi
endef
