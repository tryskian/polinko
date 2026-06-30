#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
ROOT_DIR="$POLINKO_REPO_ROOT"

echo "[start] starting morning routine in: $ROOT_DIR"
echo "[start] 1/6 workspace context"
printf 'repo root: %s\n' "$ROOT_DIR"
printf 'branch: %s\n' "$(git branch --show-current)"
git status --short --branch

echo "[start] 2/6 github-health"
if ! make --no-print-directory github-health; then
  echo "[start] github-health reported attention; continuing startup."
fi

echo "[start] 3/6 doctor-env"
make --no-print-directory doctor-env

echo "[start] 4/6 caffeinate"
make --no-print-directory caffeinate

echo "[start] 5/6 caffeinate-status"
make --no-print-directory caffeinate-status

echo "[start] 6/6 api-smoke"
make --no-print-directory api-smoke

echo "[start] REHYDRATE PROMPT"
cat <<'EOF'
Morning startup is complete.

Read docs/governance/CHARTER.md, docs/governance/STATE.md, docs/governance/DECISIONS.md, docs/runtime/RUNBOOK.md, docs/runtime/ARCHITECTURE.md, and local docs/peanut/governance/SESSION_HANDOFF.md if present.

Reply in the morning ritual before implementation:

- Context: repo root printed above, host vs devcontainer mode, active branch, clean main or feature branch, and runtime health.
- Kernel map: likely lanes from current docs/state, with one recommended first kernel.
- Startup note: one small issue or risk only if something needs attention.

Apply no-guessing controls: prefer repo-scoped edits and do not modify user shell profile file or global VS Code settings unless explicitly approved in-chat.

This reply is the chat-first alignment pass. Wait for human alignment before implementation.

After alignment, run one active kernel at a time and stop before broadening.
EOF
