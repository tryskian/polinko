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
- Decision: Add lightweight governance controls and factual-query hallucination guardrails with env flags.
- Why: Reduce risk of unsupported factual certainty and enforce tool policy boundaries during orchestration rollout.

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
- Decision: Refine retrieval behaviour by memory scope and tighten API payload typing hints where dynamic dict/list payloads are used.
- Why: Improve retrieval consistency and reduce editor/type-check noise without changing user-facing behaviour.

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
- Why: Makes retrieval-path behaviour observable to clients and tests without
  relying only on server logs, improving debugging and deterministic contract
  validation.

## D-024: Normalise quoted env values for runtime config parsing

- Category: `workflow_environment`
- Tags: `env_parsing`, `docker_env_file`, `startup_reliability`
- Decision: Normalise wrapped quotes from env values (for example
  `"OPENAI_API_KEY=\"sk-...\""` style inputs) before config validation/parsing.
- Why: Docker `--env-file` passes quoted values literally; without normalisation
  valid `.env` configurations could fail at startup in container runs.

## D-025: Parameterized hallucination judge endpoint + optional Braintrust CI gate scaffold

- Category: `eval_quality`
- Tags: `hallucination_gate`, `judge_endpoint`, `braintrust`, `ci_optional`
- Decision: Extend hallucination eval judge config with `--judge-api-key-env`
  and `--judge-base-url`, add `make hallucination-gate`, and wire an optional
  CI step that runs strict hallucination gating against an OpenAI-compatible
  Braintrust endpoint when repo vars/secrets are present.
- Why: Enables P1 judge-gate rollout without changing runtime assistant
  behaviour and avoids hard-coding a single judge provider path.

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
  default behaviour when calibration vars are not yet set.

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
  stack into rigid behaviour, and preserves natural recovery flow after
  uncertainty/grounding corrections.

## D-035: Playwright smoke covers retry-variant lineage behaviour

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

## D-037: Verification-first environment mutation policy (anti-gremlin)

- Category: `workflow_environment`
- Tags: `agent_hygiene`, `no_guessing`, `scope_control`, `env_stability`
- Decision: Adopt a strict verify-before-mutate workflow for environment fixes:
  confirm canonical repo path, host/container mode, and branch first; prefer
  repo-scoped configuration edits; block user-level shell/profile or global VS
  Code settings changes unless explicitly approved in-chat.
- Why: Prevents recurring configuration drift from speculative fixes, limits
  blast radius during troubleshooting, and preserves reproducible startup
  behaviour across sessions and agents.

## D-038: Co-reasoning interaction rubric for style/eval reliability

- Category: `eval_quality`
- Tags: `co_reasoning`, `interaction_dynamics`, `style_eval`, `benchmark_gap`
- Decision: Add an explicit co-reasoning evaluation rubric and style-eval stress
  cases that test:
  - constraint retention without rigidity
  - meta-level shift handling mid-thread
  - style adaptation without mimicry collapse
  - grounding under playful abstraction
- Why: Standard benchmark patterns miss these interaction dynamics; this rubric
  makes high-value collaborative behaviour observable and repeatable in both
  judge-based eval runs and human PASS/FAIL triage.

## D-039: Hallucination threshold calibration tie-break prefers strictest equal-metric threshold

- Category: `eval_quality`
- Tags: `hallucination_gate`, `calibration`, `tie_break`, `ci_stability`
- Decision: Update calibration selection logic to prefer the highest (strictest)
  threshold when accuracy/precision/recall are tied.
- Why: Prevents under-conservative recommendations (for example `0`) when
  multiple thresholds perform identically and observed passing-score floors are
  higher, keeping CI gate settings aligned with real eval distributions.

## D-040: Define explicit CLIP A/B escalation criterion before integration

- Date: 2026-03-10
- Category: `eval_quality`
- Tags: `clip_ab`, `go_no_go`, `multimodal`, `integration_gate`
- Decision: Promote CLIP from scaffold/proxy phase only when two consecutive
  CLIP A/B report runs (`cases_count >= 4`) meet all of:
  - proxy any-hit rate `>= 0.90`
  - any-hit delta (`proxy - baseline`) `>= 0.50`
  - zero errors and zero skipped cases in both arms
- Why: Keeps escalation objective and repeatable, and prevents integrating on a
  single favorable run or under-powered sample.

## D-041: Persist all eval submissions and add a cursor-based inbox monitor

- Category: `evidence_governance`
- Tags: `eval_inbox`, `feedback_logging`, `triage_visibility`, `workflow_speed`
- Decision: Append every UI eval submission (`PASS`, `FAIL`) to
  `docs/portfolio/raw_evidence/INBOX/eval_submissions.jsonl` and add
  `make eval-inbox` to show new entries since the last local cursor checkpoint.
