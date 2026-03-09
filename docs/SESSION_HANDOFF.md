<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-07

## Current Snapshot

- Runtime: FastAPI backend + Vite UI + CLI runner.
- Prompt behavior stays minimal and aligned to legacy `try.py` style.
- Optional Responses orchestration path is available behind env flags.
- Governance and hallucination guardrails are now available behind env flags.
- Emotional-distress guardrails are active in `/chat` composition with
  supportive boundary guidance and high-risk escalation language.
- Recursive rumination + interpersonal attribution guardrails are active for
  repeated personal "why" loops, stereotype prompts, and divination-certainty framing.
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
- Hallucination score threshold is now configurable with
  `HALLUCINATION_MIN_ACCEPTABLE_SCORE`; calibration helper is available via
  `make calibrate-hallucination-threshold`.
- P2 CLIP experiment scaffolding has started with `make eval-clip-ab` and
  report artifact mode `make eval-clip-ab-report`.
- Dedicated strict hallucination gate target is available: `make hallucination-gate`.
- CI includes optional Braintrust hallucination gate wiring when
  `BRAINTRUST_OPENAI_BASE_URL` (repo var) and `BRAINTRUST_API_KEY`
  (repo secret) are configured.
- Docker smoke path is validated (`make docker-build` + `make docker-run` + `/health`).
- Devcontainer Docker connectivity is now stabilized (Docker-outside-of-Docker
  and Docker extension UI-side routing), resolving `Containers` pane connection
  mismatch in remote sessions.
- Host-side VS Code interpreter warnings were resolved by removing stale
  workspace interpreter pins to Linux container venv binaries; host sessions
  now rely on host interpreter auto-discovery/selection.
- Environment doctor is available for local sanity checks: `make doctor-env`.
- Evidence indexing now records FAIL lifecycle state (`action_taken`, `status`)
  and supports optional triage overrides until a linked PASS closes the issue.
- Portfolio metadata audit is now available via
  `make portfolio-metadata-audit` for strict evidence/docs metadata checks.
- Adaptive style-note handling now uses decay-weighted signal, near-duplicate
  note suppression, and a max of two active notes with
  `adaptive_style_notes_updated` event logging to avoid model-input
  over-indexing from repeated guidance.
- Exploratory low-context style-patterning traces were captured (symbolic
  emoticon exchanges) and surfaced a useful eval-design signal: verbosity
  compression under minimal prompts, motif lock-in (for example star/diamond
  endings), reward over-indexing after positive preference cues, and occasional
  repetition collapse after malformed-emoticon/render events.
- Frontend Playwright smoke E2E includes retry-variant lineage coverage
  (`source_user_message_id` flow), including variant navigation and duplicate
  user-row prevention assertions.
- Style-pattern micro-eval harness is implemented for low-context scripted
  turn sequences (`make eval-style-pattern`), with report mode
  (`make eval-style-pattern-report`) and metrics for verbosity, uniqueness,
  repeat collapse, filler hits, and motif lock-in.
- Branch rules now enforce PR + required checks (`test`, `markdownlint`) on
  default branch (`main`) while allowing normal push/PR workflow on feature
  branches.
- `docs/FIGMA_NODE_TRACKER.md` is now intentionally local-only and gitignored
  for proprietary/live node-tracking use.

## Latest Local Commit

- `4f08304` on `main` (local ahead of `origin/main` by local housekeeping/docs commits)
- Summary: chore: add figma tracker to gitignore

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
6. `make portfolio-metadata-audit`
7. `cd frontend && npx playwright test e2e/smoke.spec.js`
8. `make server` and spot-check `/health`, `/chat`, `/skills/ocr`

## Known Constraint

- No open high-priority runtime constraints currently tracked.

## Immediate Next Step

- Calibrate and enable the Braintrust hallucination judge gate in CI
  (threshold confirmation + repo vars/secrets), then begin:
  - P2: CLIP multimodal retrieval A/B experiment
  - style micro-eval: low-context anti-filler + motif-diversity regression
    checks from exploratory trace

## Copy/Paste Rehydrate Prompt

`Read docs/CHARTER.md, docs/STATE.md, docs/DECISIONS.md, and docs/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, and confirm active git branch. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behavior drift and full test/build validation.`
