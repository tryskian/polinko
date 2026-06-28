# Environment doctor active virtualenv derivation.
define doctor_env_active_venv
ACTIVE_VENV=""; \
case "$$PYTHON_PATH" in \
	*/bin/python|*/bin/python3|*/bin/python3.*) \
		ACTIVE_VENV="$$(cd "$$(dirname "$$PYTHON_PATH")/.." && pwd)"; \
		;; \
esac
endef