- Why: Makes new eval activity immediately discoverable, improves remediation
  triage speed, and preserves a complete chronological submission trail.

## D-042: Repo-scoped mypy configuration and workspace diagnostics

- Category: `workflow_environment`
- Tags: `mypy`, `ruff`, `diagnostic_noise`, `repo_scoped_config`
- Decision: Add `mypy.ini` as the canonical type-check config, run mypy from
  the workspace venv binary, and configure editor diagnostics in workspace
  scope with repo-level exclusions for generated/derived high-noise paths.
- Why: Keeps type/lint signals consistent between CLI and IDE, reduces false
  positives from non-product scaffolding, and preserves focus on actionable
  runtime issues.

## D-043: Minimal CLIP proxy integration behind explicit file-search profile flag

- Category: `runtime_engineering`
- Tags: `clip_proxy`, `file_search`, `feature_flag`, `rollback`
- Decision: Add `retrieval_profile=clip_proxy_image_only` to
  `POST /skills/file_search`, gated by
  `POLINKO_CLIP_PROXY_FILE_SEARCH_ENABLED` (default `false`), where enabled
  profile requests force image-only retrieval while default behaviour remains
  unchanged.
- Why: Enables controlled CLIP-proxy rollout with an explicit rollback toggle,
  minimal behaviour drift, and deterministic API-level validation before deeper
  retrieval-path integration.

> Historical note (2026-03-21): D-044 through D-054 are retained for audit
> trail only and are deprecated as active operating guidance.

## D-044: Add report-level hybrid OpenAI readiness gate before tooling migration

- Category: `eval_quality`
- Tags: `hybrid_openai`, `readiness_gate`, `no_runtime_drift`, `adoption_plan`
- Decision: Add `make hybrid-openai-readiness` (reports-only checker) and keep
  hybrid OpenAI adoption gated by strict style + file-search + two-report CLIP
  readiness outcomes before any runtime/tooling migration.
- Why: Creates an explicit low-risk promotion contract for OpenAI-native
  adoption while preserving current runtime behaviour and rollback simplicity.

## D-045: Add append-only eval trace artifact contract in tooling layer

- Category: `evidence_governance`
- Tags: `trace_artifacts`, `hybrid_openai`, `eval_reports`, `no_runtime_drift`
- Decision: Add a shared trace schema/writer
  (`tools/eval_trace_artifacts.py`, schema `polinko.eval_trace.v1`) and wire
  report-producing eval tooling + hybrid readiness checker to append JSONL
  traces to
  `docs/portfolio/raw_evidence/INBOX/eval_trace_artifacts.jsonl`.
- Why: Creates a stable evidence contract for hybrid OpenAI adoption phases
  without changing runtime `/chat` behaviour, while improving auditability and
  promotion confidence for future OpenAI-native tooling pilots.

## D-046: Constrain Phase 3 hybrid pilot to offline tooling bridge only

- Category: `runtime_engineering`
- Tags: `hybrid_openai`, `pilot_scope`, `rollback_safe`, `no_runtime_drift`
- Decision: Define Phase 3 hybrid adoption pilot as a tooling-only bridge from
  local trace artifacts to OpenAI-compatible trace/grader metadata shape, with
  strict out-of-scope exclusion for runtime `/chat` migration, prompt behaviour
  changes, and default-on flags.
- Why: Preserves current stable runtime contract while still creating concrete
  migration evidence toward OpenAI-native tooling integration.

## D-047: Implement rollback-safe Phase 3 dry-run bridge scaffold

- Category: `runtime_engineering`
- Tags: `hybrid_openai`, `phase3`, `dry_run`, `rollback_safe`, `tooling_only`
- Decision: Implement `tools/hybrid_openai_trace_bridge.py` and
  `make hybrid-openai-pilot-dry-run` with flag-off default
  (`HYBRID_OPENAI_PILOT_ENABLED=false`) to transform local eval trace JSONL
  into OpenAI-compatible trace/grader metadata preview artifacts without
  provider upload or runtime path changes.
- Why: Starts Phase 3 execution with deterministic, testable, low-risk tooling
  progress while preserving strict rollback and runtime parity guarantees.

## D-048: Add idempotent trace backfill and schema check for Phase 3 preview quality

- Category: `evidence_governance`
- Tags: `hybrid_openai`, `phase3`, `trace_backfill`, `schema_validation`
- Decision: Add `tools/backfill_eval_trace_artifacts.py` to convert existing
  UI eval submissions into `polinko.eval_trace.v1` artifacts (idempotent by
  `submission_key`) and add
  `tools/check_hybrid_openai_bridge_preview.py` to enforce minimum-row and
  required-field validation on dry-run bridge preview output.
