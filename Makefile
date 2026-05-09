PYTHON ?= $(shell \
	if [ -x ./venv/bin/python ] && ./venv/bin/python -V >/dev/null 2>&1; then \
		echo ./venv/bin/python; \
	else \
		echo python3; \
	fi)
DOCKER ?= docker
DOCKER_IMAGE ?= polinko:dev
DOCKER_PORT ?= 8000
DEV_HOST ?= 127.0.0.1
DEV_BACKEND_PORT ?= 8000
DEV_API_DOCS_URL ?= http://$(DEV_HOST):$(DEV_BACKEND_PORT)/docs
DEV_VIZ_URL ?= http://$(DEV_HOST):$(DEV_BACKEND_PORT)/viz/pass-fail
DEV_PORTFOLIO_URL ?= http://$(DEV_HOST):$(DEV_BACKEND_PORT)/portfolio
PORTFOLIO_MOCKUP_DIR ?= docs/peanut/assets/tumbles/portfolio
PORTFOLIO_MOCKUP_PORT ?= 8765
PORTFOLIO_MOCKUP_URL ?= http://127.0.0.1:$(PORTFOLIO_MOCKUP_PORT)/landing-mockups.html
PORTFOLIO_LAUNCH ?= none
PORTFOLIO_PLAYWRIGHT_SESSION ?= $(PLAYWRIGHT_SESSION)
FRONTEND_DIR ?= frontend
OPENAI_LIMITS_URL ?= https://platform.openai.com/settings/organization/limits
OPENAI_USAGE_URL ?= https://platform.openai.com/settings/organization/usage
OPENAI_BILLING_URL ?= https://platform.openai.com/settings/organization/billing/overview
ENV_FILE ?= .env
K6_BASE_URL ?= http://127.0.0.1:8000
K6_VUS ?= 3
K6_DURATION ?= 10s
TRIVY_SEVERITY ?= HIGH,CRITICAL
GATE_PORT ?= 8066
GATE_BASE_URL ?= http://127.0.0.1:$(GATE_PORT)
GATE_SESSION_DB ?= /tmp/polinko-quality-gate-sessions.db
GATE_VECTOR_DB ?= /tmp/polinko-quality-gate-vector.db
SMOKE_PORT ?= 8067
SMOKE_BASE_URL ?= http://127.0.0.1:$(SMOKE_PORT)
SMOKE_HISTORY_DB ?= /tmp/polinko-eval-smoke-history.db
SMOKE_MEMORY_DB ?= /tmp/polinko-eval-smoke-memory.db
SMOKE_VECTOR_DB ?= /tmp/polinko-eval-smoke-vector.db
HALLUCINATION_EVAL_MODE ?= judge
HALLUCINATION_JUDGE_MODEL ?= gpt-4.1-mini
HALLUCINATION_JUDGE_API_KEY_ENV ?= OPENAI_API_KEY
HALLUCINATION_JUDGE_BASE_URL ?=
HALLUCINATION_MIN_ACCEPTABLE_SCORE ?= 5
STYLE_CASE_ATTEMPTS ?= 1
STYLE_MIN_PASS_ATTEMPTS ?= 1
RETRIEVAL_REQUEST_RETRIES ?= 2
RETRIEVAL_REQUEST_RETRY_DELAY_MS ?= 750
CLIP_AB_SOURCE_TYPES ?= image
OCR_HANDWRITING_CASES ?= .local/eval_cases/ocr_handwriting_eval_cases.json
OCR_SAFETY_CASES ?= docs/eval/beta_2_0/ocr_safety_eval_cases.json
CGPT_EXPORT_ROOT ?=
CGPT_EXPORT_ROOT_DEFAULT ?=
CGPT_EXPORT_OUTPUT_DIR ?= .local/eval_cases
OCR_CASES_FROM_EXPORT_ARGS ?=
OCR_TRANSCRIPT_CASES_ALL ?= .local/eval_cases/ocr_transcript_cases_all.json
OCR_TRANSCRIPT_CASES_GROWTH ?= .local/eval_cases/ocr_transcript_cases_growth.json
OCR_TRANSCRIPT_CASES_HANDWRITING ?= .local/eval_cases/ocr_handwriting_from_transcripts.json
OCR_TRANSCRIPT_CASES_TYPED ?= .local/eval_cases/ocr_typed_from_transcripts.json
OCR_TRANSCRIPT_CASES_ILLUSTRATION ?= .local/eval_cases/ocr_illustration_from_transcripts.json
OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK ?= .local/eval_cases/ocr_handwriting_benchmark_cases.json
OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK ?= .local/eval_cases/ocr_typed_benchmark_cases.json
OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK ?= .local/eval_cases/ocr_illustration_benchmark_cases.json
OCR_TRANSCRIPT_CASES ?= $(OCR_TRANSCRIPT_CASES_ALL)
OCR_TRANSCRIPT_REVIEW ?= .local/eval_cases/ocr_transcript_cases_review.json
OCR_TRANSCRIPT_REVIEW_PREV ?= .local/eval_cases/ocr_transcript_cases_review_prev.json
OCR_TRANSCRIPT_DELTA_MD ?= .local/eval_cases/ocr_transcript_cases_delta.md
OCR_TRANSCRIPT_DELTA_JSON ?= .local/eval_cases/ocr_transcript_cases_delta.json
OCR_HANDWRITING_BENCHMARK_TOP_K ?= 6
OCR_HANDWRITING_BENCHMARK_MIN_ANCHORS ?= 3
OCR_TYPED_BENCHMARK_TOP_K ?= 8
OCR_TYPED_BENCHMARK_MIN_ANCHORS ?= 3
OCR_ILLUSTRATION_BENCHMARK_TOP_K ?= 6
OCR_ILLUSTRATION_BENCHMARK_MIN_ANCHORS ?= 2
OCR_STABILITY_RUNS ?= 5
OCR_STABILITY_OCR_RETRIES ?= 2
OCR_STABILITY_OCR_RETRY_DELAY_MS ?= 750
OCR_STABILITY_CASE_DELAY_MS ?= 0
OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS ?= 0
OCR_MAX_CONSEC_RATE_LIMIT_ERRORS ?= 3
OCR_EVAL_TIMEOUT ?= 90
OCR_EVAL_OCR_RETRIES ?= 2
OCR_EVAL_OCR_RETRY_DELAY_MS ?= 750
OCR_STABILITY_OUTPUT ?= .local/eval_reports/ocr_transcript_stability.json
OCR_STABILITY_REPORT_DIR ?= .local/eval_reports/ocr_stability_runs
OCR_GROWTH_MAX_CASES ?= 600
OCR_GROWTH_STABILITY_OUTPUT ?= .local/eval_reports/ocr_growth_stability.json
OCR_GROWTH_STABILITY_REPORT_DIR ?= .local/eval_reports/ocr_growth_stability_runs
OCR_GROWTH_STABILITY_RUNS ?= $(OCR_STABILITY_RUNS)
OCR_GROWTH_METRICS_OUTPUT ?= .local/eval_reports/ocr_growth_metrics.json
OCR_GROWTH_METRICS_MARKDOWN ?= .local/eval_reports/ocr_growth_metrics.md
OCR_GROWTH_FAIL_COHORT_JSON ?= .local/eval_cases/ocr_growth_fail_cohort.json
OCR_GROWTH_FAIL_COHORT_MARKDOWN ?= .local/eval_reports/ocr_growth_fail_cohort.md
OCR_FAIL_COHORT_MIN_RUNS ?= 1
OCR_FAIL_COHORT_INCLUDE_UNSTABLE ?= true
OCR_FAIL_COHORT_REQUIRE_OCR_FRAMING ?= true
OCR_FAIL_COHORT_INCLUDE_EXPLORATORY ?= true
OCR_FAIL_COHORT_EXPLORATORY_MAX_CASES ?= 18
OCR_FOCUS_CASES_JSON ?= .local/eval_cases/ocr_growth_focus_cases.json
OCR_FOCUS_RUNS ?= 3
OCR_FOCUS_MAX_CASES ?= 40
OCR_FOCUS_INCLUDE_FAIL_HISTORY ?= true
OCR_FOCUS_INCLUDE_EXPLORATORY ?= true
OCR_FOCUS_OUTPUT ?= .local/eval_reports/ocr_focus_stability.json
OCR_FOCUS_REPORT_DIR ?= .local/eval_reports/ocr_focus_runs
OCR_FOCUS_FAIL_PATTERNS_JSON ?= .local/eval_reports/ocr_focus_fail_patterns.json
OCR_FOCUS_FAIL_PATTERNS_MD ?= .local/eval_reports/ocr_focus_fail_patterns.md
OCR_FOCUS_OCR_RETRIES ?= 3
OCR_FOCUS_OCR_RETRY_DELAY_MS ?= 1000
OCR_FOCUS_CASE_DELAY_MS ?= 1200
OCR_FOCUS_RATE_LIMIT_COOLDOWN_MS ?= 12000
OCR_FOCUS_SKIP_RECENT_RATE_LIMIT ?= true
OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS ?= 900
OCR_GROWTH_LIMIT_RUNS ?= 0
OCR_GROWTH_EVAL_OFFSET ?= 0
OCR_GROWTH_EVAL_MAX_CASES ?= 0
OCR_GROWTH_BATCH_SIZE ?= 40
OCR_GROWTH_OCR_RETRIES ?= 2
OCR_GROWTH_OCR_RETRY_DELAY_MS ?= 750
OCR_GROWTH_CASE_DELAY_MS ?= 0
OCR_GROWTH_RATE_LIMIT_COOLDOWN_MS ?= 0
OCR_GROWTH_BATCH_REPORT_DIR ?= .local/eval_reports/ocr_growth_batched_runs
OCR_GROWTH_BATCH_SUMMARY_JSON ?= .local/eval_reports/ocr_growth_batched_summary.json
OCR_GROWTH_BATCH_SUMMARY_MD ?= .local/eval_reports/ocr_growth_batched_summary.md
OCR_STABILITY_HANDWRITING_BENCHMARK_OUTPUT ?= .local/eval_reports/ocr_handwriting_benchmark_stability.json
OCR_STABILITY_HANDWRITING_BENCHMARK_REPORT_DIR ?= .local/eval_reports/ocr_handwriting_benchmark_runs
OCR_STABILITY_TYPED_BENCHMARK_OUTPUT ?= .local/eval_reports/ocr_typed_benchmark_stability.json
OCR_STABILITY_TYPED_BENCHMARK_REPORT_DIR ?= .local/eval_reports/ocr_typed_benchmark_runs
OCR_STABILITY_ILLUSTRATION_BENCHMARK_OUTPUT ?= .local/eval_reports/ocr_illustration_benchmark_stability.json
OCR_STABILITY_ILLUSTRATION_BENCHMARK_REPORT_DIR ?= .local/eval_reports/ocr_illustration_benchmark_runs
NOTEBOOK_START_PATH ?= output/jupyter-notebook/ocr-eval-live-filters-starter.ipynb
NOTEBOOK_START_PATH_ABS := $(abspath $(NOTEBOOK_START_PATH))
NOTEBOOK_DIR_ABS := $(abspath output/jupyter-notebook)
CAFFEINATE_PID_FILE ?= /tmp/polinko-caffeinate.pid
CAFFEINATE_LOG ?= /tmp/polinko-caffeinate.log
CAFFEINATE_CMD ?= /usr/bin/caffeinate -d -i -m
SERVER_PID_FILE ?= /tmp/polinko-server.pid
SERVER_LOG ?= /tmp/polinko-server.log
EVAL_SIDECAR_PID_FILE ?= /tmp/polinko-eval-sidecar.pid
EVAL_SIDECAR_LOG ?= /tmp/polinko-eval-sidecar.log
EVAL_SIDECAR_TARGET ?= quality-gate-deterministic
EVAL_SIDECAR_MIN_SECONDS ?= 3600
EVAL_SIDECAR_RUNS_DIR ?= .local/eval_runs
EVAL_SIDECAR_CURRENT_FILE ?= $(EVAL_SIDECAR_RUNS_DIR)/eval_sidecar_current.txt
PORTFOLIO_MOCKUP_PID_FILE ?= /tmp/polinko-portfolio-mockups.pid
PORTFOLIO_MOCKUP_LOG ?= /tmp/polinko-portfolio-mockups.log
PLAYWRIGHT_SNAPSHOT_BASE_DIR ?= docs/peanut/assets/screenshots/playwright
PLAYWRIGHT_SNAPSHOT_DAY ?= $(shell date +%d-%m-%y)
PLAYWRIGHT_SESSION ?= polinko
PWCLI_TOOL ?= tools/pwcli_daily.sh
REQUIREMENTS_IN ?= requirements.in
REQUIREMENTS_LOCK ?= requirements.lock
PIP_TOOLS_VERSION ?= 7.5.3

