#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/repo_root.sh
source "$script_dir/repo_root.sh"

polinko_cd_repo_root
ROOT_DIR="$POLINKO_REPO_ROOT"

START_TOTAL_STEPS=7
start_step_number=0

start_step() {
  start_step_number=$((start_step_number + 1))
  printf '[start] %s/%s %s\n' "$start_step_number" "$START_TOTAL_STEPS" "$1"
}

echo "[start] starting morning routine in: $ROOT_DIR"
start_step "workspace context"
printf 'repo root: %s\n' "$ROOT_DIR"
printf 'branch: %s\n' "$(git branch --show-current)"
git status --short --branch

start_step "github-health"
if ! make --no-print-directory github-health; then
  echo "[start] github-health reported attention; continuing startup."
fi

start_step "doctor-env"
make --no-print-directory doctor-env

start_step "caffeinate"
make --no-print-directory caffeinate

start_step "caffeinate-status"
make --no-print-directory caffeinate-status

start_step "server-daemon"
make --no-print-directory server-daemon

start_step "api-smoke"
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
Use the QA browser / DevTools MCP path for rendered UI checks; Playwright stays a separate explicit local-browser helper surface.

This reply is the chat-first alignment pass. Wait for human alignment before implementation.

After alignment, run one active kernel at a time and stop before broadening.
EOF
