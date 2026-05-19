# Evaluation aliases and benchmark runners.
.PHONY: ocrindex ocrmine ocrminehand ocrminetype ocrmineillu ocrminehigh ocrminelow ocrminebacklog
.PHONY: ocrall ocrwiden ocrwidensync ocrwidenbatch ocrwidenall ocrhand ocrtype ocrillu
.PHONY: ocrstable ocrstablegrowth ocrgrowth ocrfails ocrfocus ocrfocuscases ocrfocusreport ocrkernel
.PHONY: ocrhandbench ocrtypebench ocrillubench ocrstablehand ocrstabletype ocrstableillu ocrdelta
.PHONY: nulls runtime-null-audit ocr-data ocr-notebook-workflow ocr-generalization-review
.PHONY: api-smoke eval-smoke eval-retrieval eval-retrieval-report eval-file-search eval-file-search-report
.PHONY: eval-hallucination eval-hallucination-deterministic eval-hallucination-report
.PHONY: eval-style eval-style-report eval-response-behaviour eval-response-behaviour-report
.PHONY: eval-ocr-safety eval-ocr-safety-report eval-ocr eval-ocr-report
.PHONY: eval-ocr-handwriting eval-ocr-handwriting-report eval-ocr-recovery eval-ocr-recovery-report
.PHONY: eval-clip-ab eval-clip-ab-report eval-clip-ab-readiness eval-reports eval-reports-parallel
.PHONY: eval-sidecar-start eval-sidecar-status eval-sidecar-stop operator-burden-report
.PHONY: calibrate-hallucination-threshold backfill-eval-traces hallucination-gate
.PHONY: quality-gate quality-gate-deterministic cgpt-export-index ocr-cases-from-export
.PHONY: ocr-handwriting-benchmark-cases ocr-typed-benchmark-cases ocr-illustration-benchmark-cases
.PHONY: ocr-transcript-delta eval-ocr-transcript-cases eval-ocr-transcript-cases-growth
.PHONY: eval-ocr-transcript-cases-growth-batched eval-ocr-growth-fail-cohort
.PHONY: eval-ocr-focus-cases eval-ocr-focus-stability eval-ocr-focus-fail-patterns
.PHONY: eval-ocr-transcript-cases-handwriting eval-ocr-transcript-cases-handwriting-benchmark
.PHONY: eval-ocr-transcript-cases-typed eval-ocr-transcript-cases-typed-benchmark
.PHONY: eval-ocr-transcript-cases-illustration eval-ocr-transcript-cases-illustration-benchmark
.PHONY: eval-ocr-transcript-stability eval-ocr-transcript-stability-growth eval-ocr-transcript-growth
.PHONY: eval-ocr-transcript-stability-handwriting-benchmark
.PHONY: eval-ocr-transcript-stability-typed-benchmark
.PHONY: eval-ocr-transcript-stability-illustration-benchmark

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
	$(MAKE) --no-print-directory ocr-generalization-review; \
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
		$(PYTHON) -m uvicorn $(ASGI_APP) --host 127.0.0.1 --port $(SMOKE_PORT) >/tmp/polinko-api-smoke.log 2>&1 & \
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
		$(PYTHON) -m uvicorn $(ASGI_APP) --host 127.0.0.1 --port $(SMOKE_PORT) >/tmp/polinko-eval-smoke.log 2>&1 & \
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
	$(PYTHON) -m uvicorn $(ASGI_APP) --host 127.0.0.1 --port $(GATE_PORT) >/tmp/polinko-hallucination-gate.log 2>&1 & \
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
	$(PYTHON) -m uvicorn $(ASGI_APP) --host 127.0.0.1 --port $(GATE_PORT) >/tmp/polinko-quality-gate.log 2>&1 & \
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
		--output-generalization-candidates "$(OCR_GENERALIZATION_CANDIDATES)" \
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

ocr-generalization-review:
	@set -eu; \
	if [ ! -f "$(OCR_GENERALIZATION_CANDIDATES)" ]; then \
		echo "OCR generalization candidates not found: $(OCR_GENERALIZATION_CANDIDATES)"; \
		echo "Run: make ocrmine CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"; \
		exit 1; \
	fi; \
	$(PYTHON) -m tools.build_ocr_generalization_review \
		--candidates "$(OCR_GENERALIZATION_CANDIDATES)" \
		--output-review "$(OCR_GENERALIZATION_REVIEW)" \
		--max-cases "$(OCR_GENERALIZATION_REVIEW_MAX_CASES)" \
		--max-per-conversation "$(OCR_GENERALIZATION_REVIEW_MAX_PER_CONVERSATION)" \
		--include-candidate-ids "$(OCR_GENERALIZATION_REVIEW_INCLUDE_IDS)"

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