.PHONY: chat venv env deps-install deps-lock notebook-setup notebook nb notes viz ocrindex ocrmine ocrminehand ocrminetype ocrmineillu ocrminehigh ocrminelow ocrminebacklog ocrall ocrwiden ocrwidensync ocrwidenbatch ocrwidenall ocrhand ocrtype ocrillu ocrstable ocrstablegrowth ocrgrowth ocrfails ocrfocus ocrfocuscases ocrfocusreport ocrkernel ocrhandbench ocrtypebench ocrillubench ocrstablehand ocrstabletype ocrstableillu ocrdelta nulls runtime-null-audit ocr-data ocr-notebook-workflow gate eod eod-stop localhost server server-daemon server-daemon-stop server-daemon-status docs open-api-docs open-limits open-usage open-billing open-cost-console session-status test test-one test-targeted pycheck lint-docs mermaid-render d3-render public-diagrams-render transcript-fix transcript-check doctor-env backend-gate caffeinate-on caffeinate-off caffeinate-off-all caffeinate-status decaffeinate privacy-local-on privacy-local-status privacy-local-off precommit-install precommit-run act-list act-ci k6-chat-smoke trivy-fs trivy-image api-smoke eval-smoke eval-retrieval eval-retrieval-report eval-file-search eval-file-search-report eval-hallucination eval-hallucination-deterministic eval-hallucination-report eval-style eval-style-report eval-response-behaviour eval-response-behaviour-report eval-ocr-safety eval-ocr-safety-report eval-ocr eval-ocr-report eval-ocr-handwriting eval-ocr-handwriting-report eval-ocr-recovery eval-ocr-recovery-report eval-clip-ab eval-clip-ab-report eval-clip-ab-readiness eval-reports eval-reports-parallel eval-sidecar-start eval-sidecar-status eval-sidecar-stop operator-burden-report calibrate-hallucination-threshold backfill-eval-traces hallucination-gate quality-gate quality-gate-deterministic cgpt-export-index ocr-cases-from-export ocr-handwriting-benchmark-cases ocr-typed-benchmark-cases ocr-illustration-benchmark-cases ocr-transcript-delta eval-ocr-transcript-cases eval-ocr-transcript-cases-growth eval-ocr-transcript-cases-growth-batched eval-ocr-growth-fail-cohort eval-ocr-focus-cases eval-ocr-focus-stability eval-ocr-focus-fail-patterns eval-ocr-transcript-cases-handwriting eval-ocr-transcript-cases-handwriting-benchmark eval-ocr-transcript-cases-typed eval-ocr-transcript-cases-typed-benchmark eval-ocr-transcript-cases-illustration eval-ocr-transcript-cases-illustration-benchmark eval-ocr-transcript-stability eval-ocr-transcript-stability-growth eval-ocr-transcript-growth eval-ocr-transcript-stability-handwriting-benchmark eval-ocr-transcript-stability-typed-benchmark eval-ocr-transcript-stability-illustration-benchmark docker-build docker-run
.PHONY: frontend-install portfolio-build frontend-build portfolio portfolio-rebuild rebuild portfolio-playwright portfolio-mockups portfolio-mockups-stop pwcli playwright-cli playwright-snapshot-dir
chat:
	$(PYTHON) app.py

venv env:
	@set -eu; \
	if [ -f ./venv/bin/activate ]; then \
		ACTIVATE_PATH="./venv/bin/activate"; \
	elif [ -f ./polinko-repositioning-system/bin/activate ]; then \
		ACTIVATE_PATH="./polinko-repositioning-system/bin/activate"; \
	else \
		echo "No local activation script found (checked ./venv/bin/activate and ./polinko-repositioning-system/bin/activate)."; \
		exit 1; \
	fi; \
	echo "Opening shell with virtual environment: $$ACTIVATE_PATH"; \
	. "$$ACTIVATE_PATH"; \
	echo "VIRTUAL_ENV=$$VIRTUAL_ENV"; \
	exec "$$SHELL" -i

deps-install:
	$(PYTHON) -m pip install -r "$(REQUIREMENTS_LOCK)"

deps-lock:
	@set -eu; \
	if ! $(PYTHON) -m piptools --version >/dev/null 2>&1; then \
		$(PYTHON) -m pip install "pip-tools==$(PIP_TOOLS_VERSION)"; \
	fi; \
	$(PYTHON) -m piptools compile \
		--resolver=backtracking \
		--allow-unsafe \
		--strip-extras \
		--output-file "$(REQUIREMENTS_LOCK)" \
		"$(REQUIREMENTS_IN)"

notebook-setup:
	$(PYTHON) -m pip install -r requirements.notebook.txt

notebook nb notes:
	@mkdir -p "$(NOTEBOOK_DIR_ABS)"; \
	if [ -f "$(NOTEBOOK_START_PATH_ABS)" ]; then \
		$(PYTHON) -m jupyter lab --notebook-dir="$(NOTEBOOK_DIR_ABS)" "$(NOTEBOOK_START_PATH_ABS)"; \
	else \
		$(PYTHON) -m jupyter lab --notebook-dir="$(NOTEBOOK_DIR_ABS)" "$(NOTEBOOK_DIR_ABS)"; \
	fi

.PHONY: manual-evals-db manualdb
manual-evals-db manualdb:
	$(PYTHON) -m tools.build_manual_evals_db \
		--optional-history-source beta_1_0=.local/legacy_eval/archive_legacy_eval/databases/.polinko_history.db \
		--history-source current=.local/runtime_dbs/active/history.db \
		--include-eval-sessions

# Short aliases for frequent long-chain commands.
ocrindex: cgpt-export-index

ocrmine: ocr-cases-from-export

ocrminehand:
	@set -eu; \
	$(MAKE) --no-print-directory ocr-cases-from-export \
		CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		OCR_CASES_FROM_EXPORT_ARGS='--include-lanes handwriting'

ocrminetype:
	@set -eu; \
	$(MAKE) --no-print-directory ocr-cases-from-export \
		CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		OCR_CASES_FROM_EXPORT_ARGS='--include-lanes typed'

ocrmineillu:
	@set -eu; \
	$(MAKE) --no-print-directory ocr-cases-from-export \
		CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		OCR_CASES_FROM_EXPORT_ARGS='--include-lanes illustration'

ocrminehigh:
	@set -eu; \
	$(MAKE) --no-print-directory ocr-cases-from-export \
		CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		OCR_CASES_FROM_EXPORT_ARGS='--include-signal-strengths high'

ocrminelow:
	@set -eu; \
	$(MAKE) --no-print-directory ocr-cases-from-export \
		CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		OCR_CASES_FROM_EXPORT_ARGS='--include-signal-strengths low'

