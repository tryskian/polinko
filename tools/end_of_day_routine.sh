#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
ROOT_DIR="$POLINKO_REPO_ROOT"

CORE_STEP_LABELS=(
  "end-docs-check"
  "transcript-fix"
  "transcript-check"
  "doctor-env"
  "scripts-check"
  "path-leak-check"
  "risk-scan"
  "runtime-tool-reference-check"
  "operator-command-check"
  "ci-python-style"
  "ci-python-type-check"
  "lint-docs"
  "package-install-check"
  "test"
  "git diff --check"
  "security-checks"
)

TOTAL_STEPS=${#CORE_STEP_LABELS[@]}
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

run_make_step() {
  local label="$1"
  local target="$2"
  run_step "$label" make --no-print-directory "$target"
}

run_core_step() {
  local label="$1"

  case "$label" in
    "git diff --check") run_step "$label" git diff --check ;;
    end-docs-check | \
      transcript-fix | \
      transcript-check | \
      doctor-env | \
      scripts-check | \
      path-leak-check | \
      risk-scan | \
      runtime-tool-reference-check | \
      operator-command-check | \
      ci-python-style | \
      ci-python-type-check | \
      lint-docs | \
      package-install-check | \
      test | \
      security-checks)
      run_make_step "$label" "$label"
      ;;
    *)
      echo "[end] unknown closeout step: $label" >&2
      exit 2
      ;;
  esac
}

echo "[end] starting end-of-day routine in: $ROOT_DIR"
for core_step_label in "${CORE_STEP_LABELS[@]}"; do
  run_core_step "$core_step_label"
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
