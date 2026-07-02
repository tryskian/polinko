#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root

activate_path="./.venv/bin/activate"

if [ ! -f "$activate_path" ]; then
	echo "No local activation script found (checked $activate_path)."
	exit 1
fi

echo "Opening shell with virtual environment: $activate_path"
# shellcheck source=/dev/null
. "$activate_path"
echo "VIRTUAL_ENV=$VIRTUAL_ENV"
exec "$SHELL" -i