ocrminebacklog:
	@set -eu; \
	$(MAKE) --no-print-directory ocr-cases-from-export \
		CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)" \
		OCR_CASES_FROM_EXPORT_ARGS='--include-emit-statuses skipped_low_confidence'

ocrall: eval-ocr-transcript-cases

ocrwiden: eval-ocr-transcript-cases-growth-batched

ocrwidensync: eval-ocr-transcript-cases-growth

ocrwidenbatch: eval-ocr-transcript-cases-growth-batched

ocrwidenall: eval-ocr-transcript-cases-growth-batched

ocrhand: eval-ocr-transcript-cases-handwriting

ocrtype: eval-ocr-transcript-cases-typed

ocrillu: eval-ocr-transcript-cases-illustration

ocrstable: eval-ocr-transcript-stability

ocrstablegrowth: eval-ocr-transcript-stability-growth

ocrgrowth: eval-ocr-transcript-growth

ocrfails: eval-ocr-growth-fail-cohort

ocrfocuscases: eval-ocr-focus-cases

ocrfocusreport: eval-ocr-focus-fail-patterns

ocrfocus:
	@set -eu; \
	$(MAKE) --no-print-directory ocrgrowth; \
	$(MAKE) --no-print-directory ocrfails; \
	$(MAKE) --no-print-directory ocrfocuscases; \
	$(MAKE) --no-print-directory eval-ocr-focus-stability; \
	$(MAKE) --no-print-directory ocrfocusreport

ocrkernel:
	@set -eu; \
	EXPORT_ROOT="$(CGPT_EXPORT_ROOT)"; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		EXPORT_ROOT="$(CGPT_EXPORT_ROOT_DEFAULT)"; \
	fi; \
	if [ ! -d "$$EXPORT_ROOT" ]; then \
		echo "CGPT export root not found: $$EXPORT_ROOT"; \
		echo "Run: make ocrkernel CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 1; \
	fi; \
	$(MAKE) --no-print-directory doctor-env; \
	$(MAKE) --no-print-directory ocrmine CGPT_EXPORT_ROOT="$$EXPORT_ROOT"; \
	$(MAKE) --no-print-directory ocrdelta; \
	$(MAKE) --no-print-directory ocrwiden; \
	$(MAKE) --no-print-directory ocrstablegrowth; \
	$(MAKE) --no-print-directory ocrgrowth; \
	$(MAKE) --no-print-directory ocrfails; \
	$(MAKE) --no-print-directory ocrfocuscases; \
	$(MAKE) --no-print-directory eval-ocr-focus-stability; \
	$(MAKE) --no-print-directory ocrfocusreport

ocrhandbench: eval-ocr-transcript-cases-handwriting-benchmark

ocrtypebench: eval-ocr-transcript-cases-typed-benchmark

ocrillubench: eval-ocr-transcript-cases-illustration-benchmark

ocrstablehand: eval-ocr-transcript-stability-handwriting-benchmark

ocrstabletype: eval-ocr-transcript-stability-typed-benchmark

ocrstableillu: eval-ocr-transcript-stability-illustration-benchmark

ocrdelta: ocr-transcript-delta

nulls: runtime-null-audit

runtime-null-audit:
	$(PYTHON) -m tools.audit_runtime_nulls

ocr-data:
	@set -eu; \
	EXPORT_ROOT="$(CGPT_EXPORT_ROOT)"; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		EXPORT_ROOT="$(CGPT_EXPORT_ROOT_DEFAULT)"; \
	fi; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		echo "CGPT_EXPORT_ROOT is required."; \
		echo "Run: make ocr-data CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 1; \
	fi; \
	if [ ! -d "$$EXPORT_ROOT" ]; then \
		echo "CGPT export root not found: $$EXPORT_ROOT"; \
		echo "Run: make ocr-data CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 1; \
	fi; \
	$(MAKE) --no-print-directory doctor-env; \
	$(MAKE) --no-print-directory ocrmine CGPT_EXPORT_ROOT="$$EXPORT_ROOT"; \
	$(MAKE) --no-print-directory ocrdelta

ocr-notebook-workflow:
	@set -eu; \
	if [ -z "$(CGPT_EXPORT_ROOT)" ]; then \
		echo "CGPT_EXPORT_ROOT is required."; \
		echo "Example: make ocr-notebook-workflow CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 1; \
	fi; \
	$(MAKE) --no-print-directory doctor-env; \
	$(MAKE) --no-print-directory ocrmine CGPT_EXPORT_ROOT="$(CGPT_EXPORT_ROOT)"; \
	$(MAKE) --no-print-directory ocrall; \
	$(MAKE) --no-print-directory ocrstable; \
	$(MAKE) --no-print-directory ocrwiden; \
	$(MAKE) --no-print-directory ocrstablegrowth; \
	$(MAKE) --no-print-directory ocrgrowth; \
	$(MAKE) --no-print-directory ocrfails

gate: quality-gate-deterministic

eod:
	./tools/end_of_day_routine.sh

eod-stop:
	@set -eu; \
	$(MAKE) --no-print-directory server-daemon-stop || true; \
	$(MAKE) --no-print-directory caffeinate-off-all || true; \
	$(MAKE) --no-print-directory session-status || true

localhost server:
	$(PYTHON) -m uvicorn server:app --host "$(DEV_HOST)" --port "$(DEV_BACKEND_PORT)" --reload

server-daemon:
	@set -eu; \
	EXPECTED_PY="$$( $(PYTHON) -c 'import os,sys; print(os.path.realpath(sys.executable))' 2>/dev/null || true )"; \
	if [ -z "$$EXPECTED_PY" ]; then \
		echo "Unable to resolve expected Python interpreter from $(PYTHON)."; \
		exit 1; \
	fi; \
	if [ -f "$(SERVER_PID_FILE)" ]; then \
		PID=$$(cat "$(SERVER_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "server-daemon already running (PID $$PID)."; \
			exit 0; \
		fi; \
		rm -f "$(SERVER_PID_FILE)"; \
	fi; \
	if command -v lsof >/dev/null 2>&1; then \
		EXISTING_PIDS=$$(lsof -nP -iTCP:"$(DEV_BACKEND_PORT)" -sTCP:LISTEN -t 2>/dev/null | tr '\n' ' ' || true); \
		if [ -n "$$EXISTING_PIDS" ]; then \
			POLINKO_PID=""; \
			POLINKO_CMD=""; \
			for CANDIDATE_PID in $$EXISTING_PIDS; do \
				CANDIDATE_CMD=$$(ps -o command= -p "$$CANDIDATE_PID" 2>/dev/null || true); \
				CHECK_PID="$$CANDIDATE_PID"; \
				CHECK_CMD="$$CANDIDATE_CMD"; \
				if ! echo "$$CHECK_CMD" | grep -q "uvicorn server:app"; then \
					PARENT_PID=$$(ps -o ppid= -p "$$CANDIDATE_PID" 2>/dev/null | tr -d ' ' || true); \
					if [ -n "$$PARENT_PID" ]; then \
						PARENT_CMD=$$(ps -o command= -p "$$PARENT_PID" 2>/dev/null || true); \
						if echo "$$PARENT_CMD" | grep -q "uvicorn server:app"; then \
							CHECK_PID="$$PARENT_PID"; \
							CHECK_CMD="$$PARENT_CMD"; \
						fi; \
					fi; \
				fi; \
				if echo "$$CHECK_CMD" | grep -q "uvicorn server:app"; then \
					POLINKO_PID="$$CHECK_PID"; \
					POLINKO_CMD="$$CHECK_CMD"; \
					break; \
				fi; \
			done; \
			if [ -n "$$POLINKO_PID" ]; then \
				EXISTING_PY=$$(printf '%s\n' "$$POLINKO_CMD" | awk '{print $$1}'); \
				EXISTING_PY_REAL="$$( "$$EXISTING_PY" -c 'import os,sys; print(os.path.realpath(sys.executable))' 2>/dev/null || true )"; \
				if [ "$$EXISTING_PY_REAL" = "$$EXPECTED_PY" ]; then \
					echo "$$POLINKO_PID" >"$(SERVER_PID_FILE)"; \
					echo "server-daemon already active on port $(DEV_BACKEND_PORT); adopted PID $$POLINKO_PID ($$EXISTING_PY_REAL)."; \
					exit 0; \
				fi; \
				echo "server-daemon found polinko server on port $(DEV_BACKEND_PORT) with interpreter mismatch."; \
				echo "expected: $$EXPECTED_PY"; \
				echo "found:    $$EXISTING_PY_REAL"; \
				echo "Restarting server-daemon with expected interpreter."; \
				kill "$$POLINKO_PID"; \
				sleep 0.2; \
			else \
				FIRST_PID=$$(printf '%s\n' "$$EXISTING_PIDS" | awk '{print $$1}'); \
				FIRST_CMD=$$(ps -o command= -p "$$FIRST_PID" 2>/dev/null || true); \
				echo "Port $(DEV_BACKEND_PORT) is in use by a non-polinko process."; \
				echo "PID $$FIRST_PID: $$FIRST_CMD"; \
				exit 1; \
			fi; \
		fi; \
	fi; \
	nohup $(PYTHON) -m uvicorn server:app --host "$(DEV_HOST)" --port "$(DEV_BACKEND_PORT)" --reload >"$(SERVER_LOG)" 2>&1 & \
	PID=$$!; \
	echo "$$PID" >"$(SERVER_PID_FILE)"; \
	sleep 0.2; \
	if kill -0 "$$PID" 2>/dev/null; then \
		echo "server-daemon started (PID $$PID, log: $(SERVER_LOG))."; \
	else \
		rm -f "$(SERVER_PID_FILE)"; \
		echo "Failed to start server-daemon. Check $(SERVER_LOG)."; \
		exit 1; \
	fi

server-daemon-stop:
	@set -eu; \
	if [ ! -f "$(SERVER_PID_FILE)" ]; then \
		echo "No server-daemon PID file found."; \
		exit 0; \
	fi; \
	PID=$$(cat "$(SERVER_PID_FILE)" 2>/dev/null || true); \
	if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
		kill "$$PID"; \
		echo "server-daemon stopped (PID $$PID)."; \
	else \
		echo "Stale server-daemon PID file; cleaning up."; \
	fi; \
	rm -f "$(SERVER_PID_FILE)"

server-daemon-status:
	@set -eu; \
	if [ -f "$(SERVER_PID_FILE)" ]; then \
		PID=$$(cat "$(SERVER_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "server-daemon: RUNNING (PID $$PID)."; \
			exit 0; \
		fi; \
		echo "server-daemon: STALE PID file."; \
		exit 1; \
	fi; \
	echo "server-daemon: OFF."

open-api-docs:
	@set -eu; \
	$(MAKE) --no-print-directory server-daemon; \
	URL="$(DEV_API_DOCS_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "API docs URL: $$URL"

docs:
	@$(MAKE) --no-print-directory open-api-docs

open-limits:
	@set -eu; \
	URL="$(OPENAI_LIMITS_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "OpenAI limits URL: $$URL"

open-usage:
	@set -eu; \
	URL="$(OPENAI_USAGE_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "OpenAI usage URL: $$URL"

open-billing:
	@set -eu; \
	URL="$(OPENAI_BILLING_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "OpenAI billing URL: $$URL"

open-cost-console:
	@set -eu; \
	$(MAKE) --no-print-directory open-limits; \
	$(MAKE) --no-print-directory open-usage; \
	$(MAKE) --no-print-directory open-billing

viz:
	@set -eu; \
	$(MAKE) --no-print-directory server-daemon; \
	URL="$(DEV_VIZ_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "PASS/FAIL viz URL: $$URL"

frontend-install:
	@set -eu; \
	if [ ! -f "$(FRONTEND_DIR)/package.json" ]; then \
		echo "Frontend source not present at $(FRONTEND_DIR)/package.json; skipping npm install."; \
		exit 0; \
	fi; \
	npm --prefix "$(FRONTEND_DIR)" install

portfolio-build:
	@set -eu; \
	if [ ! -f "$(FRONTEND_DIR)/package.json" ]; then \
		echo "Frontend source not present at $(FRONTEND_DIR)/package.json; using tracked /portfolio fallback."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory frontend-install; \
	npm --prefix "$(FRONTEND_DIR)" run build

frontend-build: portfolio-build

portfolio:
	@set -eu; \
	$(MAKE) --no-print-directory portfolio-build; \
	$(MAKE) --no-print-directory server-daemon-stop || true; \
	$(MAKE) --no-print-directory server-daemon; \
	URL="$(DEV_PORTFOLIO_URL)"; \
	CACHE_BUST="$$(date +%s)"; \
	case "$$URL" in \
		*\?*) OPEN_URL="$$URL&rebuild=$$CACHE_BUST" ;; \
		*) OPEN_URL="$$URL?rebuild=$$CACHE_BUST" ;; \
	esac; \
	case "$(PORTFOLIO_LAUNCH)" in \
			playwright) \
				if PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" list 2>/dev/null | awk 'BEGIN { found = 0; bad = 0 } /^- $(PLAYWRIGHT_SESSION):/ { found = 1; next } found && /^- / { found = 0 } found && /headed: false/ { bad = 1 } END { exit bad ? 0 : 1 }'; then \
					PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" close >/dev/null 2>&1 || true; \
				fi; \
				if PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" tab-new "$$OPEN_URL" >/dev/null 2>&1; then \
					echo "Opened Playwright portfolio tab: $$OPEN_URL"; \
				else \
					PLAYWRIGHT_SNAPSHOT_BASE_DIR="$(PLAYWRIGHT_SNAPSHOT_BASE_DIR)" PLAYWRIGHT_SNAPSHOT_DAY="$(PLAYWRIGHT_SNAPSHOT_DAY)" PLAYWRIGHT_SESSION="$(PLAYWRIGHT_SESSION)" "$(PWCLI_TOOL)" open "$$OPEN_URL" --headed; \
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

