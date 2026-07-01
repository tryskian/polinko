#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
# shellcheck source=tools/python_runtime.sh
. "$script_dir/python_runtime.sh"
# shellcheck source=tools/process_lifecycle_common.sh
. "$script_dir/process_lifecycle_common.sh"

if [ "$#" -ne 1 ]; then
	echo "Usage: run_local_eval_gate.sh <suite>" >&2
	exit 2
fi

suite=$1
python_bin=$(polinko_default_python_bin)
asgi_app=${ASGI_APP:-server:app}
local_eval_gate_temp_root=${LOCAL_EVAL_GATE_TEMP_ROOT:-/tmp}
if [ "$local_eval_gate_temp_root" != "/" ]; then
	local_eval_gate_temp_root=${local_eval_gate_temp_root%/}
fi
local_eval_gate_start_attempts=${LOCAL_EVAL_GATE_START_ATTEMPTS:-100}
local_eval_gate_start_sleep_seconds=${LOCAL_EVAL_GATE_START_SLEEP_SECONDS:-0.2}
polinko_require_positive_integer \
	LOCAL_EVAL_GATE_START_ATTEMPTS \
	"$local_eval_gate_start_attempts" \
	"local eval gate readiness"
polinko_require_non_negative_decimal \
	LOCAL_EVAL_GATE_START_SLEEP_SECONDS \
	"$local_eval_gate_start_sleep_seconds" \
	"local eval gate readiness"
if [ -n "${SMOKE_PORT:-}" ]; then
	polinko_require_tcp_port SMOKE_PORT "$SMOKE_PORT" "local eval gate port"
fi
if [ -n "${GATE_PORT:-}" ]; then
	polinko_require_tcp_port GATE_PORT "$GATE_PORT" "local eval gate port"
fi

case "$suite" in
api-smoke|eval-smoke|hallucination-gate|quality-gate)
	;;
*)
	echo "Unknown local eval gate suite: $suite" >&2
	exit 2
	;;
esac

polinko_require_process_inspection "local eval gate PID inspection"

server_pid=

temp_artifact_path() {
	polinko_join_path "$local_eval_gate_temp_root" "$1"
}

prepare_temp_root() {
	if ! mkdir -p "$local_eval_gate_temp_root" 2>/dev/null; then
		echo "local eval gate failed to prepare temp root: $local_eval_gate_temp_root" >&2
		return 1
	fi
}

cleanup_server() {
	exit_status=${1:-0}
	if [ -n "$server_pid" ]; then
		kill "$server_pid" 2>/dev/null || true
		if ! polinko_wait_for_pid_exit "$server_pid" 30 0.1; then
			echo "Server PID $server_pid did not exit after stop signal." >&2
			exit 1
		fi
		wait "$server_pid" 2>/dev/null || true
	fi
	exit "$exit_status"
}

trap 'cleanup_server "$?"' EXIT
trap 'trap - EXIT; cleanup_server 130' INT
trap 'trap - EXIT; cleanup_server 143' TERM

choose_loopback_port() {
	"$python_bin" - <<'PY'
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
}

server_is_running() {
	polinko_pid_is_running "$server_pid"
}

start_local_server() {
	scope=$1
	base_url=$2
	port=$3
	log_path=$4

	if ! prepare_temp_root; then
		exit 1
	fi

	case "$scope" in
	smoke)
		smoke_history_db=${SMOKE_HISTORY_DB:-$(temp_artifact_path "polinko-eval-smoke-$$-history.db")}
		smoke_memory_db=${SMOKE_MEMORY_DB:-$(temp_artifact_path "polinko-eval-smoke-$$-memory.db")}
		smoke_vector_db=${SMOKE_VECTOR_DB:-$(temp_artifact_path "polinko-eval-smoke-$$-vector.db")}
		rm -f \
			"$smoke_history_db" \
			"$smoke_memory_db" \
			"$smoke_vector_db"
		POLINKO_HISTORY_DB_PATH="$smoke_history_db" \
			POLINKO_MEMORY_DB_PATH="$smoke_memory_db" \
			POLINKO_VECTOR_DB_PATH="$smoke_vector_db" \
			POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK=true \
			"$python_bin" -m uvicorn "$asgi_app" --host 127.0.0.1 --port "$port" >"$log_path" 2>&1 &
		;;
	gate)
		gate_session_db=${GATE_SESSION_DB:-$(temp_artifact_path "polinko-quality-gate-sessions.db")}
		gate_vector_db=${GATE_VECTOR_DB:-$(temp_artifact_path "polinko-quality-gate-vector.db")}
		rm -f \
			"$gate_session_db" \
			"$gate_vector_db"
		POLINKO_SESSION_DB_PATH="$gate_session_db" \
			POLINKO_VECTOR_DB_PATH="$gate_vector_db" \
			POLINKO_VECTOR_EMBEDDING_PROVIDER="${GATE_VECTOR_EMBEDDING_PROVIDER:-openai}" \
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
	polinko_require_command curl "local eval gate readiness check"
	attempt=0
	while [ "$attempt" -lt "$local_eval_gate_start_attempts" ]; do
		if ! server_is_running; then
			echo "Server failed to stay running. See $log_path"
			exit 1
		fi
		if curl -fsS "$base_url/health" >/dev/null 2>&1; then
			ready=1
			break
		fi
		sleep "$local_eval_gate_start_sleep_seconds"
		attempt=$((attempt + 1))
	done
	if ! server_is_running; then
		echo "Server failed to stay running. See $log_path"
		exit 1
	fi
	if [ "$ready" -ne 1 ]; then
		echo "Server failed to start. See $log_path"
		exit 1
	fi
}

