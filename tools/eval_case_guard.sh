#!/usr/bin/env sh

eval_case_guard_or_exit() {
	if [ "$#" -ne 4 ]; then
		echo "Usage: eval_case_guard_or_exit <cases-json> <missing-message> <missing-hint> <empty-message>" >&2
		exit 2
	fi

	_eval_case_guard_path=$1
	_eval_case_guard_missing_message=$2
	_eval_case_guard_missing_hint=$3
	_eval_case_guard_empty_message=$4

	_eval_case_guard_shell_command_common=${SHELL_COMMAND_COMMON_SCRIPT:-${script_dir:-./tools}/shell_command_common.sh}
	# shellcheck source=./tools/shell_command_common.sh
	. "$_eval_case_guard_shell_command_common"

	if [ ! -f "$_eval_case_guard_path" ]; then
		echo "$_eval_case_guard_missing_message: $_eval_case_guard_path"
		if [ -n "$_eval_case_guard_missing_hint" ]; then
			echo "$_eval_case_guard_missing_hint"
		fi
		exit 1
	fi

	_eval_case_guard_status=0
	if ! polinko_command_available polinko_default_python_bin; then
		_eval_case_guard_python_runtime=${PYTHON_RUNTIME_SCRIPT:-./tools/python_runtime.sh}
		# shellcheck source=./tools/python_runtime.sh
		. "$_eval_case_guard_python_runtime"
	fi
	_eval_case_guard_python=$(polinko_default_python_bin)
	_eval_case_guard_case_count=$("$_eval_case_guard_python" -m tools.count_eval_cases "$_eval_case_guard_path") || _eval_case_guard_status=$?
	if [ "$_eval_case_guard_status" -ne 0 ]; then
		exit "$_eval_case_guard_status"
	fi
	if [ "$_eval_case_guard_case_count" -eq 0 ]; then
		echo "$_eval_case_guard_empty_message"
		exit 0
	fi
}

if [ "${0##*/}" = "eval_case_guard.sh" ]; then
	echo "Source this helper from Make recipes instead of executing it directly." >&2
	exit 2
fi
