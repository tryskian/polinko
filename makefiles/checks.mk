# Local validation and check targets.
.PHONY: test test-one test-targeted pycheck type-check ruff-check ruff-format-check lint-docs backend-gate backend-gate-start
.PHONY: path-leak-check path-leak-audit-local precommit-install precommit-run act-list act-ci
.PHONY: mermaid-render d3-render public-diagrams-render transcript-fix transcript-check end-docs-check doctor-env

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
		echo 'Usage: make pycheck FILES="tools/foo.py tools/bar.py"'; \
		exit 2; \
	fi; \
	python3 -m py_compile $(FILES)

type-check:
	$(PYTHON) -m mypy --config-file mypy.ini

ruff-check:
	$(PYTHON) -m ruff check .

ruff-format-check:
	$(PYTHON) -m ruff format --check .

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

path-leak-check:
	$(PYTHON) -m tools.path_leak_check --scope tracked

path-leak-audit-local:
	$(PYTHON) -m tools.path_leak_check --scope local

backend-gate: backend-gate-start doctor-env test quality-gate-deterministic

backend-gate-start:
	@echo "Running backend gate (doctor + tests + deterministic quality gate)..."

precommit-install:
	$(PYTHON) -m pre_commit install --install-hooks --hook-type pre-commit

precommit-run:
	$(PYTHON) -m pre_commit run --all-files

act-list:
	act -l

act-ci:
	act -W .github/workflows/ci.yml
