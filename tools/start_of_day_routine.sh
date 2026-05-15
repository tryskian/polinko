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
Read docs/governance/CHARTER.md, docs/governance/STATE.md, docs/governance/DECISIONS.md, docs/runtime/RUNBOOK.md, docs/runtime/ARCHITECTURE.md, and local docs/peanut/governance/SESSION_HANDOFF.md if present.

In 5 bullets: current state, risks, and next kernel.

Before starting implementation, confirm environment/workspace context: canonical repo path is /abs/path/to/polinko, confirm host vs devcontainer mode, confirm active git branch, and say whether the thread is on clean main or a feature branch.

Apply no-guessing controls: prefer repo-scoped edits and do not modify user shell profile file or global VS Code settings unless explicitly approved in-chat.

Run in one active kernel at a time.

Then execute the Next Slice from SESSION_HANDOFF with minimal behavior drift and full validation.
EOF
