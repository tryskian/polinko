#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
ROOT="$POLINKO_REPO_ROOT"

EXCLUDE_FILE=".git/info/exclude"
MARKER_BEGIN="# polinko-local-privacy begin"
MARKER_END="# polinko-local-privacy end"

LOCAL_EXCLUDE_PATTERNS=(
  "docs/peanut/governance/SESSION_HANDOFF.md"
)

list_tracked_docs() {
  git ls-files 'docs/**/*.md' 'docs/*.md' 'docs/*.json' | sort -u
}

list_skip_worktree_docs() {
  git ls-files -v docs | rg '^S' || true
}

write_exclude_block() {
  mkdir -p "$(dirname "${EXCLUDE_FILE}")"
  touch "${EXCLUDE_FILE}"

  # Remove old managed block if present, then append fresh block.
  awk -v b="${MARKER_BEGIN}" -v e="${MARKER_END}" '
    $0 == b { skip=1; next }
    $0 == e { skip=0; next }
    skip != 1 { print }
  ' "${EXCLUDE_FILE}" >"${EXCLUDE_FILE}.tmp"
  mv "${EXCLUDE_FILE}.tmp" "${EXCLUDE_FILE}"

  {
    echo ""
    echo "${MARKER_BEGIN}"
    echo "# Local internal docs (machine-local)"
    for pattern in "${LOCAL_EXCLUDE_PATTERNS[@]}"; do
      echo "${pattern}"
    done
    echo "${MARKER_END}"
  } >>"${EXCLUDE_FILE}"
}

remove_exclude_block() {
  [[ -f "${EXCLUDE_FILE}" ]] || return 0
  awk -v b="${MARKER_BEGIN}" -v e="${MARKER_END}" '
    $0 == b { skip=1; next }
    $0 == e { skip=0; next }
    skip != 1 { print }
  ' "${EXCLUDE_FILE}" >"${EXCLUDE_FILE}.tmp"
  mv "${EXCLUDE_FILE}.tmp" "${EXCLUDE_FILE}"
}

apply_guard() {
  write_exclude_block
  echo "Local privacy guard applied."
  status_guard
}

status_guard() {
  echo "Skip-worktree docs:"
  if ! list_skip_worktree_docs | rg '^S' >/dev/null 2>&1; then
    echo "(none)"
  else
    list_skip_worktree_docs
  fi
  echo ""
  echo "Local excludes:"
  if [[ -f "${EXCLUDE_FILE}" ]]; then
    local block
    block="$(
      awk -v b="${MARKER_BEGIN}" -v e="${MARKER_END}" '
      $0 == b { show=1; next }
      $0 == e { show=0; next }
      show == 1 { print }
      ' "${EXCLUDE_FILE}" || true
    )"
    if [[ -n "${block}" ]]; then
      printf '%s\n' "${block}"
    else
      echo "(none)"
    fi
  else
    echo "(none)"
  fi
}

clear_guard() {
  if list_skip_worktree_docs | rg '^S' >/dev/null 2>&1; then
    echo "Clearing legacy docs skip-worktree state."
    list_tracked_docs | xargs -r git update-index --no-skip-worktree
  fi
  remove_exclude_block
  echo "Local privacy guard cleared."
  status_guard
}

usage() {
  cat <<'EOF'
Usage: tools/local_privacy_guard.sh [apply|status|clear]
  apply  - install local excludes for machine-local docs
  status - show current local privacy guard state
  clear  - remove local excludes and clear legacy docs skip-worktree state
EOF
}

cmd="${1:-status}"
case "${cmd}" in
  apply) apply_guard ;;
  status) status_guard ;;
  clear) clear_guard ;;
  *)
    usage
    exit 2
    ;;
esac
