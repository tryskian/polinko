# CI aggregation and preflight targets.
.PHONY: pr-preflight ci ci-docs ci-python-style ci-python-type-check ci-package ci-test ci-python-security ci-node-security

pr-preflight: ci
	git diff --check

ci: ci-docs ci-python-style ci-python-type-check ci-package ci-test ci-python-security ci-node-security

ci-docs: path-leak-check scripts-check local-runtime-config-check risk-scan operator-alias-check startup-contracts-check lint-docs

ci-python-style: ruff-check ruff-format-check

ci-python-type-check: type-check

ci-package: package-install-check

ci-test: test

ci-python-security: python-security-check deps-lock-check

ci-node-security: node-security-check
