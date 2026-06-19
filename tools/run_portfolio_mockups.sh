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

python_bin=${PYTHON:-python3}
launcher_python=${PORTFOLIO_MOCKUP_LAUNCHER_PYTHON:-python3}
mockup_dir=${PORTFOLIO_MOCKUP_DIR:-docs/peanut/assets/portfolio-mockups}
mockup_port=${PORTFOLIO_MOCKUP_PORT:-8765}
mockup_host=${PORTFOLIO_MOCKUP_HOST:-127.0.0.1}
mockup_url=${PORTFOLIO_MOCKUP_URL:-http://127.0.0.1:${mockup_port}/landing-mockups.html}
pid_file=${PORTFOLIO_MOCKUP_PID_FILE:-/tmp/polinko-portfolio-mockups.pid}
log_file=${PORTFOLIO_MOCKUP_LOG:-/tmp/polinko-portfolio-mockups.log}

launch_detached_mockup_server() {
	"$launcher_python" - "$pid_file" "$log_file" "$python_bin" "$mockup_port" "$mockup_host" "$mockup_dir" <<'PY'
import subprocess
import sys

pid_file, log_file, python_bin, mockup_port, mockup_host, mockup_dir = sys.argv[1:7]
args = [
    python_bin,
    "-m",
    "http.server",
    mockup_port,
    "--bind",
    mockup_host,
    "--directory",
    mockup_dir,
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

start_mockup_server() {
	if [ ! -f "$mockup_dir/landing-mockups.html" ]; then
		echo "Portfolio mockup not found: $mockup_dir/landing-mockups.html"
		exit 1
	fi

	if curl -fsS "$mockup_url" >/dev/null 2>&1; then
		echo "portfolio mockup server already reachable: $mockup_url"
		exit 0
	fi

	if [ -f "$pid_file" ]; then
		pid=$(cat "$pid_file" 2>/dev/null || true)
		if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
			kill "$pid" 2>/dev/null || true
			sleep 0.1
		fi
		rm -f "$pid_file"
	fi

	mkdir -p "$(dirname "$pid_file")" "$(dirname "$log_file")"
	if ! launch_detached_mockup_server; then
		rm -f "$pid_file"
		echo "Failed to start portfolio mockup server. Check $log_file."
		exit 1
	fi
	pid=$(cat "$pid_file" 2>/dev/null || true)
	sleep 0.5
	if kill -0 "$pid" 2>/dev/null; then
		echo "portfolio mockup server started (PID $pid, log: $log_file)."
	else
		rm -f "$pid_file"
		echo "Failed to start portfolio mockup server. Check $log_file."
		exit 1
	fi
}

status_mockup_server() {
	if [ -f "$pid_file" ]; then
		pid=$(cat "$pid_file" 2>/dev/null || true)
		if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
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
	echo "portfolio mockup server: OFF."
}

stop_mockup_server() {
	if [ ! -f "$pid_file" ]; then
		echo "No portfolio mockup PID file found."
		exit 0
	fi
	pid=$(cat "$pid_file" 2>/dev/null || true)
	if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
		kill "$pid"
		sleep 0.1
		echo "portfolio mockup server stopped (PID $pid)."
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
