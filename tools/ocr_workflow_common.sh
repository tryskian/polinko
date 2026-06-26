#!/usr/bin/env sh

_ocr_workflow_default_python_bin() {
	if [ -n "${PYTHON:-}" ]; then
		printf "%s\n" "$PYTHON"
		return
	fi
	for _ocr_workflow_candidate in ./.venv/bin/python3.14 ./.venv/bin/python ./.venv/bin/python3; do
		if [ -x "$_ocr_workflow_candidate" ] && "$_ocr_workflow_candidate" -V >/dev/null 2>&1; then
			printf "%s\n" "$_ocr_workflow_candidate"
			return
		fi
	done
	printf "%s\n" python3
}

ocr_workflow_use_eval_case_guard() {
	PYTHON=$(_ocr_workflow_default_python_bin)
	export PYTHON

	_ocr_workflow_guard_script=${EVAL_CASE_GUARD_SCRIPT:-./tools/eval_case_guard.sh}

	# shellcheck source=./tools/eval_case_guard.sh
	. "$_ocr_workflow_guard_script"
}

if [ "${0##*/}" = "ocr_workflow_common.sh" ]; then
	echo "Source this helper from OCR workflow scripts instead of executing it directly." >&2
	exit 2
fi
