# Manual eval workbench, portfolio, and local browser surface targets.
.PHONY: notebook-setup notebook nb notes
.PHONY: manual-evals-db manualdb manual-evals-db-refresh manualdb-refresh
.PHONY: manual-evals-db-status manualdb-status manual-evals-db-health manualdb-health
.PHONY: manual-evals-feedback-actionables manualdb-feedback-actionables
.PHONY: manual-evals-feedback-cohorts manualdb-feedback-cohorts
.PHONY: manual-evals-feedback-source-context manualdb-feedback-source-context
.PHONY: manual-evals-feedback-decision-draft manualdb-feedback-decision-draft
.PHONY: manual-evals-feedback-decision-preview manualdb-feedback-decision-preview
.PHONY: manual-evals-overlay-comparison-readiness manualdb-overlay-comparison-readiness
.PHONY: manual-evals-overlay-source-index-draft manualdb-overlay-source-index-draft
.PHONY: manual-evals-overlay-source-index-validate manualdb-overlay-source-index-validate
.PHONY: manual-evals-ocr-retry-candidates manualdb-ocr-retry-candidates
.PHONY: manual-evals-ocr-retry-source-verification manualdb-ocr-retry-source-verification
.PHONY: manual-evals-ocr-retry-source-provenance manualdb-ocr-retry-source-provenance
.PHONY: manual-evals-ocr-retry-input-packet manualdb-ocr-retry-input-packet
.PHONY: manual-evals-ocr-retry-rerun-manifest manualdb-ocr-retry-rerun-manifest
.PHONY: manual-evals-ocr-retry-rerun-plan manualdb-ocr-retry-rerun-plan
.PHONY: manual-evals-ocr-retry-selection-review manualdb-ocr-retry-selection-review
.PHONY: manual-evals-ocr-retry-selection-template manualdb-ocr-retry-selection-template
.PHONY: manual-evals-ocr-retry-selection-draft manualdb-ocr-retry-selection-draft
.PHONY: manual-evals-ocr-retry-selection-validate manualdb-ocr-retry-selection-validate
.PHONY: manual-evals-ocr-retry-selection-apply-preview manualdb-ocr-retry-selection-apply-preview
.PHONY: manual-evals-ocr-retry-execution-readiness manualdb-ocr-retry-execution-readiness
.PHONY: manual-evals-ocr-retry-execute manualdb-ocr-retry-execute
.PHONY: manual-evals-ocr-retry-execution-report manualdb-ocr-retry-execution-report
.PHONY: manual-evals-ocr-retry-feedback-closure-preview manualdb-ocr-retry-feedback-closure-preview
.PHONY: manual-evals-ocr-retry-feedback-closure-apply manualdb-ocr-retry-feedback-closure-apply
.PHONY: manual-evals-ocr-retry-feedback-closure-apply-report manualdb-ocr-retry-feedback-closure-apply-report
.PHONY: manual-evals-ocr-retry-feedback-closure-restore-preview manualdb-ocr-retry-feedback-closure-restore-preview
.PHONY: manual-evals-ocr-retry-feedback-closure-restore manualdb-ocr-retry-feedback-closure-restore
.PHONY: manual-evals-no-context-reclassify-preview manualdb-no-context-reclassify-preview
.PHONY: manual-evals-no-context-reclassify-apply manualdb-no-context-reclassify-apply
.PHONY: manual-evals-feedback-reclassify-preview manualdb-feedback-reclassify-preview
.PHONY: manual-evals-feedback-reclassify-apply manualdb-feedback-reclassify-apply
.PHONY: portfolio-install portfolio-app-install frontend-install portfolio-build frontend-build portfolio portfolio-rebuild rebuild
.PHONY: portfolio-open portfolio-playwright portfolio-mockups portfolio-mockups-status portfolio-mockups-stop pwcli playwright-cli playwright-snapshot-dir

manual_evals_db_health = $(MANUAL_EVALS_DB_HEALTH_COMMAND) $(1) $(strip $(2))

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
	$(MANUAL_EVALS_DB_HEALTH_COMMAND)

