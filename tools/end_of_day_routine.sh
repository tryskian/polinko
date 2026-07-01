#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
ROOT_DIR="$POLINKO_REPO_ROOT"

CORE_STEPS=(
  "end-docs-check|make --no-print-directory end-docs-check"
  "transcript-fix|make --no-print-directory transcript-fix"
  "transcript-check|make --no-print-directory transcript-check"
  "doctor-env|make --no-print-directory doctor-env"
  "scripts-check|make --no-print-directory scripts-check"
  "path-leak-check|make --no-print-directory path-leak-check"
  "risk-scan|make --no-print-directory risk-scan"
  "operator-command-check|make --no-print-directory operator-command-check"
  "ci-python-style|make --no-print-directory ci-python-style"
  "ci-python-type-check|make --no-print-directory ci-python-type-check"
  "lint-docs|make --no-print-directory lint-docs"
  "package-install-check|make --no-print-directory package-install-check"
  "test|make --no-print-directory test"
  "git diff --check|git diff --check"
  "security-checks|make --no-print-directory security-checks"
)

TOTAL_STEPS=${#CORE_STEPS[@]}
if [ "${END_SKIP_STOP:-}" = "1" ]; then
  :
else
  TOTAL_STEPS=$((TOTAL_STEPS + 1))
fi
if [ "${END_SKIP_GIT_CHECK:-}" = "1" ]; then
  :
else
  TOTAL_STEPS=$((TOTAL_STEPS + 3))
fi

STEP=1

run_step() {
  local label="$1"
  shift
  echo "[end] ${STEP}/${TOTAL_STEPS} ${label}"
  "$@"
  STEP=$((STEP + 1))
}

run_planned_step() {
  local record="$1"
  local label="${record%%|*}"
  local command="${record#*|}"
  local argv=()

  read -r -a argv <<< "$command"
  run_step "$label" "${argv[@]}"
}

echo "[end] starting end-of-day routine in: $ROOT_DIR"
for planned_step in "${CORE_STEPS[@]}"; do
  run_planned_step "$planned_step"
done

if [ "${END_SKIP_STOP:-}" = "1" ]; then
  echo "[end] stop background tasks skipped (preflight only; day is not closed)"
else
  run_step "stop background tasks" make --no-print-directory end-stop
fi

if [ "${END_SKIP_GIT_CHECK:-}" = "1" ]; then
  echo "[end] git closeout skipped (preflight only; day is not closed)"
else
  run_step "github-health" make --no-print-directory github-health
  run_step "git-prune-stale-refs" make --no-print-directory git-prune-stale-refs
  run_step "end-git-check" make --no-print-directory end-git-check
fi

echo "[end] done"
