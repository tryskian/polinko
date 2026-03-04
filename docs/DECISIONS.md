# Decisions Log

## D-001: Functionality before UI

- Decision: Build and stabilise prompt + memory + API first, then add UI.
- Why: Reduces rework and makes behaviour easier to validate.

## D-002: Prompt versioning

- Decision: Move prompt text into `core/prompts.py` with explicit `ACTIVE_PROMPT_VERSION`.
- Why: Prevent silent prompt drift and enable controlled changes.

## D-003: Regression checks

- Decision: Removed regression-eval scaffolding from runtime repo.
- Why: Product direction favours minimal prompt + direct behaviour testing in live flows.

## D-004: Persistent local memory

- Decision: Use `SQLiteSession` for CLI/API sessions.
- Why: Keeps multi-turn continuity across restarts.

## D-005: API hardening baseline

- Decision: Add startup key validation, structured logging, API key auth (optional), and rate limiting.
- Why: Improve operational safety before deployment.

## D-006: Deployment strategy pause

- Decision: Remove AWS deployment automation from repo for now.
- Why: AWS auth/identity setup caused friction; continue product progress locally first.

## D-007: Folder-first architecture

- Decision: Keep root thin (`app.py`, `config.py`, `server.py`) and place implementation in folders (`api/`, `core/`, `tools/`, `configs/`, `docs/`).
- Why: Improves navigation and supports cleaner scaling without root-level sprawl.

## D-008: CI + lock + runbook baseline

- Decision: Add GitHub Actions CI (`test`), `requirements.lock`, and `docs/RUNBOOK.md`.
- Why: Improve release safety, reproducibility, and operational troubleshooting.

## D-009: Data leverage and light retrieval

- Decision: Removed retrieval/fact-builder layer from the active runtime path.
- Why: Direct user-input flow was more stable and aligned better with desired behaviour.

## D-010: Auth principal ring + limiter bucket hygiene

- Decision: Support optional API key ring principals via `POLINKO_SERVER_API_KEYS_JSON` while keeping `POLINKO_SERVER_API_KEY` backward compatible; add periodic stale-bucket cleanup to the in-memory sliding window limiter.
- Why: Improve multi-user readiness and long-running process stability without introducing heavy identity infrastructure.

## D-011: Built-in thin web UI

- Decision: Use Vite frontend (`frontend/`) calling FastAPI endpoints.
- Why: Better UX iteration speed without changing backend runtime logic.

## D-012: Lightweight in-process API metrics

- Decision: Add `/metrics` endpoint backed by in-process counters for request totals, status counts, latency buckets, and rate-limit totals.
- Why: Improve deployment-readiness observability without introducing external infra.

## D-013: OCR provider behind feature flag

- Decision: Keep OCR scaffold mode as default and add optional `openai` provider mode via `POLINKO_OCR_PROVIDER`.
- Why: Preserve stable behaviour while enabling incremental rollout of real OCR.

## D-014: Responses orchestration as optional pipeline

- Decision: Add Responses API orchestration behind `POLINKO_RESPONSES_ORCHESTRATION_ENABLED` while keeping Runner as default.
- Why: Enable tool-driven RAG experimentation without destabilizing baseline chat behaviour.

## D-015: Governance and hallucination guardrails

- Decision: Add lightweight governance controls and factual-query hallucination guardrails with env flags.
- Why: Reduce risk of unsupported factual certainty and enforce tool policy boundaries during orchestration rollout.

## D-016: Multi-agent portfolio collaboration v1

- Decision: Add server-side collaboration state with explicit role handoffs and audit timeline per chat.
- Why: Enable controlled multi-agent workflows (researcher/strategist/editor style roles) without prompt bloat or hidden mode drift.

## D-017: Per-chat personalization memory scope

- Decision: Add per-chat memory-scope control (`session` or `global`) plus a configurable default.
- Why: Preserve tuning flexibility while preventing unwanted cross-chat retrieval bleed during focused sessions.