portfolio-playwright:
	@$(MAKE) --no-print-directory portfolio PORTFOLIO_LAUNCH=playwright PLAYWRIGHT_SESSION="$(PORTFOLIO_PLAYWRIGHT_SESSION)"

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

session-status:
	@echo "== Server =="
	@$(MAKE) --no-print-directory server-daemon-status || true
	@echo ""
	@echo "== Keep-awake =="
	@$(MAKE) --no-print-directory caffeinate-status || true

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

test-one:
	@set -eu; \
	if [ -z "$(TEST)" ]; then \
		echo 'Usage: make test-one TEST=tests.test_eval_file_search'; \
		exit 2; \
	fi; \
	$(PYTHON) -m unittest $(TEST)

test-targeted:
	@set -eu; \
	if [ -z "$(TESTS)" ]; then \
		echo 'Usage: make test-targeted TESTS="tests.test_eval_file_search tests.test_eval_retrieval"'; \
		exit 2; \
	fi; \
	$(PYTHON) -m unittest $(TESTS)

pycheck:
	@set -eu; \
	if [ -z "$(FILES)" ]; then \
		echo 'Usage: make pycheck FILES="tools/foo.py tools/bar.py"'; \
		exit 2; \
	fi; \
	python3 -m py_compile $(FILES)

lint-docs:
	npm run lint:docs

mermaid-render:
	$(PYTHON) -m tools.render_mermaid_diagrams

d3-render:
	$(PYTHON) -m tools.render_public_d3_diagrams

public-diagrams-render: mermaid-render d3-render

transcript-fix:
	$(PYTHON) -m tools.fix_transcripts

transcript-check:
	$(PYTHON) -m tools.validate_transcripts

doctor-env:
	@set -eu; \
	ACTIVE_VENV="$$(dirname "$(PYTHON)")/.."; \
	VIRTUAL_ENV="$$ACTIVE_VENV" PATH="$$ACTIVE_VENV/bin:$$PATH" "$(PYTHON)" -m tools.doctor_env

backend-gate:
	@echo "Running backend gate (doctor + tests + deterministic quality gate)..."
	@$(MAKE) doctor-env
	@$(MAKE) test
	@$(MAKE) quality-gate-deterministic

