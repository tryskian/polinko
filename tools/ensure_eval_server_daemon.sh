#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
# shellcheck source=tools/make_runtime.sh
source "$script_dir/make_runtime.sh"

polinko_cd_repo_root
ROOT_DIR="$POLINKO_REPO_ROOT"

MAKE_BIN=$(polinko_require_make_command "ensure-eval-server-daemon")

exec "$MAKE_BIN" --no-print-directory server-daemon
