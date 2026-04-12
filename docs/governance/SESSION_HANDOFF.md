<!-- @format -->

# Session Handoff (Current Only)

Last updated: 2026-04-12

## Startup

1. Confirm location and branch:
   - repo: `/Users/tryskian/Github/polinko`
   - branch: `git branch --show-current`
2. Run environment sanity:
   - `make doctor-env`
3. If frontend changed, rebuild shell output:
   - `make frontend-build`

## Current Snapshot

- Backend-first runtime remains canonical.
- Portfolio shell route is active:
  - `GET /` -> redirect to `GET /portfolio`
  - `GET /portfolio` -> `ui/index.html`
- Frontend source/build contract is active:
  - edit in `frontend/`
  - build to `ui/` with `make frontend-build`
  - no manual edits under `ui/`
- Sankey portfolio shell path is active for current cycle.
- OCR lockset/growth lane model remains active and unchanged.
- Eval gate contract remains binary pass/fail.

## Next Execution Slice

1. Portfolio shell/module progression (structure/content placement).
2. OCR hardening kernels (lockset stability + growth signal quality).
3. Keep docs aligned via canonical ownership map.

## Guardrails

- Do not duplicate historical decision timelines in this file.
- Keep command catalogs in `docs/runtime/RUNBOOK.md` only.
- Keep durable rationale/history in `docs/governance/DECISIONS.md` only.

## Session Close

- `make eod`
- Ensure clean tree or explicitly scoped modified files.
- Update only current-truth facts in `STATE` and this file.