caffeinate-on:
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate is macOS-only; skipping."; \
		exit 0; \
	fi; \
	if [ -f "$(CAFFEINATE_PID_FILE)" ]; then \
		PID=$$(cat "$(CAFFEINATE_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "caffeinate already running (PID $$PID)."; \
			exit 0; \
		fi; \
		rm -f "$(CAFFEINATE_PID_FILE)"; \
	fi; \
	EXISTING_PID=$$(pgrep -f "^/usr/bin/caffeinate -d -i -m( |$$)" | head -n 1 || true); \
	if [ -n "$$EXISTING_PID" ]; then \
		echo "$$EXISTING_PID" >"$(CAFFEINATE_PID_FILE)"; \
		echo "caffeinate already active; adopted PID $$EXISTING_PID."; \
		exit 0; \
	fi; \
	nohup $(CAFFEINATE_CMD) >"$(CAFFEINATE_LOG)" 2>&1 & \
	PID=$$!; \
	echo "$$PID" >"$(CAFFEINATE_PID_FILE)"; \
	sleep 0.1; \
	if kill -0 "$$PID" 2>/dev/null; then \
		echo "caffeinate started (PID $$PID)."; \
	else \
		rm -f "$(CAFFEINATE_PID_FILE)"; \
		echo "Failed to start caffeinate."; \
		exit 1; \
	fi

caffeinate-off:
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate is macOS-only; skipping."; \
		exit 0; \
	fi; \
	if [ ! -f "$(CAFFEINATE_PID_FILE)" ]; then \
		echo "No managed caffeinate PID file found."; \
		exit 0; \
	fi; \
	PID=$$(cat "$(CAFFEINATE_PID_FILE)" 2>/dev/null || true); \
	if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
		kill "$$PID"; \
		sleep 0.1; \
		echo "caffeinate stopped (PID $$PID)."; \
	else \
		echo "Stale PID file found; cleaning up."; \
	fi; \
	rm -f "$(CAFFEINATE_PID_FILE)"

caffeinate-off-all:
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate is macOS-only; skipping."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory caffeinate-off || true; \
	PIDS=$$(pgrep -f "^/usr/bin/caffeinate -d -i -m( |$$)" || true); \
	if [ -n "$$PIDS" ]; then \
		for PID in $$PIDS; do \
			kill "$$PID" 2>/dev/null || true; \
		done; \
		sleep 0.1; \
		echo "Stopped matching caffeinate processes: $$PIDS"; \
	else \
		echo "No matching caffeinate processes running."; \
	fi; \
	rm -f "$(CAFFEINATE_PID_FILE)"

caffeinate-status:
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate status is only available on macOS."; \
		exit 0; \
	fi; \
	if [ -f "$(CAFFEINATE_PID_FILE)" ]; then \
		PID=$$(cat "$(CAFFEINATE_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "Managed caffeinate: RUNNING (PID $$PID)."; \
		else \
			echo "Managed caffeinate: STALE PID file."; \
		fi; \
	else \
		echo "Managed caffeinate: OFF."; \
		EXISTING_PID=$$(pgrep -f "^/usr/bin/caffeinate -d -i -m( |$$)" | head -n 1 || true); \
		if [ -n "$$EXISTING_PID" ]; then \
			echo "Unmanaged caffeinate detected (PID $$EXISTING_PID); run 'make caffeinate-on' to adopt it."; \
		fi; \
	fi; \
	if command -v rg >/dev/null 2>&1; then \
		/usr/bin/pmset -g assertions | rg -n "PreventUserIdleDisplaySleep|PreventUserIdleSystemSleep|PreventDiskIdle|caffeinate" || true; \
	else \
		/usr/bin/pmset -g assertions | grep -nE "PreventUserIdleDisplaySleep|PreventUserIdleSystemSleep|PreventDiskIdle|caffeinate" || true; \
	fi

decaffeinate: caffeinate-off

privacy-local-on:
	bash tools/local_privacy_guard.sh apply

privacy-local-status:
	bash tools/local_privacy_guard.sh status

privacy-local-off:
	bash tools/local_privacy_guard.sh clear

precommit-install:
	$(PYTHON) -m pip install pre-commit

precommit-run:
	$(PYTHON) -m pre_commit run --all-files

act-list:
	act -l

act-ci:
	act -W .github/workflows/ci.yml

k6-chat-smoke:
	k6 run tests/perf/chat_smoke.js -e BASE_URL="$(K6_BASE_URL)" -e VUS="$(K6_VUS)" -e DURATION="$(K6_DURATION)"

trivy-fs:
	trivy fs --severity "$(TRIVY_SEVERITY)" --exit-code 1 .

trivy-image:
	$(DOCKER) build -t $(DOCKER_IMAGE) . && trivy image --severity "$(TRIVY_SEVERITY)" --exit-code 1 $(DOCKER_IMAGE)

eval-retrieval:
	$(PYTHON) -m tools.eval_retrieval \
		--request-retries "$(RETRIEVAL_REQUEST_RETRIES)" \
		--request-retry-delay-ms "$(RETRIEVAL_REQUEST_RETRY_DELAY_MS)"

eval-retrieval-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_retrieval \
		--run-id $$RUN_ID \
		--request-retries "$(RETRIEVAL_REQUEST_RETRIES)" \
		--request-retry-delay-ms "$(RETRIEVAL_REQUEST_RETRY_DELAY_MS)" \
		--report-json "eval_reports/retrieval-$$RUN_ID.json"

eval-file-search:
	$(PYTHON) -m tools.eval_file_search

eval-file-search-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_file_search --run-id $$RUN_ID --report-json "eval_reports/file-search-$$RUN_ID.json"

eval-hallucination:
	$(PYTHON) -m tools.eval_hallucination --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-deterministic:
	$(PYTHON) -m tools.eval_hallucination --evaluation-mode deterministic --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-hallucination-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_hallucination --run-id $$RUN_ID --report-json "eval_reports/hallucination-$$RUN_ID.json" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

calibrate-hallucination-threshold:
	$(PYTHON) -m tools.calibrate_hallucination_threshold

eval-style:
	$(PYTHON) -m tools.eval_style --case-attempts "$(STYLE_CASE_ATTEMPTS)" --min-pass-attempts "$(STYLE_MIN_PASS_ATTEMPTS)"

eval-style-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_style --run-id $$RUN_ID --report-json "eval_reports/style-$$RUN_ID.json" --case-attempts "$(STYLE_CASE_ATTEMPTS)" --min-pass-attempts "$(STYLE_MIN_PASS_ATTEMPTS)"

eval-response-behaviour:
	$(PYTHON) -m tools.eval_response_behaviour

eval-response-behaviour-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_response_behaviour --run-id $$RUN_ID --report-json "eval_reports/response-behaviour-$$RUN_ID.json"

eval-ocr-safety:
	$(PYTHON) -m tools.eval_response_behaviour --suite-id ocr_safety --cases "$(OCR_SAFETY_CASES)" --session-prefix ocr-safety-eval

eval-ocr-safety-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_response_behaviour --suite-id ocr_safety --cases "$(OCR_SAFETY_CASES)" --session-prefix ocr-safety-eval --run-id $$RUN_ID --report-json "eval_reports/ocr-safety-$$RUN_ID.json"

eval-ocr:
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)" --run-id $$RUN_ID --report-json "eval_reports/ocr-$$RUN_ID.json"

eval-ocr-handwriting:
	@set -eu; \
	if [ ! -f "$(OCR_HANDWRITING_CASES)" ]; then \
		echo "Handwriting cases file not found: $(OCR_HANDWRITING_CASES)"; \
		echo "Create it with image_path entries (see docs/runtime/RUNBOOK.md)."; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_HANDWRITING_CASES)" --strict --show-text --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-handwriting-report:
	@set -eu; \
	if [ ! -f "$(OCR_HANDWRITING_CASES)" ]; then \
		echo "Handwriting cases file not found: $(OCR_HANDWRITING_CASES)"; \
		echo "Create it with image_path entries (see docs/runtime/RUNBOOK.md)."; \
		exit 1; \
	fi; \
	mkdir -p eval_reports; \
	RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_HANDWRITING_CASES)" --strict --show-text --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)" --run-id $$RUN_ID --report-json "eval_reports/ocr-handwriting-$$RUN_ID.json"

eval-ocr-recovery:
	$(PYTHON) -m tools.eval_ocr_recovery

eval-ocr-recovery-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_ocr_recovery --run-id $$RUN_ID --report-json "eval_reports/ocr-recovery-$$RUN_ID.json"

eval-clip-ab:
	$(PYTHON) -m tools.eval_clip_ab --source-types "$(CLIP_AB_SOURCE_TYPES)"

eval-clip-ab-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_clip_ab --source-types "$(CLIP_AB_SOURCE_TYPES)" --run-id $$RUN_ID --report-json "eval_reports/clip-ab-$$RUN_ID.json"

eval-clip-ab-readiness:
	$(PYTHON) -m tools.eval_clip_ab_readiness

backfill-eval-traces:
	$(PYTHON) -m tools.backfill_eval_trace_artifacts

api-smoke:
	@echo "Running API smoke (fresh local server + small endpoint calls)..."
	@set -eu; \
		BASE_URL="$(SMOKE_BASE_URL)"; \
		rm -f "$(SMOKE_HISTORY_DB)" "$(SMOKE_MEMORY_DB)" "$(SMOKE_VECTOR_DB)"; \
		POLINKO_HISTORY_DB_PATH="$(SMOKE_HISTORY_DB)" \
		POLINKO_MEMORY_DB_PATH="$(SMOKE_MEMORY_DB)" \
		POLINKO_VECTOR_DB_PATH="$(SMOKE_VECTOR_DB)" \
		POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK=true \
		$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port $(SMOKE_PORT) >/tmp/polinko-api-smoke.log 2>&1 & \
		SERVER_PID=$$!; \
		trap 'kill $$SERVER_PID 2>/dev/null || true' EXIT INT TERM; \
		READY=0; \
		for i in $$(seq 1 100); do \
			if curl -fsS "$$BASE_URL/health" >/dev/null 2>&1; then \
				READY=1; \
				break; \
			fi; \
			sleep 0.2; \
		done; \
		if [ "$$READY" -ne 1 ]; then \
			echo "Server failed to start. See /tmp/polinko-api-smoke.log"; \
			exit 1; \
		fi; \
		$(PYTHON) -m tools.api_smoke --base-url "$$BASE_URL"; \
		echo "API smoke passed."

eval-smoke:
	@echo "Running eval smoke (fresh local server + api smoke + response behaviour + retrieval + file search)..."
	@set -eu; \
		BASE_URL="$(SMOKE_BASE_URL)"; \
		rm -f "$(SMOKE_HISTORY_DB)" "$(SMOKE_MEMORY_DB)" "$(SMOKE_VECTOR_DB)"; \
		POLINKO_HISTORY_DB_PATH="$(SMOKE_HISTORY_DB)" \
		POLINKO_MEMORY_DB_PATH="$(SMOKE_MEMORY_DB)" \
		POLINKO_VECTOR_DB_PATH="$(SMOKE_VECTOR_DB)" \
		POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK=true \
		$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port $(SMOKE_PORT) >/tmp/polinko-eval-smoke.log 2>&1 & \
		SERVER_PID=$$!; \
		trap 'kill $$SERVER_PID 2>/dev/null || true' EXIT INT TERM; \
		READY=0; \
		for i in $$(seq 1 100); do \
			if curl -fsS "$$BASE_URL/health" >/dev/null 2>&1; then \
				READY=1; \
				break; \
			fi; \
			sleep 0.2; \
		done; \
		if [ "$$READY" -ne 1 ]; then \
			echo "Server failed to start. See /tmp/polinko-eval-smoke.log"; \
			exit 1; \
		fi; \
		$(PYTHON) -m tools.api_smoke --base-url "$$BASE_URL"; \
		$(PYTHON) -m tools.eval_response_behaviour --base-url "$$BASE_URL" --strict; \
		$(PYTHON) -m tools.eval_retrieval --base-url "$$BASE_URL" --request-retries "$(RETRIEVAL_REQUEST_RETRIES)" --request-retry-delay-ms "$(RETRIEVAL_REQUEST_RETRY_DELAY_MS)"; \
		$(PYTHON) -m tools.eval_file_search --base-url "$$BASE_URL"; \
		echo "Eval smoke passed."

eval-reports:
	@$(MAKE) eval-retrieval-report
	@$(MAKE) eval-file-search-report
	@$(MAKE) eval-ocr-report
	@$(MAKE) eval-style-report
	@$(MAKE) eval-response-behaviour-report
	@$(MAKE) eval-ocr-safety-report
	@$(MAKE) eval-hallucination-report

eval-reports-parallel:
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_parallel_orchestrator --base-url "$${BASE_URL:-http://127.0.0.1:8000}" --run-id $$RUN_ID --hallucination-mode "$(HALLUCINATION_EVAL_MODE)" --hallucination-min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

