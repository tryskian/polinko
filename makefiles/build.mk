# Build, dependency, and CI checks.
.PHONY: ci ci-docs ci-python-style ci-python-type-check ci-package ci-test ci-python-security ci-node-security
.PHONY: deps-install deps-refresh refresh-deps deps-lock deps-lock-check
.PHONY: package-install-check
.PHONY: python-security-check node-security-check security-checks

ci: ci-docs ci-python-style ci-python-type-check ci-package ci-test ci-python-security ci-node-security

ci-docs: path-leak-check scripts-check lint-docs

ci-python-style: ruff-check ruff-format-check

ci-python-type-check: type-check

ci-package: package-install-check

ci-test: test

ci-python-security: python-security-check deps-lock-check

ci-node-security: node-security-check

deps-install:
	$(PYTHON) -m pip install -r "$(REQUIREMENTS_LOCK)"

deps-refresh refresh-deps:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install --upgrade --upgrade-strategy eager -r "$(REQUIREMENTS_LOCK)"
	npm install --no-audit --no-fund
	@if [ -f "$(PORTFOLIO_APP_DIR)/package.json" ]; then \
		npm --prefix "$(PORTFOLIO_APP_DIR)" install --no-audit --no-fund; \
	fi

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
		--resolver=backtracking \
		--allow-unsafe \
		--output-file="$(REQUIREMENTS_LOCK)" \
		--strip-extras \
		"$(REQUIREMENTS_IN)"
	git diff --exit-code -- "$(REQUIREMENTS_LOCK)"

package-install-check:
	$(PYTHON) -m pip install --no-build-isolation --no-deps -e .
	$(PYTHON) tools/check_package_install.py

python-security-check:
	$(PYTHON) -m pip_audit -r "$(REQUIREMENTS_LOCK)" $(PIP_AUDIT_ARGS)

node-security-check:
	npm audit --audit-level=moderate
	@if [ -f "$(PORTFOLIO_APP_DIR)/package.json" ]; then \
		npm --prefix "$(PORTFOLIO_APP_DIR)" audit --audit-level=moderate; \
	fi

security-checks: python-security-check node-security-check
