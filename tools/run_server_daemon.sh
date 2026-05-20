#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 0 ]; then
	echo "Usage: run_server_daemon.sh" >&2
	exit 2
fi

python_bin=${PYTHON:-python3}
asgi_app=${ASGI_APP:-server:app}
dev_host=${DEV_HOST:-127.0.0.1}
dev_backend_port=${DEV_BACKEND_PORT:-8000}
server_pid_file=${SERVER_PID_FILE:-/tmp/polinko-server.pid}
server_log=${SERVER_LOG:-/tmp/polinko-server.log}

expected_py="$("$python_bin" -c 'import os,sys; print(os.path.realpath(sys.executable))' 2>/dev/null || true)"
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

nohup "$python_bin" -m uvicorn "$asgi_app" --host "$dev_host" --port "$dev_backend_port" --reload >"$server_log" 2>&1 &
pid=$!
echo "$pid" >"$server_pid_file"
sleep 0.2
if kill -0 "$pid" 2>/dev/null; then
	echo "server-daemon started (PID $pid, log: $server_log)."
else
	rm -f "$server_pid_file"
	echo "Failed to start server-daemon. Check $server_log."
	exit 1
fi
