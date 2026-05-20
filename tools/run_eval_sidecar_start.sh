#!/usr/bin/env sh
set -eu

if [ "$#" -ne 0 ]; then
	echo "Usage: run_eval_sidecar_start.sh" >&2
	exit 2
fi

python_bin=${PYTHON:-python3}
target=${EVAL_SIDECAR_TARGET:-quality-gate-deterministic}
min_seconds=${EVAL_SIDECAR_MIN_SECONDS:-3600}
runs_dir=${EVAL_SIDECAR_RUNS_DIR:-.local/eval_runs}
pid_file=${EVAL_SIDECAR_PID_FILE:-/tmp/polinko-eval-sidecar.pid}
current_file=${EVAL_SIDECAR_CURRENT_FILE:-$runs_dir/eval_sidecar_current.txt}
log_path=${EVAL_SIDECAR_LOG:-/tmp/polinko-eval-sidecar.log}

if [ -f "$pid_file" ]; then
	pid=$(cat "$pid_file" 2>/dev/null || true)
	if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
		echo "eval-sidecar already running (PID $pid)."
		exit 0
	fi
	rm -f "$pid_file"
fi

mkdir -p "$(dirname "$log_path")"
nohup "$python_bin" -m tools.eval_sidecar run \
	--target "$target" \
	--min-seconds "$min_seconds" \
	--runs-dir "$runs_dir" \
	--pid-file "$pid_file" \
	--current-file "$current_file" \
	>"$log_path" 2>&1 &
pid=$!
sleep 0.2
if kill -0 "$pid" 2>/dev/null; then
	echo "eval-sidecar started (PID $pid, log: $log_path)."
else
	echo "Failed to start eval-sidecar. Check $log_path."
	exit 1
fi
