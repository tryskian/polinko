#!/usr/bin/env sh

polinko_pid_is_running() {
	_polinko_pid=$1
	[ -n "$_polinko_pid" ] || return 1
	kill -0 "$_polinko_pid" 2>/dev/null || return 1
	_polinko_pid_state=$(
		ps -o stat= -p "$_polinko_pid" 2>/dev/null | tr -d ' ' || true
	)
	case "$_polinko_pid_state" in
		Z*)
			return 1
			;;
	esac
	return 0
}

polinko_require_command() {
	_polinko_command=$1
	_polinko_context=${2:-runtime helper}
	if command -v "$_polinko_command" >/dev/null 2>&1; then
		return 0
	fi
	echo "Missing required command for $_polinko_context: $_polinko_command" >&2
	return 1
}

polinko_wait_for_pid_exit() {
	_polinko_pid=$1
	_polinko_attempts=${2:-50}
	_polinko_sleep_seconds=${3:-0.1}
	_polinko_attempt=0
	while polinko_pid_is_running "$_polinko_pid"; do
		if [ "$_polinko_attempt" -ge "$_polinko_attempts" ]; then
			return 1
		fi
		sleep "$_polinko_sleep_seconds"
		_polinko_attempt=$((_polinko_attempt + 1))
	done
	return 0
}

polinko_process_command() {
	_polinko_pid=$1
	ps -o command= -p "$_polinko_pid" 2>/dev/null || true
}

polinko_parent_pid() {
	_polinko_pid=$1
	ps -o ppid= -p "$_polinko_pid" 2>/dev/null | tr -d ' ' || true
}

if [ "${0##*/}" = "process_lifecycle_common.sh" ]; then
	echo "Source this helper from runtime shell scripts instead of executing it directly." >&2
	exit 2
fi
