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
  git ls-files -v docs | awk '/^S/ { print }'
}

prepare_exclude_file() {
  local exclude_parent
  exclude_parent="$(dirname "${EXCLUDE_FILE}")"
  if ! mkdir -p "$exclude_parent" 2>/dev/null; then
    echo "local-privacy failed to prepare exclude file parent: $exclude_parent" >&2
    return 1
  fi
  if ! touch "${EXCLUDE_FILE}" 2>/dev/null; then
    echo "local-privacy failed to prepare exclude file: ${EXCLUDE_FILE}" >&2
    return 1
  fi
}

rewrite_exclude_without_block() {
  local tmp_file
  tmp_file="${EXCLUDE_FILE}.tmp"
  if ! awk -v b="${MARKER_BEGIN}" -v e="${MARKER_END}" '
    $0 == b { skip=1; next }
    $0 == e { skip=0; next }
    skip != 1 { print }
  ' "${EXCLUDE_FILE}" >"$tmp_file"; then
    echo "local-privacy failed to rewrite exclude file: ${EXCLUDE_FILE}" >&2
    rm -f "$tmp_file"
    return 1
  fi
  if ! mv "$tmp_file" "${EXCLUDE_FILE}"; then
    echo "local-privacy failed to replace exclude file: ${EXCLUDE_FILE}" >&2
    rm -f "$tmp_file"
    return 1
  fi
}

write_exclude_block() {
  prepare_exclude_file || return 1

  # Remove old managed block if present, then append fresh block.
  rewrite_exclude_without_block || return 1

  if ! {
    echo ""
    echo "${MARKER_BEGIN}"
    echo "# Local internal docs (machine-local)"
    for pattern in "${LOCAL_EXCLUDE_PATTERNS[@]}"; do
      echo "${pattern}"
    done
    echo "${MARKER_END}"
  } >>"${EXCLUDE_FILE}"; then
    echo "local-privacy failed to append exclude block: ${EXCLUDE_FILE}" >&2
    return 1
  fi
}

remove_exclude_block() {
  [[ -f "${EXCLUDE_FILE}" ]] || return 0
  rewrite_exclude_without_block
}

apply_guard() {
  write_exclude_block
  echo "Local privacy guard applied."
  status_guard
}

status_guard() {
  local skip_worktree_docs
  skip_worktree_docs=$(list_skip_worktree_docs)
  echo "Skip-worktree docs:"
  if [[ -z "${skip_worktree_docs}" ]]; then
    echo "(none)"
  else
    printf '%s\n' "${skip_worktree_docs}"
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
      ' "${EXCLUDE_FILE}"
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
  local skip_worktree_docs
  skip_worktree_docs=$(list_skip_worktree_docs)
  if [[ -n "${skip_worktree_docs}" ]]; then
    echo "Clearing tracked docs skip-worktree state."
    while IFS= read -r tracked_doc_path; do
      [[ -n "${tracked_doc_path}" ]] || continue
      git update-index --no-skip-worktree -- "${tracked_doc_path}"
    done < <(list_tracked_docs)
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
  clear  - remove local excludes and clear tracked docs skip-worktree state
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
