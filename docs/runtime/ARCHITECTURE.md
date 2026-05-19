# Architecture

![Architecture overview](./architecture.svg)

This page is the structural map of the tracked system.

- Use `docs/runtime/RUNBOOK.md` for operator procedure.
- Use `docs/runtime/OCR_REFERENCE.md` for the OCR lane reference.
- Use `docs/runtime/SURFACE_IA.md` for web surface path roles and planned
  directory renames.

## Top-Level Map

- `main.py`
  - operator CLI chat entrypoint
- `app.py`
  - compatibility launcher for older CLI calls
- `server.py`
  - FastAPI API and chat workbench entrypoint
- `config.py`
  - environment loading and validation
- `api/`
  - HTTP layer, route spec, middleware, and wiring
- `core/`
  - runtime logic, prompting, session/history, and retrieval helpers
- `tools/`
  - local operators, evals, reports, and renderers
- `tests/`
  - API and runtime regression tests
- `docs/`
  - governance, runtime references, and research docs
- `frontend/`
  - current Vite source app for the public portfolio doorway
- `ui/`
  - current tracked static build output served by `/portfolio`

## Runtime Flow

1. `server.py` loads config from `config.py`.
2. `server.py` creates the FastAPI app through `api.app_factory`.
3. `api/` wires routes, middleware, and runtime dependencies.
4. request execution delegates into `core/` runtime and persistence modules
5. runtime history and eval state write to local SQLite stores under
   `.local/runtime_dbs/active/`
6. `POST /chat` and `/chats/*` are active chat workbench and manual-eval
   surfaces; deterministic fixture mode supports smoke tests, and default
   remains `live`
7. active gate semantics stay scoped:
   - OCR case outcomes are `pass` / `fail`
   - broader manual and non-OCR lanes may still use `retain` / `evict` after
     `fail` as upstream case curation
8. CLI chat runs through `main.py`; `app.py` only forwards legacy launches to
   that entrypoint.

## Data Surfaces

- live runtime DBs:
  - `.local/runtime_dbs/active/`
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

- API endpoints, middleware, and specs:
  - `api/`
- prompt and runtime behaviour:
  - `core/`
- eval, report, and local operator scripts:
  - `tools/`
- tracked repo truth and procedure:
  - `docs/`
- private transcripts and working notes:
  - local `docs/peanut/`
- private portfolio mockups and screenshots:
  - local `docs/peanut/assets/tumbles/portfolio/`
- web surface source/output naming:
  - `docs/runtime/SURFACE_IA.md`
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
- local `SESSION_HANDOFF`
  - active slice and next-session carryover

Policy changes are complete only when the affected surfaces agree.
