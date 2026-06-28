#!/usr/bin/env sh

polinko_pid_is_running() {
	_polinko_pid=$1
	[ -n "$_polinko_pid" ] && kill -0 "$_polinko_pid" 2>/dev/null
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
