#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${ROOT}" ]]; then
	echo "Not inside a git repository."
	exit 1
fi
cd "${ROOT}"

venv_dir="${POLINKO_DEVCONTAINER_VENV_DIR:-.venv}"
portfolio_app_dir="${POLINKO_DEVCONTAINER_PORTFOLIO_APP_DIR:-apps/portfolio}"

python3 -m venv --copies "$venv_dir"
"$venv_dir/bin/python3" -m pip install --upgrade pip
"$venv_dir/bin/python3" -m pip install -r requirements.txt

if [ -f package-lock.json ]; then
	npm ci --no-audit --no-fund
else
	npm install --no-audit --no-fund
fi

if [ -f "$portfolio_app_dir/package.json" ]; then
	if [ -f "$portfolio_app_dir/package-lock.json" ]; then
		npm --prefix "$portfolio_app_dir" ci --no-audit --no-fund
	else
		npm --prefix "$portfolio_app_dir" install --no-audit --no-fund
	fi
else
	echo "Skipping portfolio npm install; source app not present at $portfolio_app_dir/package.json."
fi
