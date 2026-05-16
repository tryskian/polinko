#!/usr/bin/env bash
set -euo pipefail

BRANCH="${END_GIT_BRANCH:-main}"
REMOTE="${END_GIT_REMOTE:-origin}"

fail() {
	echo "end-git-check: FAIL" >&2
	echo "  $1" >&2
	echo "  finish by merging the feature branch, switching to $BRANCH, pulling --ff-only, and rerunning make end-git-check" >&2
	exit 1
}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
	fail "not inside a git worktree"
fi

current_branch="$(git branch --show-current)"
if [ "$current_branch" != "$BRANCH" ]; then
	fail "expected branch $BRANCH, found ${current_branch:-detached HEAD}"
fi

if [ -n "$(git status --porcelain)" ]; then
	git status --short >&2
	fail "working tree is not clean"
fi

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
	fail "remote $REMOTE is not configured"
fi

local_sha="$(git rev-parse "refs/heads/$BRANCH")"
remote_sha="$(git ls-remote --exit-code --heads "$REMOTE" "$BRANCH" | awk '{print $1}')"

if [ -z "$remote_sha" ]; then
	fail "could not resolve $REMOTE/$BRANCH"
fi

if [ "$local_sha" != "$remote_sha" ]; then
	fail "local $BRANCH is not synced with $REMOTE/$BRANCH"
fi

echo "end-git-check: PASS ($BRANCH clean and synced with $REMOTE/$BRANCH)"
