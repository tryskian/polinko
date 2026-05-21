<!-- @format -->

# Project State

Last updated: 2026-05-20

## Current Truth

- Backend-first runtime remains canonical:
  - FastAPI API + chat-facing manual eval workbench endpoints are active
    execution and manual-eval surfaces
  - ASGI app construction lives in `src/polinko/asgi.py`
  - root `server.py` remains the `uvicorn server:app` compatibility shim
  - CLI chat implementation lives in `src/polinko/cli.py`
  - `make chat`, `polinko-chat`, and root `main.py` launch the packaged CLI
  - legacy root `app.py` has been retired after the deprecation/removal
    preflight found no active tracked or focused local ignored-lane launcher
    usage
  - Python package-boundary contract is documented; `config`, API,
    and core runtime implementation now live under `src/polinko/`
  - `pyproject.toml` and `src/polinko/` provide the editable-install rail for
    the runtime package
  - legacy root `config.py` has been retired after the legacy-import preflight
    found no active tracked or focused local ignored-lane root import usage
  - legacy root `api/` has been retired after the legacy-import preflight
    found no active tracked or focused local ignored-lane root import usage
  - legacy root `core/` has been retired after the legacy-import preflight
    found no active tracked or focused local ignored-lane root import usage
  - the package-boundary audit confirms active `src/` and `tools/` Python
    imports use `polinko.*`, while remaining root compatibility surfaces are
    launchers only
  - the entrypoint compatibility contract maps `make chat`, `python main.py`,
    `polinko-chat`, `make server`, `make localhost`, `make server-daemon`,
    local eval gates, and Docker to their packaged CLI or ASGI implementation
    paths
  - the root launcher readiness audit records `server.py` as not
    retirement-ready
    while `server:app` remains active in Docker, Make defaults, server-daemon,
    and local eval gates
  - `app.py`, `config.py`, root `api/`, and root `core/` are retired;
    remaining root launcher retirement work stays surface-specific and must
    preserve manual eval and operator workflows
  - prompt and runtime behaviour stay minimal and deterministic
  - notebooks, local evidence databases, `/chat`, and `/chats/*` remain active
    because they feed manual evals, feedback, checkpoints, exports, and
    runtime history
- The repository is the research object:
  - tracked docs, code, tests, and reports are canonical truth
  - public-facing writing is the derived publication layer from repo truth
  - local/private material stays in `docs/peanut/`
- Refactor method is human-led:
  - the human lead owns scope, method, acceptance, and go/no-go decisions
  - Codex owns implementation, validation, Git/PR flow, and hygiene execution
  - cleanup proceeds one kernel at a time from clean synced `main`
- Public-facing surfaces remain derived from repo truth:
  - the root README now points to public research docs, not local portfolio
    commands
  - portfolio source lives under `apps/portfolio/`, while tracked static output
    stays under `public/portfolio/`
  - `frontend` and `ui` are retired web-surface names; remaining Make/config
    references are compatibility aliases only
  - private portfolio mockups and screenshots stay in `docs/peanut/`
  - private portfolio mockups use `docs/peanut/assets/portfolio-mockups/`
  - promotion from private portfolio work to public docs requires explicit
    approval
- The eval contract is explicit and binary:
  - release outcomes are `pass` / `fail`
  - OCR case judgment remains `pass` / `fail`
  - OCR-ready candidate cleanup happens upstream of OCR judgment
- Polinko is entering the next method beta from a frozen Beta 2.3 snapshot:
  - fail-first evaluation is the active posture
  - Beta 2.3 evidence is frozen under `docs/eval/beta_2_3/`
  - `pre-Beta 2.4` is staged as the next research-model contract
  - the discarded run-level rollup hypothesis is not being carried forward
  - non-OCR lanes stay source-first rather than run-verdict-first
  - the manual eval workbench, including notebooks, local evidence databases,
    `/chat`, `/chats/*`, and runtime history, remains source evidence for that
    contract
  - manual eval workbench evidence rows link feedback to matching OCR
    source/result messages when a case link exists, rather than treating the
    latest OCR run in a session as the judged case
  - `/viz/pass-fail` also uses feedback-to-result message matching for manual
    eval rows, so run-specific chart rows do not borrow unrelated session
    feedback
  - active eval visualization labels use source-first monitor wording rather
    than retired run-level rollup labels
  - source-first manual eval payloads expose `summary_unit` for lane-summary
    wording; the temporary `rollup_unit` compatibility alias was retired after
    a tracked and local consumer audit found no active dependency
  - source-first manual eval payloads expose
    `schema_version=polinko.manual_eval_source_first.v1`; generated
    `manual_evals.db` metadata exposes
    `schema_version=polinko.manual_evals_db.v1`
  - `make api-smoke` includes non-browser checks for `/manual-evals/surface`
    and `/viz/pass-fail/data` so source-first schema and summary-unit drift is
    caught in the startup/runtime smoke path
  - `/manual-evals/surface` and `/viz/pass-fail/data` expose read-only
    `data_freshness` status for the local manual eval warehouse so stale,
    schema-old, unknown, or missing source data is visible without rebuilding
    local databases
  - `data_freshness` compares source history counts against the manual eval
    import scope, so idle chats outside feedback/checkpoint/OCR evidence do
    not make a freshly rebuilt warehouse stale
  - `make manual-evals-db-status` prints terminal-native freshness without
    mutating local databases, while `make manual-evals-db` preserves an
    existing warehouse under `.local_archive/manual-evals-db-refresh-*` before
    rebuilding and prints the post-refresh status
  - `make manual-evals-db-health` reports read-only source-quality signals for
    the current warehouse, including source coverage, missing image assets,
    feedback-to-result links, open feedback, and session evidence mix
  - manual eval warehouse rebuilds resolve OCR source images from extracted
    files first across private screenshot roots, tracked `docs/eval/`
    snapshots, and local export roots, then matching files inside `.zip`
    archives under configured image roots; archive-backed thumbnails are built
    without extracting files into the repo
  - generated trace artifacts from manual submissions use manual eval workbench
    names, not `ui` names
  - co-reasoning is the first promoted non-OCR lane
  - uncertainty-boundary, hallucination-boundary, retrieval, and
    response-behaviour surfaces are operationalized
  - operator burden remains the active thin lane
  - no additional non-OCR lane currently meets promotion criteria
  - the lane map is current, and the research surface remains open
  - OCR remains one mature method lane inside the broader project
  - OCR is stabilized on the current image set, with broader
    generalization pressure as the next kernel
  - OCR intake now uses transcript-mined episodes plus OCR-ready
    generalization candidates
  - OCR verdicts stay `pass` / `fail` under that broader intake
