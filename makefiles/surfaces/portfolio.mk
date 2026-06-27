# Portfolio app and mockup targets.
.PHONY: portfolio-install portfolio-app-install frontend-install portfolio-build frontend-build portfolio portfolio-rebuild rebuild
.PHONY: portfolio-open portfolio-playwright portfolio-mockups portfolio-mockups-status portfolio-mockups-stop

portfolio-install:
	@set -eu; \
	if [ ! -f "$(PORTFOLIO_APP_DIR)/package.json" ]; then \
		echo "Portfolio app source not present at $(PORTFOLIO_APP_DIR)/package.json; skipping npm install."; \
		exit 0; \
	fi; \
	if [ -f "$(PORTFOLIO_APP_DIR)/package-lock.json" ]; then \
		npm --prefix "$(PORTFOLIO_APP_DIR)" ci --no-audit --no-fund; \
	else \
		npm --prefix "$(PORTFOLIO_APP_DIR)" install --no-audit --no-fund; \
	fi

portfolio-app-install frontend-install: portfolio-install
	@echo "Legacy alias: use make portfolio-install."

portfolio-build: portfolio-install
	@set -eu; \
	if [ ! -f "$(PORTFOLIO_APP_DIR)/package.json" ]; then \
		echo "Portfolio app source not present at $(PORTFOLIO_APP_DIR)/package.json; using tracked /portfolio fallback."; \
		exit 0; \
	fi; \
	POLINKO_PORTFOLIO_STATIC_DIR="$(abspath $(PORTFOLIO_STATIC_DIR))" npm --prefix "$(PORTFOLIO_APP_DIR)" run build

frontend-build: portfolio-build
	@echo "Legacy alias: use make portfolio-build."

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

portfolio-mockups:
	@set -eu; \
	$(PORTFOLIO_MOCKUP_ENV) bash "$(PORTFOLIO_MOCKUP_SCRIPT)" start; \
	URL="$(PORTFOLIO_MOCKUP_URL)?rebuild=$$(date +%s)"; \
	if PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" tab-new "$$URL" >/dev/null 2>&1; then \
		echo "Opened Playwright mockup tab: $$URL"; \
	else \
		PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" open "$$URL" --headed; \
	fi; \
	echo "Portfolio mockup URL: $$URL"

portfolio-mockups-status:
	@$(PORTFOLIO_MOCKUP_ENV) bash "$(PORTFOLIO_MOCKUP_SCRIPT)" status

portfolio-mockups-stop:
	@$(PORTFOLIO_MOCKUP_ENV) bash "$(PORTFOLIO_MOCKUP_SCRIPT)" stop
