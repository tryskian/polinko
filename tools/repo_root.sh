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

if [ "${0##*/}" = "repo_root.sh" ]; then
  polinko_repo_root
fi
