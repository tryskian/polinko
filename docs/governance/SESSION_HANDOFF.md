<!-- @format -->

# Session Handoff

Last updated: 2026-04-21

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
- Current in-flight branch for the latest polish/docs work:
  - `codex/bigbrain/repo-docs-cleanup`
- Latest local checkpoint on that branch:
  - `d8d5aee` `Polish portfolio spacing and canonical URL`
- Governance docs are being trimmed to remove duplication and stale detail:
  - `CHARTER` = durable rules
  - `STATE` = current truth
  - `SESSION_HANDOFF` = next-session operating context
- OpenAI application push is already complete; do not split into overlapping
  engineering applications this cycle.

## Next Slice

1. Finish docs cleanup and merge the current branch.
2. Keep site follow-ups small only:
   - socials/contact polish
   - favicon
   - no rebuild
3. Add static D3/SVG evidence diagrams beside Mermaid when ready.

## Guardrails

- Keep `STATE` and `SESSION_HANDOFF` short and current-only.
- Keep `DECISIONS` for durable decisions only.
- Keep the public site austere; the repo carries the depth.
- Keep private application materials local/ignored.

## Session Close

- Follow `docs/runtime/RUNBOOK.md` (`End-of-Day Routine`).
- Finish merged and clean on `main`.
