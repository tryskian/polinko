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

python_bin=${PYTHON:-python3}
launcher_python=${SERVER_LAUNCHER_PYTHON:-python3}
asgi_app=${ASGI_APP:-server:app}
dev_host=${DEV_HOST:-127.0.0.1}
dev_backend_port=${DEV_BACKEND_PORT:-8000}
server_pid_file=${SERVER_PID_FILE:-/tmp/polinko-server.pid}
server_log=${SERVER_LOG:-/tmp/polinko-server.log}

resolve_expected_python() {
	"$python_bin" -c 'import os,sys; print(os.path.realpath(sys.executable))' 2>/dev/null || true
}

launch_detached_server() {
	"$launcher_python" - "$server_pid_file" "$server_log" "$python_bin" "$asgi_app" "$dev_host" "$dev_backend_port" <<'PY'
import subprocess
import sys

pid_file, log_file, python_bin, asgi_app, dev_host, dev_backend_port = sys.argv[1:7]
args = [
    python_bin,
    "-m",
    "uvicorn",
    asgi_app,
    "--host",
    dev_host,
    "--port",
    dev_backend_port,
    "--reload",
]

with open(log_file, "ab", buffering=0) as log:
    process = subprocess.Popen(
        args,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        close_fds=True,
    )

with open(pid_file, "w", encoding="utf-8") as handle:
    handle.write(str(process.pid))
PY
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
		if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
			echo "server-daemon already running (PID $pid)."
			exit 0
		fi
		rm -f "$server_pid_file"
	fi

	if command -v lsof >/dev/null 2>&1; then
		existing_pids=$(lsof -nP -iTCP:"$dev_backend_port" -sTCP:LISTEN -t 2>/dev/null | tr '\n' ' ' || true)
		if [ -n "$existing_pids" ]; then
			polinko_pid=""
			polinko_cmd=""
			for candidate_pid in $existing_pids; do
				candidate_cmd=$(ps -o command= -p "$candidate_pid" 2>/dev/null || true)
				check_pid="$candidate_pid"
				check_cmd="$candidate_cmd"
				if ! printf '%s\n' "$check_cmd" | grep -Fq "uvicorn $asgi_app"; then
					parent_pid=$(ps -o ppid= -p "$candidate_pid" 2>/dev/null | tr -d ' ' || true)
					if [ -n "$parent_pid" ]; then
						parent_cmd=$(ps -o command= -p "$parent_pid" 2>/dev/null || true)
						if printf '%s\n' "$parent_cmd" | grep -Fq "uvicorn $asgi_app"; then
							check_pid="$parent_pid"
							check_cmd="$parent_cmd"
						fi
					fi
				fi
				if printf '%s\n' "$check_cmd" | grep -Fq "uvicorn $asgi_app"; then
					polinko_pid="$check_pid"
					polinko_cmd="$check_cmd"
					break
				fi
			done
			if [ -n "$polinko_pid" ]; then
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
				first_cmd=$(ps -o command= -p "$first_pid" 2>/dev/null || true)
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
	if kill -0 "$pid" 2>/dev/null; then
		echo "server-daemon started (PID $pid, log: $server_log)."
	else
		rm -f "$server_pid_file"
		echo "Failed to start server-daemon. Check $server_log."
		exit 1
	fi
}

stop_server() {
	if [ ! -f "$server_pid_file" ]; then
		echo "No server-daemon PID file found."
		exit 0
	fi
	pid=$(cat "$server_pid_file" 2>/dev/null || true)
	if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
		kill "$pid"
		sleep 0.1
		echo "server-daemon stopped (PID $pid)."
	else
		echo "Stale server-daemon PID file; cleaning up."
	fi
	rm -f "$server_pid_file"
}

status_server() {
	if [ -f "$server_pid_file" ]; then
		pid=$(cat "$server_pid_file" 2>/dev/null || true)
		if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
			echo "server-daemon: RUNNING (PID $pid)."
			exit 0
		fi
		echo "server-daemon: STALE PID file."
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
