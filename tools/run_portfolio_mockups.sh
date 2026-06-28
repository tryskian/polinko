#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: run_portfolio_mockups.sh {start|status|stop}" >&2
}

if [ "$#" -eq 0 ]; then
	action=start
elif [ "$#" -eq 1 ]; then
	action=$1
else
	usage
	exit 2
fi

mockup_dir=${PORTFOLIO_MOCKUP_DIR:-docs/peanut/assets/portfolio-mockups}
mockup_port=${PORTFOLIO_MOCKUP_PORT:-8765}
mockup_host=${PORTFOLIO_MOCKUP_HOST:-127.0.0.1}
mockup_url=${PORTFOLIO_MOCKUP_URL:-http://127.0.0.1:${mockup_port}/landing-mockups.html}
pid_file=${PORTFOLIO_MOCKUP_PID_FILE:-/tmp/polinko-portfolio-mockups.pid}
log_file=${PORTFOLIO_MOCKUP_LOG:-/tmp/polinko-portfolio-mockups.log}
mockup_start_attempts=${PORTFOLIO_MOCKUP_START_ATTEMPTS:-100}
mockup_start_sleep_seconds=${PORTFOLIO_MOCKUP_START_SLEEP_SECONDS:-0.1}
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
polinko_cd_repo_root
detached_launcher="$POLINKO_REPO_ROOT/tools/launch_detached_process.py"
# shellcheck source=tools/python_runtime.sh
. "$script_dir/python_runtime.sh"
# shellcheck source=tools/process_lifecycle_common.sh
. "$script_dir/process_lifecycle_common.sh"
python_bin=$(polinko_default_python_bin)
launcher_python=${PORTFOLIO_MOCKUP_LAUNCHER_PYTHON:-$python_bin}

launch_detached_mockup_server() {
	"$launcher_python" "$detached_launcher" \
		--pid-file "$pid_file" \
		--log-file "$log_file" \
		-- \
		"$python_bin" -m http.server "$mockup_port" \
		--bind "$mockup_host" \
		--directory "$mockup_dir"
}

mockup_server_pids() {
	if ! command -v lsof >/dev/null 2>&1; then
		return 0
	fi
	lsof -nP -iTCP:"$mockup_port" -sTCP:LISTEN -t 2>/dev/null || true
}

is_expected_mockup_server() {
	local pid=$1
	local command
	command=$(polinko_process_command "$pid")
	[[ "$command" == *"http.server"* ]] &&
		[[ "$command" == *"$mockup_port"* ]] &&
		[[ "$command" == *"$mockup_dir"* ]]
}

find_expected_mockup_pid() {
	local pid
	for pid in $(mockup_server_pids); do
		if polinko_pid_is_running "$pid" && is_expected_mockup_server "$pid"; then
			printf "%s\n" "$pid"
			return 0
		fi
	done
	return 1
}

wait_for_mockup_stop() {
	local pid=$1
	if ! polinko_wait_for_pid_exit "$pid" 30 0.1; then
		echo "portfolio mockup server did not exit after stop signal (PID $pid)."
		return 1
	fi
}

wait_for_mockup_ready() {
	local pid=$1
	local attempt=0
	while [ "$attempt" -lt "$mockup_start_attempts" ]; do
		if ! polinko_pid_is_running "$pid"; then
			return 2
		fi
		if curl -fsS "$mockup_url" >/dev/null 2>&1; then
			return 0
		fi
		sleep "$mockup_start_sleep_seconds"
		attempt=$((attempt + 1))
	done
	return 1
}

adopt_reachable_mockup_server() {
	local pid
	pid=$(find_expected_mockup_pid || true)
	if [ -z "$pid" ]; then
		return 1
	fi
	mkdir -p "$(dirname "$pid_file")"
	printf "%s" "$pid" >"$pid_file"
	echo "portfolio mockup server already reachable; adopted PID $pid for lifecycle management: $mockup_url"
}

start_mockup_server() {
	if [ ! -f "$mockup_dir/landing-mockups.html" ]; then
		echo "Portfolio mockup not found: $mockup_dir/landing-mockups.html"
		exit 1
	fi
	polinko_require_command curl "portfolio mockup HTTP reachability checks"

	if [ -f "$pid_file" ]; then
		pid=$(cat "$pid_file" 2>/dev/null || true)
		if polinko_pid_is_running "$pid"; then
			if is_expected_mockup_server "$pid"; then
				if curl -fsS "$mockup_url" >/dev/null 2>&1; then
					echo "portfolio mockup server already running (PID $pid, URL: $mockup_url)."
					exit 0
				fi
				kill "$pid" 2>/dev/null || true
				if ! wait_for_mockup_stop "$pid"; then
					exit 1
				fi
			else
				echo "portfolio mockup PID file points to a non-mockup process; cleaning up."
			fi
		fi
		rm -f "$pid_file"
	fi

	if curl -fsS "$mockup_url" >/dev/null 2>&1; then
		if adopt_reachable_mockup_server; then
			exit 0
		fi
		echo "portfolio mockup server is reachable but has no managed PID file: $mockup_url"
		echo "Stop the unmanaged process or choose a free PORTFOLIO_MOCKUP_PORT."
		exit 1
	fi

	mkdir -p "$(dirname "$pid_file")" "$(dirname "$log_file")"
	if ! launch_detached_mockup_server; then
		rm -f "$pid_file"
		echo "Failed to start portfolio mockup server. Check $log_file."
		exit 1
	fi
	pid=$(cat "$pid_file" 2>/dev/null || true)
	if wait_for_mockup_ready "$pid"; then
		echo "portfolio mockup server started (PID $pid, log: $log_file)."
	else
		rm -f "$pid_file"
		echo "Failed to start portfolio mockup server. Check $log_file."
		exit 1
	fi
}

status_mockup_server() {
	polinko_require_command curl "portfolio mockup status reachability check"

	if [ -f "$pid_file" ]; then
		pid=$(cat "$pid_file" 2>/dev/null || true)
		if polinko_pid_is_running "$pid"; then
			if ! is_expected_mockup_server "$pid"; then
				echo "portfolio mockup server: STALE PID file (PID $pid is not a matching mockup server)."
				exit 1
			fi
			if curl -fsS "$mockup_url" >/dev/null 2>&1; then
				echo "portfolio mockup server: RUNNING (PID $pid, URL: $mockup_url)."
				exit 0
			fi
			echo "portfolio mockup server: RUNNING (PID $pid), but URL is not reachable: $mockup_url"
			exit 1
		fi
		echo "portfolio mockup server: STALE PID file."
		exit 1
	fi
	if curl -fsS "$mockup_url" >/dev/null 2>&1; then
		pid=$(find_expected_mockup_pid || true)
		if [ -n "$pid" ]; then
			echo "portfolio mockup server: RUNNING without managed PID file (PID $pid, URL: $mockup_url)."
		else
			echo "portfolio mockup server: URL reachable without managed PID file: $mockup_url"
		fi
		exit 1
	fi
	echo "portfolio mockup server: OFF."
}

stop_mockup_server() {
	if [ ! -f "$pid_file" ]; then
		polinko_require_command curl "portfolio mockup stop reachability check"

		if curl -fsS "$mockup_url" >/dev/null 2>&1; then
			pid=$(find_expected_mockup_pid || true)
			if [ -n "$pid" ]; then
				kill "$pid"
				if ! wait_for_mockup_stop "$pid"; then
					exit 1
				fi
				echo "portfolio mockup server stopped (PID $pid)."
				exit 0
			fi
			echo "No portfolio mockup PID file found, but URL is still reachable: $mockup_url"
			exit 1
		fi
		echo "No portfolio mockup PID file found."
		exit 0
	fi
	pid=$(cat "$pid_file" 2>/dev/null || true)
	if polinko_pid_is_running "$pid"; then
		if is_expected_mockup_server "$pid"; then
			kill "$pid"
			if ! wait_for_mockup_stop "$pid"; then
				exit 1
			fi
			echo "portfolio mockup server stopped (PID $pid)."
		else
			echo "portfolio mockup PID file points to a non-mockup process; cleaning up."
		fi
	else
		echo "Stale portfolio mockup PID file; cleaning up."
	fi
	rm -f "$pid_file"
}

case "$action" in
	start)
		start_mockup_server
		;;
	status)
		status_mockup_server
		;;
	stop)
		stop_mockup_server
		;;
	*)
		usage
		exit 2
		;;
esac
