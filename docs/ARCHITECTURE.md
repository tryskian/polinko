# Architecture

## Top-Level Map

- `app.py`
  - CLI chat entrypoint.
- `server.py`
  - FastAPI API entrypoint (`create_app(...)`).
- `config.py`
  - Environment loading + validation.
- `api/`
  - HTTP layer, route contract, middleware, auth/rate-limit integration.
- `core/`
  - Runtime logic (prompting, session/history, personalization, retrieval helpers).
- `frontend/`
  - Vite UI (deprecated for active operations; retained for archive maintenance).
- `tools/`
  - Local automation/eval/reference utilities.
- `tests/`
  - API/runtime regression tests.
- `docs/`
  - Charter, state, decisions, runbook, handoff, and operator references.

## Runtime Flow

1. `server.py` loads config from `config.py`.
2. `server.py` calls `api.app_factory.create_app(config)`.
3. `api/app_factory.py` wires routes + middleware + runtime dependencies.
4. Request execution delegates to `core/` runtime and persistence modules.
5. CLI/API surfaces are canonical; `frontend/` remains archive-maintenance only.

## Data Surfaces

- Runtime chat/session state:
  - SQLite stores (chat history + memory/vector artifacts).
- Eval runtime state (authoritative):
  - `.polinko_history.db` via `core/history_store.py`
    - `message_feedback` (binary `pass`/`fail` + tags/notes/status)
    - `eval_checkpoints` (`pass_count`, `fail_count`, `non_binary_count`)
  - active gate logic is binary-only (`pass`/`fail`); `non_binary_count` is an
    integrity signal only.
- Eval artefacts (non-authoritative):
  - `docs/portfolio/raw_evidence/archive/baseline/*` is the only active
    file-based eval artefact surface.
  - `docs/portfolio/raw_evidence` top-level intake folders/files are
    deprecated and must be archived before new eval cycles.
  - no file-log-driven eval wiring exists in runtime gate decisions.
  - archive/reset utility:
    - `tools/archive_eval_baseline.py`
    - command: `make eval-reset-baseline`
- Human reference index:
  - `.human_reference.db` built from `docs/transcripts`, `docs/research`, `docs/theory`.
  - builder: `tools/build_human_reference_db.py`
  - query presets: `tools/query_human_reference.py`
  - SQL pack: `tools/human_reference_queries.sql`
  - operator flow is offline/query-first (`make human-reference-*`).

## Placement Rules

- API endpoints/middleware/contracts: `api/`
- Prompt/runtime behaviour and policy logic: `core/`
- Deprecated UI maintenance only: `frontend/`
- Eval/report/reference scripts and one-off operators: `tools/`
- Execution state/decisions/handoff documentation: `docs/`

## Governance Flow

- Collaboration/execution policy is anchored in `docs/CHARTER.md`.
- Co-reasoning control rights are human-led for objective/scope/acceptance and
  go/no-go decisions.
- Formal decision records are appended in `docs/DECISIONS.md`.
- Operator procedure lives in `docs/RUNBOOK.md`.
- Current-state checkpoints live in `docs/STATE.md`.
- Next-session carryover constraints live in `docs/SESSION_HANDOFF.md`.
- Policy updates are complete only when all relevant surfaces above are aligned.

## Operational Commands

- Env sanity: `make doctor-env`
- Backend tests: `make test`
- Local API: `make server` or `make server-daemon`
- Optional UI archive-maintenance checks:
  - `npm --prefix frontend run -s test`
  - `npm --prefix frontend run -s build`
- Baseline eval archive/reset: `make eval-reset-baseline`
- Human reference quick query: `make human-reference-relationships`
