# CI aggregation and preflight targets.
.PHONY: build-hygiene pr-preflight ci ci-docs ci-python-style ci-python-type-check ci-package ci-test ci-python-security ci-node-security

build-hygiene: doctor-env transcript-check ci
	git diff --check

pr-preflight: build-hygiene

ci: ci-docs ci-python-style ci-python-type-check ci-package ci-test ci-python-security ci-node-security

ci-docs: path-leak-check scripts-check local-runtime-config-check risk-scan operator-command-check startup-contracts-check lint-docs

ci-python-style: ruff-check ruff-format-check

ci-python-type-check: type-check

ci-package: package-install-check

ci-test: test

ci-python-security: python-security-check deps-lock-check

ci-node-security: node-security-check
