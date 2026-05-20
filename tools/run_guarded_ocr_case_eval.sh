#!/usr/bin/env sh
set -eu

usage() {
	echo "Usage: run_guarded_ocr_case_eval.sh <cases-json> <missing-message> <missing-hint> <empty-message> -- <command> [args...]" >&2
}

if [ "$#" -lt 6 ]; then
	usage
	exit 2
fi

cases_path=$1
missing_message=$2
missing_hint=$3
empty_message=$4
shift 4

if [ "${1:-}" != "--" ]; then
	usage
	exit 2
fi
shift

if [ "$#" -eq 0 ]; then
	usage
	exit 2
fi

python_bin=${PYTHON:-python3}
guard_script=${EVAL_CASE_GUARD_SCRIPT:-./tools/eval_case_guard.sh}

export PYTHON="$python_bin"

. "$guard_script"
eval_case_guard_or_exit "$cases_path" "$missing_message" "$missing_hint" "$empty_message"

exec "$@"
