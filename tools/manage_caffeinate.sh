#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: manage_caffeinate.sh {start|stop|stop-all|status}" >&2
}

if [ "$#" -ne 1 ]; then
	usage
	exit 2
fi

action=$1
pid_file=${CAFFEINATE_PID_FILE:-/tmp/polinko-caffeinate.pid}
log_file=${CAFFEINATE_LOG:-/tmp/polinko-caffeinate.log}
caffeinate_cmd=${CAFFEINATE_CMD:-/usr/bin/caffeinate -d -i -m}
launcher_python=${CAFFEINATE_LAUNCHER_PYTHON:-python3}
match_pattern=${CAFFEINATE_MATCH_PATTERN:-^/usr/bin/caffeinate -d -i -m( |$)}
uname_bin=${UNAME_BIN:-uname}
pgrep_bin=${PGREP_BIN:-pgrep}
pmset_bin=${PMSET_BIN:-/usr/bin/pmset}

is_darwin() {
	[ "$("$uname_bin" -s)" = "Darwin" ]
}

skip_unless_darwin() {
	if is_darwin; then
		return 0
	fi
	if [ "$action" = "status" ]; then
		echo "caffeinate status is only available on macOS."
	else
		echo "caffeinate is macOS-only; skipping."
	fi
	exit 0
}

find_matching_pids() {
	if ! command -v "$pgrep_bin" >/dev/null 2>&1; then
		return 0
	fi
	"$pgrep_bin" -f "$match_pattern" || true
}

launch_detached_caffeinate() {
	"$launcher_python" - "$pid_file" "$log_file" "$caffeinate_cmd" <<'PY'
import shlex
import subprocess
import sys

pid_file, log_file, command = sys.argv[1:4]

try:
    args = shlex.split(command)
except ValueError as exc:
    raise SystemExit(f"Invalid caffeinate command: {exc}") from exc

if not args:
    raise SystemExit("Invalid caffeinate command: empty command")

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

start_caffeinate() {
	skip_unless_darwin
	mkdir -p "$(dirname "$pid_file")" "$(dirname "$log_file")"

	if [ -f "$pid_file" ]; then
		pid=$(cat "$pid_file" 2>/dev/null || true)
		if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
			echo "caffeinate already running (PID $pid)."
			exit 0
		fi
		rm -f "$pid_file"
	fi

	if ! launch_detached_caffeinate; then
		rm -f "$pid_file"
		echo "Failed to start caffeinate."
		exit 1
	fi
	pid=$(cat "$pid_file" 2>/dev/null || true)
	sleep 0.1
	if kill -0 "$pid" 2>/dev/null; then
		echo "caffeinate started (PID $pid)."
	else
		rm -f "$pid_file"
		echo "Failed to start caffeinate."
		exit 1
	fi
}

stop_caffeinate() {
	skip_unless_darwin
	if [ ! -f "$pid_file" ]; then
		echo "No managed caffeinate PID file found."
		exit 0
	fi

	pid=$(cat "$pid_file" 2>/dev/null || true)
	if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
		kill "$pid"
		sleep 0.1
		echo "caffeinate stopped (PID $pid)."
	else
		echo "Stale PID file found; cleaning up."
	fi
	rm -f "$pid_file"
}

stop_all_caffeinate() {
	skip_unless_darwin
	pids=$(find_matching_pids | tr '\n' ' ')
	if [ -n "$pids" ]; then
		for pid in $pids; do
			kill "$pid" 2>/dev/null || true
		done
		sleep 0.1
		echo "Stopped matching caffeinate processes: $pids"
	else
		echo "No matching caffeinate processes running."
	fi
	rm -f "$pid_file"
}

status_caffeinate() {
	skip_unless_darwin
	if [ -f "$pid_file" ]; then
		pid=$(cat "$pid_file" 2>/dev/null || true)
		if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
			echo "Managed caffeinate: RUNNING (PID $pid)."
		else
			echo "Managed caffeinate: STALE PID file."
		fi
	else
		echo "Managed caffeinate: OFF."
		existing_pid=$(find_matching_pids | head -n 1 || true)
		if [ -n "$existing_pid" ]; then
			echo "Unmanaged caffeinate detected (PID $existing_pid); not owned by this repo."
		fi
	fi

	if ! command -v "$pmset_bin" >/dev/null 2>&1; then
		return 0
	fi
	if command -v rg >/dev/null 2>&1; then
		"$pmset_bin" -g assertions | rg -n "PreventUserIdleDisplaySleep|PreventUserIdleSystemSleep|PreventDiskIdle|caffeinate" || true
	else
		"$pmset_bin" -g assertions | grep -nE "PreventUserIdleDisplaySleep|PreventUserIdleSystemSleep|PreventDiskIdle|caffeinate" || true
	fi
}

case "$action" in
	start)
		start_caffeinate
		;;
	stop)
		stop_caffeinate
		;;
	stop-all)
		stop_all_caffeinate
		;;
	status)
		status_caffeinate
		;;
	*)
		usage
		exit 2
		;;
esac