manual-evals-feedback-actionables manualdb-feedback-actionables:
	$(call manual_evals_db_health,--open-feedback-actionables,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-feedback-cohorts manualdb-feedback-cohorts:
	$(call manual_evals_db_health,--open-feedback-cohorts,$(MANUAL_EVALS_FEEDBACK_FILTER_ARGS))

manual-evals-feedback-source-context manualdb-feedback-source-context:
	$(call manual_evals_db_health,--feedback-source-context,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-feedback-decision-draft manualdb-feedback-decision-draft:
	$(call manual_evals_db_health,--feedback-decision-draft,$(MANUAL_EVALS_FEEDBACK_DECISION_DRAFT_ARGS))

manual-evals-feedback-decision-preview manualdb-feedback-decision-preview:
	$(call manual_evals_db_health,--feedback-decision-preview,$(MANUAL_EVALS_FEEDBACK_DECISION_ARGS))

manual-evals-overlay-comparison-readiness manualdb-overlay-comparison-readiness:
	$(call manual_evals_db_health,--overlay-ocr-comparison-readiness,$(MANUAL_EVALS_OVERLAY_COMPARISON_ARGS))

manual-evals-overlay-source-index-draft manualdb-overlay-source-index-draft:
	$(call manual_evals_db_health,--overlay-source-index-draft,$(MANUAL_EVALS_OVERLAY_SOURCE_INDEX_DRAFT_ARGS))

manual-evals-overlay-source-index-validate manualdb-overlay-source-index-validate:
	$(call manual_evals_db_health,--overlay-source-index-validate,$(MANUAL_EVALS_OVERLAY_SOURCE_INDEX_VALIDATE_ARGS))

manual-evals-ocr-retry-candidates manualdb-ocr-retry-candidates:
	$(call manual_evals_db_health,--ocr-retry-candidates,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-source-verification manualdb-ocr-retry-source-verification:
	$(call manual_evals_db_health,--ocr-retry-source-verification,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-source-provenance manualdb-ocr-retry-source-provenance:
	$(call manual_evals_db_health,--ocr-retry-source-provenance,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-input-packet manualdb-ocr-retry-input-packet:
	$(call manual_evals_db_health,--ocr-retry-input-packet,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-rerun-manifest manualdb-ocr-retry-rerun-manifest:
	$(call manual_evals_db_health,--ocr-retry-rerun-manifest,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-ocr-retry-rerun-plan manualdb-ocr-retry-rerun-plan:
	$(call manual_evals_db_health,--ocr-retry-rerun-plan,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS))

manual-evals-ocr-retry-selection-review manualdb-ocr-retry-selection-review:
	$(call manual_evals_db_health,--ocr-retry-selection-review,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS))

manual-evals-ocr-retry-selection-template manualdb-ocr-retry-selection-template:
	$(call manual_evals_db_health,--ocr-retry-selection-template,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS))

manual-evals-ocr-retry-selection-draft manualdb-ocr-retry-selection-draft:
	$(call manual_evals_db_health,--ocr-retry-selection-draft,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS) $(MANUAL_EVALS_OCR_RETRY_SELECTION_DRAFT_ARGS))

manual-evals-ocr-retry-selection-validate manualdb-ocr-retry-selection-validate:
	$(call manual_evals_db_health,--ocr-retry-selection-validate,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS) $(MANUAL_EVALS_OCR_RETRY_SELECTION_VALIDATE_ARGS))

manual-evals-ocr-retry-selection-apply-preview manualdb-ocr-retry-selection-apply-preview:
	$(call manual_evals_db_health,--ocr-retry-selection-apply-preview,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS) $(MANUAL_EVALS_OCR_RETRY_SELECTION_VALIDATE_ARGS))

manual-evals-ocr-retry-execution-readiness manualdb-ocr-retry-execution-readiness:
	$(call manual_evals_db_health,--ocr-retry-execution-readiness,$(MANUAL_EVALS_OCR_RETRY_PLAN_ARGS) $(MANUAL_EVALS_OCR_RETRY_SELECTION_VALIDATE_ARGS))

manual-evals-ocr-retry-execute manualdb-ocr-retry-execute:
	$(call manual_evals_db_health,--ocr-retry-execute,$(MANUAL_EVALS_OCR_RETRY_EXECUTE_ARGS))

manual-evals-ocr-retry-execution-report manualdb-ocr-retry-execution-report:
	$(call manual_evals_db_health,--ocr-retry-execution-report,$(MANUAL_EVALS_OCR_RETRY_EXECUTION_REPORT_ARGS))

manual-evals-ocr-retry-feedback-closure-preview manualdb-ocr-retry-feedback-closure-preview:
	$(call manual_evals_db_health,--ocr-retry-feedback-closure-preview,$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_PREVIEW_ARGS))

manual-evals-ocr-retry-feedback-closure-apply manualdb-ocr-retry-feedback-closure-apply:
	$(call manual_evals_db_health,--ocr-retry-feedback-closure-apply,$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_APPLY_ARGS))

manual-evals-ocr-retry-feedback-closure-apply-report manualdb-ocr-retry-feedback-closure-apply-report:
	$(call manual_evals_db_health,--ocr-retry-feedback-closure-apply-report,$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_APPLY_REPORT_ARGS))

manual-evals-ocr-retry-feedback-closure-restore-preview manualdb-ocr-retry-feedback-closure-restore-preview:
	$(call manual_evals_db_health,--ocr-retry-feedback-closure-restore-preview,$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_ARGS))

manual-evals-ocr-retry-feedback-closure-restore manualdb-ocr-retry-feedback-closure-restore:
	$(call manual_evals_db_health,--ocr-retry-feedback-closure-restore,$(MANUAL_EVALS_OCR_RETRY_FEEDBACK_CLOSURE_RESTORE_APPLY_ARGS))

manual-evals-no-context-reclassify-preview manualdb-no-context-reclassify-preview:
	$(call manual_evals_db_health,--no-context-feedback-reclassify-preview,$(MANUAL_EVALS_FEEDBACK_ACTIONABLE_ARGS))

manual-evals-no-context-reclassify-apply manualdb-no-context-reclassify-apply:
	$(call manual_evals_db_health,--no-context-feedback-reclassify-apply,$(MANUAL_EVALS_NO_CONTEXT_RECLASSIFY_ARGS))

manual-evals-feedback-reclassify-preview manualdb-feedback-reclassify-preview:
	$(call manual_evals_db_health,--feedback-reclassify-preview,$(MANUAL_EVALS_FEEDBACK_RECLASSIFY_ARGS))

manual-evals-feedback-reclassify-apply manualdb-feedback-reclassify-apply:
	$(call manual_evals_db_health,--feedback-reclassify-apply,$(MANUAL_EVALS_FEEDBACK_RECLASSIFY_APPLY_ARGS))

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

pwcli playwright-cli:
	@PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" \
		PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" \
		PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" \
		"$(PWCLI_TOOL)" $(ARGS)

playwright-snapshot-dir:
	@PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" \
		PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" \
		"$(PWCLI_TOOL)" --print-dir
