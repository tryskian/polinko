# Architecture

![Architecture overview](./architecture.svg)

This page is the structural map of the tracked system. Use
`docs/runtime/RUNBOOK.md` for procedure and
`docs/runtime/OCR_REFERENCE.md` for the OCR eval reference.

## Top-Level Map

- `app.py`
  - CLI chat entrypoint.
- `server.py`
  - FastAPI API entrypoint (`create_app(...)`).
- `config.py`
  - Environment loading + validation.
- `api/`
  - HTTP layer, route spec, middleware, auth/rate-limit integration.
- `core/`
  - Runtime logic (prompting, session/history, personalization, retrieval helpers).
- `tools/`
  - Local operators, evals, reports, and renderers.
- `tests/`
  - API/runtime regression tests.
- `docs/`
  - Governance, runtime references, and public research docs.

## Runtime Flow

1. `server.py` loads config from `config.py` and calls
   `api.app_factory.create_app(config)`.
2. `api/` wires routes, middleware, and runtime dependencies.
3. Request execution delegates into `core/` runtime and persistence modules.
4. Runtime history and eval state write to local SQLite stores under
   `.local/runtime_dbs/active/`.
5. `POST /chat` supports deterministic fixture mode for smoke; default remains
   `live`.
6. Eval contract stays split and binary:
   - the first gate proves hard contract correctness
   - later interpretive detail does not rewrite gate arithmetic
   - `pass` / `fail` are the only release outcomes
   - after `fail`, failure disposition is:
     - `retain`
     - `evict`
   - `retain` keeps the failure in-scope as lane evidence
   - `evict` is upstream case removal, not a third gate state
   - OCR is one mature method lane; co-reasoning now lives in the tracked style
     lane
   - detailed OCR commands live in `docs/runtime/OCR_REFERENCE.md`

## Data Surfaces

- Runtime stores:
  - live DBs live under `.local/runtime_dbs/active/`
  - archives live under `.local/runtime_dbs/archive/`
- Raw runtime/eval history:
  - `.local/runtime_dbs/active/history.db` via `core/history_store.py`
  - key tables:
    - `message_feedback`
    - `eval_checkpoints`
    - `ocr_runs`
  - active gate logic is binary-only; non-binary counts are integrity signals
  - post-fail `retain` / `evict` belongs outside gate arithmetic
  - `evict` belongs to case-design or miner cleanup upstream, not gate
    arithmetic
- Integrated manual-eval warehouse:
  - `.local/runtime_dbs/active/manual_evals.db`
  - rebuilt by `make manual-evals-db`
  - imports current `history.db` plus optional Beta 1.0 legacy history
  - app-facing source for integrated manual-eval analysis
- Local report surfaces:
  - `.local/eval_reports/` powers pass/fail views and OCR report pages
  - report timestamps and run IDs define ordering, not filesystem copy times
- Portfolio evidence surface:
  - `GET /portfolio/sankey-data` bridges Beta 1.0 manual feedback with current
    OCR report counts through an evidence-continuity anchor
  - data must stay real and visibly empty when sources are missing
  - `GET /portfolio` serves the lean tracked doorway or local `ui/index.html`
    when present
- OCR eval artefacts:
  - lockset reports, growth stability, growth metrics, and focus replay outputs
    are local operational evidence
  - historical beta docs explain transition history but do not drive active
    gates

## Placement Rules

- API endpoints/middleware/specs: `api/`
- Prompt/runtime behaviour and policy logic: `core/`
- Eval/report/reference scripts and local operators: `tools/`
- Tracked repo truth and procedure: `docs/`
- Private transcripts and working notes: local `docs/peanut/`
- Historical beta references: `docs/eval/`

## Governance Flow

- `CHARTER` defines collaboration and repo rules.
- `DECISIONS` stores durable decisions.
- `STATE` stores tracked current truth.
- `RUNBOOK` owns operator procedure.
- `OCR_REFERENCE` owns the OCR eval reference.
- local `SESSION_HANDOFF` owns next-session carryover.
- local `docs/peanut/` owns transcripts, theory, and working notes.
- A policy change is complete only when the affected surfaces agree.

## Operational Commands

- Startup ritual: `make start`
- Day-close routine: `make end`
- Branch-local closeout validation: `make end-preflight`
- Clean-main closeout gate: `make end-git-check`
- Managed wake lock:
  - `make caffeinate`
  - `make caffeinate-status`
  - `make decaffeinate-status`
  - `make decaffeinate`
- Env sanity: `make doctor-env`
- Backend tests: `make test`
- Local API: `make server` or `make server-daemon`
- Docs lint: `make lint-docs`
- Wiring spec: `docs/runtime/RUNBOOK.md`
- OCR lane reference: `docs/runtime/OCR_REFERENCE.md`
- Runtime DB lifecycle commands are retired during wiring lock.
- Local eval trace backfill (optional): `make backfill-eval-traces`
