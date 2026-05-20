#!/usr/bin/env sh
set -eu

if [ "$#" -ne 1 ]; then
	echo "Usage: run_local_eval_gate.sh <suite>" >&2
	exit 2
fi

suite=$1
python_bin=${PYTHON:-python3}
asgi_app=${ASGI_APP:-server:app}

case "$suite" in
api-smoke|eval-smoke|hallucination-gate|quality-gate)
	;;
*)
	echo "Unknown local eval gate suite: $suite" >&2
	exit 2
	;;
esac

server_pid=

cleanup_server() {
	if [ -n "$server_pid" ]; then
		kill "$server_pid" 2>/dev/null || true
		wait "$server_pid" 2>/dev/null || true
	fi
}

trap cleanup_server EXIT INT TERM

start_local_server() {
	scope=$1
	base_url=$2
	port=$3
	log_path=$4

	case "$scope" in
	smoke)
		rm -f \
			"${SMOKE_HISTORY_DB:-/tmp/polinko-eval-smoke-history.db}" \
			"${SMOKE_MEMORY_DB:-/tmp/polinko-eval-smoke-memory.db}" \
			"${SMOKE_VECTOR_DB:-/tmp/polinko-eval-smoke-vector.db}"
		POLINKO_HISTORY_DB_PATH="${SMOKE_HISTORY_DB:-/tmp/polinko-eval-smoke-history.db}" \
			POLINKO_MEMORY_DB_PATH="${SMOKE_MEMORY_DB:-/tmp/polinko-eval-smoke-memory.db}" \
			POLINKO_VECTOR_DB_PATH="${SMOKE_VECTOR_DB:-/tmp/polinko-eval-smoke-vector.db}" \
			POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK=true \
			"$python_bin" -m uvicorn "$asgi_app" --host 127.0.0.1 --port "$port" >"$log_path" 2>&1 &
		;;
	gate)
		rm -f \
			"${GATE_SESSION_DB:-/tmp/polinko-quality-gate-sessions.db}" \
			"${GATE_VECTOR_DB:-/tmp/polinko-quality-gate-vector.db}"
		POLINKO_SESSION_DB_PATH="${GATE_SESSION_DB:-/tmp/polinko-quality-gate-sessions.db}" \
			POLINKO_VECTOR_DB_PATH="${GATE_VECTOR_DB:-/tmp/polinko-quality-gate-vector.db}" \
			POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK=true \
			"$python_bin" -m uvicorn "$asgi_app" --host 127.0.0.1 --port "$port" >"$log_path" 2>&1 &
		;;
	*)
		echo "Unknown local eval gate scope: $scope" >&2
		exit 2
		;;
	esac

	server_pid=$!
	ready=0
	for _ in $(seq 1 100); do
		if curl -fsS "$base_url/health" >/dev/null 2>&1; then
			ready=1
			break
		fi
		sleep 0.2
	done
	if [ "$ready" -ne 1 ]; then
		echo "Server failed to start. See $log_path"
		exit 1
	fi
}

