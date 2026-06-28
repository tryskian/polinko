# Architecture

![Architecture overview](./architecture.svg)

This page is the structural map of the tracked system.

- Use `docs/runtime/RUNBOOK.md` for operator procedure.
- Use `docs/runtime/OCR_REFERENCE.md` for the OCR lane reference.
- Use `docs/runtime/SURFACE_IA.md` for web surface path roles, manual eval
  workbench naming, and legacy compatibility aliases.
- Use `docs/runtime/PACKAGE_BOUNDARY.md` for the Python package-boundary
  contract and remaining root launcher compatibility.
- Use `docs/runtime/LOCAL_TOOLING.md` for local operator tooling patterns that
  generate ignored inputs, validate them, and preview application before any
  execution gate.
- Use `docs/runtime/OCR_RETRY_EXECUTION_GATE.md` for the local-bundle OCR retry
  execution gate contract.
- Use `docs/runtime/RUNTIME_SURFACE_MAP.md` for the current runtime/operator
  surface map across startup, closeout, background runners, CI, and eval
  tooling.

## Top-Level Map

- `main.py`
  - compatibility launcher for direct CLI chat calls
- `server.py`
  - compatibility shim for `uvicorn server:app`
- `pyproject.toml`
  - Python package metadata and `src` layout configuration
- `src/polinko/`
  - editable-install runtime package boundary
- `src/polinko/cli.py`
  - canonical CLI chat implementation
- `src/polinko/asgi.py`
  - canonical ASGI app construction and runtime-deps access
- `src/polinko/config.py`
  - canonical environment loading and validation implementation
- `src/polinko/api/`
  - HTTP layer, route spec, middleware, and wiring
- `src/polinko/core/`
  - runtime logic, prompting, session/history, and retrieval helpers
- `tools/`
  - local operators, evals, reports, and renderers
  - includes `tools/check_package_install.py` for editable-install validation
  - includes read-only inventory/status tools for local evidence inspection
  - includes the manual-eval health CLI entrypoint plus focused
    `manual_eval_cli_*` modules for contracts, parser construction, output,
    dispatch, and shared dispatch support
- `tests/`
  - API and runtime regression tests
- `Makefile`
  - root operator target router and include order
- `makefiles/`
  - focused Make target families and configuration includes
- `makefiles/build/`
  - build target fragments for CI aggregation, dependency lock/install flows,
    package checks, and security gates
- `makefiles/build/dependencies/`
  - dependency target fragments for install, refresh, and lockfile workflows
- `makefiles/checks/`
  - check target fragments for tests, Python static analysis, docs/rendering,
    runtime audits, and local developer helpers
- `makefiles/checks/tests/`
  - test target fragments for unit-test entrypoints and the backend gate
- `makefiles/checks/python/`
  - Python check fragments for compile helpers, type checks, and Ruff checks
- `makefiles/checks/docs/`
  - documentation check fragments for linting, diagram rendering, transcripts,
    and closeout freshness
- `makefiles/checks/dev-tools/`
  - local developer helper target fragments for repo search, pre-commit, and
    local GitHub Actions runner helpers
- `makefiles/checks/runtime-audits/`
  - runtime audit target fragments for shell helper checks, path leak checks,
    runtime config/risk/operator checks, and environment doctor
- `makefiles/checks/runtime-audits/doctor-env/`
  - environment doctor fragments for interpreter source labelling, active
    virtualenv derivation, module execution, and target wiring
- `makefiles/config/runtime/`
  - runtime configuration fragments for core app URLs, local URL launching,
    OpenAI account summaries, keep-awake state, and server-daemon defaults
- `makefiles/config/runtime/openai-account/`
  - OpenAI account config fragments for base API/auth defaults, cost defaults,
    usage defaults, project/limits defaults, and env assembly
- `makefiles/config/runtime/caffeinate/`
  - repo-managed caffeinate config fragments for state files, repo/activity
    settings, wake-lock command matching, runner defaults, and env/activity
    macro assembly
