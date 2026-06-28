# Environment doctor interpreter source labelling.
define doctor_env_interpreter_source
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
esac
endef
