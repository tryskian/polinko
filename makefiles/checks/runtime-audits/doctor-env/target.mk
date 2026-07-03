# Environment doctor target.
.PHONY: doctor-env

doctor-env:
	@$(call repo_activity,make doctor-env,doctor-env)
	$(PYTHON) -m tools.run_doctor_env --python "$(PYTHON)" --python-origin "$(origin PYTHON)"