eval-sidecar-start:
	@set -eu; \
	if [ -f "$(EVAL_SIDECAR_PID_FILE)" ]; then \
		PID=$$(cat "$(EVAL_SIDECAR_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "eval-sidecar already running (PID $$PID)."; \
			exit 0; \
		fi; \
		rm -f "$(EVAL_SIDECAR_PID_FILE)"; \
	fi; \
	nohup $(PYTHON) -m tools.eval_sidecar run --target "$(EVAL_SIDECAR_TARGET)" --min-seconds "$(EVAL_SIDECAR_MIN_SECONDS)" --runs-dir "$(EVAL_SIDECAR_RUNS_DIR)" --pid-file "$(EVAL_SIDECAR_PID_FILE)" --current-file "$(EVAL_SIDECAR_CURRENT_FILE)" >"$(EVAL_SIDECAR_LOG)" 2>&1 & \
	PID=$$!; \
	sleep 0.2; \
	if kill -0 "$$PID" 2>/dev/null; then \
		echo "eval-sidecar started (PID $$PID, log: $(EVAL_SIDECAR_LOG))."; \
	else \
		echo "Failed to start eval-sidecar. Check $(EVAL_SIDECAR_LOG)."; \
		exit 1; \
	fi

eval-sidecar-status:
	$(PYTHON) -m tools.eval_sidecar status --current-file "$(EVAL_SIDECAR_CURRENT_FILE)" --pid-file "$(EVAL_SIDECAR_PID_FILE)"

eval-sidecar-stop:
	$(PYTHON) -m tools.eval_sidecar stop --current-file "$(EVAL_SIDECAR_CURRENT_FILE)" --pid-file "$(EVAL_SIDECAR_PID_FILE)"

operator-burden-report:
	$(PYTHON) -m tools.report_operator_burden_rows

hallucination-gate:
	@echo "Running hallucination gate..."
	@set -eu; \
	BASE_URL="$(GATE_BASE_URL)"; \
	rm -f "$(GATE_SESSION_DB)" "$(GATE_VECTOR_DB)"; \
	POLINKO_SESSION_DB_PATH="$(GATE_SESSION_DB)" \
	POLINKO_VECTOR_DB_PATH="$(GATE_VECTOR_DB)" \
	POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK=true \
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port $(GATE_PORT) >/tmp/polinko-hallucination-gate.log 2>&1 & \
	SERVER_PID=$$!; \
	trap 'kill $$SERVER_PID 2>/dev/null || true' EXIT INT TERM; \
	READY=0; \
	for i in $$(seq 1 100); do \
		if curl -fsS "$$BASE_URL/health" >/dev/null 2>&1; then \
			READY=1; \
			break; \
		fi; \
		sleep 0.2; \
	done; \
	if [ "$$READY" -ne 1 ]; then \
		echo "Server failed to start. See /tmp/polinko-hallucination-gate.log"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.eval_hallucination --base-url "$$BASE_URL" --strict --evaluation-mode "$(HALLUCINATION_EVAL_MODE)" --judge-model "$(HALLUCINATION_JUDGE_MODEL)" --judge-api-key-env "$(HALLUCINATION_JUDGE_API_KEY_ENV)" --judge-base-url "$(HALLUCINATION_JUDGE_BASE_URL)" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"; \
	echo "Hallucination gate passed."

quality-gate:
	@echo "Running quality gate (tests + retrieval eval + file-search eval + OCR eval + style eval + response-behaviour eval + hallucination eval)..."
	@set -eu; \
	BASE_URL="$(GATE_BASE_URL)"; \
	rm -f "$(GATE_SESSION_DB)" "$(GATE_VECTOR_DB)"; \
	POLINKO_SESSION_DB_PATH="$(GATE_SESSION_DB)" \
	POLINKO_VECTOR_DB_PATH="$(GATE_VECTOR_DB)" \
	POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK=true \
	$(PYTHON) -m uvicorn server:app --host 127.0.0.1 --port $(GATE_PORT) >/tmp/polinko-quality-gate.log 2>&1 & \
	SERVER_PID=$$!; \
	trap 'kill $$SERVER_PID 2>/dev/null || true' EXIT INT TERM; \
	READY=0; \
	for i in $$(seq 1 100); do \
		if curl -fsS "$$BASE_URL/health" >/dev/null 2>&1; then \
			READY=1; \
			break; \
		fi; \
		sleep 0.2; \
	done; \
	if [ "$$READY" -ne 1 ]; then \
		echo "Server failed to start. See /tmp/polinko-quality-gate.log"; \
		exit 1; \
	fi; \
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"; \
	$(PYTHON) -m tools.eval_retrieval --base-url "$$BASE_URL" --request-retries "$(RETRIEVAL_REQUEST_RETRIES)" --request-retry-delay-ms "$(RETRIEVAL_REQUEST_RETRY_DELAY_MS)"; \
	$(PYTHON) -m tools.eval_file_search --base-url "$$BASE_URL"; \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --base-url "$$BASE_URL" --strict --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"; \
	$(PYTHON) -m tools.eval_style --base-url "$$BASE_URL" --strict --case-attempts "$(STYLE_CASE_ATTEMPTS)" --min-pass-attempts "$(STYLE_MIN_PASS_ATTEMPTS)"; \
	$(PYTHON) -m tools.eval_response_behaviour --base-url "$$BASE_URL" --strict; \
	$(PYTHON) -m tools.eval_hallucination --base-url "$$BASE_URL" --strict --evaluation-mode "$(HALLUCINATION_EVAL_MODE)" --judge-model "$(HALLUCINATION_JUDGE_MODEL)" --judge-api-key-env "$(HALLUCINATION_JUDGE_API_KEY_ENV)" --judge-base-url "$(HALLUCINATION_JUDGE_BASE_URL)" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"; \
	echo "Quality gate passed."

quality-gate-deterministic:
	@$(MAKE) quality-gate HALLUCINATION_EVAL_MODE=deterministic STYLE_CASE_ATTEMPTS=3 STYLE_MIN_PASS_ATTEMPTS=2

cgpt-export-index:
	@set -eu; \
	EXPORT_ROOT="$(CGPT_EXPORT_ROOT)"; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		EXPORT_ROOT="$(CGPT_EXPORT_ROOT_DEFAULT)"; \
	fi; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		echo "CGPT_EXPORT_ROOT is required."; \
		echo "Run: make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 2; \
	fi; \
	if [ ! -d "$$EXPORT_ROOT" ]; then \
		echo "CGPT export root not found: $$EXPORT_ROOT"; \
		echo "Run: make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 2; \
	fi; \
	$(PYTHON) -m tools.index_cgpt_export --export-root "$$EXPORT_ROOT" --output-dir "$(CGPT_EXPORT_OUTPUT_DIR)"

ocr-cases-from-export:
	@set -eu; \
	EXPORT_ROOT="$(CGPT_EXPORT_ROOT)"; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		EXPORT_ROOT="$(CGPT_EXPORT_ROOT_DEFAULT)"; \
	fi; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		echo "CGPT_EXPORT_ROOT is required."; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 2; \
	fi; \
	if [ ! -d "$$EXPORT_ROOT" ]; then \
		echo "CGPT export root not found: $$EXPORT_ROOT"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 2; \
	fi; \
	if [ -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		cp "$(OCR_TRANSCRIPT_REVIEW)" "$(OCR_TRANSCRIPT_REVIEW_PREV)"; \
	fi; \
	$(PYTHON) -m tools.build_ocr_cases_from_export \
		--export-root "$$EXPORT_ROOT" \
		--output-cases "$(OCR_TRANSCRIPT_CASES_ALL)" \
		--output-cases-growth "$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		--output-cases-handwriting "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" \
		--output-cases-typed "$(OCR_TRANSCRIPT_CASES_TYPED)" \
		--output-cases-illustration "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" \
		--output-review "$(OCR_TRANSCRIPT_REVIEW)" \
		--max-growth-cases "$(OCR_GROWTH_MAX_CASES)" $(OCR_CASES_FROM_EXPORT_ARGS); \
			$(MAKE) --no-print-directory ocr-handwriting-benchmark-cases; \
			$(MAKE) --no-print-directory ocr-typed-benchmark-cases; \
			$(MAKE) --no-print-directory ocr-illustration-benchmark-cases; \
		$(MAKE) --no-print-directory ocr-transcript-delta

ocr-handwriting-benchmark-cases:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		echo "Transcript OCR review not found: $(OCR_TRANSCRIPT_REVIEW)"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" ]; then \
		echo "Transcript handwriting OCR cases not found: $(OCR_TRANSCRIPT_CASES_HANDWRITING)"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.build_handwriting_benchmark_cases \
		--review "$(OCR_TRANSCRIPT_REVIEW)" \
		--lane "handwriting" \
		--lane-cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" \
		--output-cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)" \
		--top-k "$(OCR_HANDWRITING_BENCHMARK_TOP_K)" \
		--min-anchor-terms "$(OCR_HANDWRITING_BENCHMARK_MIN_ANCHORS)"

ocr-typed-benchmark-cases:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		echo "Transcript OCR review not found: $(OCR_TRANSCRIPT_REVIEW)"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_TYPED)" ]; then \
		echo "Transcript typed OCR cases not found: $(OCR_TRANSCRIPT_CASES_TYPED)"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.build_handwriting_benchmark_cases \
		--review "$(OCR_TRANSCRIPT_REVIEW)" \
		--lane "typed" \
		--lane-cases "$(OCR_TRANSCRIPT_CASES_TYPED)" \
		--output-cases "$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)" \
		--top-k "$(OCR_TYPED_BENCHMARK_TOP_K)" \
		--min-anchor-terms "$(OCR_TYPED_BENCHMARK_MIN_ANCHORS)"

ocr-illustration-benchmark-cases:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		echo "Transcript OCR review not found: $(OCR_TRANSCRIPT_REVIEW)"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" ]; then \
		echo "Transcript illustration OCR cases not found: $(OCR_TRANSCRIPT_CASES_ILLUSTRATION)"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.build_handwriting_benchmark_cases \
		--review "$(OCR_TRANSCRIPT_REVIEW)" \
		--lane "illustration" \
		--lane-cases "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" \
		--output-cases "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)" \
		--top-k "$(OCR_ILLUSTRATION_BENCHMARK_TOP_K)" \
		--min-anchor-terms "$(OCR_ILLUSTRATION_BENCHMARK_MIN_ANCHORS)"

