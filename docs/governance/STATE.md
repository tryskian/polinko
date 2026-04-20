<!-- @format -->

# Project State

Last updated: 2026-04-19

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
    - website URL is live at `https://krystian.io/`, redirecting to
      `https://www.krystian.io/`.
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
  - current public website direction is intentionally lean:
    - sparse editorial doorway composition
    - name + human-facing origin/focus copy
    - understated repo CTA into the public work
    - peripheral contact links only
    - no full portfolio/storytelling UI on the public site right now
- Latest merged checkpoint is green for 2026-04-19:
  - PR #332 merged to `main` through the protected PR flow.
  - required checks passed: `test`, `markdownlint`.
  - local `main` was aligned with `origin/main` after the squash merge.
  - Netlify production builds from `main` are deterministic via
    `netlify.toml` and `tools/build_portfolio_static.py`.
  - deployed production build includes the current doorway, semantic identity
    heading, accessible repo CTA destination hint, SEO identity metadata,
    `robots.txt`, `sitemap.xml`, and `/portfolio` -> `/` redirect.
  - public credential incident is contained:
    - exposed OpenAI-shaped strings were revoked/rotated by the human.
    - GitHub secret scanning alerts #1 and #2 are resolved as `revoked`.
    - public archive branches/tags holding the transcript snapshot were
      deleted.
    - private `tryskian/polinko-build-snapshot` archive repo was deleted.
    - local stale archive refs were pruned and the old snapshot commit is no
      longer present in this clone.
- Portfolio shell route contract is active locally:
  - `GET /` redirects to `GET /portfolio`.
  - `GET /portfolio` serves local `ui/index.html` only when intentionally
    present, otherwise a tracked in-app about/contact fallback.
  - the tracked fallback currently lives in `api/app_factory.py`:
    - heading: `Krystian Fernando`
    - bio line:
      `design director who somehow became an AI research engineer when one idea came with its own hypothesis. so now i design evals around the useful signals that models reveal when they fail.`
    - method line: `for fun.`
    - primary repo CTA:
      `because every signal reshapes the experiment.`
    - primary repo CTA exposes a lightweight visible URL destination hint on
      hover/focus.
    - identity is a semantic `h1`; body copy uses paragraphs; CTA is a real
      link with visible text as its accessible name.
    - visible URL hint clears WCAG AA contrast at `4.59:1` on the current
      background and remains decorative for assistive technology.
    - contact drawer is intentionally removed for the ship pass; GitHub profile
      contact details carry the secondary contact job.
    - active visual direction:
      - austere editorial doorway
      - small uppercase static identity
      - bottom-anchored desktop copy block
      - left-rail desktop CTA with body-copy sizing
      - responsive stacked narrow-width fallback
      - single-screen landing only
    - particle-field/WebGL direction is parked for this pass
  - this fallback is acceptable as a tiny doorway; if it becomes the production
    website, extract it into a dedicated static/template surface.
  - production Netlify deploy path:
    - base directory: repo root
    - build command: `python3 tools/build_portfolio_static.py`
    - publish directory: `output/netlify`
    - generated files: `index.html`, `_redirects`, `robots.txt`,
      `sitemap.xml`
    - latest verified production deploy permalink:
      `https://69e587d4ac1836000802b59d--krystian-io.netlify.app`
  - SEO identity signals are active in the generated doorway:
    - title: `Krystian Fernando | AI Research Engineer`
    - canonical: `https://krystian.io/`
    - meta description, Open Graph, Twitter card metadata
    - JSON-LD `WebSite` + `Person` structured data reinforcing
      `Krystian Fernando` and `krystian.io`
  - DNS/SSL status:
    - Netlify DNS/SSL is live for apex + `www`.
    - `https://krystian.io/` redirects to `https://www.krystian.io/`.
    - `https://krystian.io/`, `/robots.txt`, and `/sitemap.xml` resolve to
      `200` after redirect.
    - do not add manual apex `A 75.2.60.5` while Netlify-managed
      `NETLIFY`/`NETLIFYv6` records are active.
  - frontend source/output directories are placeholders unless deliberately
    restored:
    - `frontend/` is ignored except `frontend/.gitkeep`.
    - `ui/` is ignored except `ui/.gitkeep`.
    - no active `frontend/package.json` is present.
    - no active generated `ui/index.html` is present.
  - command surface is simplified:
    - `make portfolio` is the canonical serve + open workflow.
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
- Portfolio evidence surfaces are research instruments in the repo, not the
  public website burden:
  - WebGL/data-viz work remains optional research instrumentation.
  - flat SVG/D3 Sankey or alluvial views remain valid accessibility,
    reduced-motion, performance, and direct-inspection fallbacks.
  - repo evidence surfaces must use the same real-data
    `GET /portfolio/sankey-data` payload.
  - the former local pinned-stage/FPO frontend is no longer active; treat it as
    archived design context unless deliberately restored on a new branch.
  - Mermaid pipeline diagrams in `docs/peanut/refs/llm_pipeline_diagrams.md`
    are the high-level pipeline structure baseline for the pipeline pages.
  - peanut-only visual mockups/references are exploration only, not tracked
    source of truth.
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
  - Local-only design contract:
    - `docs/peanut/refs/POLINKOFOLIO_EVIDENCE_FIELD_DESIGN.md`
  - UI guardrails: no dashboard cards, no placeholder copy, no invented
    overlays, and no fake/decorative FPO evidence panels.
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
- Codex app local image preview contract is now explicit:
  - embed previews inline with Markdown image syntax and absolute filesystem
    paths (`![label](/absolute/path.png)`).
  - do not rely on plain-text path mentions for preview rendering.

## Active Priorities

1. Portfolio shipping lane:
   - public doorway is live; keep it stable for the application push:
     - single viewport
     - static identity
     - concise human-facing origin/focus copy
     - understated repo CTA
   - next milestone is applications on 2026-04-20, using the live site and
     public repo.
   - avoid portfolio overbuild during this pass:
     - no multi-section storytelling UI
     - no Sankey/data-viz/public evidence surfaces on the landing page
     - no animation-first exploration
   - keep repo evidence visualizations as research instruments, not the public
     portfolio's main burden.
   - if the fallback page becomes production, extract it out of the large
     `app_factory.py` HTML string.
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
- `make portfolio-build`
