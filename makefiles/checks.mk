# Local validation and check targets.
.PHONY: test test-one test-targeted pycheck type-check pyright-check ruff-check ruff-format-check scripts-check lint-docs backend-gate backend-gate-start
.PHONY: path-leak-check path-leak-audit-local local-runtime-config-check risk-scan operator-alias-check precommit-install precommit-run act-list act-ci
.PHONY: mermaid-render d3-render public-diagrams-render transcript-fix transcript-check end-docs-check doctor-env repo-search repo-search-full

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

test-one:
	@set -eu; \
	if [ -z "$(TEST)" ]; then \
		echo 'Usage: make test-one TEST=tests.test_eval_file_search'; \
		exit 2; \
	fi; \
	$(PYTHON) -m unittest $(TEST)

test-targeted:
	@set -eu; \
	if [ -z "$(TESTS)" ]; then \
		echo 'Usage: make test-targeted TESTS="tests.test_eval_file_search tests.test_eval_retrieval"'; \
		exit 2; \
	fi; \
	$(PYTHON) -m unittest $(TESTS)

pycheck:
	@set -eu; \
	if [ -z "$(FILES)" ]; then \
		echo 'Usage: make pycheck FILES="tools/check_shell_scripts.py tools/check_runtime_risk_scan.py"'; \
		exit 2; \
	fi; \
	python3 -m py_compile $(FILES)

type-check:
	$(PYTHON) -m mypy --config-file mypy.ini

pyright-check:
	npm run typecheck:pyright

ruff-check:
	$(PYTHON) -m ruff check .

ruff-format-check:
	$(PYTHON) -m ruff format --check .

scripts-check:
	$(PYTHON) -m tools.check_shell_scripts

lint-docs:
	npm run lint:docs

mermaid-render:
	$(PYTHON) -m tools.render_mermaid_diagrams

d3-render:
	$(PYTHON) -m tools.render_public_d3_diagrams

public-diagrams-render: mermaid-render d3-render

transcript-fix:
	$(PYTHON) -m tools.fix_transcripts

transcript-check:
	$(PYTHON) -m tools.validate_transcripts

end-docs-check:
	$(PYTHON) -m tools.check_end_docs

doctor-env:
	@set -eu; \
	PYTHON_PATH="$(PYTHON)"; \
	ACTIVE_VENV=""; \
	case "$$PYTHON_PATH" in \
		*/bin/python|*/bin/python3|*/bin/python3.*) \
			ACTIVE_VENV="$$(cd "$$(dirname "$$PYTHON_PATH")/.." && pwd)"; \
			;; \
	esac; \
	if [ -n "$$ACTIVE_VENV" ]; then \
		VIRTUAL_ENV="$$ACTIVE_VENV" PATH="$$ACTIVE_VENV/bin:$$PATH" "$$PYTHON_PATH" -m tools.doctor_env; \
	else \
		"$$PYTHON_PATH" -m tools.doctor_env; \
	fi

repo-search:
	@set -eu; \
	if [ -z "$(Q)" ]; then \
		echo 'Usage: make repo-search Q="pattern"'; \
		exit 2; \
	fi; \
	$(PYTHON) -m tools.repo_search --query "$(Q)"

repo-search-full:
	@set -eu; \
	if [ -z "$(Q)" ]; then \
		echo 'Usage: make repo-search-full Q="pattern"'; \
		exit 2; \
	fi; \
	$(PYTHON) -m tools.repo_search --mode full --query "$(Q)"

path-leak-check:
	$(PYTHON) -m tools.path_leak_check --scope tracked

path-leak-audit-local:
	$(PYTHON) -m tools.path_leak_check --scope local-config
	$(MAKE) --no-print-directory local-runtime-config-check

local-runtime-config-check:
	$(PYTHON) -m tools.check_local_runtime_config

risk-scan:
	$(PYTHON) -m tools.check_runtime_risk_scan

operator-alias-check:
	$(PYTHON) -m tools.check_operator_aliases

backend-gate: backend-gate-start doctor-env test quality-gate-deterministic

backend-gate-start:
	@echo "Running backend gate (doctor + tests + deterministic quality gate)..."

precommit-install:
	$(PYTHON) -m pre_commit install --install-hooks --hook-type pre-commit

precommit-run:
	$(PYTHON) -m pre_commit run --all-files

act-list:
	$(ACT) -l

act-ci:
	$(ACT) -W .github/workflows/ci.yml
