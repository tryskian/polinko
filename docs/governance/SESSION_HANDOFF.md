<!-- @format -->

# Session Handoff (Current Only)

Last updated: 2026-04-17

## Startup

1. Peanut prompt:
   - "hi! new day!"
2. Follow `docs/runtime/RUNBOOK.md` (`Morning Startup Check`).

## Current Snapshot

- Backend-first runtime remains canonical.
- Repo-as-research-project is the portfolio architecture:
  - GitHub repository visibility is public.
  - public GitHub metadata is configured:
    - description: `Full-stack AI research project exploring human-AI
      alignment through OCR, evals, evidence chains, and runtime tooling.`
    - topics emphasize Python/OpenAI, AI research/safety, human-AI/HCI,
      LLM evaluation, PDF processing, FastAPI, and SQLite.
    - website URL remains blank until the landing page is live.
  - `main` is protected by the active `polinko` ruleset:
    - PR required
    - required checks: `test`, `markdownlint`
    - strict status checks enabled
    - deletion and non-fast-forward updates blocked
    - squash-only merge
  - public repo entrypoint and hygiene are merged:
    - PR #315: public repo entrypoint
    - PR #316: public repo reference sanitization
  - tracked README/docs remain canonical research documentation
  - public-facing docs/site copy should be derived separately
  - public-facing repo guide starts at `docs/public/README.md`; curated public
    pages live under `docs/public/`
  - public framing starts with human-led research and AI-assisted engineering
    collaboration, not tooling-first implementation detail
  - the public website should be about/contact and point into the work, not
    recreate the research system
- Latest merged checkpoint (2026-04-17):
  - PR #318 merged to `main` through the protected PR flow.
  - required checks passed: `test`, `markdownlint`.
  - local `main` was rebased/aligned with `origin/main` after the squash merge.
  - generated Playwright test scaffold was removed; keep only the repo-scoped
    Playwright CLI wrapper workflow.
  - orphaned local frontend build/install leftovers were cleaned; only
    `frontend/.gitkeep` and `ui/.gitkeep` remain in the frontend directories.
- Portfolio shell route is active:
  - `GET /` -> redirect to `GET /portfolio`
  - `GET /portfolio` -> local `ui/index.html` only when intentionally present;
    tracked in-app about/contact fallback otherwise
- Public portfolio scope is about/contact doorway.
- Lean portal rule:
  - website = identity and doorway
  - repo = research object, evidence, visuals, notebooks, Mermaid diagrams,
    eval data, and implementation
- Landing-page fallback is now the active public doorway:
  - tracked fallback lives in `api/app_factory.py`.
  - current heading: `Krystian Fernando`.
  - current one-liner:
    `Creative AI Research Engineer running an applied design lab to evaluate Human-AI interaction.`
  - current CTA links to the public repo:
    `because one idea turned into a lot of questions`.
  - top-right links: GitHub, LinkedIn, email.
  - current visual checkpoint is a full-viewport WebGL particle-field hero:
    - reference direction:
      `docs/peanut/assets/tumbles/particle-field-ref.png`
    - the checkpoint is visual-only; no portfolio evidence/data wiring is
      attached to it yet
    - the mesh has been lengthened with additional geometry/segment density so
      the field can breathe without stretching/flattening the texture
  - the implementation is acceptable as a tiny fallback; if it becomes the
    production website, move it out of the large `app_factory.py` HTML string
    into a dedicated static/template surface.
- Frontend source/build contract is intentionally minimal:
  - `frontend/` is local-only and ignored except `frontend/.gitkeep`
  - `ui/` is local-only and ignored except `ui/.gitkeep`
  - no active `frontend/package.json` is present
  - no active generated `ui/index.html` is present
  - if a real frontend returns, edit in `frontend/` and regenerate ignored
    `ui/`; do not hand-edit generated `ui/`
  - canonical launch command:
    - `make portfolio` (rebuild + serve + open)
    - launch URL includes a `rebuild=<timestamp>` cache-bust query.
    - default launch uses the repo Playwright session, opens a new tab when
      possible, and opens a headed Playwright browser when no session is active.
    - `make portfolio` restarts the stable no-reload `server-daemon` before
      opening so embedded fallback HTML updates deterministically.
    - system-browser launch remains available with
      `make portfolio PORTFOLIO_LAUNCH=system`.
    - `make portfolio-build` no-ops when local frontend source is absent so
      the tracked `/portfolio` fallback remains launchable.
  - `make portfolio-open` alias has been removed.
- Portfolio evidence surfaces are repo research instruments:
  - `GET /portfolio/sankey-data` supplies the real-data payload.
  - WebGL/data-viz work remains optional research instrumentation.
  - flat SVG/D3 Sankey or alluvial view remains the accessibility,
    reduced-motion, performance, and direct-inspection fallback.
  - the former local pinned-stage/FPO frontend is no longer active; treat it as
    archived design context unless deliberately restored on a new branch.
  - Mermaid pipeline diagrams in `docs/peanut/refs/llm_pipeline_diagrams.md`
    are the high-level pipeline structure baseline for pipeline pages.
  - peanut-only mockups/references are exploration only; they are not tracked
    source of truth.
  - Beta 1.0 source uses manual feedback rows from `manual_evals.db`.
  - Beta 2.0/current source uses OCR binary gate report cases from
    `.local/eval_reports/`.
  - connector graph links are source-side counts through an
    evidence-continuity anchor, not fabricated row-level joins.
  - missing sources must render as no-data, not decorative placeholder data.
  - if repo evidence visuals return, do not remove or fake the real-data
    Sankey payload contract.
  - no dashboard cards, placeholder copy, invented overlays, or fake/decorative
    FPO evidence panels.
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

1. Portfolio doorway pass:
   - review the particle-field checkpoint with fresh eyes.
   - next visual work: mesh polish only; do not overhaul the concept or switch
     visual direction.
   - animation/motion polish comes after the static field shape is accepted.
   - if keeping it as production, extract the HTML/CSS from `app_factory.py`.
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
