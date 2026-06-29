#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: manage_caffeinate.sh {start|stop|stop-all|status|activity}" >&2
}

if [ "$#" -ne 1 ]; then
	usage
	exit 2
fi

case "$1" in
	start | stop | stop-all | status | activity) ;;
	*)
		usage
		exit 2
		;;
esac

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
polinko_cd_repo_root
# shellcheck source=tools/python_runtime.sh
. "$script_dir/python_runtime.sh"

launcher_python=${CAFFEINATE_LAUNCHER_PYTHON:-$(polinko_default_python_bin)}
polinko_require_python_command \
	CAFFEINATE_LAUNCHER_PYTHON \
	"$launcher_python" \
	"caffeinate manager"
detached_launcher="$POLINKO_REPO_ROOT/tools/launch_detached_process.py"
export CAFFEINATE_DETACHED_LAUNCHER=${CAFFEINATE_DETACHED_LAUNCHER:-"$detached_launcher"}
if [ -z "${CAFFEINATE_MATCH_PATTERN:-}" ]; then
	CAFFEINATE_MATCH_PATTERN='^/usr/bin/caffeinate -d -i -m( |$)'
fi
export CAFFEINATE_MATCH_PATTERN

exec "$launcher_python" "$POLINKO_REPO_ROOT/tools/manage_caffeinate.py" "$1"
