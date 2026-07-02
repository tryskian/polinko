#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root

MAKE_BIN="${MAKE:-make}"
if ! command -v "$MAKE_BIN" >/dev/null 2>&1; then
	echo "session-status: missing make command: $MAKE_BIN" >&2
	exit 2
fi

STATUS_STEP_LABELS=(
	"Server"
	"Eval sidecar"
	"Keep-awake"
)

run_make_status() {
	label=$1
	target=$2
	echo "== $label =="
	"$MAKE_BIN" --no-print-directory "$target"
}

run_status_step() {
	label=$1
	case "$label" in
		"Server")
			run_make_status "$label" "server-daemon-status"
			;;
		"Eval sidecar")
			run_make_status "$label" "eval-sidecar-status"
			;;
		"Keep-awake")
			run_make_status "$label" "caffeinate-status"
			;;
		*)
			echo "session-status: unknown status step: $label" >&2
			return 2
			;;
	esac
}

status=0
first=1
for label in "${STATUS_STEP_LABELS[@]}"; do
	if [ "$first" -eq 0 ]; then
		echo ""
	fi
	first=0
	if run_status_step "$label"; then
		continue
	fi
	step_status=$?
	status=$step_status
done

exit "$status"
