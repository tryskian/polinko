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

target=${EVAL_SIDECAR_TARGET-quality-gate-deterministic}
min_seconds=${EVAL_SIDECAR_MIN_SECONDS-3600}
sidecar_start_attempts=${EVAL_SIDECAR_START_ATTEMPTS:-100}
sidecar_start_sleep_seconds=${EVAL_SIDECAR_START_SLEEP_SECONDS:-0.1}
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
polinko_cd_repo_root
# shellcheck source=tools/python_runtime.sh
. "$script_dir/python_runtime.sh"
# shellcheck source=tools/process_lifecycle_common.sh
. "$script_dir/process_lifecycle_common.sh"
sidecar_repo_slug=${EVAL_SIDECAR_REPO_SLUG-${POLINKO_REPO_ROOT##*/}}
polinko_require_non_empty_token \
	EVAL_SIDECAR_REPO_SLUG \
	"$sidecar_repo_slug" \
	"repo slug" \
	"eval-sidecar runtime state"
sidecar_runtime_root=${EVAL_SIDECAR_RUNTIME_ROOT:-/tmp/polinko-runtime}
sidecar_state_dir=${EVAL_SIDECAR_STATE_DIR:-$sidecar_runtime_root/$sidecar_repo_slug}
runs_dir=${EVAL_SIDECAR_RUNS_DIR:-.local/eval_runs}
pid_file=${EVAL_SIDECAR_PID_FILE:-$sidecar_state_dir/eval-sidecar.pid}
current_file=${EVAL_SIDECAR_CURRENT_FILE:-$runs_dir/eval_sidecar_current.txt}
log_path=${EVAL_SIDECAR_LOG:-$sidecar_state_dir/eval-sidecar.log}
detached_launcher="$POLINKO_REPO_ROOT/tools/launch_detached_process.py"
polinko_require_positive_integer \
	EVAL_SIDECAR_START_ATTEMPTS \
	"$sidecar_start_attempts" \
	"eval-sidecar readiness"
polinko_require_non_empty_token \
	EVAL_SIDECAR_TARGET \
	"$target" \
	"Make target" \
	"eval-sidecar target"
polinko_require_positive_integer \
	EVAL_SIDECAR_MIN_SECONDS \
	"$min_seconds" \
	"eval-sidecar duration"
polinko_require_non_negative_decimal \
	EVAL_SIDECAR_START_SLEEP_SECONDS \
	"$sidecar_start_sleep_seconds" \
	"eval-sidecar readiness"
python_bin=$(polinko_default_python_bin)
launcher_python=${EVAL_SIDECAR_LAUNCHER_PYTHON:-$python_bin}

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

pid_matches_eval_sidecar() {
	local pid=$1
	local command parent_pid parent_command
	command=$(polinko_process_command "$pid")
	if printf '%s\n' "$command" | grep -Fq "tools.eval_sidecar run"; then
		return 0
	fi
	parent_pid=$(polinko_parent_pid "$pid")
	if [ -z "$parent_pid" ]; then
		return 1
	fi
	parent_command=$(polinko_process_command "$parent_pid")
	printf '%s\n' "$parent_command" | grep -Fq "tools.eval_sidecar run"
}

stop_managed_pid() {
	local pid=$1
	kill "$pid"
	if ! polinko_wait_for_pid_exit "$pid" 30 0.1; then
		echo "eval-sidecar did not exit after stop signal (PID $pid); leaving PID file in place."
		return 1
	fi
	rm -f "$pid_file"
}

wait_for_sidecar_ready() {
	local pid=$1
	local attempt=0
	local run_dir
	while [ "$attempt" -lt "$sidecar_start_attempts" ]; do
		if ! polinko_pid_is_running "$pid"; then
			return 2
		fi
		if [ -f "$current_file" ]; then
			run_dir=$(cat "$current_file" 2>/dev/null || true)
			if [ -n "$run_dir" ] && [ -f "$run_dir/status.json" ]; then
				return 0
			fi
		fi
		sleep "$sidecar_start_sleep_seconds"
		attempt=$((attempt + 1))
	done
	return 1
}

print_sidecar_context() {
	echo "Repo: $sidecar_repo_slug"
	echo "Repo root: $POLINKO_REPO_ROOT"
	echo "PID file: $pid_file"
	echo "Log file: $log_path"
	echo "Current file: $current_file"
}

prepare_runtime_parent() {
	local label path parent
	label=$1
	path=$2
	parent=$(dirname "$path")
	if ! mkdir -p "$parent" 2>/dev/null; then
		echo "eval-sidecar failed to prepare $label parent: $parent" >&2
		return 1
	fi
}

prepare_runtime_paths() {
	prepare_runtime_parent "PID file" "$pid_file" || return 1
	prepare_runtime_parent "log file" "$log_path" || return 1
	prepare_runtime_parent "current file" "$current_file" || return 1
}

start_sidecar() {
	polinko_require_process_inspection "eval-sidecar PID inspection"

	if [ -f "$pid_file" ]; then
		pid=$(cat "$pid_file" 2>/dev/null || true)
		if polinko_pid_is_running "$pid"; then
			if ! pid_matches_eval_sidecar "$pid"; then
				echo "eval-sidecar PID file points to a non-sidecar process; cleaning up."
				rm -f "$pid_file"
			else
				if [ ! -f "$current_file" ]; then
					echo "eval-sidecar current file missing: $current_file"
					echo "eval-sidecar already running without run context (PID $pid)."
					exit 1
				fi
				echo "eval-sidecar already running (PID $pid)."
				exit 0
			fi
		else
			rm -f "$pid_file"
		fi
	fi

	if ! prepare_runtime_paths; then
		exit 1
	fi
	if ! polinko_require_python_command \
		EVAL_SIDECAR_LAUNCHER_PYTHON \
		"$launcher_python" \
		"eval-sidecar detached launcher"; then
		exit 2
	fi
	if ! launch_detached_sidecar; then
		rm -f "$pid_file"
		echo "Failed to start eval-sidecar. Check $log_path."
		exit 1
	fi
	pid=$(cat "$pid_file" 2>/dev/null || true)
	if wait_for_sidecar_ready "$pid"; then
		echo "eval-sidecar started (PID $pid, log: $log_path)."
	else
		if polinko_pid_is_running "$pid" && pid_matches_eval_sidecar "$pid"; then
			echo "eval-sidecar did not become ready (PID $pid); leaving PID file in place."
		else
			rm -f "$pid_file"
		fi
		echo "Failed to start eval-sidecar. Check $log_path."
		exit 1
	fi
}

status_sidecar() {
	polinko_require_process_inspection "eval-sidecar PID inspection"
	print_sidecar_context

	if [ -f "$pid_file" ]; then
		pid=$(cat "$pid_file" 2>/dev/null || true)
		if polinko_pid_is_running "$pid"; then
			if ! pid_matches_eval_sidecar "$pid"; then
				echo "eval-sidecar: STALE PID file (PID $pid is not a matching sidecar)."
				exit 1
			fi
		else
			echo "eval-sidecar: STALE PID file."
			exit 1
		fi
	fi
	if [ ! -f "$current_file" ]; then
		if [ -f "$pid_file" ]; then
			pid=$(cat "$pid_file" 2>/dev/null || true)
			if polinko_pid_is_running "$pid"; then
				echo "eval-sidecar: RUNNING (PID $pid)."
				echo "eval-sidecar current file missing: $current_file"
				exit 1
			fi
		fi
		echo "eval-sidecar: OFF."
		exit 0
	fi
	"$python_bin" -m tools.eval_sidecar status --current-file "$current_file" --pid-file "$pid_file"
}

stop_sidecar() {
	polinko_require_process_inspection "eval-sidecar PID inspection"

	if [ ! -f "$current_file" ]; then
		if [ -f "$pid_file" ]; then
			pid=$(cat "$pid_file" 2>/dev/null || true)
			if polinko_pid_is_running "$pid"; then
				if ! pid_matches_eval_sidecar "$pid"; then
					echo "eval-sidecar PID file points to a non-sidecar process; cleaning up."
					rm -f "$pid_file"
				else
					echo "eval-sidecar current file missing: $current_file"
					if ! stop_managed_pid "$pid"; then
						exit 1
					fi
					echo "eval-sidecar stopped managed PID $pid without current run context."
				fi
				exit 0
			fi
			rm -f "$pid_file"
		fi
		echo "No eval-sidecar run found."
		exit 0
	fi
	if [ -f "$pid_file" ]; then
		pid=$(cat "$pid_file" 2>/dev/null || true)
		if polinko_pid_is_running "$pid" && ! pid_matches_eval_sidecar "$pid"; then
			echo "eval-sidecar PID file points to a non-sidecar process; cleaning up."
			rm -f "$pid_file"
		elif ! polinko_pid_is_running "$pid"; then
			rm -f "$pid_file"
		fi
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
