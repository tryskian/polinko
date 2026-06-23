#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: run_eval_sidecar_start.sh {start|status|stop}" >&2
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
launcher_python=${EVAL_SIDECAR_LAUNCHER_PYTHON:-python3}
target=${EVAL_SIDECAR_TARGET:-quality-gate-deterministic}
min_seconds=${EVAL_SIDECAR_MIN_SECONDS:-3600}
runs_dir=${EVAL_SIDECAR_RUNS_DIR:-.local/eval_runs}
pid_file=${EVAL_SIDECAR_PID_FILE:-/tmp/polinko-eval-sidecar.pid}
current_file=${EVAL_SIDECAR_CURRENT_FILE:-$runs_dir/eval_sidecar_current.txt}
log_path=${EVAL_SIDECAR_LOG:-/tmp/polinko-eval-sidecar.log}
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
detached_launcher="$script_dir/launch_detached_process.py"

launch_detached_sidecar() {
	"$launcher_python" "$detached_launcher" \
		--pid-file "$pid_file" \
		--log-file "$log_path" \
		-- \
		"$python_bin" -m tools.eval_sidecar run \
		--target "$target" \
		--min-seconds "$min_seconds" \
		--runs-dir "$runs_dir" \
		--pid-file "$pid_file" \
		--current-file "$current_file"
}

pid_is_running() {
	local pid=$1
	[ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

stop_managed_pid() {
	local pid=$1
	kill "$pid"
	sleep 0.1
	rm -f "$pid_file"
}

start_sidecar() {
	if [ -f "$pid_file" ]; then
		pid=$(cat "$pid_file" 2>/dev/null || true)
		if pid_is_running "$pid"; then
			if [ ! -f "$current_file" ]; then
				echo "eval-sidecar current file missing: $current_file"
				echo "eval-sidecar already running without run context (PID $pid)."
				exit 1
			fi
			echo "eval-sidecar already running (PID $pid)."
			exit 0
		fi
		rm -f "$pid_file"
	fi

	mkdir -p "$(dirname "$pid_file")" "$(dirname "$log_path")" "$(dirname "$current_file")"
	if ! launch_detached_sidecar; then
		rm -f "$pid_file"
		echo "Failed to start eval-sidecar. Check $log_path."
		exit 1
	fi
	pid=$(cat "$pid_file" 2>/dev/null || true)
	sleep 0.2
	if kill -0 "$pid" 2>/dev/null; then
		echo "eval-sidecar started (PID $pid, log: $log_path)."
	else
		rm -f "$pid_file"
		echo "Failed to start eval-sidecar. Check $log_path."
		exit 1
	fi
}

status_sidecar() {
	if [ ! -f "$current_file" ]; then
		if [ -f "$pid_file" ]; then
			pid=$(cat "$pid_file" 2>/dev/null || true)
			if pid_is_running "$pid"; then
				echo "eval-sidecar: RUNNING (PID $pid)."
				echo "eval-sidecar current file missing: $current_file"
				exit 1
			fi
			echo "eval-sidecar: STALE PID file."
			exit 1
		fi
		echo "eval-sidecar: OFF."
		exit 0
	fi
	"$python_bin" -m tools.eval_sidecar status --current-file "$current_file" --pid-file "$pid_file"
}

stop_sidecar() {
	if [ ! -f "$current_file" ]; then
		if [ -f "$pid_file" ]; then
			pid=$(cat "$pid_file" 2>/dev/null || true)
			if pid_is_running "$pid"; then
				echo "eval-sidecar current file missing: $current_file"
				stop_managed_pid "$pid"
				echo "eval-sidecar stopped managed PID $pid without current run context."
				exit 0
			fi
			rm -f "$pid_file"
		fi
		echo "No eval-sidecar run found."
		exit 0
	fi
	"$python_bin" -m tools.eval_sidecar stop --current-file "$current_file" --pid-file "$pid_file"
}

case "$action" in
	start)
		start_sidecar
		;;
	status)
		status_sidecar
		;;
	stop)
		stop_sidecar
		;;
	*)
		usage
		exit 2
		;;
esac