ocr-transcript-delta:
	@set -eu; \
	$(PYTHON) -m tools.report_ocr_case_mining_delta \
		--current-review "$(OCR_TRANSCRIPT_REVIEW)" \
		--previous-review "$(OCR_TRANSCRIPT_REVIEW_PREV)" \
		--output-markdown "$(OCR_TRANSCRIPT_DELTA_MD)" \
		--output-json "$(OCR_TRANSCRIPT_DELTA_JSON)"; \
	echo "OCR transcript delta report: $(OCR_TRANSCRIPT_DELTA_MD)"

eval-ocr-transcript-cases:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES)" ]; then \
		echo "Transcript OCR cases not found: $(OCR_TRANSCRIPT_CASES)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES)" --strict --show-text --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-transcript-cases-growth:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_GROWTH)" ]; then \
		echo "Transcript OCR growth cases not found: $(OCR_TRANSCRIPT_CASES_GROWTH)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_GROWTH)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript OCR growth cases available yet; skipping eval."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	PYTHONUNBUFFERED=1 $(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_GROWTH)" --show-text --offset "$(OCR_GROWTH_EVAL_OFFSET)" --max-cases "$(OCR_GROWTH_EVAL_MAX_CASES)" --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-transcript-cases-growth-batched:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_GROWTH)" ]; then \
		echo "Transcript OCR growth cases not found: $(OCR_TRANSCRIPT_CASES_GROWTH)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_GROWTH)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript OCR growth cases available yet; skipping eval."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	PYTHONUNBUFFERED=1 $(PYTHON) -m tools.eval_ocr_batched \
		--base-url "http://127.0.0.1:8000" \
		--cases "$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		--batch-size "$(OCR_GROWTH_BATCH_SIZE)" \
		--ocr-retries "$(OCR_GROWTH_OCR_RETRIES)" \
		--ocr-retry-delay-ms "$(OCR_GROWTH_OCR_RETRY_DELAY_MS)" \
		--offset "$(OCR_GROWTH_EVAL_OFFSET)" \
		--max-cases "$(OCR_GROWTH_EVAL_MAX_CASES)" \
		--report-dir "$(OCR_GROWTH_BATCH_REPORT_DIR)" \
		--output-json "$(OCR_GROWTH_BATCH_SUMMARY_JSON)" \
		--output-markdown "$(OCR_GROWTH_BATCH_SUMMARY_MD)"

eval-ocr-transcript-cases-handwriting:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" ]; then \
		echo "Transcript handwriting OCR cases not found: $(OCR_TRANSCRIPT_CASES_HANDWRITING)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_HANDWRITING)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript handwriting OCR cases available yet; skipping eval."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" --strict --show-text --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-transcript-cases-handwriting-benchmark:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)" ]; then \
		echo "Transcript handwriting benchmark OCR cases not found: $(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript handwriting benchmark OCR cases available yet; skipping eval."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)" --strict --show-text --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-transcript-cases-typed:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_TYPED)" ]; then \
		echo "Transcript typed OCR cases not found: $(OCR_TRANSCRIPT_CASES_TYPED)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_TYPED)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript typed OCR cases available yet; skipping eval."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_TYPED)" --strict --show-text --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-transcript-cases-typed-benchmark:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)" ]; then \
		echo "Transcript typed benchmark OCR cases not found: $(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript typed benchmark OCR cases available yet; skipping eval."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)" --strict --show-text --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-transcript-cases-illustration:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" ]; then \
		echo "Transcript illustration OCR cases not found: $(OCR_TRANSCRIPT_CASES_ILLUSTRATION)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript illustration OCR cases available yet; skipping eval."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" --strict --show-text --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-transcript-cases-illustration-benchmark:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)" ]; then \
		echo "Transcript illustration benchmark OCR cases not found: $(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript illustration benchmark OCR cases available yet; skipping eval."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	$(PYTHON) -m tools.eval_ocr --timeout "$(OCR_EVAL_TIMEOUT)" --cases "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)" --strict --show-text --ocr-retries "$(OCR_EVAL_OCR_RETRIES)" --ocr-retry-delay-ms "$(OCR_EVAL_OCR_RETRY_DELAY_MS)" --max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)"

eval-ocr-transcript-stability:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES)" ]; then \
		echo "Transcript OCR cases not found: $(OCR_TRANSCRIPT_CASES)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
		PYTHONUNBUFFERED=1 $(PYTHON) -m tools.eval_ocr_stability \
			--base-url "http://127.0.0.1:8000" \
			--cases "$(OCR_TRANSCRIPT_CASES)" \
			--runs "$(OCR_STABILITY_RUNS)" \
			--timeout "$(OCR_EVAL_TIMEOUT)" \
			--ocr-retries "$(OCR_STABILITY_OCR_RETRIES)" \
			--ocr-retry-delay-ms "$(OCR_STABILITY_OCR_RETRY_DELAY_MS)" \
			--case-delay-ms "$(OCR_STABILITY_CASE_DELAY_MS)" \
			--rate-limit-cooldown-ms "$(OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS)" \
			--max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)" \
			--stop-on-rate-limit-abort \
			--strict \
			--report-dir "$(OCR_STABILITY_REPORT_DIR)" \
			--output-json "$(OCR_STABILITY_OUTPUT)"

eval-ocr-transcript-growth:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_GROWTH)" ]; then \
		echo "Transcript OCR growth cases not found: $(OCR_TRANSCRIPT_CASES_GROWTH)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	if [ ! -d "$(OCR_GROWTH_STABILITY_REPORT_DIR)" ]; then \
		echo "OCR growth runs dir not found: $(OCR_GROWTH_STABILITY_REPORT_DIR)"; \
		echo "Run: make ocrstablegrowth"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.eval_ocr_growth_metrics \
		--cases "$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		--runs-dir "$(OCR_GROWTH_STABILITY_REPORT_DIR)" \
		--output-json "$(OCR_GROWTH_METRICS_OUTPUT)" \
		--output-markdown "$(OCR_GROWTH_METRICS_MARKDOWN)" \
		--limit-runs "$(OCR_GROWTH_LIMIT_RUNS)"

eval-ocr-growth-fail-cohort:
	@set -eu; \
	if [ ! -f "$(OCR_GROWTH_STABILITY_OUTPUT)" ]; then \
		echo "OCR growth stability report not found: $(OCR_GROWTH_STABILITY_OUTPUT)"; \
		echo "Run: make ocrstablegrowth"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_GROWTH)" ]; then \
		echo "Transcript OCR growth cases not found: $(OCR_TRANSCRIPT_CASES_GROWTH)"; \
		echo "Run: make ocrmine"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		echo "Transcript OCR review report not found: $(OCR_TRANSCRIPT_REVIEW)"; \
		echo "Run: make ocrmine"; \
		exit 1; \
	fi; \
	FAIL_COHORT_ARGS="--min-runs $(OCR_FAIL_COHORT_MIN_RUNS)"; \
	if [ "$(OCR_FAIL_COHORT_INCLUDE_UNSTABLE)" = "true" ]; then \
		FAIL_COHORT_ARGS="$$FAIL_COHORT_ARGS --include-unstable"; \
	fi; \
	if [ "$(OCR_FAIL_COHORT_REQUIRE_OCR_FRAMING)" = "true" ]; then \
		FAIL_COHORT_ARGS="$$FAIL_COHORT_ARGS --require-ocr-framing"; \
	fi; \
	if [ "$(OCR_FAIL_COHORT_INCLUDE_EXPLORATORY)" = "true" ]; then \
		FAIL_COHORT_ARGS="$$FAIL_COHORT_ARGS --include-exploratory"; \
	fi; \
	FAIL_COHORT_ARGS="$$FAIL_COHORT_ARGS --exploratory-max-cases $(OCR_FAIL_COHORT_EXPLORATORY_MAX_CASES)"; \
	$(PYTHON) -m tools.build_ocr_growth_fail_cohort \
		--stability-report "$(OCR_GROWTH_STABILITY_OUTPUT)" \
		--cases "$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		--metrics "$(OCR_GROWTH_METRICS_OUTPUT)" \
		--review "$(OCR_TRANSCRIPT_REVIEW)" \
		--output-json "$(OCR_GROWTH_FAIL_COHORT_JSON)" \
		--output-markdown "$(OCR_GROWTH_FAIL_COHORT_MARKDOWN)" \
		$$FAIL_COHORT_ARGS

eval-ocr-focus-cases:
	@set -eu; \
	if [ ! -f "$(OCR_GROWTH_FAIL_COHORT_JSON)" ]; then \
		echo "OCR growth fail cohort not found: $(OCR_GROWTH_FAIL_COHORT_JSON)"; \
		echo "Run: make ocrfails"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_GROWTH)" ]; then \
		echo "Transcript OCR growth cases not found: $(OCR_TRANSCRIPT_CASES_GROWTH)"; \
		echo "Run: make ocrmine"; \
		exit 1; \
	fi; \
	FOCUS_ARGS=""; \
	if [ "$(OCR_FOCUS_INCLUDE_FAIL_HISTORY)" = "false" ]; then \
		FOCUS_ARGS="--exclude-fail-history"; \
	fi; \
	if [ "$(OCR_FOCUS_INCLUDE_EXPLORATORY)" = "false" ]; then \
		FOCUS_ARGS="$$FOCUS_ARGS --exclude-exploratory"; \
	fi; \
	$(PYTHON) -m tools.build_ocr_focus_cases \
		--cohort "$(OCR_GROWTH_FAIL_COHORT_JSON)" \
		--source-cases "$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		--output-cases "$(OCR_FOCUS_CASES_JSON)" \
		--max-cases "$(OCR_FOCUS_MAX_CASES)" \
		$$FOCUS_ARGS

