# Runtime, shell, and local configuration audit targets.
.PHONY: scripts-check path-leak-check path-leak-audit-local local-runtime-config-check risk-scan operator-alias-check doctor-env

scripts-check:
	@$(call repo_activity,make scripts-check,scripts-check)
	$(PYTHON) -m tools.check_shell_scripts

path-leak-check:
	@$(call repo_activity,make path-leak-check,path-leak-check)
	$(PYTHON) -m tools.path_leak_check --scope tracked

path-leak-audit-local:
	$(PYTHON) -m tools.path_leak_check --scope local-config
	$(MAKE) --no-print-directory local-runtime-config-check

local-runtime-config-check:
	@$(call repo_activity,make local-runtime-config-check,local-runtime-config-check)
	$(PYTHON) -m tools.check_local_runtime_config

risk-scan:
	@$(call repo_activity,make risk-scan,risk-scan)
	$(PYTHON) -m tools.check_runtime_risk_scan

operator-alias-check:
	@$(call repo_activity,make operator-alias-check,operator-alias-check)
	$(PYTHON) -m tools.check_operator_aliases

doctor-env:
	@$(call repo_activity,make doctor-env,doctor-env)
	@set -eu; \
	PYTHON_PATH="$(PYTHON)"; \
	PYTHON_ORIGIN="$(origin PYTHON)"; \
	INTERPRETER_SOURCE="make PYTHON"; \
	case "$$PYTHON_ORIGIN" in \
		"command line") INTERPRETER_SOURCE="command-line PYTHON override" ;; \
		environment|environment\ override) INTERPRETER_SOURCE="environment PYTHON override" ;; \
		*) \
			case "$$PYTHON_PATH" in \
				./.venv/*|.venv/*) INTERPRETER_SOURCE="repo .venv selected by Make" ;; \
				python3) INTERPRETER_SOURCE="host python3 fallback selected by Make" ;; \
			esac; \
			;; \
	esac; \
	ACTIVE_VENV=""; \
	case "$$PYTHON_PATH" in \
		*/bin/python|*/bin/python3|*/bin/python3.*) \
			ACTIVE_VENV="$$(cd "$$(dirname "$$PYTHON_PATH")/.." && pwd)"; \
			;; \
	esac; \
	if [ -n "$$ACTIVE_VENV" ]; then \
		POLINKO_DOCTOR_INTERPRETER_SOURCE="$$INTERPRETER_SOURCE" VIRTUAL_ENV="$$ACTIVE_VENV" PATH="$$ACTIVE_VENV/bin:$$PATH" "$$PYTHON_PATH" -m tools.doctor_env; \
	else \
		POLINKO_DOCTOR_INTERPRETER_SOURCE="$$INTERPRETER_SOURCE" "$$PYTHON_PATH" -m tools.doctor_env; \
	fi
