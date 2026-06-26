#!/usr/bin/env bash
set -euo pipefail

polinko_repo_root() {
  local lib_dir
  lib_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
  cd -- "$lib_dir/.." && pwd
}

polinko_cd_repo_root() {
  POLINKO_REPO_ROOT="$(polinko_repo_root)"
  cd -- "$POLINKO_REPO_ROOT"
}

polinko_default_python_bin() {
  if [ -n "${PYTHON:-}" ]; then
    printf "%s\n" "$PYTHON"
    return 0
  fi

  local candidate
  for candidate in ./.venv/bin/python3.14 ./.venv/bin/python ./.venv/bin/python3; do
    if [ -x "$candidate" ] && "$candidate" -V >/dev/null 2>&1; then
      printf "%s\n" "$candidate"
      return 0
    fi
  done

  printf "%s\n" python3
}

if [ "${0##*/}" = "repo_root.sh" ]; then
  polinko_repo_root
fi
