#!/usr/bin/env sh

OCR_WORKFLOW_EXPORT_ROOT=""

ocr_workflow_resolve_export_root() {
	_ocr_workflow_export_root=${CGPT_EXPORT_ROOT:-}

	if [ -z "$_ocr_workflow_export_root" ]; then
		_ocr_workflow_export_root=${CGPT_EXPORT_ROOT_DEFAULT:-}
	fi

	printf "%s\n" "$_ocr_workflow_export_root"
}

ocr_workflow_require_export_root() {
	_ocr_workflow_hint_target=$1
	_ocr_workflow_failure_status=${2:-2}
	OCR_WORKFLOW_EXPORT_ROOT=$(ocr_workflow_resolve_export_root)

	if [ -z "$OCR_WORKFLOW_EXPORT_ROOT" ]; then
		echo "CGPT_EXPORT_ROOT is required."
		echo "Run: make $_ocr_workflow_hint_target CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"
		return "$_ocr_workflow_failure_status"
	fi
	if [ ! -d "$OCR_WORKFLOW_EXPORT_ROOT" ]; then
		echo "CGPT export root not found: $OCR_WORKFLOW_EXPORT_ROOT"
		echo "Run: make $_ocr_workflow_hint_target CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT"
		return "$_ocr_workflow_failure_status"
	fi
}

ocr_workflow_use_eval_case_guard() {
	_ocr_workflow_python_runtime=${PYTHON_RUNTIME_SCRIPT:-./tools/python_runtime.sh}
	# shellcheck source=./tools/python_runtime.sh
	. "$_ocr_workflow_python_runtime"
	PYTHON=$(polinko_default_python_bin)
	export PYTHON

	_ocr_workflow_guard_script=${EVAL_CASE_GUARD_SCRIPT:-./tools/eval_case_guard.sh}

	# shellcheck source=./tools/eval_case_guard.sh
	. "$_ocr_workflow_guard_script"
}

if [ "${0##*/}" = "ocr_workflow_common.sh" ]; then
	echo "Source this helper from OCR workflow scripts instead of executing it directly." >&2
	exit 2
fi
