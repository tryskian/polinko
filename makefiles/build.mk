# Build, dependency, and CI checks.
.PHONY: ci ci-docs ci-python-style ci-test ci-python-security ci-node-security
.PHONY: deps-install deps-lock deps-lock-check
.PHONY: python-security-check node-security-check security-checks

ci: ci-docs ci-python-style ci-test ci-python-security ci-node-security

ci-docs: path-leak-check lint-docs

ci-python-style: ruff-check ruff-format-check

ci-test: test

ci-python-security: python-security-check deps-lock-check

ci-node-security: node-security-check

deps-install:
	$(PYTHON) -m pip install -r "$(REQUIREMENTS_LOCK)"

deps-lock:
	@set -eu; \
	if ! $(PYTHON) -m piptools --version >/dev/null 2>&1; then \
		$(PYTHON) -m pip install "pip-tools==$(PIP_TOOLS_VERSION)"; \
	fi; \
	$(PYTHON) -m piptools compile \
		--resolver=backtracking \
		--allow-unsafe \
		--strip-extras \
		--output-file "$(REQUIREMENTS_LOCK)" \
		"$(REQUIREMENTS_IN)"

deps-lock-check:
	$(PYTHON) -m piptools compile \
		--allow-unsafe \
		--output-file="$(REQUIREMENTS_LOCK)" \
		--strip-extras \
		"$(REQUIREMENTS_IN)"
	git diff --exit-code -- "$(REQUIREMENTS_LOCK)"

python-security-check:
	$(PYTHON) -m pip_audit -r "$(REQUIREMENTS_LOCK)" $(PIP_AUDIT_ARGS)

node-security-check:
	npm audit --audit-level=moderate
	@if [ -f "$(PORTFOLIO_APP_DIR)/package.json" ]; then \
		npm --prefix "$(PORTFOLIO_APP_DIR)" audit --audit-level=moderate; \
	fi

security-checks: python-security-check node-security-check
