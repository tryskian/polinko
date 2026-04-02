PYTHON ?= $(shell \
	if [ -x ./polinko-repositioning-system/bin/python ] && ./polinko-repositioning-system/bin/python -V >/dev/null 2>&1; then \
		echo ./polinko-repositioning-system/bin/python; \
	elif [ -x ./venv/bin/python ] && ./venv/bin/python -V >/dev/null 2>&1; then \
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
ENV_FILE ?= .env
K6_BASE_URL ?= http://127.0.0.1:8000
K6_VUS ?= 3
K6_DURATION ?= 10s
TRIVY_SEVERITY ?= HIGH,CRITICAL
GATE_PORT ?= 8066
GATE_BASE_URL ?= http://127.0.0.1:$(GATE_PORT)
GATE_SESSION_DB ?= /tmp/polinko-quality-gate-sessions.db
GATE_VECTOR_DB ?= /tmp/polinko-quality-gate-vector.db
HALLUCINATION_EVAL_MODE ?= judge
HALLUCINATION_JUDGE_MODEL ?= gpt-4.1-mini
HALLUCINATION_JUDGE_API_KEY_ENV ?= OPENAI_API_KEY
BRAINTRUST_OPENAI_BASE_URL ?=
HALLUCINATION_JUDGE_BASE_URL ?=
HALLUCINATION_MIN_ACCEPTABLE_SCORE ?= 5
STYLE_CASE_ATTEMPTS ?= 1
STYLE_MIN_PASS_ATTEMPTS ?= 1
RETRIEVAL_REQUEST_RETRIES ?= 2
RETRIEVAL_REQUEST_RETRY_DELAY_MS ?= 750
CLIP_AB_SOURCE_TYPES ?= image
OCR_HANDWRITING_CASES ?= .local/eval_cases/ocr_handwriting_eval_cases.json
CGPT_EXPORT_ROOT ?=
CGPT_EXPORT_ROOT_DEFAULT ?= /Users/tryskian/Library/CloudStorage/Dropbox/CGPT-DATA-EXPORT
CGPT_EXPORT_OUTPUT_DIR ?= .local/eval_cases
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
OCR_STABILITY_OUTPUT ?= .local/eval_reports/ocr_transcript_stability.json
OCR_STABILITY_REPORT_DIR ?= .local/eval_reports/ocr_stability_runs
OCR_GROWTH_MAX_CASES ?= 600
OCR_GROWTH_STABILITY_OUTPUT ?= .local/eval_reports/ocr_growth_stability.json
OCR_GROWTH_STABILITY_REPORT_DIR ?= .local/eval_reports/ocr_growth_stability_runs
OCR_GROWTH_METRICS_OUTPUT ?= .local/eval_reports/ocr_growth_metrics.json
OCR_GROWTH_METRICS_MARKDOWN ?= .local/eval_reports/ocr_growth_metrics.md
OCR_GROWTH_FAIL_COHORT_JSON ?= .local/eval_cases/ocr_growth_fail_cohort.json
OCR_GROWTH_FAIL_COHORT_MARKDOWN ?= .local/eval_reports/ocr_growth_fail_cohort.md
OCR_GROWTH_LIMIT_RUNS ?= 0
OCR_GROWTH_EVAL_OFFSET ?= 0
OCR_GROWTH_EVAL_MAX_CASES ?= 0
OCR_GROWTH_BATCH_SIZE ?= 40
OCR_GROWTH_OCR_RETRIES ?= 2
OCR_GROWTH_OCR_RETRY_DELAY_MS ?= 750
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

.PHONY: chat venv env notebook-setup notebook nb notes ocrindex ocrmine ocrall ocrwiden ocrwidenbatch ocrwidenall ocrhand ocrtype ocrillu ocrstable ocrstablegrowth ocrgrowth ocrfails ocrhandbench ocrtypebench ocrillubench ocrstablehand ocrstabletype ocrstableillu ocrdelta ocr-data ocr-notebook-workflow gate eod localhost server server-daemon server-daemon-stop server-daemon-status docs open-api-docs session-status test lint-docs transcript-fix transcript-check doctor-env backend-gate caffeinate-on caffeinate-off caffeinate-status decaffeinate privacy-local-on privacy-local-status privacy-local-off precommit-install precommit-run act-list act-ci k6-chat-smoke trivy-fs trivy-image eval-retrieval eval-retrieval-report eval-file-search eval-file-search-report eval-hallucination eval-hallucination-deterministic eval-hallucination-braintrust eval-hallucination-report eval-style eval-style-report eval-ocr eval-ocr-report eval-ocr-handwriting eval-ocr-handwriting-report eval-ocr-recovery eval-ocr-recovery-report eval-clip-ab eval-clip-ab-report eval-clip-ab-readiness eval-cleanup eval-reports eval-reports-parallel calibrate-hallucination-threshold backfill-eval-traces hallucination-gate quality-gate quality-gate-deterministic evidence-index evidence-refresh portfolio-metadata-audit cgpt-export-index ocr-cases-from-export ocr-handwriting-benchmark-cases ocr-typed-benchmark-cases ocr-illustration-benchmark-cases ocr-transcript-delta eval-ocr-transcript-cases eval-ocr-transcript-cases-growth eval-ocr-transcript-cases-growth-batched eval-ocr-growth-fail-cohort eval-ocr-transcript-cases-handwriting eval-ocr-transcript-cases-handwriting-benchmark eval-ocr-transcript-cases-typed eval-ocr-transcript-cases-typed-benchmark eval-ocr-transcript-cases-illustration eval-ocr-transcript-cases-illustration-benchmark eval-ocr-transcript-stability eval-ocr-transcript-stability-growth eval-ocr-transcript-growth eval-ocr-transcript-stability-handwriting-benchmark eval-ocr-transcript-stability-typed-benchmark eval-ocr-transcript-stability-illustration-benchmark docker-build docker-run

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

notebook-setup:
	$(PYTHON) -m pip install -r requirements.notebook.txt

notebook nb notes:
	@if [ -f "$(NOTEBOOK_START_PATH_ABS)" ]; then \
		$(PYTHON) -m jupyter lab --notebook-dir="$(NOTEBOOK_DIR_ABS)" "$(NOTEBOOK_START_PATH_ABS)"; \
	else \
		$(PYTHON) -m jupyter lab --notebook-dir="$(NOTEBOOK_DIR_ABS)" "$(NOTEBOOK_DIR_ABS)"; \
	fi

# Short aliases for frequent long-chain commands.
ocrindex: cgpt-export-index

ocrmine: ocr-cases-from-export

ocrall: eval-ocr-transcript-cases

ocrwiden: eval-ocr-transcript-cases-growth

ocrwidenbatch: eval-ocr-transcript-cases-growth

ocrwidenall: eval-ocr-transcript-cases-growth-batched

ocrhand: eval-ocr-transcript-cases-handwriting

ocrtype: eval-ocr-transcript-cases-typed

ocrillu: eval-ocr-transcript-cases-illustration

ocrstable: eval-ocr-transcript-stability

ocrstablegrowth: eval-ocr-transcript-stability-growth

ocrgrowth: eval-ocr-transcript-growth

ocrfails: eval-ocr-growth-fail-cohort

ocrhandbench: eval-ocr-transcript-cases-handwriting-benchmark

ocrtypebench: eval-ocr-transcript-cases-typed-benchmark

ocrillubench: eval-ocr-transcript-cases-illustration-benchmark

ocrstablehand: eval-ocr-transcript-stability-handwriting-benchmark

ocrstabletype: eval-ocr-transcript-stability-typed-benchmark

ocrstableillu: eval-ocr-transcript-stability-illustration-benchmark

ocrdelta: ocr-transcript-delta

ocr-data:
	@set -eu; \
	EXPORT_ROOT="$(CGPT_EXPORT_ROOT)"; \
	if [ -z "$$EXPORT_ROOT" ]; then \
		EXPORT_ROOT="$(CGPT_EXPORT_ROOT_DEFAULT)"; \
	fi; \
	if [ ! -d "$$EXPORT_ROOT" ]; then \
		echo "CGPT export root not found: $$EXPORT_ROOT"; \
		echo "Run: make ocr-data CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 1; \
	fi; \
	$(MAKE) --no-print-directory ocr-notebook-workflow CGPT_EXPORT_ROOT="$$EXPORT_ROOT"

ocr-notebook-workflow:
	@set -eu; \
	if [ -z "$(CGPT_EXPORT_ROOT)" ]; then \
		echo "CGPT_EXPORT_ROOT is required."; \
		echo "Example: make ocr-notebook-workflow CGPT_EXPORT_ROOT=/Users/tryskian/Library/CloudStorage/Dropbox/CGPT-DATA-EXPORT"; \
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

session-status:
	@echo "== Server =="
	@$(MAKE) --no-print-directory server-daemon-status || true
	@echo ""
	@echo "== Keep-awake =="
	@$(MAKE) --no-print-directory caffeinate-status || true

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

lint-docs:
	npm run lint:docs

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

eval-hallucination-braintrust:
	@set -eu; \
	BASE_URL="$(HALLUCINATION_JUDGE_BASE_URL)"; \
	if [ -z "$$BASE_URL" ]; then \
		BASE_URL="$(BRAINTRUST_OPENAI_BASE_URL)"; \
	fi; \
	if [ -z "$$BASE_URL" ]; then \
		echo "Missing Braintrust base URL."; \
		echo "Set BRAINTRUST_OPENAI_BASE_URL (recommended: https://api.braintrust.dev/v1/proxy)"; \
		echo "or pass HALLUCINATION_JUDGE_BASE_URL explicitly."; \
		exit 2; \
	fi; \
	if [ -z "$${BRAINTRUST_API_KEY:-}" ]; then \
		echo "Missing BRAINTRUST_API_KEY in environment."; \
		exit 2; \
	fi; \
	$(PYTHON) -m tools.eval_hallucination --evaluation-mode judge --judge-api-key-env BRAINTRUST_API_KEY --judge-base-url "$$BASE_URL" --judge-model "$(HALLUCINATION_JUDGE_MODEL)" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

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

eval-ocr:
	$(PYTHON) -m tools.eval_ocr

eval-ocr-report:
	@mkdir -p eval_reports
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_ocr --run-id $$RUN_ID --report-json "eval_reports/ocr-$$RUN_ID.json"

eval-ocr-handwriting:
	@set -eu; \
	if [ ! -f "$(OCR_HANDWRITING_CASES)" ]; then \
		echo "Handwriting cases file not found: $(OCR_HANDWRITING_CASES)"; \
		echo "Create it with image_path entries (see docs/runtime/RUNBOOK.md)."; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.eval_ocr --cases "$(OCR_HANDWRITING_CASES)" --strict --show-text

eval-ocr-handwriting-report:
	@set -eu; \
	if [ ! -f "$(OCR_HANDWRITING_CASES)" ]; then \
		echo "Handwriting cases file not found: $(OCR_HANDWRITING_CASES)"; \
		echo "Create it with image_path entries (see docs/runtime/RUNBOOK.md)."; \
		exit 1; \
	fi; \
	mkdir -p eval_reports; \
	RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_ocr --cases "$(OCR_HANDWRITING_CASES)" --strict --show-text --run-id $$RUN_ID --report-json "eval_reports/ocr-handwriting-$$RUN_ID.json"

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

eval-cleanup:
	@set -eu; \
	if [ ! -f "tools/cleanup_eval_chats.py" ]; then \
		echo "tools/cleanup_eval_chats.py is local-only and not tracked in this repo."; \
		echo "Skipping eval cleanup."; \
		exit 0; \
	fi; \
	$(PYTHON) -m tools.cleanup_eval_chats

eval-reports:
	@$(MAKE) eval-retrieval-report
	@$(MAKE) eval-file-search-report
	@$(MAKE) eval-ocr-report
	@$(MAKE) eval-style-report
	@$(MAKE) eval-hallucination-report

eval-reports-parallel:
	@RUN_ID=$$(date +%Y%m%d-%H%M%S); \
	$(PYTHON) -m tools.eval_parallel_orchestrator --base-url "$${BASE_URL:-http://127.0.0.1:8000}" --run-id $$RUN_ID --hallucination-mode "$(HALLUCINATION_EVAL_MODE)" --hallucination-min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"

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
	@echo "Running quality gate (tests + retrieval eval + file-search eval + OCR eval + style eval + hallucination eval)..."
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
	$(PYTHON) -m tools.eval_ocr --base-url "$$BASE_URL" --strict; \
	$(PYTHON) -m tools.eval_style --base-url "$$BASE_URL" --strict --case-attempts "$(STYLE_CASE_ATTEMPTS)" --min-pass-attempts "$(STYLE_MIN_PASS_ATTEMPTS)"; \
	$(PYTHON) -m tools.eval_hallucination --base-url "$$BASE_URL" --strict --evaluation-mode "$(HALLUCINATION_EVAL_MODE)" --judge-model "$(HALLUCINATION_JUDGE_MODEL)" --judge-api-key-env "$(HALLUCINATION_JUDGE_API_KEY_ENV)" --judge-base-url "$(HALLUCINATION_JUDGE_BASE_URL)" --min-acceptable-score "$(HALLUCINATION_MIN_ACCEPTABLE_SCORE)"; \
	echo "Quality gate passed."

quality-gate-deterministic:
	@$(MAKE) quality-gate HALLUCINATION_EVAL_MODE=deterministic STYLE_CASE_ATTEMPTS=3 STYLE_MIN_PASS_ATTEMPTS=2

evidence-index:
	$(PYTHON) -m tools.build_evidence_index

evidence-refresh:
	@set -eu; \
	$(MAKE) evidence-index; \
	INDEX_JSON="docs/portfolio/raw_evidence/index.json"; \
	if [ -f "$$INDEX_JSON" ]; then \
		if command -v rg >/dev/null 2>&1; then \
			TOTAL=$$(rg -o '"evidence_id"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
			OPEN=$$(rg -o '"status": "OPEN"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
			CLOSED=$$(rg -o '"status": "CLOSED"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
		else \
			TOTAL=$$(grep -o '"evidence_id"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
			OPEN=$$(grep -o '"status": "OPEN"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
			CLOSED=$$(grep -o '"status": "CLOSED"' "$$INDEX_JSON" | wc -l | tr -d ' '); \
		fi; \
		echo "Evidence refresh summary: total=$$TOTAL open=$$OPEN closed=$$CLOSED"; \
	fi

portfolio-metadata-audit:
	$(PYTHON) -m tools.audit_portfolio_metadata --strict

cgpt-export-index:
	@set -eu; \
	if [ -z "$(CGPT_EXPORT_ROOT)" ]; then \
		echo "Set CGPT_EXPORT_ROOT to your export root path."; \
		echo "Example: make cgpt-export-index CGPT_EXPORT_ROOT=/Users/tryskian/Library/CloudStorage/Dropbox/CGPT-DATA-EXPORT"; \
		exit 2; \
	fi; \
	$(PYTHON) -m tools.index_cgpt_export --export-root "$(CGPT_EXPORT_ROOT)" --output-dir "$(CGPT_EXPORT_OUTPUT_DIR)"

ocr-cases-from-export:
	@set -eu; \
	if [ -z "$(CGPT_EXPORT_ROOT)" ]; then \
		echo "Set CGPT_EXPORT_ROOT to your export root path."; \
		echo "Example: make ocr-cases-from-export CGPT_EXPORT_ROOT=/Users/tryskian/Library/CloudStorage/Dropbox/CGPT-DATA-EXPORT"; \
		exit 2; \
	fi; \
	if [ -f "$(OCR_TRANSCRIPT_REVIEW)" ]; then \
		cp "$(OCR_TRANSCRIPT_REVIEW)" "$(OCR_TRANSCRIPT_REVIEW_PREV)"; \
	fi; \
	$(PYTHON) -m tools.build_ocr_cases_from_export \
		--export-root "$(CGPT_EXPORT_ROOT)" \
		--output-cases "$(OCR_TRANSCRIPT_CASES_ALL)" \
		--output-cases-growth "$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		--output-cases-handwriting "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" \
		--output-cases-typed "$(OCR_TRANSCRIPT_CASES_TYPED)" \
		--output-cases-illustration "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" \
		--output-review "$(OCR_TRANSCRIPT_REVIEW)" \
		--max-growth-cases "$(OCR_GROWTH_MAX_CASES)"; \
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
	$(PYTHON) -m tools.eval_ocr --cases "$(OCR_TRANSCRIPT_CASES)" --strict --show-text

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
	$(PYTHON) -m tools.eval_ocr --cases "$(OCR_TRANSCRIPT_CASES_GROWTH)" --show-text --offset "$(OCR_GROWTH_EVAL_OFFSET)" --max-cases "$(OCR_GROWTH_EVAL_MAX_CASES)"

eval-ocr-transcript-cases-growth-batched:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES_GROWTH)" ]; then \
		echo "Transcript OCR growth cases not found: $(OCR_TRANSCRIPT_CASES_GROWTH)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	$(PYTHON) -m tools.eval_ocr_batched \
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
	$(PYTHON) -m tools.eval_ocr --cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING)" --strict --show-text

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
	$(PYTHON) -m tools.eval_ocr --cases "$(OCR_TRANSCRIPT_CASES_HANDWRITING_BENCHMARK)" --strict --show-text

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
	$(PYTHON) -m tools.eval_ocr --cases "$(OCR_TRANSCRIPT_CASES_TYPED)" --strict --show-text

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
	$(PYTHON) -m tools.eval_ocr --cases "$(OCR_TRANSCRIPT_CASES_TYPED_BENCHMARK)" --strict --show-text

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
	$(PYTHON) -m tools.eval_ocr --cases "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION)" --strict --show-text

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
	$(PYTHON) -m tools.eval_ocr --cases "$(OCR_TRANSCRIPT_CASES_ILLUSTRATION_BENCHMARK)" --strict --show-text

eval-ocr-transcript-stability:
	@set -eu; \
	if [ ! -f "$(OCR_TRANSCRIPT_CASES)" ]; then \
		echo "Transcript OCR cases not found: $(OCR_TRANSCRIPT_CASES)"; \
		echo "Run: make ocr-cases-from-export CGPT_EXPORT_ROOT=/path/to/export"; \
		exit 1; \
	fi; \
	$(MAKE) --no-print-directory server-daemon; \
	$(PYTHON) -m tools.eval_ocr_stability \
		--base-url "http://127.0.0.1:8000" \
		--cases "$(OCR_TRANSCRIPT_CASES)" \
		--runs "$(OCR_STABILITY_RUNS)" \
		--ocr-retries "$(OCR_STABILITY_OCR_RETRIES)" \
		--ocr-retry-delay-ms "$(OCR_STABILITY_OCR_RETRY_DELAY_MS)" \
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
	$(PYTHON) -m tools.build_ocr_growth_fail_cohort \
		--stability-report "$(OCR_GROWTH_STABILITY_OUTPUT)" \
		--cases "$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		--metrics "$(OCR_GROWTH_METRICS_OUTPUT)" \
		--output-json "$(OCR_GROWTH_FAIL_COHORT_JSON)" \
		--output-markdown "$(OCR_GROWTH_FAIL_COHORT_MARKDOWN)" \
		--min-runs "$(OCR_STABILITY_RUNS)"

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
	$(PYTHON) -m tools.eval_ocr_stability \
		--base-url "http://127.0.0.1:8000" \
		--cases "$(OCR_TRANSCRIPT_CASES_GROWTH)" \
		--runs "$(OCR_STABILITY_RUNS)" \
		--offset "$(OCR_GROWTH_EVAL_OFFSET)" \
		--max-cases "$(OCR_GROWTH_EVAL_MAX_CASES)" \
		--ocr-retries "$(OCR_GROWTH_OCR_RETRIES)" \
		--ocr-retry-delay-ms "$(OCR_GROWTH_OCR_RETRY_DELAY_MS)" \
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
		--strict \
		--report-dir "$(OCR_STABILITY_ILLUSTRATION_BENCHMARK_REPORT_DIR)" \
		--output-json "$(OCR_STABILITY_ILLUSTRATION_BENCHMARK_OUTPUT)"

docker-build:
	$(DOCKER) build -t $(DOCKER_IMAGE) .

docker-run:
	$(DOCKER) run --rm -p $(DOCKER_PORT):8000 --env-file $(ENV_FILE) $(DOCKER_IMAGE)
