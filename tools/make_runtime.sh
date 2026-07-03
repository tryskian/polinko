#!/usr/bin/env sh

_polinko_shell_command_common=${SHELL_COMMAND_COMMON_SCRIPT:-${script_dir:-./tools}/shell_command_common.sh}
# shellcheck source=./tools/shell_command_common.sh
. "$_polinko_shell_command_common"

polinko_make_bin() {
	printf "%s\n" "${MAKE:-make}"
}

polinko_require_make_command() {
	_polinko_make_context=${1:-make runtime}
	_polinko_make_bin=$(polinko_make_bin)
	if polinko_command_available "$_polinko_make_bin"; then
		printf "%s\n" "$_polinko_make_bin"
		return 0
	fi
	printf "%s: missing make command: %s\n" \
		"$_polinko_make_context" \
		"$_polinko_make_bin" >&2
	return 2
}

if [ "${0##*/}" = "make_runtime.sh" ]; then
	echo "Source this helper from runtime shell scripts instead of executing it directly." >&2
	exit 2
fi
