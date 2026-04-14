<!-- @format -->

# Session Handoff (Current Only)

Last updated: 2026-04-14

## Startup

1. Peanut prompt:
   - "hi! new day!"
2. Confirm location and branch:
   - repo: `/Users/tryskian/Github/polinko`
   - branch: `git branch --show-current`
3. Run environment sanity:
   - `make doctor-env`
4. If frontend changed, rebuild shell output:
   - `make portfolio-build`

## Current Snapshot

- Backend-first runtime remains canonical.
- Latest end-of-day closeout completed cleanly (2026-04-14):
  - `make eod` passed transcript/doc checks, env doctor, docs lint, and tests
    (`393` passing).
  - `server-daemon` is OFF and managed `caffeinate` is OFF.
- Portfolio shell route is active:
  - `GET /` -> redirect to `GET /portfolio`
  - `GET /portfolio` -> `ui/index.html`
- Frontend source/build contract is active:
  - edit in `frontend/`
  - build to `ui/` with `make portfolio-build`
  - no manual edits under `ui/`
  - canonical launch command:
    - `make portfolio` (rebuild + serve + open)
    - launch URL includes a `rebuild=<timestamp>` cache-bust query.
  - `make portfolio-open` alias has been removed.
- Portfolio UI interaction model is pinned-stage stepping:
  - document scroll is locked (`scrollY` should stay `0`).
  - one wheel/touch/key gesture advances one exact scene.
  - vertical scenes move through `.board` transform.
  - horizontal chapter moves through `.horizontal-track` transform.
  - active sequence:
    `hero -> intro -> pipeline-one -> sankey -> pipeline-two -> conclusion ->
    about-lab`
- Twin Sankey portfolio shell path is active for current cycle:
  - `GET /portfolio/sankey-data` supplies the real-data payload.
  - left side uses Beta 1.0 manual feedback rows from `manual_evals.db`.
  - right side uses current OCR binary gate report cases from
    `.local/eval_reports/`.
  - connector graph links are source-side counts through an
    evidence-continuity anchor, not fabricated row-level joins.
  - missing sources must render as no-data, not decorative placeholder data.
- Portfolio UI checkpoint:
  - pinned-stage stepping is the current interaction baseline.
  - next design pass should improve the Sankey and pipeline visuals on top of
    the pinned stage, not reintroduce native scroll snap/scrub behavior.
  - do not remove or fake the real-data Sankey payload contract while refining
    the frontend shell.
- OCR lockset/growth lane model remains active and unchanged.
- Eval gate contract remains binary pass/fail.
- `/viz/pass-fail` is a fail-signal instrument:
  - default chart source is `.local/eval_reports/` OCR binary gate reports.
  - `manual_evals.db` remains the integrated manual-eval warehouse and fallback
    data path.
- Transcripts/raw reports/screenshots are evidence anchors; do not replace them
  with recursive summaries.
- Playwright wrapper defaults are deterministic and repo-scoped:
  - config path: `.local/logs/playwright/cli.config.json`
  - default session: `polinko`
  - snapshot folders: `docs/peanut/assets/screenshots/playwright/DD-MM-YY`

## Next Execution Slice

1. Portfolio frontend design pass:
   - preserve pinned-stage stepping.
   - refine the Sankey and pipeline visual composition.
   - preserve backend evidence/data contracts unless explicitly changing them.
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
- `make eod` includes `make eod-docs-check`; update `STATE` and this handoff
  first so current-truth docs carry today's `Last updated` date.
- Ensure clean tree or explicitly scoped modified files.
- Update only current-truth facts in `STATE` and this file.