## D-018: Expose personalization scope in web UI

- Decision: Add a per-chat memory-scope selector in the frontend header backed by personalization API endpoints.
- Why: Make retrieval tuning accessible during live sessions without manual API calls.

## D-019: Deterministic hallucination eval isolation

- Decision: Force hallucination-eval generated chats into `memory_scope=session` before each case run.
- Why: Prevent cross-case contamination from global memory retrieval and reduce evaluator flakiness.

## D-020: Single-command quality gate

- Decision: Add `make quality-gate` to run unit tests + retrieval eval + strict hallucination eval against a temporary local API server.
- Why: Standardize pre-push validation and catch regressions early with one deterministic command.

## D-021: Per-scope retrieval tuning + type-safe payload hints

- Decision: Refine retrieval behavior by memory scope and tighten API payload typing hints where dynamic dict/list payloads are used.
- Why: Improve retrieval consistency and reduce editor/type-check noise without changing user-facing behavior.

## D-022: Managed SQLite session cleanup for cross-thread handles

- Decision: Wrap upstream `SQLiteSession` with a managed session that tracks and closes all created sqlite connections on `close()`.
- Why: Upstream session cleanup only closes current-thread locals; this left worker-thread handles open and triggered strict `ResourceWarning` noise during tests.

## D-023: File search backend/fallback classification in API responses

- Decision: Extend `POST /skills/file_search` response with explicit `backend`,
  `fallback_reason`, and `candidate_count` fields.
- Why: Makes retrieval-path behavior observable to clients and tests without
  relying only on server logs, improving debugging and deterministic contract
  validation.

## D-024: Normalize quoted env values for runtime config parsing

- Decision: Normalize wrapped quotes from env values (for example
  `"OPENAI_API_KEY=\"sk-...\""` style inputs) before config validation/parsing.
- Why: Docker `--env-file` passes quoted values literally; without normalization
  valid `.env` configurations could fail at startup in container runs.

## D-025: Parameterized hallucination judge endpoint + optional Braintrust CI gate scaffold

- Decision: Extend hallucination eval judge config with `--judge-api-key-env`
  and `--judge-base-url`, add `make hallucination-gate`, and wire an optional
  CI step that runs strict hallucination gating against an OpenAI-compatible
  Braintrust endpoint when repo vars/secrets are present.
- Why: Enables P1 judge-gate rollout without changing runtime assistant
  behavior and avoids hard-coding a single judge provider path.

## D-026: Host/container interpreter separation for VS Code Python resolution

- Decision: Keep host-side Python interpreter selection unpinned from
  container-built venv binaries and rely on host auto-discovery (or explicit
  host interpreter) outside the devcontainer.
- Why: Prevent recurring `Could not resolve interpreter path` failures caused by
  macOS attempting to execute Linux ELF venv binaries created in container
  workflows.

## D-027: Evidence triage tracks action-taken state until passing evidence exists

- Decision: Extend evidence indexing to track `recommended_action`,
  `action_taken`, and `status` for FAIL records, with optional triage override
  input and auto-closure when a later PASS artifact exists for the same chat.
- Why: Preserve remediation traceability and avoid losing unresolved FAIL
  context between eval cycles.

## D-028: Portfolio metadata audit as a strict gate

- Decision: Add a dedicated metadata audit command (`make portfolio-metadata-audit`)
  that validates evidence index completeness and evidence-log field coverage.
- Why: Ensures portfolio claims remain traceable to complete, machine-readable
  metadata before publication.

## D-029: Configurable hallucination gate threshold + calibration helper

- Decision: Make hallucination gate score threshold configurable via
  `HALLUCINATION_MIN_ACCEPTABLE_SCORE` and add a report-based calibration helper
  (`make calibrate-hallucination-threshold`).
- Why: Supports explicit Braintrust threshold tuning in CI while preserving
  default behavior when calibration vars are not yet set.
