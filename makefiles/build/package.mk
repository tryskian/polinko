# Package install and startup-contract targets.
.PHONY: package-install-check startup-contracts-check

package-install-check:
	@$(call repo_activity,make package-install-check,package-install-check)
	$(PYTHON) -m pip install --no-build-isolation --no-deps -e .
	$(PYTHON) tools/check_package_install.py

startup-contracts-check:
	@$(call repo_activity,make startup-contracts-check,startup-contracts-check)
	$(PYTHON) -m unittest tests.test_startup_contracts
