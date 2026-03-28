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
- `tools/`
  - Local automation/eval/reference utilities.
- `tests/`
  - API/runtime regression tests.
- `docs/`
  - Charter, state, decisions, runbook, handoff, operator references, and
    live archive lanes.

## Runtime Flow

1. `server.py` loads config from `config.py`.
2. `server.py` calls `api.app_factory.create_app(config)`.
3. `api/app_factory.py` wires routes + middleware + runtime dependencies.
4. Request execution delegates to `core/` runtime and persistence modules.
5. `POST /chat` supports harness override (`harness_mode=fixture`) for
   deterministic UI smoke without model calls; default remains `live`.
6. CLI/API surfaces are canonical; archived frontend context is tracked only in
   `docs/live_archive/legacy_frontend/`.

## Data Surfaces

- Runtime chat/session state:
  - SQLite stores (chat history + memory/vector artifacts).
  - Runtime DBs live under `.local/runtime_dbs/active/`; archives under
    `.local/runtime_dbs/archive/`.
- Eval runtime state (authoritative):
  - `.local/runtime_dbs/active/history.db` via `core/history_store.py`
    - `message_feedback` (binary `pass`/`fail` + tags/notes/status)
    - `eval_checkpoints` (`pass_count`, `fail_count`, `non_binary_count`)
  - active gate logic is binary-only (`pass`/`fail`); `non_binary_count` is an
    integrity signal only.
  - checkpoint API responses include explicit fail-closed `gate_outcome`
    (`pass`/`fail`) derived from counts.
  - canonical policy/reward semantics and conceptual ER model:
    `docs/EVAL_POLICY_MODEL.md`
  - canonical gate wiring contract and phase policy:
    `docs/EVAL_WIRING_SPEC.md`
  - canonical UI integration contract:
    `docs/UI_EVAL_ADAPTER_CONTRACT.md`
- Eval artefacts (non-authoritative):
  - Git history is the canonical retention mechanism for tracked project state.
  - local eval artefacts are operational outputs (default under `eval_reports/`)
    and are non-authoritative for runtime gate decisions.
  - no file-log-driven eval wiring exists in runtime gate decisions.
  - deprecated eval/frontend context is reference-only under `docs/live_archive/`
    and cannot drive active gate decisions.
- Reference visualisation:
  - markdown-native relationship graph generated from docs links.
  - builder: `tools/build_reference_graph.py`
  - operator flow: `make reference-graph` -> `docs/REFERENCE_GRAPH.md`.
- Eval relationship visualisation:
  - markdown-native relationship report generated from runtime history DB.
  - builder: `tools/build_eval_relationship_graph.py`
  - operator flow: `make eval-viz` ->
    `.local/visuals/eval_relationship_graph.md` (local-only output).

## Placement Rules

- API endpoints/middleware/contracts: `api/`
- Prompt/runtime behaviour and policy logic: `core/`
- Eval/report/reference scripts and one-off operators: `tools/`
- Execution state/decisions/handoff documentation: `docs/`
- Deprecated implementation references: `docs/live_archive/`

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
- Wiring visual contract: `docs/EVAL_WIRING_SPEC.md`
- Runtime DB lifecycle commands are retired during wiring lock
  (see `docs/RUNBOOK.md`).
- Local eval trace backfill (optional): `make backfill-eval-traces`
- Docs relationship graph: `make reference-graph`
- Eval relationship graph: `make eval-viz`
