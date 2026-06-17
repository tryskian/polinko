#!/usr/bin/env sh

ocr_workflow_use_eval_case_guard() {
	PYTHON=${PYTHON:-python3}
	export PYTHON

	_ocr_workflow_guard_script=${EVAL_CASE_GUARD_SCRIPT:-./tools/eval_case_guard.sh}

	# shellcheck source=./tools/eval_case_guard.sh
	. "$_ocr_workflow_guard_script"
}

if [ "${0##*/}" = "ocr_workflow_common.sh" ]; then
	echo "Source this helper from OCR workflow scripts instead of executing it directly." >&2
	exit 2
fi