- `makefiles/config/surfaces/`
  - role-owned configuration fragments for notebooks, manual eval workbench,
    local browser helpers, and portfolio/mockup surfaces
- `makefiles/config/surfaces/portfolio/`
  - portfolio configuration fragments for app/path defaults, mockup server
    defaults, mockup env assembly, and launch-mode defaults
- `makefiles/config/surfaces/manual-evals/`
  - manual-eval configuration fragments for shared filters,
    feedback/reclassify flows, overlay/source-index settings, and OCR retry
    settings
- `makefiles/config/surfaces/manual-evals/ocr-retry/`
  - manual-eval OCR retry configuration fragments for base inputs, selection
    args, execution/report args, and feedback closure backup/restore args
- `makefiles/config/evals/`
  - role-owned eval configuration fragments for quality gates, OCR case
    sources, eval sidecar, OCR runners, and report workflows
- `makefiles/config/evals/gates/`
  - eval gate configuration fragments for quality-gate server settings,
    eval-smoke settings, hallucination judge settings, suite harness defaults,
    and local gate runner wiring
- `makefiles/config/evals/gates/runner/`
  - local eval gate runner environment fragments for base runtime, smoke
    stores, gate stores, retrieval/OCR, and behaviour gates
- `makefiles/config/evals/ocr-cases/`
  - OCR-case configuration fragments for source paths, export settings,
    transcript-derived case paths, review outputs, benchmark selectors, and
    intake workflow wiring
- `makefiles/config/evals/ocr-cases/intake-workflow/`
  - OCR intake workflow environment fragments for script/base runtime,
    export-root wiring, transcript case paths, transcript review/delta,
    generalization review, growth caps, and benchmark selectors
- `makefiles/config/evals/ocr-runs/`
  - OCR-run configuration fragments for defaults, common helper wiring, direct
    runners, transcript lanes, focus stability, and growth workflows
- `makefiles/config/evals/ocr-runs/direct-runners/`
  - direct OCR runner configuration fragments for handwriting, case, and
    stability runner env wiring
- `makefiles/config/evals/ocr-runs/focus/`
  - OCR focus stability workflow env fragments for script defaults, runtime
    helpers, runner script, eval guards, case path, run controls, report
    outputs, rate-limit backoff, fail-cohort input, and composed env assembly
- `makefiles/config/evals/ocr-runs/transcript-lanes/`
  - OCR-run transcript-lane configuration fragments for base transcript
    workflow env and lane-specific workflow env
- `makefiles/config/evals/ocr-runs/transcript-lanes/lane-workflow/`
  - OCR transcript-lane workflow env fragments for script/runner wiring, case
    paths, eval runtime, stability/rate-limit settings, benchmark report
    outputs, and composed env assembly
- `makefiles/config/evals/ocr-runs/growth/`
  - OCR-run growth configuration fragments for growth stability workflow env
    and growth case/batch workflow env
- `makefiles/config/evals/ocr-runs/growth/stability-workflow/`
  - OCR growth stability workflow env fragments for script defaults, runtime
    helpers, runner script, case path, run-control/rate-limit knobs,
    report outputs, and composed env assembly
- `makefiles/config/evals/ocr-runs/growth/case-workflow/`
  - OCR growth case workflow env fragments for script defaults, runtime
    helpers, runner scripts, case knobs, batch knobs, report outputs, and
    composed env assembly
- `makefiles/config/evals/ocr-runs/defaults/`
  - OCR-run default fragments for stability, growth/fail-cohort, focus,
    growth batch, and benchmark defaults
- `makefiles/config/evals/reports/`
  - eval report configuration fragments for report runner env, parallel report
    runner env, OCR report builder env, OCR report workflow env, and OCR lane
    inventory defaults
- `makefiles/config/evals/reports/ocr-builder/`
  - OCR report builder configuration fragments for base runtime,
    growth-metrics, growth-fail-cohort, focus-case, and focus-fail-pattern
    env wiring
