<!-- @format -->

# Project State

Last updated: 2026-04-17

## Current Truth

- Runtime is local-first and backend-first:
  - FastAPI API + CLI are canonical execution surfaces.
  - Prompt/runtime behavior remains minimal and deterministic.
- Repo-as-research-project is the current portfolio architecture:
  - GitHub repository visibility is public.
  - public GitHub metadata is configured:
    - description: `Full-stack AI research project exploring human-AI
      alignment through OCR, evals, evidence chains, and runtime tooling.`
    - topics emphasize Python/OpenAI, AI research/safety, human-AI/HCI,
      LLM evaluation, PDF processing, FastAPI, and SQLite.
    - website URL remains blank until the landing page is live.
  - `main` is protected by the active `polinko` ruleset:
    - pull request required
    - required checks: `test`, `markdownlint`
    - strict status checks enabled
    - branch deletion and non-fast-forward updates blocked
    - squash-only merge
  - public entrypoint/hygiene work is merged:
    - PR #315: curated public repo entrypoint
    - PR #316: sanitized public repo references
  - the repository carries the research proof: source, tests, evals,
    databases/contracts, Mermaid diagrams, governance docs, runtime docs, and
    evidence chains
  - tracked README/docs remain canonical research documentation
  - public-facing docs/site copy should be derived separately and must not
    replace canonical research docs
  - public-facing repo entrypoint now starts at `docs/public/README.md`, with
    curated method/hypothesis/research/diagrams pages under `docs/public/`
  - public framing leads with human-led research and AI-assisted engineering
    collaboration before implementation details
  - the public portfolio website should be a lightweight about/contact doorway
    into the work, not a full recreation of the research system
  - current landing-page direction is intentionally austere:
    - sparse `krystian.io`-style composition
    - name + concise human-facing one-liner
    - faint WebGL alignment field as atmosphere only
    - understated text link CTA, not a pill/button
    - local-only mockups live under ignored `docs/peanut/assets/tumbles/`
- End-of-day closeout is green for 2026-04-16:
  - PR #317 merged to `main`.
  - final `make eod` passed end-to-end (`doctor-env`, `lint-docs`, `test`
    with 393 passing tests, and `eod-git-check`).
  - local `main` is clean and synced with `origin/main`.
  - managed background runtime tasks are stopped (`server-daemon` and managed
    `caffeinate`).
- Portfolio shell route contract is active:
  - `GET /` redirects to `GET /portfolio`.
  - `GET /portfolio` serves local `ui/index.html` when present, otherwise a
    tracked in-app about/contact fallback.
  - frontend source/output directories are local-only:
    - `frontend/` is ignored except `frontend/.gitkeep`.
    - `ui/` is ignored except `ui/.gitkeep`.
  - command surface is simplified:
    - `make portfolio` is the canonical rebuild + serve + open workflow when
      local frontend source is present, otherwise it serves the tracked
      `/portfolio` fallback.
    - `make portfolio` opens a cache-busted URL so the browser does not reuse a
      stale shell bundle.
    - default launch uses the repo-scoped Playwright session, opens a new tab
      when possible, and opens a headed Playwright browser when no session is
      active.
    - `make portfolio` restarts the stable no-reload `server-daemon` before
      opening so embedded fallback HTML updates deterministically.
    - system-browser launch remains available with
      `make portfolio PORTFOLIO_LAUNCH=system`.
    - `make portfolio-build` is the canonical build-only workflow and no-ops
      when local frontend source is absent.
    - stale alias `make portfolio-open` has been removed.
  - current frontend implementation remains a local FPO scaffold while the
    public website is simplified toward a lean landing/about doorway.
  - frontend interaction model currently uses pinned-stage stepping:
    - browser document scroll is locked (`scrollY` should remain `0`).
    - GSAP `Observer` maps one wheel/touch/key gesture to one exact scene.
    - `.board` transforms on x/y between mapped scenes.
    - scroll guard includes a gesture-stop failsafe so hard trackpad/wheel
      momentum should not skip sections or lock at section `02`.
