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

- Keep behaviour stable and backend-first; legacy runtime web UI is archived
  from active operations.
- Portfolio shell routes are allowed as presentation-only surfaces:
  - `GET /` redirects to `GET /portfolio`
  - `GET /portfolio` serves low-fi IA/content shell only
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
  - recurring growth execution is batch-first; sync is reserved for interactive probes
- Rate and budget controls are tracked separately:
  - throughput limits (`RPM`/`TPM`/queue)
  - spend/credits (usage + billing)
- Run `make doctor-env` when local environment behaviour looks suspicious.
- Run `make quality-gate` before push when backend/prompt/retrieval logic changes.
- Streamline-first operator rule: keep one canonical make target per workflow action
  and remove superseded aliases in the same change.

## Workflow

- Inspect before optimise when system intent or provenance is unclear.
- Inspect-first is mandatory when concrete evidence is provided:
  - if a source/path/image/log is named, inspect it before interpretation
  - do not substitute summary/inference for direct inspection
  - if not yet inspected, state that explicitly and pause claims
  - inference-before-inspection is a fail event in this workflow
- `docs/runtime/RUNBOOK.md` (`Inspect-First Rule (Directed Mode)`) is the
  execution-level authority for this contract.
- Human-directed precision takes priority over agent-side summarisation/cleanup.
- Keep deprecated eval/runtime context in `docs/eval/beta_1_0/`; keep active docs
  and runtime specs binary-only.
- Never delete local files as a first action:
  - archive first
  - delete only when explicitly approved as a final cleanup step
- Beta tracking policy:
  - track beta eval docs/assets in `docs/eval/beta_1_0/` and
    `docs/eval/beta_2_0/` for transition traceability
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
  - use shell-safe PR body workflow:
    - never pass multiline Markdown directly in `gh pr create --body "..."`
    - use `--body-file <path>` (preferred) or a quoted heredoc
    - avoid inline backticks in shell-quoted body strings
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
- Historical eval transition evidence is maintained under
  `docs/eval/beta_1_0/`.

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
- In scope: portfolio presentation shell work (IA/low-fi first) as a
  non-runtime surface.
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
  - build the integrated manual/eval data surface from `manual_evals.db`
    (`make manual-evals-db`)
  - treat current and Beta 1.0 history DBs as import sources only; the
    app-facing eval surface should be one canonical derived DB with era/source
    provenance
  - expose read-only API endpoints for summary + runs + thumbnails + session
    feedback/checkpoint context
  - keep UI work presentation-only against that API contract
  - defer UI styling/interaction iterations until backend kernels are stable
- Portfolio governance pin:
  - keep portfolio strategy and role-targeting canon in Notion
    (single-source planning surface).
  - lock case-study presentation architecture to:
    - primary: `Failure Museum`
    - secondary: `Before/After Engine`
    - secondary: `Operator's Console` (live status layer, placed last)
  - embed `Claim Stress Test` inside each case card (not as a standalone section)
  - keep case-study scope binary-eval-centered; `Reasoning Loops` remains
    background context for this package
  - run portfolio work in consolidation mode:
    - reuse existing transcript/decision/eval evidence
    - remove duplicate/drift surfaces
    - avoid restart-from-scratch narrative rewrites
  - treat beta 1.0 as the binary-transition evidence layer, not irrelevant
    archive; beta 2.0/current eval evidence is meaningful by contrast against
    the beta 1.0 transition decisions.
  - keep Beta 1.0 and Beta 2.0 equally prominent in evidence mapping across
    documents, databases, evals, and logic.