eval-ocr-focus-stability:
	@set -eu; \
	if [ ! -f "$(OCR_FOCUS_CASES_JSON)" ]; then \
		echo "OCR focus cases not found: $(OCR_FOCUS_CASES_JSON)"; \
		echo "Run: make ocrfocuscases"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_FOCUS_CASES_JSON)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No OCR focus cases available; skipping focus stability run."; \
		exit 0; \
	fi; \
	if [ "$(OCR_FOCUS_SKIP_RECENT_RATE_LIMIT)" = "true" ] && [ -f "$(OCR_FOCUS_OUTPUT)" ]; then \
		SKIP=$$($(PYTHON) -m tools.should_skip_ocr_run --report "$(OCR_FOCUS_OUTPUT)" --backoff-seconds "$(OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS)"); \
		if [ "$$SKIP" = "1" ]; then \
			echo "Skipping focus stability replay: recent rate-limit abort is still within backoff window ($(OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS)s)."; \
			exit 0; \
		fi; \
	fi; \
	if [ "$(OCR_FOCUS_SKIP_RECENT_RATE_LIMIT)" = "true" ] && [ -f "$(OCR_GROWTH_FAIL_COHORT_JSON)" ]; then \
		SKIP=$$($(PYTHON) -m tools.should_skip_ocr_run --report "$(OCR_GROWTH_FAIL_COHORT_JSON)" --backoff-seconds "$(OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS)"); \
		if [ "$$SKIP" = "1" ]; then \
			echo "Skipping focus stability replay: recent growth fail cohort shows active rate-limit pressure (backoff $(OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS)s)."; \
			exit 0; \
		fi; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
		$(PYTHON) -m tools.eval_ocr_stability \
			--base-url "http://127.0.0.1:8000" \
			--cases "$(OCR_FOCUS_CASES_JSON)" \
			--runs "$(OCR_FOCUS_RUNS)" \
			--timeout "$(OCR_EVAL_TIMEOUT)" \
			--ocr-retries "$(OCR_FOCUS_OCR_RETRIES)" \
			--ocr-retry-delay-ms "$(OCR_FOCUS_OCR_RETRY_DELAY_MS)" \
			--case-delay-ms "$(OCR_FOCUS_CASE_DELAY_MS)" \
			--rate-limit-cooldown-ms "$(OCR_FOCUS_RATE_LIMIT_COOLDOWN_MS)" \
			--max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)" \
			--stop-on-rate-limit-abort \
			--strict \
			--report-dir "$(OCR_FOCUS_REPORT_DIR)" \
			--output-json "$(OCR_FOCUS_OUTPUT)"

eval-ocr-focus-fail-patterns:
	@set -eu; \
	if [ ! -f "$(OCR_FOCUS_OUTPUT)" ]; then \
		echo "OCR focus stability report not found: $(OCR_FOCUS_OUTPUT)"; \
		echo "Run: make eval-ocr-focus-stability"; \
		exit 1; \
	fi; \
	if [ ! -f "$(OCR_FOCUS_CASES_JSON)" ]; then \
		echo "OCR focus cases not found: $(OCR_FOCUS_CASES_JSON)"; \
		echo "Run: make ocrfocuscases"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.report_ocr_focus_fail_patterns \
		--stability-report "$(OCR_FOCUS_OUTPUT)" \
		--focus-cases "$(OCR_FOCUS_CASES_JSON)" \
		--output-json "$(OCR_FOCUS_FAIL_PATTERNS_JSON)" \
		--output-markdown "$(OCR_FOCUS_FAIL_PATTERNS_MD)"

eval-ocr-transcript-stability-growth:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_GROWTH)" ]; then \
		echo "Transcript OCR growth cases not found: $(OCR_TRANSCRIPT_CASES_GROWTH)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_GROWTH)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript OCR growth cases available yet; skipping stability run."; \
		exit 0; \
	fi; \
	OUTPUT_JSON="$(OCR_GROWTH_STABILITY_OUTPUT)"; \
	if [ "$(OCR_GROWTH_EVAL_OFFSET)" -gt 0 ] || [ "$(OCR_GROWTH_EVAL_MAX_CASES)" -gt 0 ]; then \
		OUTPUT_JSON=".local/eval_reports/ocr_growth_stability.slice-offset$(OCR_GROWTH_EVAL_OFFSET)-max$(OCR_GROWTH_EVAL_MAX_CASES).json"; \
		echo "Using sliced growth stability output: $$OUTPUT_JSON"; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
			PYTHONUNBUFFERED=1 $(PYTHON) -m tools.eval_ocr_stability \
				--base-url "http://127.0.0.1:8000" \
				--cases "$(OCR_TRANSCRIPT_CASES_GROWTH)" \
				--runs "$(OCR_GROWTH_STABILITY_RUNS)" \
				--offset "$(OCR_GROWTH_EVAL_OFFSET)" \
				--max-cases "$(OCR_GROWTH_EVAL_MAX_CASES)" \
			--timeout "$(OCR_EVAL_TIMEOUT)" \
			--ocr-retries "$(OCR_GROWTH_OCR_RETRIES)" \
			--ocr-retry-delay-ms "$(OCR_GROWTH_OCR_RETRY_DELAY_MS)" \
			--case-delay-ms "$(OCR_GROWTH_CASE_DELAY_MS)" \
			--rate-limit-cooldown-ms "$(OCR_GROWTH_RATE_LIMIT_COOLDOWN_MS)" \
			--max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)" \
			--stop-on-rate-limit-abort \
			--report-dir "$(OCR_GROWTH_STABILITY_REPORT_DIR)" \
			--output-json "$$OUTPUT_JSON"

eval-ocr-transcript-stability-handwriting-benchmark:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)" ]; then \
		echo "Transcript handwriting benchmark OCR cases not found: $(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript handwriting benchmark OCR cases available yet; skipping stability run."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
			$(PYTHON) -m tools.eval_ocr_stability \
				--base-url "http://127.0.0.1:8000" \
				--cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)" \
				--runs "$(OCR_STABILITY_RUNS)" \
				--timeout "$(OCR_EVAL_TIMEOUT)" \
				--ocr-retries "$(OCR_STABILITY_OCR_RETRIES)" \
				--ocr-retry-delay-ms "$(OCR_STABILITY_OCR_RETRY_DELAY_MS)" \
				--case-delay-ms "$(OCR_STABILITY_CASE_DELAY_MS)" \
				--rate-limit-cooldown-ms "$(OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS)" \
				--max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)" \
				--stop-on-rate-limit-abort \
				--strict \
				--report-dir "$(OCR_STABILITY_HANDWRITING_BENCHMARK_REPORT_DIR)" \
				--output-json "$(OCR_STABILITY_HANDWRITING_BENCHMARK_OUTPUT)"

eval-ocr-transcript-stability-typed-benchmark:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)" ]; then \
		echo "Transcript typed benchmark OCR cases not found: $(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript typed benchmark OCR cases available yet; skipping stability run."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
			$(PYTHON) -m tools.eval_ocr_stability \
				--base-url "http://127.0.0.1:8000" \
				--cases "$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)" \
				--runs "$(OCR_STABILITY_RUNS)" \
				--timeout "$(OCR_EVAL_TIMEOUT)" \
				--ocr-retries "$(OCR_STABILITY_OCR_RETRIES)" \
				--ocr-retry-delay-ms "$(OCR_STABILITY_OCR_RETRY_DELAY_MS)" \
				--case-delay-ms "$(OCR_STABILITY_CASE_DELAY_MS)" \
				--rate-limit-cooldown-ms "$(OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS)" \
				--max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)" \
				--stop-on-rate-limit-abort \
				--strict \
				--report-dir "$(OCR_STABILITY_TYPED_BENCHMARK_REPORT_DIR)" \
				--output-json "$(OCR_STABILITY_TYPED_BENCHMARK_OUTPUT)"

eval-ocr-transcript-stability-illustration-benchmark:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)" ]; then \
		echo "Transcript illustration benchmark OCR cases not found: $(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	CASE_COUNT=$$($(PYTHON) -c 'import json,pathlib; p=pathlib.Path("$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)"); d=json.loads(p.read_text()); print(len(d.get("cases", [])))'); \
	if [ "$$CASE_COUNT" -eq 0 ]; then \
		echo "No transcript illustration benchmark OCR cases available yet; skipping stability run."; \
		exit 0; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
			$(PYTHON) -m tools.eval_ocr_stability \
				--base-url "http://127.0.0.1:8000" \
				--cases "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)" \
				--runs "$(OCR_STABILITY_RUNS)" \
				--timeout "$(OCR_EVAL_TIMEOUT)" \
				--ocr-retries "$(OCR_STABILITY_OCR_RETRIES)" \
				--ocr-retry-delay-ms "$(OCR_STABILITY_OCR_RETRY_DELAY_MS)" \
				--case-delay-ms "$(OCR_STABILITY_CASE_DELAY_MS)" \
				--rate-limit-cooldown-ms "$(OCR_STABILITY_RATE_LIMIT_COOLDOWN_MS)" \
				--max-consecutive-rate-limit-errors "$(OCR_MAX_CONSEC_RATE_LIMIT_ERRORS)" \
				--stop-on-rate-limit-abort \
				--strict \
				--report-dir "$(OCR_STABILITY_ILLUSTRATION_BENCHMARK_REPORT_DIR)" \
				--output-json "$(OCR_STABILITY_ILLUSTRATION_BENCHMARK_OUTPUT)"

docker-build:
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run:
	$(DOCKER) run --rm -p $(DOCKER_PORT):8000 --env-file $(ENV_FILE) $(DOCKER_IMAGE)
