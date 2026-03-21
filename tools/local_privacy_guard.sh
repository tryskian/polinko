#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${ROOT}" ]]; then
  echo "Not inside a git repository."
  exit 1
fi
cd "${ROOT}"

EXCLUDE_FILE=".git/info/exclude"
MARKER_BEGIN="# polinko-local-privacy begin"
MARKER_END="# polinko-local-privacy end"

LOCAL_EXCLUDE_PATTERNS=(
  "docs/INSTANCE_HANDOFF.md"
  "docs/POL1_COMMS.md"
)

list_tracked_docs() {
  git ls-files 'docs/**/*.md' 'docs/*.md' 'docs/*.json' | sort -u
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
  list_tracked_docs | xargs -r git update-index --skip-worktree
  echo "Local privacy guard applied."
  status_guard
}

status_guard() {
  echo "Skip-worktree docs:"
  if ! git ls-files -v docs | rg '^S' >/dev/null 2>&1; then
    echo "(none)"
  else
    git ls-files -v docs | rg '^S'
  fi
  echo ""
  echo "Local excludes:"
  if [[ -f "${EXCLUDE_FILE}" ]]; then
    awk -v b="${MARKER_BEGIN}" -v e="${MARKER_END}" '
      $0 == b { show=1; next }
      $0 == e { show=0; next }
      show == 1 { print }
    ' "${EXCLUDE_FILE}" || true
  else
    echo "(none)"
  fi
}

clear_guard() {
  list_tracked_docs | xargs -r git update-index --no-skip-worktree
  remove_exclude_block
  echo "Local privacy guard cleared."
  status_guard
}

usage() {
  cat <<'EOF'
Usage: tools/local_privacy_guard.sh [apply|status|clear]
  apply  - mark docs as local-only and install local excludes
  status - show current local-only guard state
  clear  - remove local-only guard state
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
