# Polinko Charter

## Mission

Build a reliable, local-first human-AI collaboration system for alignment research, with production-grade runtime tooling across OCR, evals, and evidence chains.

## Product Behaviour Rules

- Prompt authority is `core/prompts.py` (`ACTIVE_PROMPT` / `ACTIVE_PROMPT_VERSION`).
- Style intent:
  - Conversational, laid back, witty, resonant, creative
  - Concise but insightful
  - UK English
  - No follow-up questions
  - No human emotions/traits language

## Engineering Principles

- Keep behaviour stable before adding UI complexity.
- Preserve prompt continuity through minimal, explicit prompt instructions.
- Fail fast on config/auth issues.
- Prefer deterministic, testable backend changes.
- Keep release gates binary (`PASS`/`FAIL`) and keep nuanced interpretation in diagnostic artifacts.
- Treat human judgment and AI execution as a joint workflow: explicit constraints first, implementation second, validation always.
- Run `make doctor-env` when local environment behavior looks suspicious.
- Run `make quality-gate` before push when backend/prompt/retrieval logic changes.

## Core Runtime

- CLI runner: `app.py`
- API entrypoint: `server.py` (FastAPI)
- API implementation: `api/app_factory.py`
- Prompt versions: `core/prompts.py`
- API tests: `tests/test_api.py`
- Primary workflow tool: Codex
- Primary model/runtime provider: OpenAI API

## Security / Ops Baseline

- `OPENAI_API_KEY` required at startup.
- `.env` supports `KEY=value` and quoted `KEY="value"` formats.
- Optional backend API key auth via `POLINKO_SERVER_API_KEY` or
  `POLINKO_SERVER_API_KEYS_JSON`.
- `/chat` rate limited (`POLINKO_RATE_LIMIT_PER_MINUTE`) with `Retry-After` header on 429.
- Structured JSON logs with request IDs in `server.py`.

## Scope (Current)

- In scope: local development, API hardening, test coverage.
- In scope: retrieval/OCR/file-search reliability, eval hardening, and evidence traceability.
- Paused: Figma-first UI parity while backend retrieval milestones are being finalized.
- Paused: cloud deployment automation (removed from repo for now; Azure is the preferred target when resumed).
