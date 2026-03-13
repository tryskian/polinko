# Project State (Reset Baseline)

## Current Status

- Docs have been reset to a clean operational baseline.
- Previous documentation lineage is archived at `docs/archive/2026-03-13-pre-reset/`.
- Product-facing brand is now Nautorus (phase-1 rename rollout).
- Runtime compatibility prefixes remain `POLINKO_*` in this phase to avoid env/config breakage.
- Core repo workflow is stable: feature branch -> PR -> checks -> merge.
- Active implementation focus is eval operations (review queue, checkpoints, retry behavior).

## Verified Workflow

- `main` is protected and merged only through PR checks.
- Validation stack in active use:
  - backend tests
  - frontend build
  - Playwright smoke coverage
  - eval commands/reports

## Known Constraints

- Cloud task threads and local IDE threads can diverge; use handoff docs as source-of-truth.
- Braintrust settings are optional/scoped and should not be forced into default env.

## Key Paths

- Runtime/app: `api/`, `core/`, `frontend/`
- Eval tools: `tools/`
- Handoff docs: `docs/CHARTER.md`, `docs/STATE.md`, `docs/DECISIONS.md`, `docs/SESSION_HANDOFF.md`
- Archive snapshot: `docs/archive/2026-03-13-pre-reset/`

## Suggested Next Steps

1. Continue eval operations stream with one scoped PR at a time.
2. Keep evidence capture tied to each merge (tests + eval report artifact).
3. Record any policy/process changes in the new decision ledger.
