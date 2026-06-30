#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
ROOT="$POLINKO_REPO_ROOT"

venv_dir="${POLINKO_DEVCONTAINER_VENV_DIR:-.venv}"
bootstrap_python="${POLINKO_DEVCONTAINER_BOOTSTRAP_PYTHON:-python3.14}"
venv_python="$venv_dir/bin/python3"

require_command() {
	local label=$1
	local command_name=$2

	if ! command -v "$command_name" >/dev/null 2>&1; then
		printf "setup-devcontainer: missing %s command: %s\n" "$label" "$command_name" >&2
		return 1
	fi
}

require_command "bootstrap Python" "$bootstrap_python"
require_command "npm" "npm"

"$bootstrap_python" -m venv --copies "$venv_dir"

if [ ! -x "$venv_python" ]; then
	printf "setup-devcontainer: expected venv Python not found: %s\n" "$venv_python" >&2
	exit 1
fi

"$venv_python" -m pip install --upgrade pip
"$venv_python" -m pip install -r requirements.txt

if [ -f package-lock.json ]; then
	npm ci --no-audit --no-fund
else
	npm install --no-audit --no-fund
fi
