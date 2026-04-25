<!-- @format -->

# Project State

Last updated: 2026-04-25

## Current Truth

- Backend-first runtime remains canonical:
  - FastAPI API + CLI are the execution surfaces.
  - prompt/runtime behavior stays minimal and deterministic.
- Repo-as-research-project is the active public architecture:
  - repository is public
  - repo is the research surface
  - website is a lightweight doorway into the work
  - public-facing docs live under `docs/public/` and `docs/research/`
  - OpenAI Codex is the active repo-local coding agent and engineering
    collaborator
  - OpenAI Platform APIs are used for model-backed runtime and eval calls
- Branch protection on `main` remains active:
  - PR required
  - required checks: `test`, `markdownlint`
  - strict status checks enabled
  - squash-only merge
- Public site/domain state:
  - production site is live at `https://www.krystian.io/`
  - `https://krystian.io/` redirects to `https://www.krystian.io/`
  - generated static output includes:
    - `index.html`
    - `_redirects`
    - `robots.txt`
    - `sitemap.xml`
  - canonical URL/SEO metadata should use `https://www.krystian.io/`
- Public docs/research surface is cleaner than the initial application push:
  - `docs/` now has a landing page
  - architecture has a visual-first entry
  - README carries badges and a compact research surface link
  - curated research surface lives under `docs/research/`
  - README/Charter/State/Method now make Codex collaboration explicit for
    external readers
- Portfolio surface remains intentionally lean:
  - single-screen about/contact doorway
  - tracked fallback lives in `api/app_factory.py`
  - `GET /` redirects to `GET /portfolio`
  - portfolio shell is presentation-only and must not carry research-system
    complexity
- Current portfolio fallback contract:
  - semantic `h1`
  - paragraph body copy
  - repo CTA is a real link with a visible destination hint
  - no contact drawer
  - no animation-first/UI-heavy exploration in the public surface
  - favicon now uses tracked `api/static/favicon.png`
  - current visible identity line keeps the `creative designer who somehow
    became...` phrasing and swaps in `Applied AI Systems Designer`
- Operator command surface:
  - `make day-start` / `make sod` are available as startup shortcuts
  - `make eod` remains end-of-day only
- Local frontend contract is intentionally minimal:
  - `frontend/` is local-only and ignored except `.gitkeep`
  - `ui/` is local-only and ignored except `.gitkeep`
  - if a real frontend returns, edit in `frontend/` and regenerate ignored `ui/`
- Canonical local portfolio command flow:
  - `make portfolio` rebuilds/serves and prints a cache-busted URL
  - default launch is `none`
  - `make portfolio-playwright` is explicit/opt-in only
  - `make portfolio-build` no-ops when local frontend source is absent
- Evidence/visualization lane:
  - Mermaid diagrams remain the structural baseline
  - static Mermaid render pipeline is repo-pinned
  - static D3/SVG diagrams now sit beside Mermaid as real proof artifacts
  - D3 diagrams should stay real generated evidence artifacts, not portfolio UI
  - no fake placeholder evidence panels
- Eval lane remains OCR-forward and binary:
  - lockset is release-gating
  - growth is fail-tolerant
  - `/viz/pass-fail` is a fail-signal instrument
  - `manual_evals.db` remains the integrated manual-eval warehouse
- Application state:
  - initial OpenAI application push is complete
  - do not duplicate-submit overlapping engineering applications in the same
    cycle
  - private application forms/resume exports remain local and ignored
- Documentation rule:
  - `DECISIONS` is durable archive
  - `STATE` is the tracked public current-truth surface
  - operator handoff stays local in `docs/peanut/governance/SESSION_HANDOFF.md`

## Active Priorities

1. Keep the public doorway stable and credible.
2. Keep repo research surfaces compact, visual, and easy to scan.
3. Continue OCR reliability work without changing binary gate semantics.
4. Keep governance/runtime docs aligned and non-duplicative.

## Canonical Sources

- Rules: `docs/governance/CHARTER.md`
- Current truth: `docs/governance/STATE.md`
- Procedures: `docs/runtime/RUNBOOK.md`
- Structure: `docs/runtime/ARCHITECTURE.md`
- Durable history: `docs/governance/DECISIONS.md`

## Validation Baseline

- `make doctor-env`
- `make lint-docs`
- `make test`
