<!-- @format -->

# Session Handoff (Current Only)

Last updated: 2026-04-13

## Startup

1. Peanut prompt:
   - "hi! new day!"
2. Confirm location and branch:
   - repo: `/Users/tryskian/Github/polinko`
   - branch: `git branch --show-current`
3. Run environment sanity:
   - `make doctor-env`
4. If frontend changed, rebuild shell output:
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
- Twin Sankey portfolio shell path is active for current cycle:
  - `GET /portfolio/sankey-data` supplies the real-data payload.
  - left side uses Beta 1.0 manual feedback rows from `manual_evals.db`.
  - right side uses current OCR binary gate report cases from
    `.local/eval_reports/`.
  - bridge links are source-side counts through an evidence-continuity anchor,
    not fabricated row-level joins.
  - missing sources must render as no-data, not decorative placeholder data.
- OCR lockset/growth lane model remains active and unchanged.
- Eval gate contract remains binary pass/fail.
- `/viz/pass-fail` is a fail-signal instrument:
  - default chart source is `.local/eval_reports/` OCR binary gate reports.
  - `manual_evals.db` remains the integrated manual-eval warehouse and fallback
    data path.
- Transcripts/raw reports/screenshots are evidence anchors; do not replace them
  with recursive summaries.

## Next Execution Slice

1. Portfolio shell/module progression (content placement + Sankey refinement).
2. OCR hardening kernels (lockset stability + growth signal quality).
3. Keep docs aligned via canonical ownership map.

## Guardrails

- Do not duplicate historical decision timelines in this file.
- Keep command catalogs in `docs/runtime/RUNBOOK.md` only.
- Keep durable rationale/history in `docs/governance/DECISIONS.md` only.
- Keep evidence anchors intact; summaries must point back to decisions/source
  evidence rather than becoming the evidence.

## Session Close

- Peanut prompt includes terms:
  - "wind down" or "human time"
- `make eod`
- Ensure clean tree or explicitly scoped modified files.
- Update only current-truth facts in `STATE` and this file.
