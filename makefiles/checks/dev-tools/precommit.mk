# Local pre-commit helper targets.
.PHONY: precommit-install precommit-run

precommit-install:
	@$(call repo_activity,make precommit-install,precommit-install)
	$(PYTHON) -m pre_commit install --install-hooks --hook-type pre-commit

precommit-run:
	@$(call repo_activity,make precommit-run,precommit-run)
	$(PYTHON) -m pre_commit run --all-files
