# API docs local URL print and launch targets.
.PHONY: docs docs-open open-api-docs open-api-docs-browser

open-api-docs: server-daemon
	@set -eu; \
	URL="$(DEV_API_DOCS_URL)"; \
	case "$(LOCAL_BROWSER_LAUNCH)" in none|system) ;; \
		*) echo "Invalid LOCAL_BROWSER_LAUNCH='$(LOCAL_BROWSER_LAUNCH)' (expected none or system)."; exit 2 ;; \
	esac; \
	echo "API docs URL: $$URL"
ifeq ($(LOCAL_BROWSER_LAUNCH),system)
	@set -eu; \
	URL="$(DEV_API_DOCS_URL)"; \
	bash "$(LOCAL_URL_LAUNCHER_SCRIPT)" "$$URL"
endif

docs: open-api-docs

docs-open open-api-docs-browser: server-daemon
	@set -eu; \
	URL="$(DEV_API_DOCS_URL)"; \
	bash "$(LOCAL_URL_LAUNCHER_SCRIPT)" "$$URL"; \
	echo "API docs URL: $$URL"
