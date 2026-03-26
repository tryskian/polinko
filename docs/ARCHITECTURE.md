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
  - Vite UI (chat, eval controls, checkpoint triage/export).
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
5. UI (`frontend/`) calls API routes (`/chat`, `/skills/*`, `/chats/*`) over JSON.

## Data Surfaces

- Runtime chat/session state:
  - SQLite stores (chat history + memory/vector artifacts).
- Eval/operator evidence:
  - `docs/portfolio/raw_evidence/*` (PASS/FAIL/INBOX + metadata/audit outputs).
  - active feedback/checkpoint contract is strict binary (`pass`/`fail`) with
    `non_binary_count` reserved for integrity checks.
- Human reference index:
  - `.human_reference.db` built from `docs/transcripts`, `docs/research`, `docs/theory`.
  - builder: `tools/build_human_reference_db.py`
  - query presets: `tools/query_human_reference.py`
  - SQL pack: `tools/human_reference_queries.sql`
  - operator flow is offline/query-first (`make human-reference-*`).

## Placement Rules

- API endpoints/middleware/contracts: `api/`
- Prompt/runtime behaviour and policy logic: `core/`
- UI behaviour and interaction model: `frontend/`
- Eval/report/reference scripts and one-off operators: `tools/`
- Execution state/decisions/handoff documentation: `docs/`

## Governance Flow

- Collaboration/execution policy is anchored in `docs/CHARTER.md`.
- Formal decision records are appended in `docs/DECISIONS.md`.
- Operator procedure lives in `docs/RUNBOOK.md`.
- Current-state checkpoints live in `docs/STATE.md`.
- Next-session carryover constraints live in `docs/SESSION_HANDOFF.md`.
- Policy updates are complete only when all relevant surfaces above are aligned.

## Operational Commands

- Env sanity: `make doctor-env`
- Backend tests: `make test`
- Frontend tests: `npm --prefix frontend run -s test`
- Frontend build: `npm --prefix frontend run -s build`
- Local API: `make server` or `make server-daemon`
- UI dev: `make ui-dev`
- Human reference quick query: `make human-reference-relationships`
