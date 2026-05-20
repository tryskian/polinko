# Architecture

![Architecture overview](./architecture.svg)

This page is the structural map of the tracked system.

- Use `docs/runtime/RUNBOOK.md` for operator procedure.
- Use `docs/runtime/OCR_REFERENCE.md` for the OCR lane reference.
- Use `docs/runtime/SURFACE_IA.md` for web surface path roles and planned
  directory renames.
- Use `docs/runtime/PACKAGE_BOUNDARY.md` for the Python package-boundary
  migration contract and compatibility layer.

## Top-Level Map

- `main.py`
  - compatibility launcher for direct CLI chat calls
- `app.py`
  - lazy compatibility shim for older CLI calls
- `server.py`
  - compatibility shim for `uvicorn server:app`
- `config.py`
  - compatibility shim for older config imports
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
- `api/`
  - compatibility shims for older `api.*` imports
- `src/polinko/core/`
  - runtime logic, prompting, session/history, and retrieval helpers
- `core/`
  - compatibility shims for older `core.*` imports
- `tools/`
  - local operators, evals, reports, and renderers
  - includes `tools/check_package_install.py` for editable-install validation
- `tests/`
  - API and runtime regression tests
- `Makefile`
  - root operator target router and include order
- `makefiles/`
  - focused Make target families and configuration includes
- `makefiles/evals/`
  - eval target fragments for aliases, core suites, gates, OCR intake, and OCR
    runners
- `docs/`
  - governance, runtime references, and research docs
- `apps/portfolio/`
  - current Vite source app for the public portfolio doorway
  - default `PORTFOLIO_APP_DIR`
- `public/portfolio/`
  - current tracked static build output served by `/portfolio`
  - default `PORTFOLIO_STATIC_DIR`

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
   `polinko-chat`, root `main.py`, and legacy `app.py` launch that packaged
   entrypoint.

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
- evidence diagram payload:
  - built from the Sankey payload generator
  - bridges Beta 1.0 manual feedback with current OCR report counts

## Placement Rules

- active `src/` and `tools/` Python imports use `polinko.*`
- API endpoints, middleware, and specs:
  - `src/polinko/api/`
  - root `api/` stays compatibility-only during the package-boundary migration
- prompt and runtime behaviour:
  - `src/polinko/core/`
  - root `core/` stays compatibility-only during the package-boundary migration
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
- Python package-boundary migration contract:
  - `docs/runtime/PACKAGE_BOUNDARY.md`
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
- local `SESSION_HANDOFF`
  - active slice and next-session carryover

Policy changes are complete only when the affected surfaces agree.
