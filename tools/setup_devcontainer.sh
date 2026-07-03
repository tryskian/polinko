#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"
# shellcheck source=tools/process_lifecycle_common.sh
. "$script_dir/process_lifecycle_common.sh"

polinko_cd_repo_root
ROOT="$POLINKO_REPO_ROOT"

venv_dir="${POLINKO_DEVCONTAINER_VENV_DIR:-.venv}"
bootstrap_python="${POLINKO_DEVCONTAINER_BOOTSTRAP_PYTHON:-python3.14}"
venv_python="$venv_dir/bin/python3"

run_setup_step() {
	local label=$1
	shift

	if ! "$@"; then
		printf "setup-devcontainer: failed to %s\n" "$label" >&2
		return 1
	fi
}

polinko_require_labeled_command "$bootstrap_python" "bootstrap Python" "setup-devcontainer"
polinko_require_labeled_command "npm" "npm" "setup-devcontainer"

run_setup_step "create virtual environment: $venv_dir" "$bootstrap_python" -m venv --copies "$venv_dir"

if [ ! -x "$venv_python" ]; then
	printf "setup-devcontainer: expected venv Python not found: %s\n" "$venv_python" >&2
	exit 1
fi

run_setup_step "upgrade pip" "$venv_python" -m pip install --upgrade pip
run_setup_step "install Python requirements" "$venv_python" -m pip install -r requirements.txt

if [ -f package-lock.json ]; then
	run_setup_step "install Node dependencies from lockfile" npm ci --no-audit --no-fund
else
	run_setup_step "install Node dependencies" npm install --no-audit --no-fund
fi
