<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-03

## Current Snapshot

- Runtime: FastAPI backend + Vite UI + CLI runner.
- Prompt behavior stays minimal and aligned to legacy `try.py` style.
- Optional Responses orchestration path is available behind env flags.
- Governance and hallucination guardrails are now available behind env flags.
- Per-scope retrieval tuning is implemented and validated in API flow.
- Collaboration v1 is live with explicit role handoff endpoints + per-chat handoff timeline.
- Personalization v1 is live: per-chat retrieval memory scope (`session` or `global`).
- Personalization scope is now controllable from the web UI header (per active chat).
- `/chat` now returns `memory_used` retrieval citations when vector context is applied.
- OCR is feature-flagged:
  - `POLINKO_OCR_PROVIDER=scaffold` (default fallback)
  - `POLINKO_OCR_PROVIDER=openai` (real image OCR path)
- API now includes `/metrics` and chat export with OCR runs.
- Session/resource cleanup improved by explicitly closing per-request SQLite sessions.
- Runtime session cleanup hardened with a managed SQLite session wrapper that closes
  cross-thread connections on `close()`.
- Retrieval evaluator is now available (`make eval-retrieval`) and currently passes all 12 cases.
- OCR/PDF structured extraction now fail-open on malformed/unexpected enrichment errors.
- File-search API now returns backend/fallback classification (`backend`,
  `fallback_reason`, `candidate_count`) for deterministic client-side diagnostics.
- Hallucination eval harness now enforces session-local memory scope per case to reduce nondeterministic cross-case leakage.
- Single-command quality gate is available and passing: `make quality-gate`.
- Hallucination judge path now supports configurable key env + base URL for
  OpenAI-compatible judge providers (including Braintrust gateway wiring).
- Dedicated strict hallucination gate target is available: `make hallucination-gate`.
- CI includes optional Braintrust hallucination gate wiring when
  `BRAINTRUST_OPENAI_BASE_URL` (repo var) and `BRAINTRUST_API_KEY`
  (repo secret) are configured.
- Docker smoke path is validated (`make docker-build` + `make docker-run` + `/health`).
- Environment doctor is available for local sanity checks: `make doctor-env`.

## Latest Local Commit

- `de77f75` on `main` (synced with `origin/main`)
- Summary: chore: stabilize env/docker workflow and harden retrieval tests

## Key Files To Read First

- `docs/CHARTER.md`
- `docs/STATE.md`
- `docs/DECISIONS.md`
- `api/app_factory.py`
- `config.py`
- `tests/test_api.py`

## Quick Validation (Local)

1. `make quality-gate`
2. `make quality-gate-deterministic` (if judge key is unavailable)
3. `make hallucination-gate HALLUCINATION_EVAL_MODE=deterministic`
4. `make doctor-env`
5. `cd frontend && npm run build`
6. `make server` and spot-check `/health`, `/chat`, `/skills/ocr`

## Known Constraint

- No open high-priority runtime constraints currently tracked.

## Immediate Next Step

- Calibrate and enable the Braintrust hallucination judge gate in CI
  (threshold confirmation + repo vars/secrets), then begin:
  - P2: CLIP multimodal retrieval A/B experiment

## Copy/Paste Rehydrate Prompt

`Read docs/CHARTER.md, docs/STATE.md, docs/DECISIONS.md, and docs/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behavior drift and full test/build validation.`