run_api_smoke() {
	base_url=${SMOKE_BASE_URL:-http://127.0.0.1:8067}

	echo "Running API smoke (fresh local server + small endpoint calls)..."
	start_local_server smoke "$base_url" "${SMOKE_PORT:-8067}" /tmp/polinko-api-smoke.log
	"$python_bin" -m tools.api_smoke --base-url "$base_url"
	echo "API smoke passed."
}

run_eval_smoke() {
	base_url=${SMOKE_BASE_URL:-http://127.0.0.1:8067}

	echo "Running eval smoke (fresh local server + api smoke + response behaviour + retrieval + file search)..."
	start_local_server smoke "$base_url" "${SMOKE_PORT:-8067}" /tmp/polinko-eval-smoke.log
	"$python_bin" -m tools.api_smoke --base-url "$base_url"
	"$python_bin" -m tools.eval_response_behaviour --base-url "$base_url" --strict
	"$python_bin" -m tools.eval_retrieval \
		--base-url "$base_url" \
		--request-retries "${RETRIEVAL_REQUEST_RETRIES:-2}" \
		--request-retry-delay-ms "${RETRIEVAL_REQUEST_RETRY_DELAY_MS:-750}"
	"$python_bin" -m tools.eval_file_search --base-url "$base_url"
	echo "Eval smoke passed."
}

run_hallucination_gate() {
	base_url=${GATE_BASE_URL:-http://127.0.0.1:8066}

	echo "Running hallucination gate..."
	start_local_server gate "$base_url" "${GATE_PORT:-8066}" /tmp/polinko-hallucination-gate.log
	"$python_bin" -m tools.eval_hallucination \
		--base-url "$base_url" \
		--strict \
		--evaluation-mode "${HALLUCINATION_EVAL_MODE:-judge}" \
		--judge-model "${HALLUCINATION_JUDGE_MODEL:-gpt-4.1-mini}" \
		--judge-api-key-env "${HALLUCINATION_JUDGE_API_KEY_ENV:-OPENAI_API_KEY}" \
		--judge-base-url "${HALLUCINATION_JUDGE_BASE_URL:-}" \
		--min-acceptable-score "${HALLUCINATION_MIN_ACCEPTABLE_SCORE:-5}"
	echo "Hallucination gate passed."
}

run_quality_gate() {
	base_url=${GATE_BASE_URL:-http://127.0.0.1:8066}

	echo "Running quality gate (tests + retrieval eval + file-search eval + OCR eval + style eval + response-behaviour eval + hallucination eval)..."
	start_local_server gate "$base_url" "${GATE_PORT:-8066}" /tmp/polinko-quality-gate.log
	"$python_bin" -m unittest discover -s tests -p "test_*.py"
	"$python_bin" -m tools.eval_retrieval \
		--base-url "$base_url" \
		--request-retries "${RETRIEVAL_REQUEST_RETRIES:-2}" \
		--request-retry-delay-ms "${RETRIEVAL_REQUEST_RETRY_DELAY_MS:-750}"
	"$python_bin" -m tools.eval_file_search --base-url "$base_url"
	"$python_bin" -m tools.eval_ocr \
		--timeout "${OCR_EVAL_TIMEOUT:-90}" \
		--base-url "$base_url" \
		--strict \
		--ocr-retries "${OCR_EVAL_OCR_RETRIES:-2}" \
		--ocr-retry-delay-ms "${OCR_EVAL_OCR_RETRY_DELAY_MS:-750}" \
		--max-consecutive-rate-limit-errors "${OCR_MAX_CONSEC_RATE_LIMIT_ERRORS:-3}"
	"$python_bin" -m tools.eval_style \
		--base-url "$base_url" \
		--strict \
		--case-attempts "${STYLE_CASE_ATTEMPTS:-1}" \
		--min-pass-attempts "${STYLE_MIN_PASS_ATTEMPTS:-1}"
	"$python_bin" -m tools.eval_response_behaviour --base-url "$base_url" --strict
	"$python_bin" -m tools.eval_hallucination \
		--base-url "$base_url" \
		--strict \
		--evaluation-mode "${HALLUCINATION_EVAL_MODE:-judge}" \
		--judge-model "${HALLUCINATION_JUDGE_MODEL:-gpt-4.1-mini}" \
		--judge-api-key-env "${HALLUCINATION_JUDGE_API_KEY_ENV:-OPENAI_API_KEY}" \
		--judge-base-url "${HALLUCINATION_JUDGE_BASE_URL:-}" \
		--min-acceptable-score "${HALLUCINATION_MIN_ACCEPTABLE_SCORE:-5}"
	echo "Quality gate passed."
}

case "$suite" in
api-smoke)
	run_api_smoke
	;;
eval-smoke)
	run_eval_smoke
	;;
hallucination-gate)
	run_hallucination_gate
	;;
quality-gate)
	run_quality_gate
	;;
esac
