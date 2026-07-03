#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: run_server_daemon.sh {start|stop|status}" >&2
}

if [ "$#" -eq 0 ]; then
	action=start
elif [ "$#" -eq 1 ]; then
	action=$1
else
	usage
	exit 2
fi

asgi_app=${ASGI_APP:-server:app}
dev_host=${DEV_HOST:-127.0.0.1}
dev_backend_port=${DEV_BACKEND_PORT:-8000}
server_health_host=${SERVER_HEALTH_HOST:-127.0.0.1}
server_health_url=${SERVER_HEALTH_URL:-http://$server_health_host:$dev_backend_port/health}
server_start_attempts=${SERVER_START_ATTEMPTS:-100}
server_start_sleep_seconds=${SERVER_START_SLEEP_SECONDS:-0.2}
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
polinko_cd_repo_root
# shellcheck source=tools/python_runtime.sh
. "$script_dir/python_runtime.sh"
# shellcheck source=tools/process_lifecycle_common.sh
. "$script_dir/process_lifecycle_common.sh"
server_repo_slug=${SERVER_REPO_SLUG:-${POLINKO_REPO_ROOT##*/}}
polinko_require_non_empty_token \
	SERVER_REPO_SLUG \
	"$server_repo_slug" \
	"repo slug" \
	"server-daemon runtime state"
server_runtime_root=${SERVER_RUNTIME_ROOT:-/tmp/polinko-runtime}
server_state_dir=${SERVER_STATE_DIR:-$server_runtime_root/$server_repo_slug}
server_pid_file=${SERVER_PID_FILE:-$server_state_dir/server.pid}
server_log=${SERVER_LOG:-$server_state_dir/server.log}
detached_launcher="$POLINKO_REPO_ROOT/tools/launch_detached_process.py"
polinko_require_tcp_port DEV_BACKEND_PORT "$dev_backend_port" "server-daemon launch"
polinko_require_url_port_matches \
	SERVER_HEALTH_URL \
	"$server_health_url" \
	"$dev_backend_port" \
	"server-daemon health check"
polinko_require_positive_integer \
	SERVER_START_ATTEMPTS \
	"$server_start_attempts" \
	"server-daemon readiness"
polinko_require_non_negative_decimal \
	SERVER_START_SLEEP_SECONDS \
	"$server_start_sleep_seconds" \
	"server-daemon readiness"
python_bin=$(polinko_default_python_bin)
launcher_python=${SERVER_LAUNCHER_PYTHON:-$python_bin}

resolve_expected_python() {
	"$python_bin" -c 'import os,sys; print(os.path.realpath(sys.executable))' 2>/dev/null || true
}

server_pids_on_port() {
	if ! polinko_command_available lsof; then
		return 0
	fi
	lsof -nP -iTCP:"$dev_backend_port" -sTCP:LISTEN -t 2>/dev/null || true
}

pid_matches_polinko_server() {
	local pid=$1
	local command parent_pid parent_command
	command=$(polinko_process_command "$pid")
	if printf '%s\n' "$command" | grep -Fq "uvicorn $asgi_app"; then
		return 0
	fi
	parent_pid=$(polinko_parent_pid "$pid")
	if [ -z "$parent_pid" ]; then
		return 1
	fi
	parent_command=$(polinko_process_command "$parent_pid")
	printf '%s\n' "$parent_command" | grep -Fq "uvicorn $asgi_app"
}

polinko_server_pid_on_port() {
	local candidate_pid candidate_cmd check_pid check_cmd parent_pid parent_cmd
	for candidate_pid in $(server_pids_on_port); do
		candidate_cmd=$(polinko_process_command "$candidate_pid")
		check_pid="$candidate_pid"
		check_cmd="$candidate_cmd"
		if ! printf '%s\n' "$check_cmd" | grep -Fq "uvicorn $asgi_app"; then
			parent_pid=$(polinko_parent_pid "$candidate_pid")
			if [ -n "$parent_pid" ]; then
				parent_cmd=$(polinko_process_command "$parent_pid")
				if printf '%s\n' "$parent_cmd" | grep -Fq "uvicorn $asgi_app"; then
					check_pid="$parent_pid"
					check_cmd="$parent_cmd"
				fi
			fi
		fi
		if printf '%s\n' "$check_cmd" | grep -Fq "uvicorn $asgi_app"; then
			printf "%s\n" "$check_pid"
			return 0
		fi
	done
	return 1
}

launch_detached_server() {
	"$launcher_python" "$detached_launcher" \
		--pid-file "$server_pid_file" \
		--log-file "$server_log" \
		-- \
		"$python_bin" -m uvicorn "$asgi_app" \
		--host "$dev_host" \
		--port "$dev_backend_port" \
		--reload
}

wait_for_server_stop() {
	local pid=$1
	if ! polinko_wait_for_pid_exit "$pid" 30 0.1; then
		echo "server-daemon did not exit after stop signal (PID $pid)."
		return 1
	fi
}

wait_for_server_ready() {
	local pid=$1
	local attempt=0
	while [ "$attempt" -lt "$server_start_attempts" ]; do
		if ! polinko_pid_is_running "$pid"; then
			return 2
		fi
		if curl -fsS "$server_health_url" >/dev/null 2>&1; then
			return 0
		fi
		sleep "$server_start_sleep_seconds"
		attempt=$((attempt + 1))
	done
	return 1
}

print_server_context() {
	echo "Repo: $server_repo_slug"
	echo "Repo root: $POLINKO_REPO_ROOT"
	echo "PID file: $server_pid_file"
	echo "Log file: $server_log"
}

prepare_runtime_parent() {
	local label path parent
	label=$1
	path=$2
	parent=$(dirname "$path")
	if ! mkdir -p "$parent" 2>/dev/null; then
		echo "server-daemon failed to prepare $label parent: $parent" >&2
		return 1
	fi
}

prepare_runtime_paths() {
	prepare_runtime_parent "PID file" "$server_pid_file" || return 1
	prepare_runtime_parent "log file" "$server_log" || return 1
}

start_server() {
	expected_py=$(resolve_expected_python)
	if [ -z "$expected_py" ]; then
		echo "Unable to resolve expected Python interpreter from $python_bin."
		exit 1
	fi
	polinko_require_process_inspection "server-daemon PID inspection"

	if ! prepare_runtime_paths; then
		exit 1
	fi

	if [ -f "$server_pid_file" ]; then
		pid=$(cat "$server_pid_file" 2>/dev/null || true)
		if polinko_pid_is_running "$pid"; then
			if pid_matches_polinko_server "$pid"; then
				echo "server-daemon already running (PID $pid)."
				exit 0
			fi
			echo "server-daemon PID file points to a non-server process; cleaning up."
			rm -f "$server_pid_file"
		else
			rm -f "$server_pid_file"
		fi
	fi

	if polinko_command_available lsof; then
		existing_pids=$(server_pids_on_port | tr '\n' ' ' || true)
		if [ -n "$existing_pids" ]; then
			polinko_pid=$(polinko_server_pid_on_port || true)
			if [ -n "$polinko_pid" ]; then
				polinko_cmd=$(polinko_process_command "$polinko_pid")
				existing_py=$(printf '%s\n' "$polinko_cmd" | awk '{print $1}')
				existing_py_real="$("$existing_py" -c 'import os,sys; print(os.path.realpath(sys.executable))' 2>/dev/null || true)"
				if [ "$existing_py_real" = "$expected_py" ]; then
					echo "$polinko_pid" >"$server_pid_file"
					echo "server-daemon already active on port $dev_backend_port; adopted PID $polinko_pid ($existing_py_real)."
					exit 0
				fi
				echo "server-daemon found polinko server on port $dev_backend_port with interpreter mismatch."
				echo "expected: $expected_py"
				echo "found:    $existing_py_real"
				echo "Restarting server-daemon with expected interpreter."
				kill "$polinko_pid"
				if ! wait_for_server_stop "$polinko_pid"; then
					exit 1
				fi
			else
				first_pid=$(printf '%s\n' "$existing_pids" | awk '{print $1}')
				first_cmd=$(polinko_process_command "$first_pid")
				echo "Port $dev_backend_port is in use by a non-polinko process."
				echo "PID $first_pid: $first_cmd"
				exit 1
			fi
		fi
	fi

	polinko_require_command curl "server-daemon readiness check"
	if ! polinko_require_python_command \
		SERVER_LAUNCHER_PYTHON \
		"$launcher_python" \
		"server-daemon detached launcher"; then
		exit 2
	fi

	if ! launch_detached_server; then
		rm -f "$server_pid_file"
		echo "Failed to start server-daemon. Check $server_log."
		exit 1
	fi
	pid=$(cat "$server_pid_file" 2>/dev/null || true)
	if wait_for_server_ready "$pid"; then
		echo "server-daemon started (PID $pid, log: $server_log)."
	else
		if polinko_pid_is_running "$pid" && pid_matches_polinko_server "$pid"; then
			echo "server-daemon did not become ready (PID $pid); leaving PID file in place."
		else
			rm -f "$server_pid_file"
		fi
		echo "Failed to start server-daemon. Check $server_log."
		exit 1
	fi
}

stop_server() {
	polinko_require_process_inspection "server-daemon PID inspection"

	stale_cleaned=0
	if [ -f "$server_pid_file" ]; then
		pid=$(cat "$server_pid_file" 2>/dev/null || true)
		if polinko_pid_is_running "$pid"; then
			if ! pid_matches_polinko_server "$pid"; then
				echo "server-daemon PID file points to a non-server process; cleaning up."
				rm -f "$server_pid_file"
				stale_cleaned=1
			else
				kill "$pid"
				if ! wait_for_server_stop "$pid"; then
					exit 1
				fi
				rm -f "$server_pid_file"
				echo "server-daemon stopped (PID $pid)."
				exit 0
			fi
		else
			echo "Stale server-daemon PID file; cleaning up."
			rm -f "$server_pid_file"
			stale_cleaned=1
		fi
	fi

	pid=$(polinko_server_pid_on_port || true)
	if [ -n "$pid" ]; then
		kill "$pid"
		if ! wait_for_server_stop "$pid"; then
			exit 1
		fi
		echo "server-daemon stopped matching server without PID file (PID $pid)."
		exit 0
	fi
	if [ "$stale_cleaned" -eq 1 ]; then
		exit 0
	fi
	echo "No server-daemon PID file found."
}

status_server() {
	polinko_require_process_inspection "server-daemon PID inspection"
	print_server_context

	if [ -f "$server_pid_file" ]; then
		pid=$(cat "$server_pid_file" 2>/dev/null || true)
		if polinko_pid_is_running "$pid"; then
			if ! pid_matches_polinko_server "$pid"; then
				echo "server-daemon: STALE PID file (PID $pid is not a matching server)."
				exit 1
			fi
			echo "server-daemon: RUNNING (PID $pid)."
			exit 0
		fi
		echo "server-daemon: STALE PID file."
		exit 1
	fi
	pid=$(polinko_server_pid_on_port || true)
	if [ -n "$pid" ]; then
		echo "server-daemon: RUNNING without managed PID file (PID $pid)."
		exit 1
	fi
	echo "server-daemon: OFF."
}

case "$action" in
	start)
		start_server
		;;
	stop)
		stop_server
		;;
	status)
		status_server
		;;
	*)
		usage
		exit 2
		;;
esac