- Branch protection on `main` remains active:
  - PR required
  - strict status checks enabled
  - squash-only merge
- Development setup and dependency gates are aligned to canonical paths:
  - devcontainer setup creates `.venv`
  - devcontainer VS Code settings use repo-owned Ruff and mypy tooling from
    `.venv`
  - Python dependencies use `requirements.in` plus generated
    `requirements.txt`, matching pip-tools and Dependabot conventions
  - portfolio Node setup uses `apps/portfolio/`
  - root and portfolio npm locks both have audit and Dependabot coverage
  - portfolio installs prefer `npm ci` when a lockfile is present
  - pre-commit runs lightweight repo-owned Ruff and markdownlint checks, while
    mypy remains a CI/closeout gate and Pyright remains advisory
- The type-check gate is explicit and scoped:
  - `make type-check` runs mypy against active `src/` and `tools/` Python
    code
  - frozen eval snapshots, local `docs/peanut` material, and untyped tests are
    excluded from the type-check gate
  - `make ci-python-type-check`, GitHub CI, and `make end` enforce the same
    scoped mypy surface
  - Pyright is repo-owned as an advisory/editor check:
    `make pyright-check` runs the pinned root Node dependency against
    `pyrightconfig.json`, but mypy remains the required CI and closeout gate
- Test and runtime resource hygiene is explicit:
  - sqlite connections are closed through explicit lifecycle handling
  - tests reject direct `with sqlite3.connect(...)` usage so Python 3.14
    ResourceWarning noise stays out of `make test`
- Runtime lifecycle controls are repo-managed:
  - `make caffeinate` launches the managed wake-lock process in a detached
    child session through the configured Python launcher
  - `make caffeinate-status`, `make decaffeinate`, and `make end` operate on
    the repo-owned PID without adopting unrelated user wake-lock processes
  - local URL helpers such as `make docs`, `make open-api-docs`, and
    `make viz` print the target URL by default instead of launching a browser
  - explicit browser launch remains available through `make docs-open`,
    `make open-api-docs-browser`, `make viz-open`, and `make open-viz`
- Documentation roles are explicit:
  - `CHARTER` holds durable rules
  - `STATE` holds tracked current truth
  - `RUNBOOK` holds operator procedure
  - `ARCHITECTURE` holds stable system shape
  - `PACKAGE_BOUNDARY` holds the Python package-boundary contract
  - `make package-install-check` verifies the editable-install rail
  - local `SESSION_HANDOFF` holds the active slice
  - `make end` now mirrors the legacy `make eod` closeout routine directly

## Active Priorities

1. Keep the public doorway stable and credible.
2. Keep tracked research docs compact and non-duplicative.
3. Keep the promoted non-OCR lane visible as the broader proof surface grows.
4. Keep operator-burden and related thin-lane work grounded in real evidence
   and distinct lane signal.
5. Keep OCR moving from current-set stability into generalization pressure.
6. Keep cleanup/refactor work anchored to the frozen Beta 2.3 baseline.
7. Keep exploring new seams without forcing promotion before the signal earns
   it.

## Canonical Sources

- Rules:
  - `docs/governance/CHARTER.md`
- Current truth:
  - `docs/governance/STATE.md`
- Procedure:
  - `docs/runtime/RUNBOOK.md`
- Structure:
  - `docs/runtime/ARCHITECTURE.md`
- Durable history:
  - `docs/governance/DECISIONS.md`
- Active local carryover:
  - `docs/peanut/governance/SESSION_HANDOFF.md`

## Validation Baseline

- `make doctor-env`
- `make api-smoke`
- `make ruff-check`
- `make ruff-format-check`
- `make lint-docs`
- `make package-install-check`
- `make type-check`
- `make test`
- `make security-checks`
- `make ci` when checking the local equivalent of GitHub CI job targets
- `make end`
- `make end-docs-check` when validating current-truth freshness explicitly
- `make end-git-check` after merge and sync