- Why: Removes manual inspection as the only quality gate for Phase 3 pilot
  artifacts, allows deterministic replay from existing eval history, and keeps
  tooling adoption measurable without runtime `/chat` migration risk.

## D-049: Binary eval outcome is the release-grade signal; tags remain diagnostic

- Category: `eval_quality`
- Tags: `binary_first`, `pass_fail`, `determinism`, `human_machine_bridge`
- Decision: Treat binary eval outcome (`PASS`/`FAIL`) as the primary gate
  signal across runtime-quality loops. Keep tags/notes as secondary metadata
  for diagnosis and remediation planning.
- Why: This aligns evaluation output with deterministic implementation actions
  (ship/hold/fix), while preserving high-context human reasoning in transcripts
  and notes. In practice: nuanced interpretation informs the diagnosis, binary
  outcome informs the decision.

## D-050: Add OpenAI custom-eval dataset export contract from local trace artifacts

- Category: `evidence_governance`
- Tags: `hybrid_openai`, `custom_eval`, `jsonl_export`, `item_schema`
- Decision: Add deterministic tooling export from
  `polinko.eval_trace.v1` artifacts to OpenAI custom-eval dataset rows
  (`tools/export_openai_eval_dataset.py`) plus an artifact checker
  (`tools/check_openai_eval_dataset_export.py`), wired via
  `make hybrid-openai-export-dataset`, `make hybrid-openai-export-check`, and
  `make hybrid-openai-export-cycle`.
- Why: Provides a direct bridge into OpenAI Eval API inputs
  (dataset JSONL + `data_source_config.item_schema`) while keeping runtime
  `/chat` behaviour unchanged and preserving rollback-safe, tooling-only
  adoption.

## D-051: Add manual-first provider execution helper for OpenAI eval pilot

- Category: `runtime_engineering`
- Tags: `hybrid_openai`, `manual_first`, `provider_pilot`, `no_runtime_drift`
- Decision: Add `tools/prepare_openai_eval_pilot.py` plus Make targets
  `hybrid-openai-prepare-pilot-payloads` and `hybrid-openai-execute-pilot` so
  pilot execution is explicit and reversible:
  - prepare mode writes create-eval and create-run payloads only
  - execute mode can upload dataset, create eval, and start run when requested
  - runtime `/chat` path remains unchanged
- Why: Moves Phase 3 from artifact-only export into controlled provider-side
  validation while keeping the default workflow manual-first and preserving
  rollback safety.

## D-052: Worktree-first implementation with parallel eval orchestration and single director merge control

- Category: `collaboration_method`
- Tags: `worktree_first`, `multi_agent`, `parallel_eval`, `single_decider`
- Decision: Standardize on worktrees for concurrent code tracks, use multi-agent
  delegation only for bounded parallel analysis tasks, and add a parallel eval
  orchestrator command (`make eval-reports-parallel`) while keeping final
  PASS/FAIL promotion decisions centralized in one director thread.
- Why: Increases throughput without merge chaos, preserves deterministic
  decision authority, and keeps parallel computation observable via per-suite
  reports/logs plus one consolidated artifact.

## D-053: Package product workflow in Agent Builder while keeping repo runtime canonical (Historical)

- Category: `workflow_environment`
- Tags: `agent_builder`, `packaging`, `openai_native`, `source_of_truth`
- Decision: Use OpenAI Agent Builder as the product packaging/orchestration
  layer (workflow publishing + deployment integration) while keeping this repo's
  backend/eval stack as the canonical implementation and regression source of
  truth.
- Status: superseded by D-058 (Agent Builder/hybrid pilot path deprecated as
  active workflow).

## D-054: Human-directed micro-constraints drive meaningful product quality

- Category: `collaboration_method`
- Tags: `human_ai_collaboration`, `micro_decisions`, `naming_contract`, `quality_signal`
- Decision: Treat small human-directed adjustments (for example, consistent
  naming like `hallucination_risk`) as first-class quality controls in the
  product workflow.
- Why: These micro-constraints encode intent and domain meaning that autonomous
  generation does not reliably infer on its own, and they measurably improve
  coherence, eval interpretability, and release readiness.

## D-054b: Defer provider-side eval execution until explicit ship-readiness (Historical)

