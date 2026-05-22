# Manual eval workbench, portfolio, and local browser surface targets.
.PHONY: notebook-setup notebook nb notes manual-evals-db manualdb manual-evals-db-refresh manualdb-refresh manual-evals-db-status manualdb-status manual-evals-db-health manualdb-health manual-evals-feedback-actionables manualdb-feedback-actionables manual-evals-feedback-cohorts manualdb-feedback-cohorts manual-evals-ocr-retry-candidates manualdb-ocr-retry-candidates manual-evals-ocr-retry-source-verification manualdb-ocr-retry-source-verification manual-evals-ocr-retry-source-provenance manualdb-ocr-retry-source-provenance manual-evals-ocr-retry-input-packet manualdb-ocr-retry-input-packet manual-evals-ocr-retry-rerun-manifest manualdb-ocr-retry-rerun-manifest manual-evals-ocr-retry-rerun-plan manualdb-ocr-retry-rerun-plan manual-evals-ocr-retry-selection-review manualdb-ocr-retry-selection-review manual-evals-ocr-retry-selection-template manualdb-ocr-retry-selection-template manual-evals-ocr-retry-selection-draft manualdb-ocr-retry-selection-draft manual-evals-ocr-retry-selection-validate manualdb-ocr-retry-selection-validate manual-evals-ocr-retry-selection-apply-preview manualdb-ocr-retry-selection-apply-preview manual-evals-ocr-retry-execution-readiness manualdb-ocr-retry-execution-readiness manual-evals-ocr-retry-execute manualdb-ocr-retry-execute manual-evals-ocr-retry-execution-report manualdb-ocr-retry-execution-report manual-evals-ocr-retry-feedback-closure-preview manualdb-ocr-retry-feedback-closure-preview manual-evals-ocr-retry-feedback-closure-apply manualdb-ocr-retry-feedback-closure-apply manual-evals-ocr-retry-feedback-closure-apply-report manualdb-ocr-retry-feedback-closure-apply-report manual-evals-ocr-retry-feedback-closure-restore-preview manualdb-ocr-retry-feedback-closure-restore-preview manual-evals-ocr-retry-feedback-closure-restore manualdb-ocr-retry-feedback-closure-restore manual-evals-no-context-reclassify-preview manualdb-no-context-reclassify-preview manual-evals-no-context-reclassify-apply manualdb-no-context-reclassify-apply
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

manual-evals-db manualdb manual-evals-db-refresh manualdb-refresh:
	$(PYTHON) -m tools.build_manual_evals_db \
		--optional-history-source beta_1_0=.local/legacy_eval/archive_legacy_eval/databases/.polinko_history.db \
		--history-source current=.local/runtime_dbs/active/history.db \
		--include-eval-sessions \
		--backup-existing \
		--status-summary

manual-evals-db-status manualdb-status:
	$(PYTHON) -m tools.manual_evals_db_status

manual-evals-db-health manualdb-health:
	$(PYTHON) -m tools.manual_evals_db_health

manual-evals-feedback-actionables manualdb-feedback-actionables:
	$(PYTHON) -m tools.manual_evals_db_health --open-feedback-actionables $(strip $(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-feedback-cohorts manualdb-feedback-cohorts:
	$(PYTHON) -m tools.manual_evals_db_health --open-feedback-cohorts $(strip $(MANUAL_EVALS_FEEDBACK_FILTER_ARGS))

manual-evals-ocr-retry-candidates manualdb-ocr-retry-candidates:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-candidates $(strip $(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-source-verification manualdb-ocr-retry-source-verification:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-source-verification $(strip $(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-source-provenance manualdb-ocr-retry-source-provenance:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-source-provenance $(strip $(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-input-packet manualdb-ocr-retry-input-packet:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-input-packet $(strip $(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-rerun-manifest manualdb-ocr-retry-rerun-manifest:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-rerun-manifest $(strip $(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-rerun-plan manualdb-ocr-retry-rerun-plan:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-rerun-plan $(strip $(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS))

manual-evals-ocr-retry-selection-review manualdb-ocr-retry-selection-review:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-selection-review $(strip $(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS))

manual-evals-ocr-retry-selection-template manualdb-ocr-retry-selection-template:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-selection-template $(strip $(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS))

manual-evals-ocr-retry-selection-draft manualdb-ocr-retry-selection-draft:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-selection-draft $(strip $(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS)) $(strip $(MANUAL_EVALS_OCR_RETRY_SELECTION_DRAFT_ARGS))

manual-evals-ocr-retry-selection-validate manualdb-ocr-retry-selection-validate:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-selection-validate $(strip $(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS)) $(strip $(MANUAL_EVALS_OCR_RETRY_SELECTION_VALIDATE_ARGS))

manual-evals-ocr-retry-selection-apply-preview manualdb-ocr-retry-selection-apply-preview:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-selection-apply-preview $(strip $(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS)) $(strip $(MANUAL_EVALS_OCR_RETRY_SELECTION_VALIDATE_ARGS))

manual-evals-ocr-retry-execution-readiness manualdb-ocr-retry-execution-readiness:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-execution-readiness $(strip $(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS)) $(strip $(MANUAL_EVALS_OCR_RETRY_SELECTION_VALIDATE_ARGS))

manual-evals-ocr-retry-execute manualdb-ocr-retry-execute:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-execute $(strip $(MANUAL_EVALS_OCR_RETRY_EXECUTE_ARGS))

manual-evals-ocr-retry-execution-report manualdb-ocr-retry-execution-report:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-execution-report $(strip $(MANUAL_EVALS_OCR_RETRY_EXECUTION_REPORT_ARGS))

manual-evals-ocr-retry-feedback-closure-preview manualdb-ocr-retry-feedback-closure-preview:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-feedback-closure-preview $(strip $(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_ARGS))

manual-evals-ocr-retry-feedback-closure-apply manualdb-ocr-retry-feedback-closure-apply:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-feedback-closure-apply $(strip $(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_APPLY_ARGS))

manual-evals-ocr-retry-feedback-closure-apply-report manualdb-ocr-retry-feedback-closure-apply-report:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-feedback-closure-apply-report $(strip $(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_ARGS))

manual-evals-ocr-retry-feedback-closure-restore-preview manualdb-ocr-retry-feedback-closure-restore-preview:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-feedback-closure-restore-preview $(strip $(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_ARGS))

manual-evals-ocr-retry-feedback-closure-restore manualdb-ocr-retry-feedback-closure-restore:
	$(PYTHON) -m tools.manual_evals_db_health --ocr-retry-feedback-closure-restore $(strip $(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_APPLY_ARGS))

manual-evals-no-context-reclassify-preview manualdb-no-context-reclassify-preview:
	$(PYTHON) -m tools.manual_evals_db_health --no-context-feedback-reclassify-preview $(strip $(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-no-context-reclassify-apply manualdb-no-context-reclassify-apply:
	$(PYTHON) -m tools.manual_evals_db_health --no-context-feedback-reclassify-apply $(strip $(MANUAL_EVALS_NO_CONTEXT_RECLASSIFY_ARGS))

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
