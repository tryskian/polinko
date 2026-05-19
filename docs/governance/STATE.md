<!-- @format -->

# Project State

Last updated: 2026-05-19

## Current Truth

- Backend-first runtime remains canonical:
  - FastAPI API + chat workbench endpoints are active execution and manual-eval
    surfaces
  - CLI chat runs through `main.py`
  - `app.py` remains only as a compatibility launcher during the entrypoint
    migration
  - prompt and runtime behaviour stay minimal and deterministic
  - `/chat` and `/chats/*` remain active because they feed manual evals,
    feedback, checkpoints, exports, and runtime history
- The repository is the research object:
  - tracked docs, code, tests, and reports are canonical truth
  - public-facing writing is the derived publication layer from repo truth
  - local/private material stays in `docs/peanut/`
- Public-facing surfaces remain derived from repo truth:
  - the root README now points to public research docs, not local portfolio
    commands
  - portfolio source lives under `apps/portfolio/`, while tracked static output
    stays under `public/portfolio/`
  - private portfolio mockups and screenshots stay in `docs/peanut/`
  - private portfolio mockups use `docs/peanut/assets/portfolio-mockups/`
  - promotion from private portfolio work to public docs requires explicit
    approval
- The eval contract is explicit and binary:
  - release outcomes are `pass` / `fail`
  - OCR case judgment remains `pass` / `fail`
  - OCR-ready candidate cleanup happens upstream of OCR judgment
- Polinko is entering the next method beta from a frozen Beta 2.3 snapshot:
  - fail-first evaluation is the active posture
  - Beta 2.3 evidence is frozen under `docs/eval/beta_2_3/`
  - `pre-Beta 2.4` is staged as the next research-model contract
  - the fail-pressure pulse hypothesis is not being carried forward
  - non-OCR lanes stay source-first rather than pulse-verdict-first
  - manual evals, `/chat`, `/chats/*`, and runtime history remain source
    evidence for that contract
  - co-reasoning is the first promoted non-OCR lane
  - uncertainty-boundary, hallucination-boundary, retrieval, and
    response-behaviour surfaces are operationalized
  - operator burden remains the active thin lane
  - no additional non-OCR lane currently meets promotion criteria
  - the lane map is current, and the research surface remains open
  - OCR remains one mature method lane inside the broader project
  - OCR is stabilized on the current image set, with broader
    generalization pressure as the next kernel
  - OCR intake now uses transcript-mined episodes plus OCR-ready
    generalization candidates
  - OCR verdicts stay `pass` / `fail` under that broader intake
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
  - `make end` now mirrors the legacy `make eod` closeout routine directly

## Active Priorities

1. Keep the public doorway stable and credible.
2. Keep tracked research docs compact and non-duplicative.
3. Keep the promoted non-OCR lane visible as the broader proof surface grows.
4. Keep operator-burden and related thin-lane work grounded in real evidence
   and distinct lane signal.
5. Keep OCR moving from current-set stability into generalization pressure.
6. Keep cleanup/refactor work anchored to the frozen Beta 2.3 baseline.
7. Keep exploring new seams without forcing promotion before the signal earns
   it.

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
- `make security-checks`
- `make ci` when checking the local equivalent of GitHub CI job targets
- `make end`
- `make end-docs-check` when validating current-truth freshness explicitly
- `make end-git-check` after merge and sync
