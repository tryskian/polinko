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

polinko_venv_dir() {
	_polinko_venv_value=${VENV:-.venv}
	if [ -z "$_polinko_venv_value" ]; then
		_polinko_venv_value=.venv
	fi
	case "$_polinko_venv_value" in
		/* | ./*)
			printf "%s\n" "$_polinko_venv_value"
			;;
		*)
			printf "./%s\n" "$_polinko_venv_value"
			;;
	esac
}

polinko_default_python_bin() {
	if [ -n "${PYTHON:-}" ]; then
		polinko_require_python_command PYTHON "$PYTHON" "python runtime" || return $?
		printf "%s\n" "$PYTHON"
		return
	fi

	_polinko_venv_dir=$(polinko_venv_dir)
	for candidate in "$_polinko_venv_dir/bin/python3.14" "$_polinko_venv_dir/bin/python3" "$_polinko_venv_dir/bin/python"; do
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