- `makefiles/surfaces/`
  - role-owned target fragments for notebooks, manual eval workbench,
    portfolio/mockup workflows, and local browser helpers
- `makefiles/surfaces/portfolio/`
  - portfolio target fragments for dependency install, static build, preview
    launch modes, and mockup lifecycle
- `makefiles/surfaces/portfolio/preview/`
  - portfolio preview fragments for the server-backed launch recipe and
    rebuild/system/playwright launch-mode aliases
- `makefiles/surfaces/portfolio/preview/launch/`
  - portfolio launch recipe fragments for cache-busted URL construction,
    Playwright launch, system/no-launch handling, and target wiring
- `makefiles/surfaces/manual-evals/`
  - manual-eval target fragments for warehouse database, feedback,
    overlay/source-index, and OCR retry helper workflows
- `makefiles/surfaces/manual-evals/feedback/`
  - manual-eval feedback fragments for review/navigation, decision drafts and
    previews, and reclassification preview/apply workflows
- `makefiles/surfaces/manual-evals/ocr-retry/`
  - manual-eval OCR retry target fragments for read-only packets, selection
    and readiness, execution/reporting, and feedback closure
- `makefiles/evals/`
  - eval target fragments for aliases, core suites, gates, OCR intake, and OCR
    runners
- `makefiles/evals/ocr-intake/`
  - OCR intake target fragments for export/case-mining targets, benchmark case
    builders, and review/delta helpers
- `makefiles/evals/gates/`
  - eval gate target fragments for smoke gates, sidecar lifecycle, operator
    reports, and quality/hallucination gates
- `makefiles/evals/ocr-runs/`
  - OCR-run target fragments for base transcript runners, growth runners,
    transcript lanes, report-derived views, and focus stability
- `makefiles/evals/ocr-runs/lanes/`
  - OCR-run transcript lane target fragments for lane case builds and
    benchmark stability runs
- `makefiles/evals/core/`
  - core eval target fragments for retrieval/file-search, quality and
    response-behaviour, direct OCR suites, CLIP, report aggregation, and trace
    maintenance
- `makefiles/evals/core/quality/`
  - quality eval target fragments for hallucination, style, and
    response-behaviour
- `makefiles/evals/core/ocr/`
  - direct OCR eval target fragments for safety, base OCR, handwriting, and
    recovery
- `makefiles/evals/aliases/`
  - eval alias target fragments for OCR intake/mining, OCR run/focus/benchmark
    shorthands, and utility/inventory aliases
- `makefiles/evals/aliases/utilities/`
  - utility alias fragments for runtime-null audit, OCR inventory, and OCR
    data/notebook workflows
- `makefiles/evals/aliases/ocr-intake/`
  - OCR intake alias fragments for base intake aliases, lane-filter aliases,
    and signal/status filter aliases
- `makefiles/evals/aliases/ocr-runs/`
  - OCR-run alias fragments for transcript/growth aliases, modality aliases,
    focus/stability aliases, the OCR kernel workflow alias, and benchmark
    aliases
- `makefiles/runtime/`
  - runtime target fragments for core lifecycle, server-daemon, local URL,
    OpenAI account, keep-awake, and privacy guard targets
- `makefiles/runtime/local-urls/`
  - runtime local URL target fragments for API docs URLs and PASS/FAIL viz
    URLs
- `makefiles/runtime/core/`
  - runtime core target fragments for interactive entrypoints,
    startup/closeout lifecycle, git hygiene, and consolidated status
- `docs/`
  - governance, runtime references, and research docs
- `apps/portfolio/`
  - current Vite source app for the public portfolio doorway
  - default `PORTFOLIO_APP_DIR`
- `public/portfolio/`
  - current tracked static build output served by `/portfolio`
  - default `PORTFOLIO_STATIC_DIR`
- `frontend/` and `ui/`
  - retired web surface directory names
  - legacy Make/config aliases remain compatibility-only where documented

## Runtime Flow

