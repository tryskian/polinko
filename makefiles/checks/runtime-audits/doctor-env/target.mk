# Environment doctor target.
.PHONY: doctor-env

doctor-env:
	@$(call repo_activity,make doctor-env,doctor-env)
	@set -eu; \
	$(doctor_env_interpreter_source); \
	$(doctor_env_active_venv); \
	$(doctor_env_run)
