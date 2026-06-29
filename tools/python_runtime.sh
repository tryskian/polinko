#!/usr/bin/env sh

polinko_default_python_bin() {
	if [ -n "${PYTHON:-}" ]; then
		if ! command -v "$PYTHON" >/dev/null 2>&1; then
			printf "Configured PYTHON is not executable or not on PATH: %s\n" "$PYTHON" >&2
			return 2
		fi
		printf "%s\n" "$PYTHON"
		return
	fi

	for candidate in ./.venv/bin/python3.14 ./.venv/bin/python ./.venv/bin/python3; do
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
