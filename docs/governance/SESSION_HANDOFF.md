<!-- @format -->

# Session Handoff

Last updated: 2026-04-23

## Startup

1. Say the peanut prompt:
   - `hi! new day!`
2. Read docs in this order:
   - `docs/governance/CHARTER.md`
   - `docs/governance/STATE.md`
   - `docs/runtime/RUNBOOK.md`
   - this file
3. Confirm working location and branch:
   - canonical repo or deliberate worktree
   - feature branch for active implementation
4. Give the morning kernel breakdown before editing.

## Current Snapshot

- Backend/API remains canonical; the website is a doorway only.
- Public site is live at `https://www.krystian.io/` with apex redirecting.
- Public repo/docs are the main proof surface.
- README/docs/proof cleanup is merged on `main`:
  - `#346` docs entrypoints/navigation
  - `#347` README badges + public proof packet
- Current in-flight branch:
  - `codex/bigbrain/favicon-png-swap`
- Current branch checkpoints:
  - `72e2333` `Swap portfolio favicon to PNG`
  - `ab90842` `Update portfolio identity copy`
- Current site copy and asset state:
  - public site uses `favicon.png`
  - visible identity line uses `design creative`
- OpenAI application push is already complete; do not split into overlapping
  engineering applications this cycle.
- Local application tailoring work exists under `docs/peanut/` and `output/pdf/`
  but remains ignored/local-only.

## Next Slice

1. Merge the current favicon/site-copy branch when ready.
2. Keep site follow-ups small only:
   - contact/social placement polish
   - no rebuild
3. Continue role-specific local application materials only as needed.

## Guardrails

- Keep `STATE` and `SESSION_HANDOFF` short and current-only.
- Keep `DECISIONS` for durable decisions only.
- Keep the public site austere; the repo carries the depth.
- Keep private application materials local/ignored.

## Session Close

- Follow `docs/runtime/RUNBOOK.md` (`End-of-Day Routine`).
- Finish merged and clean on `main`.
