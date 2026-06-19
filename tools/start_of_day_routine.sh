#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[start] starting morning routine in: $ROOT_DIR"
echo "[start] 1/5 workspace context"
printf 'repo root: %s\n' "$ROOT_DIR"
printf 'branch: %s\n' "$(git branch --show-current)"
git status --short --branch

echo "[start] 2/5 doctor-env"
make --no-print-directory doctor-env

echo "[start] 3/5 caffeinate"
make --no-print-directory caffeinate

echo "[start] 4/5 caffeinate-status"
make --no-print-directory caffeinate-status

echo "[start] 5/5 api-smoke"
make --no-print-directory api-smoke

echo "[start] REHYDRATE PROMPT"
cat <<'EOF'
Morning startup is complete.

Read docs/governance/CHARTER.md, docs/governance/STATE.md, docs/governance/DECISIONS.md, docs/runtime/RUNBOOK.md, docs/runtime/ARCHITECTURE.md, and local docs/peanut/governance/SESSION_HANDOFF.md if present.

Reply in the morning ritual:

- Context: repo root printed above, host vs devcontainer mode, active branch, clean main or feature branch, and runtime health.
- Kernel candidates: likely lanes from current docs/state, with one recommended first kernel.
- Startup note: one small issue or risk only if something needs attention.

Apply no-guessing controls: prefer repo-scoped edits and do not modify user shell profile file or global VS Code settings unless explicitly approved in-chat.

After alignment, run one active kernel at a time and stop before broadening.

Then pause for alignment with the human lead before implementation.
EOF