run_api_smoke() {
	port=${SMOKE_PORT:-$(choose_loopback_port)}
	base_url=${SMOKE_BASE_URL:-http://127.0.0.1:$port}
	polinko_require_url_port_matches SMOKE_BASE_URL "$base_url" "$port" "api-smoke local server"

	echo "Running API smoke (fresh local server + small endpoint calls)..."
	start_local_server smoke "$base_url" "$port" "$(temp_artifact_path "polinko-api-smoke.log")"
	"$python_bin" -m tools.api_smoke --base-url "$base_url"
	echo "API smoke passed."
}

run_eval_smoke() {
	port=${SMOKE_PORT:-$(choose_loopback_port)}
	base_url=${SMOKE_BASE_URL:-http://127.0.0.1:$port}
	polinko_require_url_port_matches SMOKE_BASE_URL "$base_url" "$port" "eval-smoke local server"

	echo "Running eval smoke (fresh local server + api smoke + response behaviour + retrieval + file search)..."
	start_local_server smoke "$base_url" "$port" "$(temp_artifact_path "polinko-eval-smoke.log")"
	"$python_bin" -m tools.api_smoke --base-url "$base_url"
	"$python_bin" -m tools.eval_response_behaviour --base-url "$base_url" --strict
	"$python_bin" -m tools.eval_retrieval \
		--base-url "$base_url" \
		--request-retries "${RETRIEVAL_REQUEST_RETRIES:-2}" \
		--request-retry-delay-ms "${RETRIEVAL_REQUEST_RETRY_DELAY_MS:-750}" \
		--chat-harness-mode "${RETRIEVAL_CHAT_HARNESS_MODE:-live}"
	"$python_bin" -m tools.eval_file_search --base-url "$base_url"
	echo "Eval smoke passed."
}

run_hallucination_gate() {
	port=${GATE_PORT:-8066}
	base_url=${GATE_BASE_URL:-http://127.0.0.1:$port}
	polinko_require_url_port_matches GATE_BASE_URL "$base_url" "$port" "hallucination-gate local server"

	echo "Running hallucination gate..."
	start_local_server gate "$base_url" "$port" "$(temp_artifact_path "polinko-hallucination-gate.log")"
	"$python_bin" -m tools.eval_hallucination \
		--base-url "$base_url" \
		--strict \
		--evaluation-mode "${HALLUCINATION_EVAL_MODE:-judge}" \
		--judge-model "${HALLUCINATION_JUDGE_MODEL:-gpt-4.1-mini}" \
		--judge-api-key-env "${HALLUCINATION_JUDGE_API_KEY_ENV:-OPENAI_API_KEY}" \
		--judge-base-url "${HALLUCINATION_JUDGE_BASE_URL:-}" \
		--chat-harness-mode "${HALLUCINATION_CHAT_HARNESS_MODE:-live}" \
		--min-acceptable-score "${HALLUCINATION_MIN_ACCEPTABLE_SCORE:-5}"
	echo "Hallucination gate passed."
}

run_quality_gate() {
	port=${GATE_PORT:-8066}
	base_url=${GATE_BASE_URL:-http://127.0.0.1:$port}
	polinko_require_url_port_matches GATE_BASE_URL "$base_url" "$port" "quality-gate local server"

	echo "Running quality gate (tests + retrieval eval + file-search eval + OCR eval + style eval + response-behaviour eval + hallucination eval)..."
	start_local_server gate "$base_url" "$port" "$(temp_artifact_path "polinko-quality-gate.log")"
	"$python_bin" -m unittest discover -s tests -p "test_*.py"
	"$python_bin" -m tools.eval_retrieval \
		--base-url "$base_url" \
		--request-retries "${RETRIEVAL_REQUEST_RETRIES:-2}" \
		--request-retry-delay-ms "${RETRIEVAL_REQUEST_RETRY_DELAY_MS:-750}" \
		--chat-harness-mode "${RETRIEVAL_CHAT_HARNESS_MODE:-live}"
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
		--min-pass-attempts "${STYLE_MIN_PASS_ATTEMPTS:-1}" \
		--evaluation-mode "${STYLE_EVAL_MODE:-judge}" \
		--chat-harness-mode "${STYLE_CHAT_HARNESS_MODE:-live}"
	"$python_bin" -m tools.eval_response_behaviour \
		--base-url "$base_url" \
		--strict \
		--chat-harness-mode "${RESPONSE_BEHAVIOUR_CHAT_HARNESS_MODE:-live}"
	"$python_bin" -m tools.eval_hallucination \
		--base-url "$base_url" \
		--strict \
		--evaluation-mode "${HALLUCINATION_EVAL_MODE:-judge}" \
		--judge-model "${HALLUCINATION_JUDGE_MODEL:-gpt-4.1-mini}" \
		--judge-api-key-env "${HALLUCINATION_JUDGE_API_KEY_ENV:-OPENAI_API_KEY}" \
		--judge-base-url "${HALLUCINATION_JUDGE_BASE_URL:-}" \
		--chat-harness-mode "${HALLUCINATION_CHAT_HARNESS_MODE:-live}" \
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
