# Decisions Log

## Taxonomy

- `Category` values:
  - `runtime_engineering`
  - `eval_quality`
  - `collaboration_method`
  - `evidence_governance`
  - `workflow_environment`
  - `research_experiment`
- `Tags`: lowercase snake_case labels for quick filtering.

## Entry Style

- Keep entries short and operational:
  - `Category`: exactly one taxonomy value.
  - `Tags`: 3-5 concise labels.
  - `Decision`: one sentence with the key change.
  - `Why`: one sentence with the primary rationale.

## D-001: Functionality before UI

- Category: `runtime_engineering`
- Tags: `build_order`, `backend_first`, `stability`
- Decision: Build and stabilise prompt + memory + API first, then add UI.
- Why: Reduces rework and makes behaviour easier to validate.

## D-002: Prompt versioning

- Category: `runtime_engineering`
- Tags: `prompt_versioning`, `change_control`, `drift_prevention`
- Decision: Move prompt text into `core/prompts.py` with explicit `ACTIVE_PROMPT_VERSION`.
- Why: Prevent silent prompt drift and enable controlled changes.

## D-003: Regression checks

- Category: `eval_quality`
- Tags: `regression_testing`, `runtime_scope`, `live_flow_validation`
- Decision: Removed regression-eval scaffolding from runtime repo.
- Why: Product direction favours minimal prompt + direct behaviour testing in live flows.

## D-004: Persistent local memory

- Category: `runtime_engineering`
- Tags: `sqlite_session`, `persistence`, `continuity`
- Decision: Use `SQLiteSession` for CLI/API sessions.
- Why: Keeps multi-turn continuity across restarts.

## D-005: API hardening baseline

- Category: `runtime_engineering`
- Tags: `api_hardening`, `auth`, `rate_limit`, `logging`
- Decision: Add startup key validation, structured logging, API key auth (optional), and rate limiting.
- Why: Improve operational safety before deployment.

## D-006: Deployment strategy pause

- Category: `workflow_environment`
- Tags: `deployment`, `aws_pause`, `local_first`
- Decision: Remove AWS deployment automation from repo for now.
- Why: AWS auth/identity setup caused friction; continue product progress locally first.

## D-007: Folder-first architecture

- Category: `workflow_environment`
- Tags: `repo_structure`, `maintainability`, `scalability`
- Decision: Keep root thin (`app.py`, `config.py`, `server.py`) and place implementation in folders (`api/`, `core/`, `tools/`, `configs/`, `docs/`).
- Why: Improves navigation and supports cleaner scaling without root-level sprawl.

## D-008: CI + lock + runbook baseline

- Category: `workflow_environment`
- Tags: `ci`, `dependency_lock`, `runbook`, `reproducibility`
- Decision: Add GitHub Actions CI (`test`), `requirements.lock`, and `docs/RUNBOOK.md`.
- Why: Improve release safety, reproducibility, and operational troubleshooting.

## D-009: Data leverage and light retrieval

- Category: `runtime_engineering`
- Tags: `retrieval_simplification`, `direct_input_flow`, `stability`
- Decision: Removed retrieval/fact-builder layer from the active runtime path.
- Why: Direct user-input flow was more stable and aligned better with desired behaviour.

## D-010: Auth principal ring + limiter bucket hygiene

- Category: `runtime_engineering`
- Tags: `api_key_ring`, `rate_limiter`, `multi_user`, `bucket_cleanup`
- Decision: Support optional API key ring principals via `POLINKO_SERVER_API_KEYS_JSON` while keeping `POLINKO_SERVER_API_KEY` backward compatible; add periodic stale-bucket cleanup to the in-memory sliding window limiter.
- Why: Improve multi-user readiness and long-running process stability without introducing heavy identity infrastructure.

## D-011: Built-in thin web UI

- Category: `workflow_environment`
- Tags: `web_ui`, `vite`, `iteration_speed`
- Decision: Use Vite frontend (`frontend/`) calling FastAPI endpoints.
- Why: Better UX iteration speed without changing backend runtime logic.

## D-012: Lightweight in-process API metrics

- Category: `runtime_engineering`
- Tags: `observability`, `metrics`, `latency`, `in_process`
- Decision: Add `/metrics` endpoint backed by in-process counters for request totals, status counts, latency buckets, and rate-limit totals.
- Why: Improve deployment-readiness observability without introducing external infra.

## D-013: OCR provider behind feature flag

- Category: `runtime_engineering`
- Tags: `ocr_provider`, `feature_flag`, `incremental_rollout`
- Decision: Keep OCR scaffold mode as default and add optional `openai` provider mode via `POLINKO_OCR_PROVIDER`.
- Why: Preserve stable behaviour while enabling incremental rollout of real OCR.

## D-014: Responses orchestration as optional pipeline

- Category: `runtime_engineering`
- Tags: `responses_orchestration`, `pipeline_toggle`, `rag`
- Decision: Add Responses API orchestration behind `POLINKO_RESPONSES_ORCHESTRATION_ENABLED` while keeping Runner as default.
- Why: Enable tool-driven RAG experimentation without destabilizing baseline chat behaviour.