- Category: `runtime_engineering`
- Tags: `hybrid_openai`, `local_first`, `execution_policy`, `ship_readiness`
- Decision: Keep OpenAI provider-side pilot execution
  (`make hybrid-openai-execute-pilot`) deferred during normal development;
  continue local export + payload preparation cycles and only execute provider
  runs after explicit ship-readiness approval.
- Why: Preserves local determinism and reduces rollout risk while the runtime
  and eval contracts continue hardening; avoids premature coupling to external
  provider execution before release intent.

## D-055: Canonicalize tooling imports for mypy stability

- Category: `workflow_environment`
- Tags: `mypy`, `import_hygiene`, `tooling_consistency`, `maintenance`
- Decision: Remove dual-path fallback imports in eval/pilot tooling files and
  standardize on canonical `from tools...` imports.
- Why: Eliminates mypy `import-not-found`/`no-redef` noise from branchy import
  patterns and keeps type-checking deterministic across local and CI runs.

## D-056: Keep gate logic binary; keep human nuance diagnostic

- Category: `eval_quality`
- Tags: `binary_gate`, `human_perception`, `determinism`, `style_baseline`
- Decision: Keep eval gate outcomes strictly binary (`PASS`/`FAIL`) and set
  `em_dash_style` as a hard-fail signal during style-baseline stabilization;
  keep nuanced interpretation in notes/transcripts instead of gate semantics.
- Why: Mapping human-perception nuance directly into gate logic introduces
  ambiguity and drift; separating deterministic decisions from diagnostic
  context preserves machine clarity while retaining high-context human insight.
- Captured engineering response: Keep final scoring in strict binary
  (`PASS`/`FAIL`), and keep human nuance in secondary layers (notes,
  transcripts, recovery analysis) rather than in the decision gate itself.

## D-057: Store eval checkpoints as dual streams for cross-dimension signals

- Category: `eval_quality`
- Tags: `dual_stream`, `checkpoint_contract`, `ui_api_sync`
- Decision: Allow checkpoint rows to persist simultaneous positive and negative
  rubric signals as separate streams (`pass: ...` and `fail: ...`) rather than
  forcing a single top-level summary label.
- Why: This preserves diagnostic fidelity for responses that pass one dimension
  and fail another (for example strong style with hallucination risk), while
  keeping deterministic downstream counting via independent `pass_count` and
  `fail_count` aggregation.

## D-060: Canonicalize eval outcome contract to binary while preserving legacy read compatibility

- Category: `eval_quality`
- Tags: `binary_contract`, `legacy_compat`, `pass_fail`, `api_ui_sync`
- Decision: Treat `pass`/`fail` as the only accepted feedback outcomes at write
  time, while preserving read compatibility for legacy stored outcomes by
  normalizing non-pass values to `fail` in API/UI response paths.
- Why: Removes deprecated outcome ambiguity from active workflows without
  discarding historical evidence; keeps deterministic gating and migration-safe
  legacy visibility.

## D-058: Deprecate hybrid/Agent Builder pilot workflow as active execution path

- Category: `workflow_environment`
- Tags: `deprecation`, `local_first`, `operating_mode`, `docs_cleanup`
- Decision: Mark hybrid OpenAI pilot tooling and Agent Builder mirror planning
  as archived/deprecated in active docs, and treat local glue-code + manual
  eval loop as the only active execution path.
- Why: Reduces operator drift and planning noise, keeps daily execution
  deterministic, and aligns documentation with actual implementation behaviour.

## D-059: Human-judgment-first execution; agentic parallelism only after architecture lock

- Category: `collaboration_method`
- Tags: `human_ai_collaboration`, `architecture_first`, `execution_control`, `multi_agent`
- Decision: Keep the active build loop human-judgment-first and director-led
  until architecture, acceptance criteria, and evaluation rubric are explicit.
  Use multi-agent/parallel workflows only after those constraints are locked,
  and only for bounded tasks with deterministic validation.
- Why: Agentic parallelism amplifies throughput but also amplifies ambiguity.
  Establishing architecture first prevents interpretation drift, reduces
  rework/tangle risk, and keeps outcomes reviewable against clear criteria.

## D-061: Human-reference workflow is FK-backed and query-first

- Category: `evidence_governance`
- Tags: `human_reference`, `sqlite`, `foreign_keys`, `operator_simplicity`
- Decision: Keep human-reference operations centred on `.human_reference.db`
  rebuild + preset SQL/CLI queries (`make human-reference-*`), with explicit
  FK links (`links.source_path`/`links.target_path` -> `documents.path`) for
  reliable relationship traversal and DB-viewer ER rendering.
- Why: This keeps the workflow easy to operate offline, avoids maintaining a
  separate bespoke visualization surface, and preserves clear relationship
  semantics for imagineer-facing exploration.
