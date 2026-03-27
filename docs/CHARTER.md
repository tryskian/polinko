# Polinko Charter

## Mission

Build a reliable GPT-powered assistant with stable tone, persistent memory, and production-ready API foundations.

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
- Preserve prompt continuity through minimal, explicit prompt instructions.
- Fail fast on config/auth issues.
- Prefer deterministic, testable backend changes.
- Keep eval gate semantics strictly binary (`pass`/`fail`) across API, CLI, and
  tooling.
- Run `make doctor-env` when local environment behaviour looks suspicious.
- Run `make quality-gate` before push when backend/prompt/retrieval logic changes.

## Workflow

- Inspect before optimise when system intent or provenance is unclear.
- Human-directed precision takes priority over agent-side summarisation/cleanup.
- Keep deprecated workflow context in `docs/live_archive/`; keep active docs and
  runtime contracts binary-only.
- During eval wiring lock, avoid DB init/refresh flows; allow only archive/reset
  maintenance commands until contract sign-off
  (`docs/EVAL_WIRING_SPEC.md` is canonical in this phase).
- Keep benchmarking product-supportive:
  - hypothesis benchmarking informs build decisions but does not replace product delivery
  - use one canonical benchmark spec to control sequencing and confounders
- Engineer owns proactive technical hygiene:
  - identify drift/gremlin-risk paths early
  - execute cleanup/validation/doc alignment without waiting for reminders
  - escalate only when trade-offs or approvals are genuinely required
- Collaboration model is `Reasoning Loops`:
  - imagineer leads hypotheses/theory framing, visual culture shape, and eval
    operations
  - engineer leads implementation, tooling/process decisions, validation, and
    execution recommendations
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
  `docs/live_archive/legacy_frontend/`.

## Security / Ops Baseline

- `OPENAI_API_KEY` required at startup.
- `.env` supports `KEY=value` and quoted `KEY="value"` formats.
- Optional backend API key auth via `POLINKO_SERVER_API_KEY` or
  `POLINKO_SERVER_API_KEYS_JSON`.
- `/chat` rate limited (`POLINKO_RATE_LIMIT_PER_MINUTE`) with `Retry-After` header on 429.
- Structured JSON logs with request IDs in `server.py`.

## Scope (Current)

- In scope: local development, API hardening, test coverage.
- In scope: retrieval/OCR/file-search reliability and eval hardening.
- Archived: web UI as an active execution surface; retained only in
  live-archive references.
- Paused: cloud deployment automation (removed from repo for now; Azure is the preferred target when resumed).
