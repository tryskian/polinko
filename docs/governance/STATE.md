<!-- @format -->

# Project State

Last updated: 2026-05-15

## Current Truth

- Backend-first runtime remains canonical:
  - FastAPI API + CLI are the execution surfaces
  - prompt and runtime behaviour stay minimal and deterministic
- The repository is the research object:
  - tracked docs, code, tests, and reports are canonical truth
  - public-facing writing is the derived publication layer from repo truth
  - local/private material stays in `docs/peanut/`
- The public website remains a doorway into the work:
  - `GET /` redirects to `GET /portfolio`
  - the public surface points into the work
  - the portfolio shell remains intentionally lean
- The eval contract is explicit and binary:
  - release outcomes are `pass` / `fail`
  - after `fail`, failure disposition is `retain` / `evict`
  - `retain` keeps the failure as active evidence
  - `evict` removes malformed or stale cases upstream
- Polinko is in a serious method beta:
  - fail-first evaluation is the active posture
  - co-reasoning is the first promoted non-OCR lane
  - OCR remains one mature method lane inside the broader project
- Branch protection on `main` remains active:
  - PR required
  - strict status checks enabled
  - squash-only merge
- Documentation roles are explicit:
  - `CHARTER` holds durable rules
  - `STATE` holds tracked current truth
  - `RUNBOOK` holds operator procedure
  - `ARCHITECTURE` holds stable system shape
  - local `SESSION_HANDOFF` holds the active slice

## Active Priorities

1. Keep the public doorway stable and credible.
2. Keep tracked research docs compact and non-duplicative.
3. Keep the promoted non-OCR lane visible as the broader proof surface grows.
4. Keep operator-burden and related thin-lane work grounded in real evidence
   and distinct lane signal.
5. Keep mature method lanes green and reopen parked lanes only from clear
   evidence.

## Canonical Sources

- Rules:
  - `docs/governance/CHARTER.md`
- Current truth:
  - `docs/governance/STATE.md`
- Procedure:
  - `docs/runtime/RUNBOOK.md`
- Structure:
  - `docs/runtime/ARCHITECTURE.md`
- Durable history:
  - `docs/governance/DECISIONS.md`
- Active local carryover:
  - `docs/peanut/governance/SESSION_HANDOFF.md`

## Validation Baseline

- `make doctor-env`
- `make api-smoke`
- `make lint-docs`
- `make test`
- `make end-git-check` after merge and sync
