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

	if [ ! -f "$_eval_case_guard_path" ]; then
		echo "$_eval_case_guard_missing_message: $_eval_case_guard_path"
		if [ -n "$_eval_case_guard_missing_hint" ]; then
			echo "$_eval_case_guard_missing_hint"
		fi
		exit 1
	fi

	_eval_case_guard_status=0
	_eval_case_guard_case_count=$(${PYTHON:-python3} -m tools.count_eval_cases "$_eval_case_guard_path") || _eval_case_guard_status=$?
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
