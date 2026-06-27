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
- `makefiles/checks/`
  - check target fragments for tests, Python static analysis, docs/rendering,
    runtime audits, and local developer helpers
- `makefiles/config/runtime/`
  - runtime configuration fragments for core app URLs, local URL launching,
    OpenAI account summaries, keep-awake state, and server-daemon defaults
- `makefiles/config/surfaces/`
  - role-owned configuration fragments for notebooks, manual eval workbench,
    local browser helpers, and portfolio/mockup surfaces
- `makefiles/config/evals/`
  - role-owned eval configuration fragments for quality gates, OCR case
    sources, eval sidecar, OCR runners, and report workflows
- `makefiles/config/evals/ocr-runs/`
  - OCR-run configuration fragments for defaults, common helper wiring, direct
    runners, transcript lanes, focus stability, and growth workflows
- `makefiles/surfaces/`
  - role-owned target fragments for notebooks, manual eval workbench,
    portfolio/mockup workflows, and local browser helpers
- `makefiles/surfaces/manual-evals/`
  - manual-eval target fragments for warehouse database, feedback,
    overlay/source-index, and OCR retry helper workflows
- `makefiles/evals/`
  - eval target fragments for aliases, core suites, gates, OCR intake, and OCR
    runners
- `makefiles/runtime/`
  - runtime target fragments for core lifecycle, server-daemon, local URL,
    OpenAI account, keep-awake, and privacy guard targets
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
