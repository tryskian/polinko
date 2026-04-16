<!-- @format -->

# Session Handoff (Current Only)

Last updated: 2026-04-16

## Startup

1. Peanut prompt:
   - "hi! new day!"
2. Follow `docs/runtime/RUNBOOK.md` (`Morning Startup Check`).

## Current Snapshot

- Backend-first runtime remains canonical.
- Repo-as-research-project is the portfolio architecture:
  - tracked README/docs remain canonical research documentation
  - public-facing docs/site copy should be derived separately
  - public-facing repo guide starts at `docs/public/README.md`; curated public
    pages live under `docs/public/`
  - the public website should be about/contact and point into the work, not
    recreate the research system
- Latest end-of-day closeout completed cleanly (2026-04-15):
  - PR #313 merged to `main`.
  - final `make eod` passed transcript/doc checks, env doctor, docs lint,
    tests (`393` passing), stop checks, and `eod-git-check`.
  - local `main` finished clean and synced with `origin/main`.
  - `server-daemon` is OFF and managed `caffeinate` is OFF.
- Portfolio shell route is active:
  - `GET /` -> redirect to `GET /portfolio`
  - `GET /portfolio` -> `ui/index.html`
- Public portfolio scope is about/contact doorway.
- Lean portal rule:
  - website = identity and doorway
  - repo = research object, evidence, visuals, notebooks, Mermaid diagrams,
    eval data, and implementation
- Current frontend remains a local FPO scaffold while the public site is
  simplified.
- Frontend source/build contract is active:
  - edit in `frontend/`
  - build to `ui/` with `make portfolio-build`
  - no manual edits under `ui/`
  - canonical launch command:
    - `make portfolio` (rebuild + serve + open)
    - launch URL includes a `rebuild=<timestamp>` cache-bust query.
    - default launch uses the system browser for the human-facing UI.
    - Codex/debug launch uses `make portfolio-playwright`, which opens a
      Playwright tab in the repo Playwright session.
  - `make portfolio-open` alias has been removed.
- Portfolio UI interaction model is pinned-stage stepping:
  - document scroll is locked (`scrollY` should stay `0`).
  - one wheel/touch/key gesture advances one exact scene.
  - scenes move through `.board` x/y transforms.
  - scroll guard includes a gesture-stop failsafe so hard trackpad/wheel
    momentum should not skip sections or lock at section `02`.
  - active sequence:
    `hero -> intro -> pipeline-one -> evidence-map -> pipeline-two ->
    conclusion -> about-lab`
  - active map:
    `home -> intro`, then down through `pipeline-one -> evidence-map ->
    pipeline-two -> conclusion`, then right to `about-lab`
- Portfolio evidence surfaces are repo research instruments:
  - `GET /portfolio/sankey-data` supplies the real-data payload.
  - WebGL/data-viz work remains optional research instrumentation.
  - flat SVG/D3 Sankey or alluvial view remains the accessibility,
    reduced-motion, performance, and direct-inspection fallback.
  - current frontend implementation uses the tracked stacked SVG evidence-map
    FPO at `frontend/src/stacked-evidence-map-fpo.svg`; keep it as the
    evidence-map visual/function baseline while refining style.
  - current pipeline panels use `frontend/src/pipeline-fpo.svg` as FPO.
  - Mermaid pipeline diagrams in `docs/peanut/refs/llm_pipeline_diagrams.md`
    are the high-level pipeline structure baseline for pipeline pages.
  - peanut-only mockups/references are exploration only; do not replace the
    working FPO or pipeline structure unless readability/function is preserved.
  - the frontend still fetches `/portfolio/sankey-data`, exposes
    `window.__POLINKO_SANKEY_DATA__`, and sets readiness state on
    `#evidence-map`.
  - Beta 1.0 source uses manual feedback rows from `manual_evals.db`.
  - Beta 2.0/current source uses OCR binary gate report cases from
    `.local/eval_reports/`.
  - connector graph links are source-side counts through an
    evidence-continuity anchor, not fabricated row-level joins.
  - missing sources must render as no-data, not decorative placeholder data.
- Portfolio UI checkpoint:
  - pinned-stage stepping is the current interaction baseline.
  - blueprint/free-pan exploration was intentionally abandoned for this UI
    because scroll and pan gestures conflict; keep deterministic
    one-gesture-per-section stepping.
  - next design pass should prototype the Evidence Field inside the pinned
    stage, not reintroduce native scroll snap/scrub behavior.
  - WebGL interaction is drag-to-rotate only; do not capture wheel/trackpad
    gestures inside the canvas.
  - do not remove or fake the real-data Sankey payload contract while refining
    the frontend shell.
  - no weird headlines, dashboard cards, placeholder copy, invented
    explanatory overlays, or fake/decorative FPO evidence panels.
  - Local-only design contract:
    - `docs/peanut/refs/POLINKOFOLIO_EVIDENCE_FIELD_DESIGN.md`
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
   - simplify public website toward a lean hero/contact portal.
   - keep repository evidence visualizations as research instruments.
   - preserve backend evidence/data contracts unless explicitly changing them.
2. OCR hardening kernels (lockset stability + growth signal quality).
3. Keep docs aligned via canonical ownership map.

## Guardrails

- Do not duplicate historical decision timelines in this file.
- Keep command catalogs in `docs/runtime/RUNBOOK.md` only.
- Keep durable process/engineering/tooling/runtime/eval rationale in
  `docs/governance/DECISIONS.md` only.
- Refresh this file in place; do not append daily log sections.
- Keep evidence anchors intact; summaries must point back to decisions/source
  evidence rather than becoming the evidence.

## Session Close

- Follow `docs/runtime/RUNBOOK.md` (`End-of-Day Routine`).
- Ensure clean tree or explicitly scoped modified files.
- Update only current-truth facts in `STATE` and this file.
