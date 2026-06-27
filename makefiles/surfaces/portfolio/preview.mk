# Portfolio preview launch targets.
.PHONY: portfolio portfolio-rebuild rebuild portfolio-open portfolio-playwright

portfolio: portfolio-build server-daemon-stop server-daemon
	@set -eu; \
	URL="$(DEV_PORTFOLIO_URL)"; \
	CACHE_BUST="$$(date +%s)"; \
	case "$$URL" in \
		*\?*) OPEN_URL="$$URL&rebuild=$$CACHE_BUST" ;; \
		*) OPEN_URL="$$URL?rebuild=$$CACHE_BUST" ;; \
	esac; \
	case "$(PORTFOLIO_LAUNCH)" in \
			playwright) \
				if PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PORTFOLIO_PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" list 2>/dev/null | awk 'BEGIN { found = 0; bad = 0 } /^- $(PORTFOLIO_PLAYWRIGHT_SESSION):/ { found = 1; next } found && /^- / { found = 0 } found && /headed: false/ { bad = 1 } END { exit bad ? 0 : 1 }'; then \
					PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PORTFOLIO_PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" close >/dev/null 2>&1 || true; \
				fi; \
				if PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PORTFOLIO_PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" tab-new "$$OPEN_URL" >/dev/null 2>&1; then \
					echo "Opened Playwright portfolio tab: $$OPEN_URL"; \
				else \
					PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PORTFOLIO_PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" open "$$OPEN_URL" --headed; \
				fi ;; \
		system) \
			bash "$(LOCAL_URL_LAUNCHER_SCRIPT)" "$$OPEN_URL" ;; \
		none) \
			echo "Portfolio URL: $$OPEN_URL" ;; \
		*) \
			echo "Invalid PORTFOLIO_LAUNCH='$(PORTFOLIO_LAUNCH)' (expected playwright, system, or none)."; \
			exit 2 ;; \
		esac; \
		echo "Portfolio shell URL: $$OPEN_URL"

portfolio-rebuild rebuild: portfolio

portfolio-open: PORTFOLIO_LAUNCH = system
portfolio-open: portfolio

portfolio-playwright: PORTFOLIO_LAUNCH = playwright
portfolio-playwright: portfolio
