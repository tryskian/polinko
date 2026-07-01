#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root

REMOTE="${END_GIT_REMOTE:-origin}"

fail() {
	echo "git-prune-stale-refs: FAIL" >&2
	echo "  $1" >&2
	echo "  check the configured git remote and rerun make git-prune-stale-refs" >&2
	exit 1
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
	fail "not inside a git worktree"
fi

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
	fail "remote $REMOTE is not configured"
fi

if ! git remote prune "$REMOTE"; then
	fail "git remote prune $REMOTE failed"
fi

echo "git-prune-stale-refs: PASS (checked stale refs for $REMOTE)"
