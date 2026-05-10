#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[start] starting morning routine in: $ROOT_DIR"
echo "[start] read these docs:"
echo "  - docs/governance/CHARTER.md"
echo "  - docs/governance/STATE.md"
echo "  - docs/governance/DECISIONS.md"
echo "  - docs/runtime/RUNBOOK.md"
echo "  - docs/runtime/ARCHITECTURE.md"
if [ -f "docs/peanut/governance/SESSION_HANDOFF.md" ]; then
  echo "  - docs/peanut/governance/SESSION_HANDOFF.md"
fi

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

echo "[start] done"
