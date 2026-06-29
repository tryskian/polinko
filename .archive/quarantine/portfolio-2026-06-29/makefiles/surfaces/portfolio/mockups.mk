# Portfolio mockup lifecycle targets.
.PHONY: portfolio-mockups portfolio-mockups-status portfolio-mockups-stop

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