## D-015: Governance and hallucination guardrails

- Category: `runtime_engineering`
- Tags: `governance`, `hallucination_guardrails`, `safety_controls`
- Decision: Add lightweight governance controls with factual-query hallucination guardrails plus emotional, recursive-rumination, and interpersonal-attribution safety boundaries in chat input composition.
- Why: Reduce unsupported factual certainty, avoid dependency/loop amplification, and prevent stereotype or motive-certainty framing in sensitive interpersonal prompts.

## D-016: Multi-agent portfolio collaboration v1

- Category: `collaboration_method`
- Tags: `multi_agent`, `role_handoff`, `workflow_state`, `human_ai_collaboration`
- Decision: Add server-side collaboration state with explicit role handoffs and audit timeline per chat.
- Why: Enable controlled multi-agent workflows (researcher/strategist/editor style roles) without prompt bloat or hidden mode drift.

## D-017: Per-chat personalization memory scope

- Category: `collaboration_method`
- Tags: `personalization`, `memory_scope`, `focus_control`
- Decision: Add per-chat memory-scope control (`session` or `global`) plus a configurable default.
- Why: Preserve tuning flexibility while preventing unwanted cross-chat retrieval bleed during focused sessions.

## D-018: Expose personalization scope in web UI

- Category: `collaboration_method`
- Tags: `ui_control`, `memory_scope`, `live_tuning`
- Decision: Add a per-chat memory-scope selector in the frontend header backed by personalization API endpoints.
- Why: Make retrieval tuning accessible during live sessions without manual API calls.

## D-019: Deterministic hallucination eval isolation

- Category: `eval_quality`
- Tags: `hallucination_eval`, `determinism`, `session_isolation`
- Decision: Force hallucination-eval generated chats into `memory_scope=session` before each case run.
- Why: Prevent cross-case contamination from global memory retrieval and reduce evaluator flakiness.

## D-020: Single-command quality gate

- Category: `eval_quality`
- Tags: `quality_gate`, `pre_push`, `deterministic_validation`
- Decision: Add `make quality-gate` to run unit tests + retrieval eval + strict hallucination eval against a temporary local API server.
- Why: Standardize pre-push validation and catch regressions early with one deterministic command.

## D-021: Per-scope retrieval tuning + type-safe payload hints

- Category: `runtime_engineering`
- Tags: `retrieval_tuning`, `memory_scope`, `type_hints`
- Decision: Refine retrieval behavior by memory scope and tighten API payload typing hints where dynamic dict/list payloads are used.
- Why: Improve retrieval consistency and reduce editor/type-check noise without changing user-facing behavior.

## D-022: Managed SQLite session cleanup for cross-thread handles

- Category: `runtime_engineering`
- Tags: `sqlite_cleanup`, `thread_safety`, `resource_warning`
- Decision: Wrap upstream `SQLiteSession` with a managed session that tracks and closes all created sqlite connections on `close()`.
- Why: Upstream session cleanup only closes current-thread locals; this left worker-thread handles open and triggered strict `ResourceWarning` noise during tests.

## D-023: File search backend/fallback classification in API responses

- Category: `runtime_engineering`
- Tags: `file_search`, `api_contract`, `fallback_visibility`, `observability`
- Decision: Extend `POST /skills/file_search` response with explicit `backend`,
  `fallback_reason`, and `candidate_count` fields.
- Why: Makes retrieval-path behavior observable to clients and tests without
  relying only on server logs, improving debugging and deterministic contract
  validation.

## D-024: Normalize quoted env values for runtime config parsing

- Category: `workflow_environment`
- Tags: `env_parsing`, `docker_env_file`, `startup_reliability`
- Decision: Normalize wrapped quotes from env values (for example
  `"OPENAI_API_KEY=\"sk-...\""` style inputs) before config validation/parsing.
- Why: Docker `--env-file` passes quoted values literally; without normalization
  valid `.env` configurations could fail at startup in container runs.

## D-025: Parameterized hallucination judge endpoint + optional Braintrust CI gate scaffold

- Category: `eval_quality`
- Tags: `hallucination_gate`, `judge_endpoint`, `braintrust`, `ci_optional`
- Decision: Extend hallucination eval judge config with `--judge-api-key-env`
  and `--judge-base-url`, add `make hallucination-gate`, and wire an optional
  CI step that runs strict hallucination gating against an OpenAI-compatible
  Braintrust endpoint when repo vars/secrets are present.
- Why: Enables P1 judge-gate rollout without changing runtime assistant
  behavior and avoids hard-coding a single judge provider path.

## D-026: Host/container interpreter separation for VS Code Python resolution

- Category: `workflow_environment`
- Tags: `devcontainer`, `interpreter_resolution`, `host_container_split`
- Decision: Keep host-side Python interpreter selection unpinned from
  container-built venv binaries and rely on host auto-discovery (or explicit
  host interpreter) outside the devcontainer.
- Why: Prevent recurring `Could not resolve interpreter path` failures caused by
  macOS attempting to execute Linux ELF venv binaries created in container
  workflows.

