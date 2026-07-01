#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
ROOT_DIR="$POLINKO_REPO_ROOT"

MAKE_BIN="${MAKE:-make}"
if ! command -v "$MAKE_BIN" >/dev/null 2>&1; then
	echo "ensure-eval-server-daemon: missing make command: $MAKE_BIN" >&2
	exit 2
fi

exec "$MAKE_BIN" --no-print-directory server-daemon
