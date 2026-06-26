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
server_pid_file=${SERVER_PID_FILE:-/tmp/polinko-server.pid}
server_log=${SERVER_LOG:-/tmp/polinko-server.log}
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
polinko_cd_repo_root
detached_launcher="$POLINKO_REPO_ROOT/tools/launch_detached_process.py"
# shellcheck source=tools/python_runtime.sh
. "$script_dir/python_runtime.sh"
python_bin=$(polinko_default_python_bin)
launcher_python=${SERVER_LAUNCHER_PYTHON:-$python_bin}

resolve_expected_python() {
	"$python_bin" -c 'import os,sys; print(os.path.realpath(sys.executable))' 2>/dev/null || true
}

pid_is_running() {
	local pid=$1
	[ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

server_pids_on_port() {
	if ! command -v lsof >/dev/null 2>&1; then
		return 0
	fi
	lsof -nP -iTCP:"$dev_backend_port" -sTCP:LISTEN -t 2>/dev/null || true
}

process_command() {
	local pid=$1
	ps -o command= -p "$pid" 2>/dev/null || true
}

polinko_server_pid_on_port() {
	local candidate_pid candidate_cmd check_pid check_cmd parent_pid parent_cmd
	for candidate_pid in $(server_pids_on_port); do
		candidate_cmd=$(process_command "$candidate_pid")
		check_pid="$candidate_pid"
		check_cmd="$candidate_cmd"
		if ! printf '%s\n' "$check_cmd" | grep -Fq "uvicorn $asgi_app"; then
			parent_pid=$(ps -o ppid= -p "$candidate_pid" 2>/dev/null | tr -d ' ' || true)
			if [ -n "$parent_pid" ]; then
				parent_cmd=$(process_command "$parent_pid")
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

start_server() {
	expected_py=$(resolve_expected_python)
	if [ -z "$expected_py" ]; then
		echo "Unable to resolve expected Python interpreter from $python_bin."
		exit 1
	fi

	mkdir -p "$(dirname "$server_pid_file")" "$(dirname "$server_log")"

	if [ -f "$server_pid_file" ]; then
		pid=$(cat "$server_pid_file" 2>/dev/null || true)
		if pid_is_running "$pid"; then
			echo "server-daemon already running (PID $pid)."
			exit 0
		fi
		rm -f "$server_pid_file"
	fi

	if command -v lsof >/dev/null 2>&1; then
		existing_pids=$(server_pids_on_port | tr '\n' ' ' || true)
		if [ -n "$existing_pids" ]; then
			polinko_pid=$(polinko_server_pid_on_port || true)
			if [ -n "$polinko_pid" ]; then
				polinko_cmd=$(process_command "$polinko_pid")
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
				sleep 0.2
			else
				first_pid=$(printf '%s\n' "$existing_pids" | awk '{print $1}')
				first_cmd=$(process_command "$first_pid")
				echo "Port $dev_backend_port is in use by a non-polinko process."
				echo "PID $first_pid: $first_cmd"
				exit 1
			fi
		fi
	fi

	if ! launch_detached_server; then
		rm -f "$server_pid_file"
		echo "Failed to start server-daemon. Check $server_log."
		exit 1
	fi
	pid=$(cat "$server_pid_file" 2>/dev/null || true)
	sleep 0.2
	if pid_is_running "$pid"; then
		echo "server-daemon started (PID $pid, log: $server_log)."
	else
		rm -f "$server_pid_file"
		echo "Failed to start server-daemon. Check $server_log."
		exit 1
	fi
}

stop_server() {
	stale_cleaned=0
	if [ -f "$server_pid_file" ]; then
		pid=$(cat "$server_pid_file" 2>/dev/null || true)
		if pid_is_running "$pid"; then
			kill "$pid"
			sleep 0.1
			rm -f "$server_pid_file"
			echo "server-daemon stopped (PID $pid)."
			exit 0
		fi
		echo "Stale server-daemon PID file; cleaning up."
		rm -f "$server_pid_file"
		stale_cleaned=1
	fi

	pid=$(polinko_server_pid_on_port || true)
	if [ -n "$pid" ]; then
		kill "$pid"
		sleep 0.1
		echo "server-daemon stopped matching server without PID file (PID $pid)."
		exit 0
	fi
	if [ "$stale_cleaned" -eq 1 ]; then
		exit 0
	fi
	echo "No server-daemon PID file found."
}

status_server() {
	if [ -f "$server_pid_file" ]; then
		pid=$(cat "$server_pid_file" 2>/dev/null || true)
		if pid_is_running "$pid"; then
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
