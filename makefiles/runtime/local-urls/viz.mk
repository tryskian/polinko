# PASS/FAIL viz local URL print and launch targets.
.PHONY: viz viz-open

viz: server-daemon
	@set -eu; \
	URL="$(DEV_VIZ_URL)"; \
	case "$(LOCAL_BROWSER_LAUNCH)" in none|system) ;; \
		*) echo "Invalid LOCAL_BROWSER_LAUNCH='$(LOCAL_BROWSER_LAUNCH)' (expected none or system)."; exit 2 ;; \
	esac; \
	echo "PASS/FAIL viz URL: $$URL"
ifeq ($(LOCAL_BROWSER_LAUNCH),system)
	@set -eu; \
	URL="$(DEV_VIZ_URL)"; \
	bash "$(LOCAL_URL_LAUNCHER_SCRIPT)" "$$URL"
endif

viz-open: server-daemon
	@set -eu; \
	URL="$(DEV_VIZ_URL)"; \
	bash "$(LOCAL_URL_LAUNCHER_SCRIPT)" "$$URL"; \
	echo "PASS/FAIL viz URL: $$URL"
