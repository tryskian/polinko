#!/usr/bin/env sh

polinko_make_bin() {
	printf "%s\n" "${MAKE:-make}"
}

polinko_require_make_command() {
	_polinko_make_context=${1:-make runtime}
	_polinko_make_bin=$(polinko_make_bin)
	if command -v "$_polinko_make_bin" >/dev/null 2>&1; then
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