## D-027: Evidence triage tracks action-taken state until passing evidence exists

- Category: `evidence_governance`
- Tags: `triage`, `remediation`, `fail_to_pass`, `traceability`
- Decision: Extend evidence indexing to track `recommended_action`,
  `action_taken`, and `status` for FAIL records, with optional triage override
  input and auto-closure when a later PASS artifact exists for the same chat.
- Why: Preserve remediation traceability and avoid losing unresolved FAIL
  context between eval cycles.

## D-028: Portfolio metadata audit as a strict gate

- Category: `evidence_governance`
- Tags: `metadata`, `audit`, `portfolio_readiness`, `strict_gate`
- Decision: Add a dedicated metadata audit command (`make portfolio-metadata-audit`)
  that validates evidence index completeness and evidence-log field coverage.
- Why: Ensures portfolio claims remain traceable to complete, machine-readable
  metadata before publication.

## D-029: Configurable hallucination gate threshold + calibration helper

- Category: `eval_quality`
- Tags: `threshold_tuning`, `calibration`, `hallucination_gate`
- Decision: Make hallucination gate score threshold configurable via
  `HALLUCINATION_MIN_ACCEPTABLE_SCORE` and add a report-based calibration helper
  (`make calibrate-hallucination-threshold`).
- Why: Supports explicit Braintrust threshold tuning in CI while preserving
  default behavior when calibration vars are not yet set.

## D-030: Start P2 multimodal retrieval A/B harness with CLIP-proxy arm

- Category: `research_experiment`
- Tags: `ab_test`, `multimodal`, `clip_proxy`, `retrieval`
- Decision: Add a non-runtime evaluation harness (`make eval-clip-ab`) that
  compares baseline mixed-source retrieval vs an image-prioritized proxy arm on
  image-context cases.
- Why: Establishes measurable A/B scaffolding now, so full CLIP embedding
  integration can be validated against a stable experiment contract later.

## D-031: Human-AI collaboration feedback pipeline beyond engineering evals

- Category: `collaboration_method`
- Tags: `pass_fail_feedback`, `reason_tags`, `alignment_signal`, `cross_domain`
- Decision: Treat per-response PASS/FAIL reason tagging as a first-class
  collaboration signal across all working modes (engineering, research, theory,
  and portfolio curation), not only CI/eval harnesses.
- Why: Captures unaided human alignment/reward signal directly from live
  interaction, enables deterministic remediation trails (`FAIL -> action ->
  PASS`), and reduces documentation friction by generating structured evidence
  metadata from normal usage.

## D-032: Azure-first target when cloud deployment resumes

- Category: `workflow_environment`
- Tags: `deployment_target`, `azure_first`, `cloud_pause`
- Decision: Keep cloud deployment automation paused for now, and treat Azure as
  the preferred first target when deployment work resumes.
- Why: Aligns future deployment planning with the OpenAI ecosystem and keeps
  docs consistent while avoiding immediate infra churn.

## D-033: Eval-generated chats use deterministic titles

- Category: `eval_quality`
- Tags: `eval_hygiene`, `chat_naming`, `ui_clarity`, `traceability`
- Decision: Update eval harness chat creation to set `title=session_id` for
  generated chats instead of relying on default `New chat`.
- Why: Prevents ambiguous sidebar artifacts during retained eval runs and keeps
  eval sessions easy to identify and clean up.

## D-034: Adaptive note merge prevents feedback over-indexing in model input

- Category: `collaboration_method`
- Tags: `adaptive_notes`, `input_hygiene`, `over_indexing_control`, `style_recovery`
- Decision: Build model input notes with near-duplicate suppression, decay-weighted
  feedback scoring, and a hard cap of two active adaptive notes, while logging
  note transitions per chat.
- Why: Keeps runtime guidance subtle and stable so repeated feedback does not
  stack into rigid behavior, and preserves natural recovery flow after
  uncertainty/grounding corrections.

## D-035: Playwright smoke covers retry-variant lineage behavior

- Category: `eval_quality`
- Tags: `playwright`, `e2e`, `retry_variant`, `regression_guard`
- Decision: Extend frontend smoke E2E coverage to validate retry-generated
  assistant variants (`source_user_message_id` lineage), including variant
  navigation and no duplicate user prompt rows.
- Why: Protects the highest-risk UI/runtime integration path with fast
  deterministic browser checks after variant and feedback-flow changes.

## D-036: Human-boundary guardrail family for distress, recursive rumination, and interpersonal certainty

- Category: `runtime_engineering`
- Tags: `safety_guardrails`, `human_ai_boundaries`, `rumination_loop`, `interpersonal_attribution`
- Decision: Extend `/chat` guardrail composition with emotional-distress,
  recursive-why-loop, and interpersonal/divination-attribution boundaries that
  block motive certainty and stereotype reinforcement while preserving
  supportive tone.
- Why: Reduce collusive or certainty-escalating responses in sensitive personal
  prompts and keep real-time adaptation inside explicit safety boundaries.
