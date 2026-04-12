<!-- @format -->

# Project State

Last updated: 2026-04-12

## Current Truth

- Runtime is local-first and backend-first:
  - FastAPI API + CLI are canonical execution surfaces.
  - Prompt/runtime behavior remains minimal and deterministic.
- Portfolio shell route contract is active:
  - `GET /` redirects to `GET /portfolio`.
  - `GET /portfolio` serves `ui/index.html` (build output).
  - source of truth for shell edits is `frontend/`.
- Sankey portfolio shell iteration is active in the frontend lane:
  - four-section sankey strip prototype is currently under refinement.
  - source remains `frontend/` with generated output in `ui/`.
- OCR-forward eval model remains active:
  - lockset lane is release-gating.
  - growth lane is fail-tolerant and signal-seeking.
- Eval gate semantics remain strict binary (`pass`/`fail`).

## Active Priorities

1. Portfolio shipping lane:
   - keep shell structure clean and navigable.
   - fill evidence modules incrementally against locked architecture.
2. OCR reliability lane:
   - continue growth/lockset operations without changing binary gate semantics.
3. Documentation hygiene lane:
   - keep facts single-sourced via canonical ownership.

## Canonical Sources

- Rules/authority: `docs/governance/CHARTER.md`
- Structure: `docs/runtime/ARCHITECTURE.md`
- Commands/procedure: `docs/runtime/RUNBOOK.md`
- Decision history: `docs/governance/DECISIONS.md`

## Validation Baseline

- `make doctor-env`
- `make lint-docs`
- `make test`
- `make frontend-build` (when `frontend/` changes)
