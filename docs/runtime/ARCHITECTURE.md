# Architecture

![Architecture overview](./architecture.svg)

This page is the structural map of the tracked system.

- Use `docs/runtime/RUNBOOK.md` for operator procedure.
- Use `docs/runtime/OCR_REFERENCE.md` for the OCR lane reference.

## Top-Level Map

- `app.py`
  - CLI chat entrypoint
- `server.py`
  - FastAPI API entrypoint
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

## Runtime Flow

1. `server.py` loads config from `config.py`.
2. `server.py` creates the FastAPI app through `api.app_factory`.
3. `api/` wires routes, middleware, and runtime dependencies.
4. request execution delegates into `core/` runtime and persistence modules
5. runtime history and eval state write to local SQLite stores under
   `.local/runtime_dbs/active/`
6. `POST /chat` supports deterministic fixture mode for smoke; default remains
   `live`
7. active gate semantics remain binary:
   - release outcomes are `pass` / `fail`
   - after `fail`, failure disposition is `retain` / `evict`

## Data Surfaces

- live runtime DBs:
  - `.local/runtime_dbs/active/`
- runtime and eval history:
  - `.local/runtime_dbs/active/history.db`
  - key tables:
    - `message_feedback`
    - `eval_checkpoints`
    - `ocr_runs`
- integrated manual-eval warehouse:
  - `.local/runtime_dbs/active/manual_evals.db`
- local report surfaces:
  - `.local/eval_reports/`
- local eval cases and artefacts:
  - `.local/eval_cases/`
- portfolio evidence surface:
  - `GET /portfolio/sankey-data`
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
