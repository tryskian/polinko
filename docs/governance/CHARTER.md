# Polinko Charter

## Mission

Build a reliable GPT-powered assistant with stable tone, persistent memory,
OCR-forward reliability loops, and production-ready API foundations.

## Product Behaviour Rules

- Prompt authority is `core/prompts.py` (`ACTIVE_PROMPT` / `ACTIVE_PROMPT_VERSION`).
- Style intent:
  - Conversational, laid back, witty, resonant, creative
  - Concise but insightful
  - UK English
  - No follow-up questions
  - No human emotions/traits language

## Engineering Principles

- Keep behaviour stable and backend-first; web UI is archived from active operations.
- Eval direction/orchestration is owned by the core backend lane; UI work is
  presentation-only and must not redefine eval policy.
- Preserve prompt continuity through minimal, explicit prompt instructions.
- Fail fast on config/auth issues.
- Prefer deterministic, testable backend changes.
- Keep eval gate semantics strictly binary (`pass`/`fail`) across API, CLI, and
  tooling.
- Keep operator notes out of gate logic:
  - notes are for human review/refinement workflow
  - notes must not mutate runtime config/prompt wiring by default
  - behavioural changes come through explicit eval-process updates, validated in
    the normal quality gates
- Keep OCR as the primary reliability lane:
  - lockset lane is release-gating and must remain green
  - growth lane is fail-tolerant and used to measure pass-from-fail movement
- Run `make doctor-env` when local environment behaviour looks suspicious.
- Run `make quality-gate` before push when backend/prompt/retrieval logic changes.
- Streamline-first operator rule: keep one canonical make target per workflow action
  and remove superseded aliases in the same change.

## Workflow

- Inspect before optimise when system intent or provenance is unclear.
- Human-directed precision takes priority over agent-side summarisation/cleanup.
- Keep deprecated workflow context in `.archive/live_archive/`; keep active docs and
  runtime specs binary-only.
- Never delete local files as a first action:
  - archive first
  - delete only when explicitly approved as a final cleanup step
- Beta tracking policy:
  - track legacy eval docs/assets in `docs/eval/legacy/` for transition
    traceability
  - keep raw DB snapshots and confidential internals local-only unless
    explicitly approved for tracking
- During eval wiring lock, avoid DB init/refresh flows; allow only archive/reset
  maintenance commands until spec sign-off
  (`docs/runtime/RUNBOOK.md` is canonical in this phase).
- Keep benchmarking product-supportive:
  - hypothesis benchmarking informs build decisions but does not replace product delivery
  - use one canonical benchmark spec to control sequencing and confounders
  - keep benchmark/case-study framing stack-scoped (baseline/advanced/binary),
    not model-name scoped
- Engineer owns proactive technical hygiene:
  - identify drift/gremlin-risk paths early
  - execute cleanup/validation/doc alignment without waiting for reminders
  - escalate only when trade-offs or approvals are genuinely required
  - execute user requests directly by default
- Automation lane policy:
  - default mode is `paused` (single manual lane).
  - re-enable only with explicit human go/no-go.
- Collaboration model is `Reasoning Loops`:
  - imagineer leads hypotheses/theory framing, visual culture shape, and eval
    operations
  - imagineer + engineer own eval process notes as a human co-reasoning layer
  - imagineer is not expected to run terminal commands or Git operations
  - engineer leads implementation, tooling/process decisions, validation, and
    execution recommendations
  - engineer executes commands, validations, and branch/PR/merge flow end-to-end
  - auxiliary UI lanes may implement surfaces, but eval policy authority remains
    with the core engineer/imagineer loop
- Human work-management authority is required in co-reasoning:
  - human sets objective, scope boundaries, and acceptance criteria
  - human resolves ambiguous meaning-level trade-offs where no deterministic
    rule exists
  - human controls go/no-go and next-slice prioritisation
  - engineer executes proactively inside that control frame

## Core Runtime

- CLI runner: `app.py`
- API entrypoint: `server.py` (FastAPI)
- API implementation: `api/app_factory.py`
- Prompt versions: `core/prompts.py`
- API tests: `tests/test_api.py`
- Archived web UI context is documented under
  `.archive/live_archive/legacy_frontend/`.

## Security / Ops Baseline

- `OPENAI_API_KEY` required at startup.
- `.env` supports `KEY=value` and quoted `KEY="value"` formats.
- Backend endpoints do not require `x-api-key`; localhost runtime is the
  trusted development boundary.
- `/chat` rate limited (`POLINKO_RATE_LIMIT_PER_MINUTE`) with `Retry-After` header on 429.
- Structured JSON logs with request IDs in `server.py`.

## Scope (Current)

- In scope: local development, API hardening, test coverage.
- In scope: retrieval/OCR/file-search reliability and eval hardening.
- In scope: OCR-forward eval operations (`lockset` + `growth`) with
  transcript-backed case mining and stability replay.
- In scope: local notebook visual analysis for OCR evals (`make notes`).
- Archived: web UI as an active execution surface; retained only in
  live-archive references.
- Paused: cloud deployment automation (removed from repo for now; Azure is the preferred target when resumed).
- Include later (deferred cookbook track):
  - see `docs/runtime/RUNBOOK.md` (`Cookbook Queue`)
- Cookbook priority pin (next integration kernel):
  - `Vision Fine-tuning on GPT-4o for Visual Question Answering` is first in
    the cookbook integration sequence.
- Runtime progress pin (next engineering kernel):
  - build a manual-eval data surface from `manual_evals.db`
  - expose read-only API endpoints for summary + runs + thumbnails + session
    feedback/checkpoint context
  - keep UI work presentation-only against that API contract
