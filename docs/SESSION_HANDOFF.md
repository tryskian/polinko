<!-- @format -->

# Session Handoff (Current State Only)

## Date

- Update this at end-of-day only (YYYY-MM-DD).

## Current Snapshot

- Workflow baseline: Codex for implementation flow + OpenAI API for runtime/eval model operations.
- Runtime surface: FastAPI backend + Vite UI + CLI runner.
- Operating model: human-directed architecture and acceptance criteria, AI-accelerated implementation and validation.
- Gate policy: release decisions are binary (`PASS`/`FAIL`); nuanced interpretation stays in notes/transcripts.

## Active Branch and Commit

- Branch: `<branch_name>`
- HEAD: `<commit_sha>`
- Scope summary: `<one-line summary>`

## Working Tree Status

- Dirty files: `<file list or none>`
- Notes: `<important local-only context>`

## Key Files To Read First

1. `docs/CHARTER.md`
2. `docs/STATE.md`
3. `docs/DECISIONS.md`
4. `docs/RUNBOOK.md`

## Quick Validation (Local)

1. `make doctor-env`
2. `make lint-docs`
3. `make test`
4. `make quality-gate-deterministic`

## Immediate Next Step

- `<single next action>`
