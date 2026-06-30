#!/usr/bin/env sh

polinko_require_python_command() {
	_polinko_python_name=$1
	_polinko_python_value=$2
	_polinko_python_context=${3:-python runtime}
	if command -v "$_polinko_python_value" >/dev/null 2>&1; then
		return 0
	fi
	printf "Configured %s is not executable or not on PATH for %s: %s\n" \
		"$_polinko_python_name" \
		"$_polinko_python_context" \
		"$_polinko_python_value" >&2
	return 2
}

polinko_default_python_bin() {
	if [ -n "${PYTHON:-}" ]; then
		polinko_require_python_command PYTHON "$PYTHON" "python runtime" || return $?
		printf "%s\n" "$PYTHON"
		return
	fi

	for candidate in ./.venv/bin/python3.14 ./.venv/bin/python3 ./.venv/bin/python; do
		if [ -x "$candidate" ] && "$candidate" -V >/dev/null 2>&1; then
			printf "%s\n" "$candidate"
			return
		fi
	done

	if command -v python3 >/dev/null 2>&1; then
		printf "%s\n" python3
		return
	fi

	printf "No usable Python interpreter found.\n" >&2
	return 2
}

if [ "${0##*/}" = "python_runtime.sh" ]; then
	echo "Source this helper from runtime shell scripts instead of executing it directly." >&2
	exit 2
fi
