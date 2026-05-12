<!-- @format -->

# Project State

Last updated: 2026-05-12

## Current Truth

- Backend-first runtime remains canonical:
  - FastAPI API + CLI are the execution surfaces.
  - prompt/runtime behavior stays minimal and deterministic.
- Repo-as-research remains the public architecture:
  - repository is public
  - repo is the research surface
  - website is a lightweight doorway
  - public-facing docs live under `docs/public/` and `docs/research/`
- Eval contract is now explicit across tracked surfaces:
  - release outcomes stay `pass` / `fail`
  - after `fail`, failure disposition is:
    - `retain`
    - `evict`
  - gate stack stays explicit:
    - `pass / fail`
    - if `fail`, then `retain / evict`
    - rerun
    - `pass / fail`
  - `retain` keeps the failure as in-scope evidence in the active lane
  - `evict` removes malformed, noisy, or known-bad cases upstream instead of
    becoming a third gate state
  - the first gate proves hard contract correctness before richer
    interpretation
  - thin new lanes can start human-owned and row-local before larger judging
    systems
- Polinko is now in `Beta 2.2`:
  - serious method beta
  - explicit gate contract
  - first promoted non-OCR lane
- Human-led collaboration remains explicit:
  - Krystian owns theory, evidence interpretation, and publication decisions
  - OpenAI Codex is the active repo-local coding agent and engineering
    collaborator
  - OpenAI Platform APIs are used for model-backed runtime and eval calls
- Branch protection on `main` remains active:
  - PR required
  - required checks:
    - `dependency-review`
    - `python-security`
    - `node-security`
    - `test`
    - `markdownlint`
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
- Public docs/research surface is now the main explanatory layer:
  - `docs/` now has a landing page
  - root README points into a compact public reading path
  - curated research surface lives under `docs/research/`
  - Method and Charter make collaboration boundaries explicit
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
    became...` phrasing and swaps in `Applied AI Research Engineer`
- Operator command surface:
  - `make start` is the scripted morning startup pass
  - `make end` is operational day-close
  - `make end-git-check` is the final clean-main verification step
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
- Eval lane remains fail-first and binary across lanes:
  - lockset is release-gating
  - growth is fail-tolerant
  - `/viz/pass-fail` is the current live fail-signal instrument:
    - live chart stays on the active window
    - tracked lane cards keep the wider multi-lane surface visible
    - lane cards now link directly to the tracked artifact and promoted note
    - `manual_evals.db` remains the integrated manual-eval warehouse
  - dependency security is now a first-class repo gate:
    - PR dependency review blocks vulnerable dependency diffs
    - CI audits locked Python and Node dependency surfaces
    - CI rejects `requirements.in` / `requirements.lock` drift
  - current promoted non-OCR lane:
    - co-reasoning reliability now closes `14/14` in the latest tracked style snapshot
    - latest one-hour deterministic beta soak closes at `19/21` pass cycles
    - former dominant style pressure did not recur in the broad gate
    - uncertainty-boundary stability is now closed with:
      - resumed soak total: `3961s`
      - `21/21` pass cycles
      - `0` fail cycles
      - `0` recurring failure signals
    - tracked hallucination-boundary coverage is now wider and still green:
      - latest tracked snapshot: `9/9` pass
      - tracked case count: `9`
      - new distinct seams: archive-lore and archive-discipline fabrication
      - current signal-shape surface is now explicit
    - retrieval grounding now has fresh tracked snapshots across both visible branches:
      - retrieval recall: `12/12` pass
      - file search: `5/5` pass
    - current broad gate is holding across style, uncertainty, and co-reasoning
  - current mature method lane is green:
    - growth stability: `25/25` stable, `0` flaky
    - fail-history cohort: `0` active cases
    - runtime OCR follow-up is currently parked
    - current remaining OCR signal is low-pressure exploratory output
      variability inside stable PASS behavior
    - if OCR follow-up reopens, it should be case-design-only and start from:
      - `gx-68844003-002`
      - `gx-6952d743-021`
- Broader hypothesis lane is active again:
  - export-backed behaviour mining now confirms real non-OCR evidence surfaces
  - current backlog counts:
    - co-reasoning reliability: `18` conversations / `14` families
    - operator burden shift: `9` / `8`
    - hallucination boundary: `33` / `24`
    - retrieval grounding: `47` / `40`
    - OCR confidence boundary: `15` / `10`
  - co-reasoning reliability is now the first promoted non-OCR lane
  - tracked style stress lane now has a current tracked snapshot at `14/14`
  - operator burden now has a seeded thin-lane row surface:
    - tracked rows: `7`
    - pass rows: `4`
    - retained fail rows: `2`
    - evicted fail rows: `1`
  - operator burden now has enough export-backed cue coverage to read the lane
    shape clearly without jumping to larger automation
  - the current top export-backed slice is duplicate-heavy and does not
    presently earn more distinct row promotion
- Documentation rule:
  - `DECISIONS` is durable archive
  - `STATE` is the tracked public current-truth surface
  - operator handoff stays local in `docs/peanut/governance/SESSION_HANDOFF.md`

## Active Priorities

1. Keep the public doorway stable and credible.
2. Keep repo research surfaces compact, visual, and easy to scan.
3. Keep the first promoted non-OCR lane visible now that the broad gate is
   holding across style, uncertainty, and co-reasoning.
4. Keep operator-burden row promotion distinct, visible, and resistant to
   clone inflation or over-automation.
5. Keep the mature OCR method lane green and reopen it only from the remaining
   case-design-only watchlist.
6. Keep governance/runtime docs aligned and non-duplicative.

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
