# Architecture

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
  - Local automation/eval/reference utilities.
- `tests/`
  - API/runtime regression tests.
- `docs/`
  - Charter, state, decisions, runbook, handoff, operator references, and
    eval lane references.

## Runtime Flow

1. `server.py` loads config from `config.py`.
2. `server.py` calls `api.app_factory.create_app(config)`.
3. `api/app_factory.py` wires routes + middleware + runtime dependencies.
4. Request execution delegates to `core/` runtime and persistence modules.
5. `POST /chat` supports harness override (`harness_mode=fixture`) for
   deterministic smoke without model calls; default remains `live`.
6. CLI/API surfaces remain canonical; beta transition evidence is maintained
   under `docs/eval/` and mapped in `docs/eval/README.md`.
7. OCR-forward quality loop is the active reliability engine:
   - transcript case miner builds local OCR case sets
   - lockset lane gates release quality (strict binary pass/fail)
   - growth lane captures fail-heavy novel cases for pass-from-fail tracking

## Data Surfaces

- Runtime chat/session state:
  - SQLite stores (chat history + memory/vector artifacts).
  - Runtime DBs live under `.local/runtime_dbs/active/`; archives under
    `.local/runtime_dbs/archive/`.
- Eval runtime state (raw source):
  - `.local/runtime_dbs/active/history.db` via `core/history_store.py`
    - `message_feedback` (binary `pass`/`fail` + tags/notes/status)
    - `eval_checkpoints` (`pass_count`, `fail_count`, `non_binary_count`)
    - `ocr_runs` raw OCR history used by the live pulse chart timeline
  - active gate logic is binary-only (`pass`/`fail`); `non_binary_count` is an
    integrity signal only.
  - checkpoint API responses include explicit fail-closed `gate_outcome`
    (`pass`/`fail`) derived from counts.
  - canonical policy/gate/ui specs are maintained in `docs/runtime/RUNBOOK.md`.
- Canonical eval warehouse:
  - `.local/runtime_dbs/active/manual_evals.db`
    - rebuilt by `make manual-evals-db`
    - imports current `history.db` plus optional Beta 1.0 history from
      `.local/legacy_eval/archive_legacy_eval/databases/.polinko_history.db`
    - stores integrated rows with explicit `era`, source DB, source session,
      and source run provenance
  - this is the single app-facing eval database for analysis/UI work; raw
    history files are import sources, not separate eval truths.
- Eval visualization surfaces (hybrid):
  - `.local/runtime_dbs/active/manual_evals.db`
    - recent integrated OCR rows feed the bucketed `text` / `handwriting` /
      `illustration` chart in `/viz/pass-fail`
    - feedback/status context feeds the headline summary and latest detail rows
    - Beta 1.0/current provenance remains visible through `era` and source
      columns
  - design intent:
    - local-only, visual-forward, near-real-time surface
    - insight-first summary rather than dense dashboard analysis
- Eval artefacts (non-authoritative):
  - Git history is the canonical retention mechanism for tracked project state.
  - local eval artefacts are operational outputs (default under `eval_reports/`)
    and are non-authoritative for runtime gate decisions.
  - no file-log-driven eval wiring exists in runtime gate decisions.
  - beta transition evidence is reference-only for active runtime gates:
    - `docs/eval/beta_1_0/` records binary-transition evidence
    - `docs/eval/beta_2_0/` records binary-operational evidence
    - neither path can drive active gate decisions directly
- OCR eval lanes (active):
  - lockset gate: stable benchmark subset that must stay green
  - growth lane: exploratory/novel subset where failures are expected signal
  - local case/report surfaces (untracked):
    - `.local/eval_cases/`
      - includes widened growth set:
        `.local/eval_cases/ocr_transcript_cases_growth.json`
      - includes growth fail cohort:
        `.local/eval_cases/ocr_growth_fail_cohort.json`
    - `.local/eval_reports/`
      - includes growth stability:
        `.local/eval_reports/ocr_growth_stability.json`
    - growth metrics:
      - `.local/eval_reports/ocr_growth_metrics.json`
      - `.local/eval_reports/ocr_growth_metrics.md`
    - growth fail cohort report:
      - `.local/eval_reports/ocr_growth_fail_cohort.md`
  - local notebook exploration:
    - `output/jupyter-notebook/ocr-eval-live-filters-starter.ipynb`

## Placement Rules

- API endpoints/middleware/specs: `api/`
- Prompt/runtime behaviour and policy logic: `core/`
- Eval/report/reference scripts and one-off operators: `tools/`
- Execution state/decisions/handoff documentation: `docs/`
- Historical beta transition references: `docs/eval/README.md`

## Governance Flow

- Collaboration/execution policy is anchored in `docs/governance/CHARTER.md`.
- Co-reasoning control rights are human-led for objective/scope/acceptance and
  go/no-go decisions.
- Formal decision records are appended in `docs/governance/DECISIONS.md`.
- Operator procedure lives in `docs/runtime/RUNBOOK.md`.
- Current-state checkpoints live in `docs/governance/STATE.md`.
- Next-session carryover constraints live in `docs/governance/SESSION_HANDOFF.md`.
- Policy updates are complete only when all relevant surfaces above are aligned.

## Operational Commands

- Env sanity: `make doctor-env`
- Backend tests: `make test`
- Local API: `make server` or `make server-daemon`
- Wiring spec: `docs/runtime/RUNBOOK.md`
- Runtime DB lifecycle commands are retired during wiring lock
  (see `docs/runtime/RUNBOOK.md`).
- Local eval trace backfill (optional): `make backfill-eval-traces`
- Growth-lane metrics report: `make ocrgrowth`
- Growth-lane fail cohort materialisation: `make ocrfails`
  - selection is constrained to growth-lane cases that map to OCR-framed
    transcript review episodes (`ocr_framing_signal=true`)
