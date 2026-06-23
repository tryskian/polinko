#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
ROOT_DIR="$POLINKO_REPO_ROOT"

TOTAL_STEPS=17
if [ "${END_SKIP_STOP:-}" = "1" ]; then
  TOTAL_STEPS=$((TOTAL_STEPS - 1))
fi
if [ "${END_SKIP_GIT_CHECK:-}" = "1" ]; then
  TOTAL_STEPS=$((TOTAL_STEPS - 1))
fi

STEP=1

run_step() {
  local label="$1"
  shift
  echo "[end] ${STEP}/${TOTAL_STEPS} ${label}"
  "$@"
  STEP=$((STEP + 1))
}

echo "[end] starting end-of-day routine in: $ROOT_DIR"
run_step "end-docs-check" make --no-print-directory end-docs-check
run_step "transcript-fix" make --no-print-directory transcript-fix
run_step "transcript-check" make --no-print-directory transcript-check
run_step "doctor-env" make --no-print-directory doctor-env
run_step "scripts-check" make --no-print-directory scripts-check
run_step "path-leak-check" make --no-print-directory path-leak-check
run_step "risk-scan" make --no-print-directory risk-scan
run_step "operator-alias-check" make --no-print-directory operator-alias-check
run_step "ci-python-style" make --no-print-directory ci-python-style
run_step "ci-python-type-check" make --no-print-directory ci-python-type-check
run_step "lint-docs" make --no-print-directory lint-docs
run_step "package-install-check" make --no-print-directory package-install-check
run_step "test" make --no-print-directory test
run_step "git diff --check" git diff --check
run_step "security-checks" make --no-print-directory security-checks

if [ "${END_SKIP_STOP:-}" = "1" ]; then
  echo "[end] stop background tasks skipped (preflight only; day is not closed)"
else
  run_step "stop background tasks" make --no-print-directory end-stop
fi

if [ "${END_SKIP_GIT_CHECK:-}" = "1" ]; then
  echo "[end] git closeout skipped (preflight only; day is not closed)"
else
  run_step "end-git-check" make --no-print-directory end-git-check
fi

echo "[end] done"
