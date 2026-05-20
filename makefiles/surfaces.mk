# Notebooks, manual eval DBs, portfolio, and local browser surface targets.
.PHONY: notebook-setup notebook nb notes manual-evals-db manualdb
.PHONY: portfolio-install portfolio-app-install frontend-install portfolio-build frontend-build portfolio portfolio-rebuild rebuild
.PHONY: portfolio-playwright portfolio-mockups portfolio-mockups-stop pwcli playwright-cli playwright-snapshot-dir

notebook-setup:
	$(PYTHON) -m pip install -r requirements.notebook.txt

notebook nb notes:
	@mkdir -p "$(NOTEBOOK_DIR_ABS)"; \
	if [ -f "$(NOTEBOOK_START_PATH_ABS)" ]; then \
		$(PYTHON) -m jupyter lab --notebook-dir="$(NOTEBOOK_DIR_ABS)" "$(NOTEBOOK_START_PATH_ABS)"; \
	else \
		$(PYTHON) -m jupyter lab --notebook-dir="$(NOTEBOOK_DIR_ABS)" "$(NOTEBOOK_DIR_ABS)"; \
	fi

manual-evals-db manualdb:
	$(PYTHON) -m tools.build_manual_evals_db \
		--optional-history-source beta_1_0=.local/legacy_eval/archive_legacy_eval/databases/.polinko_history.db \
		--history-source current=.local/runtime_dbs/active/history.db \
		--include-eval-sessions

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

portfolio-build: portfolio-install
	@set -eu; \
	if [ ! -f "$(PORTFOLIO_APP_DIR)/package.json" ]; then \
		echo "Portfolio app source not present at $(PORTFOLIO_APP_DIR)/package.json; using tracked /portfolio fallback."; \
		exit 0; \
	fi; \
	POLINKO_PORTFOLIO_STATIC_DIR="$(abspath $(PORTFOLIO_STATIC_DIR))" npm --prefix "$(PORTFOLIO_APP_DIR)" run build

frontend-build: portfolio-build

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
			if command -v open >/dev/null 2>&1; then \
				open "$$OPEN_URL"; \
			elif command -v xdg-open >/dev/null 2>&1; then \
				xdg-open "$$OPEN_URL" >/dev/null 2>&1 || true; \
			else \
				echo "Open this URL in your browser: $$OPEN_URL"; \
			fi ;; \
		none) \
			echo "Open this URL in your browser: $$OPEN_URL" ;; \
		*) \
			echo "Invalid PORTFOLIO_LAUNCH='$(PORTFOLIO_LAUNCH)' (expected playwright, system, or none)."; \
			exit 2 ;; \
		esac; \
		echo "Portfolio shell URL: $$OPEN_URL"

portfolio-rebuild rebuild: portfolio

portfolio-playwright: PORTFOLIO_LAUNCH = playwright
portfolio-playwright: portfolio

portfolio-mockups:
	@set -eu; \
	if [ ! -f "$(PORTFOLIO_MOCKUP_DIR)/landing-mockups.html" ]; then \
		echo "Portfolio mockup not found: $(PORTFOLIO_MOCKUP_DIR)/landing-mockups.html"; \
		exit 1; \
	fi; \
	if ! curl -fsS "$(PORTFOLIO_MOCKUP_URL)" >/dev/null 2>&1; then \
		if [ -f "$(PORTFOLIO_MOCKUP_PID_FILE)" ]; then \
			PID=$$(cat "$(PORTFOLIO_MOCKUP_PID_FILE)" 2>/dev/null || true); \
			if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
				kill "$$PID" 2>/dev/null || true; \
			fi; \
			rm -f "$(PORTFOLIO_MOCKUP_PID_FILE)"; \
		fi; \
		nohup $(PYTHON) -m http.server "$(PORTFOLIO_MOCKUP_PORT)" --bind 127.0.0.1 --directory "$(PORTFOLIO_MOCKUP_DIR)" >"$(PORTFOLIO_MOCKUP_LOG)" 2>&1 & \
		PID=$$!; \
		echo "$$PID" >"$(PORTFOLIO_MOCKUP_PID_FILE)"; \
		sleep 0.5; \
		if ! kill -0 "$$PID" 2>/dev/null; then \
			rm -f "$(PORTFOLIO_MOCKUP_PID_FILE)"; \
			echo "Failed to start portfolio mockup server. Check $(PORTFOLIO_MOCKUP_LOG)."; \
			exit 1; \
		fi; \
		echo "portfolio mockup server started (PID $$PID, log: $(PORTFOLIO_MOCKUP_LOG))."; \
	fi; \
	URL="$(PORTFOLIO_MOCKUP_URL)?rebuild=$$(date +%s)"; \
	if PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" tab-new "$$URL" >/dev/null 2>&1; then \
		echo "Opened Playwright mockup tab: $$URL"; \
	else \
		PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" open "$$URL" --headed; \
	fi; \
	echo "Portfolio mockup URL: $$URL"

portfolio-mockups-stop:
	@set -eu; \
	if [ ! -f "$(PORTFOLIO_MOCKUP_PID_FILE)" ]; then \
		echo "No portfolio mockup PID file found."; \
		exit 0; \
	fi; \
	PID=$$(cat "$(PORTFOLIO_MOCKUP_PID_FILE)" 2>/dev/null || true); \
	if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
		kill "$$PID"; \
		echo "portfolio mockup server stopped (PID $$PID)."; \
	else \
		echo "Stale portfolio mockup PID file; cleaning up."; \
	fi; \
	rm -f "$(PORTFOLIO_MOCKUP_PID_FILE)"

pwcli playwright-cli:
	@PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" \
		PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" \
		PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" \
		"$(PWCLI_TOOL)" $(ARGS)

playwright-snapshot-dir:
	@PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" \
		PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" \
		"$(PWCLI_TOOL)" --print-dir