1. `server.py` forwards `server:app` compatibility to `polinko.asgi`.
2. `polinko.asgi` loads config from `polinko.config`.
3. `polinko.asgi` creates the FastAPI app through `polinko.api.app_factory`.
4. `src/polinko/api/` wires routes, middleware, and runtime dependencies.
5. request execution delegates into `polinko.core` runtime and persistence
   modules
6. runtime history and eval state write to local SQLite stores under
   `.local/runtime_dbs/active/`
7. `POST /chat` and `/chats/*` are active chat-facing manual eval workbench
   surfaces; deterministic fixture mode supports smoke tests, and default
   remains `live`
8. active gate semantics stay scoped:
   - OCR case outcomes are `pass` / `fail`
   - broader manual and non-OCR lanes may still use `retain` / `evict` after
     `fail` as upstream case curation
9. CLI chat implementation runs through `polinko.cli`; `make chat`,
   `polinko-chat`, and root `main.py` launch that packaged entrypoint. The
   legacy root `app.py` launcher is retired.

## Data Surfaces

- live runtime DBs:
  - `.local/runtime_dbs/active/`
- manual eval workbench:
  - notebooks launched by `make notes`, `make notebook`, and `make nb`
  - local evidence databases
  - chat artifacts, feedback, checkpoints, notes, exports, and runtime history
- runtime, workbench, and eval history:
  - `.local/runtime_dbs/active/history.db`
  - key tables:
    - `chats`
    - `messages`
    - `message_feedback`
    - `eval_checkpoints`
    - `ocr_runs`
- integrated manual-eval warehouse:
  - `.local/runtime_dbs/active/manual_evals.db`
- local report surfaces:
  - `.local/eval_reports/`
- local eval cases and artefacts:
  - `.local/eval_cases/`
- local notebook workspace:
  - `.local/notebooks/`
- read-only OCR inventory:
  - `make ocr-inventory`
  - `make ocr-inventory-json`
  - reports local evidence shape and freshness without eval execution
- evidence diagram payload:
  - built from the Sankey payload generator
  - bridges Beta 1.0 manual feedback with current OCR report counts

## Placement Rules

- active `src/` and `tools/` Python imports use `polinko.*`
- API endpoints, middleware, and specs:
  - `src/polinko/api/`
- prompt and runtime behaviour:
  - `src/polinko/core/`
- eval, report, and local operator scripts:
  - `tools/`
- tracked repo truth and procedure:
  - `docs/`
- private transcripts and working notes:
  - local `docs/peanut/`
- private portfolio mockups and screenshots:
  - local `docs/peanut/assets/portfolio-mockups/`
- web surface source/output naming:
  - `docs/runtime/SURFACE_IA.md`
- manual eval workbench trace naming:
  - `manual_eval_workbench/eval_submission`
  - `manual_eval_workbench_submission`
- Python package-boundary migration contract:
  - `docs/runtime/PACKAGE_BOUNDARY.md`
- local operator tooling contract:
  - `docs/runtime/LOCAL_TOOLING.md`
- historical beta references:
  - `docs/eval/`

## Governance Flow

- `CHARTER`
  - durable rules and collaboration model
- `DECISIONS`
  - durable decision history
- `STATE`
  - tracked current truth
- `RUNBOOK`
  - operator procedure
- `OCR_REFERENCE`
  - OCR eval lane reference
- `PACKAGE_BOUNDARY`
  - Python package-boundary migration contract
- `LOCAL_TOOLING`
  - local inventory/status, operator input, validation, preview, and
    execution-gate contract
- `OCR_RETRY_EXECUTION_GATE`
  - local-bundle OCR retry execution gate shape, mutation boundary, and
    rollback/inspection/closure-preview/apply-design contract
- `RUNTIME_SURFACE_MAP`
  - current startup, closeout, runner, CI, and eval/tooling map
- local `SESSION_HANDOFF`
  - active slice and next-session carryover

Policy changes are complete only when the affected surfaces agree.
