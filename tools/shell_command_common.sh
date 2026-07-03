#!/usr/bin/env sh

polinko_command_available() {
	_polinko_command=$1
	if command -v "$_polinko_command" >/dev/null 2>&1; then
		return 0
	fi
	return 1
}

polinko_require_command() {
	_polinko_command=$1
	_polinko_context=${2:-runtime helper}
	if polinko_command_available "$_polinko_command"; then
		return 0
	fi
	echo "Missing required command for $_polinko_context: $_polinko_command" >&2
	return 1
}

polinko_require_labeled_command() {
	_polinko_command=$1
	_polinko_label=$2
	_polinko_context=${3:-runtime helper}
	if polinko_command_available "$_polinko_command"; then
		return 0
	fi
	printf "%s: missing %s command: %s\n" \
		"$_polinko_context" \
		"$_polinko_label" \
		"$_polinko_command" >&2
	return 1
}

if [ "${0##*/}" = "shell_command_common.sh" ]; then
	echo "Source this helper from runtime shell scripts instead of executing it directly." >&2
	exit 2
fi