- Portfolio evidence surfaces are research instruments in the repo, not the
  public website burden:
  - WebGL/data-viz work remains optional research instrumentation.
  - flat SVG/D3 Sankey or alluvial views remain valid accessibility,
    reduced-motion, performance, and direct-inspection fallbacks.
  - repo evidence surfaces must use the same real-data
    `GET /portfolio/sankey-data` payload.
  - current local frontend implementation uses the stacked SVG evidence-map
    FPO at `frontend/src/stacked-evidence-map-fpo.svg`; preserve this as the
    evidence-map visual/function baseline while refining style.
  - current pipeline panels use the pipeline FPO source at
    `frontend/src/pipeline-fpo.svg`.
  - Mermaid pipeline diagrams in `docs/peanut/refs/llm_pipeline_diagrams.md`
    are the high-level pipeline structure baseline for the pipeline pages.
  - peanut-only visual mockups/references are exploration only; do not replace
    the working FPO or pipeline structure unless readability/function is
    preserved.
  - the frontend still fetches `GET /portfolio/sankey-data`, stores the result
    in `window.__POLINKO_SANKEY_DATA__`, and sets readiness state on
    `#evidence-map`.
  - current stage sequence is:
    - `hero -> intro -> pipeline-one -> evidence-map -> pipeline-two ->
      conclusion -> about-lab`
  - current stage map is:
    - `home -> intro`, then down through `pipeline-one -> evidence-map ->
      pipeline-two -> conclusion`, then right to `about-lab`
  - blueprint/free-pan exploration was intentionally abandoned for this UI
    because wheel-scroll and pan gestures conflict; keep deterministic
    pinned-stage stepping for this portfolio shell.
  - the backend evidence payload still uses Beta 1.0 manual feedback rows from
    `.local/runtime_dbs/active/manual_evals.db` and current OCR binary gate
    report cases from `.local/eval_reports/`.
  - the connector graph uses source-side signal/category counts only; it is not
    a row-level join between legacy and current datasets.
  - `graphs.bridge` remains an API payload key for compatibility; it is not a
    portfolio IA label.
  - missing required sources produce an explicit no-data state, not decorative
    placeholder links.
  - beta 1.0 marks the transition to binary eval semantics and is the evidence
    layer for interpreting beta 2.0/current eval data.
  - beta 1.0 manual evaluations are meaningful data, not weaker evidence.
  - beta 1.0 and beta 2.0 should remain equally prominent across documents,
    databases, evals, and logic; see `docs/eval/README.md`.
  - `.local/runtime_dbs/active/manual_evals.db` is the single integrated
    app-facing eval warehouse; it is rebuilt from current history plus optional
    Beta 1.0 history with era/source provenance.
  - `eval_viz.db` is retired from the active app-facing path; the previous
    active local cache was archived under `.local/runtime_dbs/archive/`.
  - the full local beta 1.0 parity source is
    `<local-beta-1.0-snapshot>`.
  - canonical beta 1.0 context is in earlier `DECISIONS` entries, not only the
    latest entries.
  - legacy and current eval eras may both include OCR evidence.
  - legacy OCR evidence includes screenshot-backed/manual eval artifacts under
    `docs/eval/beta_1_0/`.
  - local-only transcripts under `docs/peanut/transcripts/` are source
    evidence for reasoning/eval interpretation; `DECISIONS` records the
    binding interpretation and must not contradict transcript evidence.
  - long-term context should preserve evidence chains; do not replace source
    transcripts/reports with summary-of-summary state.
  - local source remains `frontend/` with generated local output in `ui/`; both
    directories are ignored except tracked `.gitkeep` placeholders.
  - Local-only design contract:
    - `docs/peanut/refs/POLINKOFOLIO_EVIDENCE_FIELD_DESIGN.md`
  - UI guardrails: no weird headlines, no dashboard cards, no placeholder
    copy, no invented overlays, and no fake/decorative FPO evidence panels.
- OCR-forward eval model remains active:
  - lockset lane is release-gating.
  - growth lane is fail-tolerant and signal-seeking.
- Eval gate semantics remain strict binary (`pass`/`fail`).
- Pass/fail visualization defaults to Pol-3 OCR binary gate reports under
  `.local/eval_reports/` so FAIL pressure stays visible.
- `manual_evals.db` remains the canonical integrated manual-eval warehouse and
  fallback/explicit DB path, not the primary strict-gate chart source.
- Playwright capture flow is deterministic and repo-scoped:
  - wrapper config path: `.local/logs/playwright/cli.config.json`
  - wrapper default session: `polinko`
  - snapshot folders rotate by date under
    `docs/peanut/assets/screenshots/playwright/DD-MM-YY`.

## Active Priorities

1. Portfolio shipping lane:
   - simplify the public website toward about/contact.
   - keep repo evidence visualizations as research instruments, not the public
     portfolio's main burden.
   - preserve real-data evidence contracts unless explicitly changing backend
     data shape.
2. OCR reliability lane:
   - continue growth/lockset operations without changing binary gate semantics.
   - keep FAIL-first observability in `/viz/pass-fail`.
3. Documentation hygiene lane:
   - keep facts anchored to source evidence + binding decisions; avoid
     recursive summary drift.
   - follow `docs/runtime/RUNBOOK.md` for startup and end-of-day routines.
   - refresh `STATE` and `SESSION_HANDOFF` in place as current-truth running
     docs; do not append daily log sections.
   - append to `DECISIONS` only for durable process, engineering/tooling,
     runtime/API, dependency/workflow, or eval-governance decisions.

## Canonical Sources

- Rules/authority: `docs/governance/CHARTER.md`
- Structure: `docs/runtime/ARCHITECTURE.md`
- Commands/procedure: `docs/runtime/RUNBOOK.md`
- Decision history: `docs/governance/DECISIONS.md`

## Validation Baseline

- `make doctor-env`
- `make eod-docs-check`
- `make lint-docs`
- `make test`
- `make portfolio-build` (when local `frontend/` changes)
