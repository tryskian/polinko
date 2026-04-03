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
- Decision: Add GitHub Actions CI (`test`), `requirements.lock`, and `docs/runtime/RUNBOOK.md`.
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
- Tags: `file_search`, `api_spec`, `fallback_visibility`, `observability`
- Decision: Extend `POST /skills/file_search` response with explicit `backend`,
  `fallback_reason`, and `candidate_count` fields.
- Why: Makes retrieval-path behaviour observable to clients and tests without
  relying only on server logs, improving debugging and deterministic spec
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
  integration can be validated against a stable experiment spec later.

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
  - zero errors in both arms
- Why: Keeps escalation objective and repeatable, and prevents integrating on a
  single favorable run or under-powered sample.

## D-041: Persist all eval submissions and add a cursor-based inbox monitor

- Status: Superseded by `D-068`/`D-069` (runtime now uses SQLite state only; `raw_evidence` intake folders are archived)
- Note: Legacy inbox helper (`make eval-inbox`, `tools/eval_inbox.py`) removed from active surface.

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
- Why: Creates an explicit low-risk promotion spec for OpenAI-native
  adoption while preserving current runtime behaviour and rollback simplicity.

## D-045: Add append-only eval trace artifact spec in tooling layer

- Category: `evidence_governance`
- Tags: `trace_artifacts`, `hybrid_openai`, `eval_reports`, `no_runtime_drift`
- Decision: Add a shared trace schema/writer
  (`tools/eval_trace_artifacts.py`, schema `polinko.eval_trace.v1`) and wire
  report-producing eval tooling + hybrid readiness checker to append JSONL
  traces to
  `docs/portfolio/raw_evidence/INBOX/eval_trace_artifacts.jsonl`.
- Why: Creates a stable evidence spec for hybrid OpenAI adoption phases
  without changing runtime `/chat` behaviour, while improving auditability and
  promotion confidence for future OpenAI-native tooling pilots.
- Status: Superseded by `D-073` (trace default path is local operational output
  under `eval_reports/eval_trace_artifacts.jsonl`; Git history is canonical
  retention for tracked state).

## D-046: Constrain Phase 3 hybrid pilot to offline tooling bridge only

- Category: `runtime_engineering`
- Tags: `hybrid_openai`, `pilot_scope`, `rollback_safe`, `no_runtime_drift`
- Decision: Define Phase 3 hybrid adoption pilot as a tooling-only bridge from
  local trace artifacts to OpenAI-compatible trace/grader metadata shape, with
  strict out-of-scope exclusion for runtime `/chat` migration, prompt behaviour
  changes, and default-on flags.
- Why: Preserves current stable runtime spec while still creating concrete
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

## D-050: Add OpenAI custom-eval dataset export spec from local trace artifacts

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
- Tags: `human_ai_collaboration`, `micro_decisions`, `naming_spec`, `quality_signal`
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
  and eval specs continue hardening; avoids premature coupling to external
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
- Tags: `dual_stream`, `checkpoint_spec`, `ui_api_sync`
- Decision: Allow checkpoint rows to persist simultaneous positive and negative
  rubric signals as separate streams (`pass: ...` and `fail: ...`) rather than
  forcing a single top-level summary label.
- Why: This preserves diagnostic fidelity for responses that pass one dimension
  and fail another (for example strong style with hallucination risk), while
  keeping deterministic downstream counting via independent `pass_count` and
  `fail_count` aggregation.

## D-060: Canonicalize eval outcome spec to binary while preserving legacy read compatibility

- Category: `eval_quality`
- Tags: `binary_spec`, `legacy_compat`, `pass_fail`, `api_ui_sync`
- Decision: Treat `pass`/`fail` as the only accepted feedback outcomes at write
  time, while preserving read compatibility for legacy stored outcomes by
  normalizing non-pass values to `fail` in API/UI response paths.
- Why: Removes deprecated outcome ambiguity from active workflows without
  discarding historical evidence; keeps deterministic gating and migration-safe
  legacy visibility.
- Status: Superseded by `D-067` hard-cut spec removal of compatibility
  fallbacks.

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
- Status: Superseded by `D-076` (human-reference SQLite workflow is archive-only).

## D-062: Inspect-first execution and explicit legacy cutlines

- Category: `collaboration_method`
- Tags: `inspect_first`, `human_directed`, `legacy_context`, `cutline_control`
- Decision: When context appears noisy or ambiguous, pause and inspect before
  cleanup/refactor, and keep legacy infrastructure/context (including MCP
  wiring) until an explicit migration cutline is directed.
- Why: Prevents summary-first optimisation from removing meaningful context and
  keeps rebuild outputs coherent, reviewable, and usable.

## D-063: Introduce build-block guardrail for fresh-path iteration

- Category: `workflow_environment`
- Tags: `drift_control`, `readme_spec`, `local_ci_parity`
- Decision: Add deterministic preflight guard checks for README-to-route parity,
  Makefile tool-module wiring, local lint parity with CI scope, and local-only
  eval-cleanup guard behaviour.
- Why: Supports step-by-step fresh-path execution without hard resets by
  catching spec drift and local-only dependency leaks before wider refactor
  moves.

## D-064: Standardise Reasoning Loops as the human-AI collaboration model

- Category: `collaboration_method`
- Tags: `reasoning_loops`, `human_ai_collaboration`, `role_clarity`, `hypothesis_driven`
- Decision: Use `Reasoning Loops` as the canonical term for the active
  collaboration mode, with explicit split of responsibilities:
  - imagineer leads hypotheses/theory framing, visual culture direction, and
    live eval operation
  - engineer leads implementation, tooling/process decisions, validation, and
    execution recommendations
- Why: Shared language and role clarity reduce collaboration drift, preserve
  voice authenticity, and make decisions easier to audit in transcripts and
  evidence.

## D-065: Fail-closed eval checkpointing with explicit legacy outcome normalisation

- Category: `eval_quality`
- Tags: `binary_spec`, `fail_closed`, `checkpoint_guard`, `legacy_normalisation`
- Decision: Enforce fail-closed checkpoint submission when non-binary feedback
  outcomes are present, and pair it with an explicit normalisation utility path
  to migrate legacy outcome rows into binary `pass`/`fail`.
- Why: Prevents silent ambiguity in release-gate artefacts, keeps checkpoint
  semantics deterministic, and provides an auditable migration path instead of
  implicit coercion at checkpoint time.
- Status: Superseded by `D-067` (normalisation utility removed from active flow).

## D-066: Archive legacy eval intake structure from active evidence flow

- Category: `evidence_governance`
- Tags: `legacy_archive`, `binary_flow`, `evidence_index`, `active_buckets`
- Decision: Treat legacy `MIXED` intake structure as archive-only and keep
  active evidence indexing/reporting scoped to `PASS`/`FAIL`/`INBOX` buckets.
- Why: Prevents non-binary artefacts from re-entering daily eval operations and
  keeps evidence refresh outputs aligned with the current binary gate spec.
- Status: Superseded by `D-068` (top-level `raw_evidence` intake folders/files
  are deprecated; archive snapshots only).

## D-067: Hard-cut eval spec to strict binary with no compatibility fallbacks

- Category: `eval_quality`
- Tags: `binary_spec`, `hard_cutover`, `api_ui_sync`, `spec_simplification`
- Decision: Remove legacy compatibility paths from active feedback/checkpoint
  runtime:
  - accept only `pass`/`fail` outcomes
  - require explicit `positive_tags`/`negative_tags` streams (no `tags`-only fallback)
  - expose checkpoint integrity via `non_binary_count` (no active `other_count` label)
  - remove `eval-feedback-normalize` migration tooling from active operator flow
- Why: Eliminates hidden coercion paths, keeps API/UI/test specs explicit,
  and prevents deprecated semantics from re-entering daily execution.

## D-068: Add one-command baseline archive reset before new binary cycles

- Category: `evidence_governance`
- Tags: `archive_reset`, `binary_only`, `eval_hygiene`, `fresh_baseline`
- Decision: Add `make eval-reset-baseline` (tool:
  `tools/archive_eval_baseline.py`) to move deprecated eval intake
  artefacts/evidence records into timestamped archive snapshots before starting
  a fresh binary eval cycle.
- Why: Keeps active eval surfaces clean, prevents stale evidence from steering
  new binary decisions, and preserves full historical traceability in archive
  paths.

## D-069: Deprecate UI from active eval/runtime operations

- Category: `workflow_environment`
- Tags: `ui_deprecation`, `backend_first`, `cli_first`, `runtime_control`
- Decision: Treat the web UI as deprecated for active build and eval
  operations; backend API + CLI are the canonical execution surfaces.
- Why: Reduces hidden state vectors and interaction drift, keeps runtime
  behaviour deterministic, and simplifies auditability while the binary eval
  baseline is being hardened.

## D-070: Engineer-led proactive hygiene is default execution mode

- Category: `collaboration_method`
- Tags: `proactive_hygiene`, `ownership`, `drift_control`, `execution_mode`
- Decision: Make proactive technical hygiene the default engineering mode:
  - detect and address drift/gremlin-risk paths before they become blockers
  - run required cleanup/validation/doc propagation without waiting for prompts
  - ask for input only when approvals or high-impact trade-offs are needed
- Why: Reduces coordination overhead, keeps `main` clean continuously, and
  preserves imagineer focus on hypotheses/theory while engineering handles
  technical control surfaces end-to-end.

## D-071: Human-managed work control is mandatory in co-reasoning loops

- Category: `collaboration_method`
- Tags: `reasoning_loops`, `human_governance`, `scope_control`, `decision_rights`
- Decision: In human-AI co-reasoning, work-management control remains human-led:
  - human owns objective function, scope boundaries, and acceptance criteria
  - human decides ambiguity trade-offs and go/no-go cutlines
  - engineer executes implementation/proactive hygiene within that frame
- Why: Model behaviour optimises local completion patterns and can drift toward
  summary-first or over-targeted execution without full product-context
  accountability; human governance keeps outputs aligned to intent, meaning, and
  usable end-state quality.

## D-072: Canonical eval policy model is fail-closed, high-value-only, and policy-dominant

- Date: `2026-03-27`
- Category: `eval_quality`
- Tags: `binary_gate`, `fail_closed`, `policy_guardrails`, `high_value_evals`
- Decision: Standardise eval decision semantics as:
  - `reward ⊨ alignment`
  - `reward ⊭ adjustment`
  - `reward ⊭ intensity`
  - `PASS ⇔ policy_pass ∧ high_value_alignment_pass ∧ evidence_complete`
  - otherwise `FAIL`
- Why: Keeps release decisions deterministic, blocks reward-only optimisation
  drift, and ensures policy constraints remain the hard control surface while
  preserving rich diagnostics outside the binary gate output.
- Implementation note: Concept model and ER mapping are documented in
  `docs/runtime/RUNBOOK.md`.

## D-073: Remove archive-folder workflow; use Git-native retention

- Date: `2026-03-27`
- Category: `evidence_governance`
- Tags: `git_native`, `archive_removal`, `workflow_simplification`, `binary_hygiene`
- Decision:
  - remove active archive/reset operator flow (`make eval-reset-baseline`)
  - remove archive-reset utility module (`tools/archive_eval_baseline.py`)
  - set eval trace default output to `eval_reports/eval_trace_artifacts.jsonl`
  - treat Git history as the canonical archive for tracked docs/code
- Why: The archive-folder layer duplicated Git semantics, added operator
  overhead, and introduced path complexity without improving release decision
  quality.
- Supersedes: `D-068` for active operations.

## D-074: Introduce a tracked live archive lane for deprecated eval/frontend context

- Date: `2026-03-27`
- Category: `evidence_governance`
- Tags: `live_archive`, `legacy_reference`, `frontend_deprecation`, `binary_hygiene`
- Decision:
  - create `.archive/live_archive/` as the single tracked reference surface for
    deprecated implementation context
  - split lanes by concern:
    - `.archive/live_archive/legacy_eval/`
    - `.archive/live_archive/legacy_frontend/`
  - keep archive lane read-only for reference; active runtime specs remain
    sourced from canonical docs/code
- Why: Preserves inspectability/traceability of deprecated context without
  reintroducing legacy wiring into active runtime and eval decisions.

## D-075: Remove legacy hallucination-mode labels from active eval case spec

- Date: `2026-03-27`
- Category: `eval_quality`
- Tags: `binary_spec`, `criteria_cleanup`, `policy_profile`, `hallucination_eval`
- Decision:
  - replace active hallucination case label `expected_mode` with
    `policy_profile`
  - use only:
    - `evidence_required`
    - `uncertainty_required`
  - remove deprecated criteria tags from OCR recovery case guidance
    (`grounding_gap` and related legacy labels)
- Why: Drops legacy criteria vocabulary from active eval wiring so new UI and
  backend flows align to policy-profile semantics without ambiguity.

## D-076: Archive SQLite human-reference workflow

- Date: `2026-03-27`
- Category: `evidence_governance`
- Tags: `human_reference`, `archive_only`
- Decision:
  - move SQLite human-reference workflow to archive-only status in
    `.archive/live_archive/legacy_human_reference/`
  - leave legacy human-reference make targets as archive notices
- Why: Reduces operator complexity without keeping an active DB/query workflow
  in the critical path.

## D-077: Remove frontend codebase from active repository surface

- Date: `2026-03-27`
- Category: `workflow_environment`
- Tags: `frontend_removal`, `backend_cli_only`, `surface_reduction`, `drift_control`
- Decision:
  - remove `frontend/` from active repository contents
  - remove active UI make targets/wiring and update dev flow to backend-only
  - retain legacy frontend context through live-archive docs + Git history
- Why: Eliminates hidden UI state/wiring vectors while preparing a clean-slate
  UI rebuild and keeps active execution surfaces deterministic.

## D-080: Tooling audit and legacy cleanup

- Date: `2026-03-27`
- Category: `workflow_environment`
- Tags: `artifact_cleanup`, `legacy_tools`, `runtime_db_paths`, `archive_only`
- Decision:
  - Archived human-reference helpers and SQL into `.archive/live_archive/legacy_human_reference/`.
  - Removed legacy workbench server/target and eval inbox helper (`make eval-inbox`, `tools/eval_inbox.py`).
  - Retired local runtime DB scripts/targets during wiring lock; no local DB lifecycle commands remain.
- Why: Reduce hidden gremlins and keep the active execution surface minimal and aligned with current binary eval specs.

## D-081: Expose fail-closed checkpoint gate outcome in API responses

- Date: `2026-03-28`
- Category: `eval_quality`
- Tags: `binary_gate`, `checkpoint_spec`, `decision_clarity`, `api_sync`
- Decision:
  - add explicit `gate_outcome` (`pass`/`fail`) to checkpoint response payloads
  - derive `gate_outcome` fail-closed from checkpoint counts:
    - `pass` iff `total_count > 0`, `fail_count == 0`, and `non_binary_count == 0`
    - `fail` otherwise
- Why: Removes operator inference overhead on go/no-go decisions while keeping
  gate semantics deterministic and count-driven.

## D-082: Block retired runtime DB command references in active docs

- Date: `2026-03-28`
- Category: `workflow_environment`
- Tags: `doc_spec`, `wiring_lock`, `drift_control`
- Decision:
  - remove retired runtime DB command references (`make db-reset`,
    `make db-archive`, `make db-visuals`) from active docs
  - enforce via deterministic doc guard checks in active validation
- Why: Prevents documentation drift from reintroducing deprecated local DB
  lifecycle flows during wiring lock.

## D-083: Mark benchmark A/B/C as decision-ready and use it to drive backend priority

- Date: `2026-03-28`
- Category: `research_experiment`
- Tags: `benchmark`, `minimal_config`, `binary_gate`, `priority_derivation`
- Decision:
  - mark benchmark phases A/B/C as decision-ready with verdict:
    - A=`PASS` (baseline anchor)
    - B=`FAIL` (traditional complexity underperforms)
    - C=`PASS` (binary current target)
  - derive next backend work from this verdict by prioritising
    operation-binding diagnostics (`benchmark D`) into deterministic
    implementation slices.
- Why: Keeps research sequencing product-supportive and converts benchmark
  output into explicit engineering prioritisation instead of open-ended
  interpretation.

## D-084: Add deterministic chat harness mode for UI smoke outside CLI

- Date: `2026-03-28`
- Category: `workflow_environment`
- Tags: `chat_harness`, `fixture_mode`, `deterministic_testing`, `minimal_drift`
- Decision:
  - add optional `POST /chat` harness fields:
    - `harness_mode` (`live`|`fixture`)
    - `fixture_output` (explicit deterministic fixture response)
  - keep default runtime behaviour unchanged (`live`)
  - add env default override:
    - `POLINKO_CHAT_HARNESS_DEFAULT_MODE` (`live`|`fixture`)
  - add API/config tests to lock live-vs-fixture spec behaviour
- Why: Allows UI testing outside CLI without backend breakage or model-call
  dependency while preserving canonical live path for production behaviour.

## D-085: Publish canonical UI eval adapter spec for new frontend

- Date: `2026-03-28`
- Category: `workflow_environment`
- Tags: `ui_adapter`, `chat_spec`, `binary_eval`, `integration`
- Decision:
  - add canonical UI adapter spec:
    - `docs/runtime/RUNBOOK.md`
  - define copy-ready TypeScript request/response shapes for:
    - `POST /chat`
    - feedback + checkpoint endpoints
  - define one explicit UI interaction flow for message -> eval -> checkpoint
    rendering
  - document binary tag/outcome validation and error handling matrix for UI
    implementation parity
- Why: Removes UI/backend ambiguity and gives a single deterministic spec for
  integrating eval functionality into the new frontend.

## D-088: Deliver local-first UI shell for chat and binary eval operations

- Date: `2026-03-28`
- Category: `workflow_environment`
- Tags: `ui_shell`, `binary_eval`, `operator_surface`, `minimal_drift`
- Decision:
  - add a lightweight local UI shell served at:
    - `GET /ui`
  - implement shell as repo-local static file:
    - `ui/index.html`
  - scope shell functionality to canonical adapter flow:
    - send message (`POST /chat`)
    - render thread (`GET /chats/{session_id}/messages`)
    - submit binary eval (`POST /chats/{session_id}/feedback`)
    - render/create checkpoints
      (`GET/POST /chats/{session_id}/feedback/checkpoints`)
  - include fixture-mode controls for deterministic smoke only
    (`harness_mode=fixture`)
- Why: Provides a durable non-CLI operator surface for day-to-day eval work
  with minimal implementation overhead and no behaviour drift in backend gate
  semantics.

## D-089: Archive deprecated coordination docs and keep top-level docs operational

- Date: `2026-03-28`
- Category: `workflow_environment`
- Tags: `docs_hygiene`, `live_archive`, `operator_clarity`, `straggler_cleanup`
- Decision:
  - move deprecated coordination docs from top-level `docs/` into:
    - `.archive/live_archive/legacy_coordination/`
  - keep `docs/governance/WORKSTREAMS.md` active and refresh it for current
    imagineer/engineer `Reasoning Loops` collaboration semantics
  - remove `.DS_Store` files from `docs/` surfaces
- Why: Reduces operator clutter in active docs while preserving historical
  context in one predictable archive lane.

## D-090: Retire active UI shell surface and remove `ui/` from runtime path

- Date: `2026-03-28`
- Category: `workflow_environment`
- Tags: `ui_retirement`, `surface_reduction`, `api_cli_canonical`, `drift_control`
- Decision:
  - remove active local UI shell assets:
    - delete `ui/index.html`
  - remove active API UI shell route:
    - delete `GET /ui`
  - remove UI-open helper targets from `Makefile`:
    - `open-ui`
    - `ui`
  - keep frontend history/reference in live archive only:
    - `.archive/live_archive/legacy_frontend/`
- Why: Reduces active-surface complexity and keeps the canonical operator path
  constrained to backend API + CLI during binary-spec hardening.

## D-091: Add transcript-backed OCR eval case mining from ChatGPT export

- Date: `2026-03-29`
- Category: `eval_quality`
- Tags: `ocr`, `transcript_mining`, `local_only_artifacts`, `precision_first`
- Decision:
  - add export indexing and transcript mining tools:
    - `tools/index_cgpt_export.py`
    - `tools/build_ocr_cases_from_export.py`
  - add make entrypoints for operator flow:
    - `make cgpt-export-index`
    - `make ocr-cases-from-export`
    - `make eval-ocr-transcript-cases`
  - keep generated export/index/case artifacts local-only under `.local/`
  - keep strict OCR gating on mined cases (`pass`/`fail`) without introducing
    legacy tag taxonomies into gate semantics
- Why: Enables reproducible OCR benchmarking against real transcript-backed
  handwriting/cursive signals while preserving local confidentiality and binary
  eval discipline.

## D-092: Add lightweight primary-source grounding method to case-study benchmark

- Date: `2026-03-29`
- Category: `research_experiment`
- Tags: `primary_source_grounding`, `case_study`, `scope_control`, `binary_gate`
- Decision:
  - add a lightweight primary-source grounding addendum to:
    - `docs/runtime/RUNBOOK.md`
  - constrain this phase to:
    - method definition + 1-2 mapped examples
    - no full corpus ingestion/tooling in active runtime scope
  - keep gate outcomes binary (`pass`/`fail`) and store nuance in notes/transcripts
- Why: Preserves case-study relevance and research rigor now without derailing
  product delivery into premature corpus infrastructure work.

## D-093: Split transcript OCR mining into typed and handwriting lanes with anchor-hardening

- Date: `2026-03-29`
- Category: `eval_quality`
- Tags: `ocr_lanes`, `typed_handwriting_split`, `anchor_hardening`, `strict_binary`
- Decision:
  - extend transcript OCR mining outputs to three local case sets:
    - combined (`ocr_transcript_cases_all.json`)
    - handwriting (`ocr_handwriting_from_transcripts.json`)
    - typed (`ocr_typed_from_transcripts.json`)
  - add lane-specific eval entrypoints:
    - `make eval-ocr-transcript-cases-handwriting`
    - `make eval-ocr-transcript-cases-typed`
  - harden generated assertions to use OCR-anchor terms (`must_contain_any`)
    rather than brittle narrative phrase regex chains
- Why: Preserves strict pass/fail gating while reducing false negatives from
  conversational wording noise and makes typed-vs-handwriting performance
  visible as separate quality lanes.

## D-094: Add illustration as a first-class transcript OCR lane

- Date: `2026-03-29`
- Category: `eval_quality`
- Tags: `ocr_lanes`, `illustration_lane`, `multimodal_coverage`, `strict_binary`
- Decision:
  - extend transcript OCR lane classification to include `illustration`
    alongside `typed` and `handwriting`
  - add dedicated local output artifact:
    - `ocr_illustration_from_transcripts.json`
  - add lane-specific eval entrypoint:
    - `make eval-ocr-transcript-cases-illustration`
  - keep lane semantics binary (`pass`/`fail`) and preserve existing strict OCR
    eval gate behaviour
- Why: Illustration-heavy OCR (diagrams/sketches with embedded text) has
  different failure modes than plain typed or handwriting samples, so it needs
  a distinct quality lane to keep benchmark signals interpretable.

## D-095: Mark selected live-archive lanes local-only and automate venv startup tasks

- Date: `2026-03-29`
- Category: `workflow_environment`
- Tags: `confidentiality`, `local_only_docs`, `vscode_tasks`, `venv_automation`
- Decision:
  - mark these archive lanes local-only via `.gitignore`:
    - `.archive/live_archive/legacy_eval/`
    - `.archive/live_archive/legacy_human_reference/`
  - remove those files from git tracking while retaining them locally
  - simplify VS Code startup task commands to rely on `make` interpreter
    auto-discovery instead of inline `source .../activate` chains
  - include `make doctor-env` in `workspace bootstrap` task dependencies
- Why: Keeps deprecated/internal material confidential in the new tree and
  reduces startup fragility by centralising environment selection in Makefile
  logic.

## D-096: Add mandatory morning worktree confirmation to startup routine

- Date: `2026-03-29`
- Category: `workflow_environment`
- Tags: `worktree_policy`, `startup_guard`, `parallel_execution`, `drift_control`
- Decision:
  - add a fixed morning check before implementation:
    - confirm canonical repo vs dedicated worktree path
    - confirm active branch
    - confirm automation is isolated to a separate worktree when running
  - codify this in:
    - `docs/runtime/RUNBOOK.md`
    - `docs/governance/SESSION_HANDOFF.md`
  - include worktree confirmation in the copy/paste rehydrate prompt
- Why: Human and automation both run parallel tracks; explicit startup
  worktree confirmation prevents cross-lane edits and reduces branch/workspace
  conflicts at the start of each session.

## D-097: Make command execution ownership explicit in Reasoning Loops

- Date: `2026-03-29`
- Category: `collaboration_method`
- Tags: `reasoning_loops`, `execution_ownership`, `operator_clarity`, `workflow`
- Decision:
  - codify command/Git execution ownership as engineer-side by default
  - codify imagineer role as objective/scope/acceptance/go-no-go control, not
    terminal operation
  - reflect this in:
    - `docs/governance/CHARTER.md`
    - `docs/runtime/RUNBOOK.md`
    - `docs/governance/SESSION_HANDOFF.md`
- Why: Prevents ineffective handoffs where the model asks the human to run
  routine engineering commands, keeps workflow consistent with role boundaries,
  and reduces operational friction.

## D-098: Adopt execution-first policy for engineer actions

- Date: `2026-03-29`
- Category: `collaboration_method`
- Tags: `execution_first`, `operator_experience`, `no_handoff_drift`, `workflow`
- Decision:
  - when the user requests action, engineer executes directly by default
  - keep human role focused on objective/scope/acceptance/go-no-go decisions
- Why: Reduces friction and ambiguity in human-AI collaboration and aligns
  behaviour with the agreed imagineer/engineer split.

## D-099: Harden OCR lane classification with embedded camera filenames and bounded typed hints

- Date: `2026-03-29`
- Category: `eval_quality`
- Tags: `ocr_lanes`, `lane_classification`, `handwriting_recovery`, `precision_guard`
- Decision:
  - classify embedded camera-style names (for example
    `file-...-IMG_6821.jpeg`, `file-...-DSC_####`) as `handwriting`
  - keep screenshot-name matching explicit for `typed` classification
  - bound typed hint token matching (notably `ui`) to standalone tokens to
    prevent substring false matches (for example `quick`)
  - preserve strict binary pass/fail gates and existing lane eval entrypoints
- Why: Restores missed handwriting cases without widening conversational noise,
  keeps illustration coverage intact, and removes a deterministic false-typed
  path from lane hint matching.

## D-100: Promote ask-level OCR corrections via transcription anchors, not correction-word anchors

- Date: `2026-03-29`
- Category: `eval_quality`
- Tags: `ocr_lanes`, `ask_correction`, `anchor_stability`, `strict_binary`
- Decision:
  - treat ask-message correction signals as medium-confidence promotion only
    when OCR intent + transcription anchors are present
  - keep high-confidence correction classification reserved for follow-up
    correction phrases
  - continue recording ask-level correction phrases in review diagnostics, but
    do not use them directly as eval case anchor requirements
- Why: Prevents brittle failures from correction-word anchors (for example
  `insight`/`weight`) while still recovering additional handwriting cases under
  strict binary pass/fail gates.

## D-101: Tighten transcript case emission to anchor-rich OCR phrases

- Date: `2026-03-29`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `anchor_threshold`, `precision_guard`, `strict_binary`
- Decision:
  - require at least `3` anchor terms before emitting a mined transcript OCR
    case
  - remove `probably` from forbidden-word checks to avoid false negatives on
    valid OCR outputs that include probability language
  - add regression coverage for single-anchor episodes to ensure they remain
    review-only and are not emitted as eval cases
- Why: Keeps transcript-derived cases focused on high-information OCR phrases
  and prevents brittle over-filtering from conversational wording.

## D-102: Prevent over-stemming in OCR anchor variant expansion

- Date: `2026-03-29`
- Category: `eval_quality`
- Tags: `anchor_normalization`, `ocr_transcripts`, `precision_guard`, `stability`
- Decision:
  - refine anchor variant expansion rules so plural stemming does not generate
    malformed forms (for example `focus -> focu`, `abacus -> abacu`)
  - preserve useful inflection handling (`tumbles -> tumble`,
    `floating -> float`, `classes -> class`)
  - add explicit regression tests for allowed stems and blocked malformed forms
- Why: Cleaner anchors improve transcript OCR case readability and reduce
  avoidable noise in strict eval requirements without changing binary gate
  semantics.

## D-103: Promote literal-intent transcript episodes with guarded phrase quality

- Date: `2026-03-29`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `confidence_gating`, `precision_guard`, `strict_binary`
- Decision:
  - add a medium-confidence promotion path for literal OCR-intent episodes when
    transcription phrases are strong (`>=3` anchors), multi-token, and not
    positive-only followup confirmations
  - keep correction/framing paths unchanged, including follow-up correction as
    the high-confidence path
  - add regression tests for:
    - safe literal-intent promotion without explicit framing
    - non-promotion for weak-anchor literal asks
    - non-promotion for single-token variant lists
- Why: Recovers valid transcript OCR cases under strict binary gates while
  blocking noisy promotions that degrade pass-rate precision.

## D-104: Keep case-study comparisons stack-scoped (no model naming)

- Date: `2026-03-29`
- Category: `research_method`
- Tags: `case_study`, `benchmarking`, `stack_comparison`, `evidence_framing`
- Decision:
  - express benchmark and portfolio comparisons in stack terms only:
    - baseline stack
    - advanced stack
    - binary stack
  - avoid model-specific naming in the core narrative framing
  - map claims to measurable outcomes:
    quality, decision clarity, iteration speed, and maintenance overhead
- Why: Maintains durable, implementation-relevant evidence framing without
  coupling the case study to transient model/version naming.

## D-105: Expand OCR framing detection to include transcript wording

- Date: `2026-03-29`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `framing_detection`, `precision_safe`, `coverage`
- Decision:
  - expand transcript miner framing detection from `transcrib*` only to
    `transcrib*` + `transcript*` lexical forms
  - keep existing anchor quality gates (`>=3` anchor terms) and strict binary
    eval validation unchanged
- Why: Recovers missed literal OCR episodes phrased as
  “here’s the transcription” without widening low-signal conversational noise.

## D-106: Add explicit transcript miner emit/skip diagnostics

- Date: `2026-03-29`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `diagnostics`, `operator_visibility`, `precision_guard`
- Decision:
  - add explicit per-episode review diagnostics to transcript OCR mining:
    `emit_status`, `anchor_terms`, `anchor_terms_count`
  - add command-summary counters:
    `emitted_cases`, `skipped_low_confidence`,
    `skipped_duplicate_image_path`, `skipped_insufficient_anchor_terms`
  - keep existing confidence and binary gate semantics unchanged
- Why: Makes precision tuning measurable without manual JSON forensics and
  reduces ambiguity when deciding the next safe promotion kernel.

## D-107: Expand illustration-lane hint vocabulary for topology sketch episodes

- Date: `2026-03-30`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `lane_classification`, `illustration_coverage`, `precision_safe`
- Decision:
  - extend illustration hint matching with topology/sketch vocabulary:
    `topolog*`, `trapezi*`, `prism`
  - keep existing confidence/anchor gates unchanged
  - require full strict lane + stability validation before accepting promoted
    cases
- Why: Correctly routes geometry-sketch transcript episodes that were being
  typed-labeled, lifting illustration coverage without broadening low-signal
  promotions.

## D-108: Add review-summary aggregates to transcript OCR mining output

- Date: `2026-03-30`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `review_schema`, `operator_visibility`, `precision_guard`
- Decision:
  - add a top-level `summary` block in
    `.local/eval_cases/ocr_transcript_cases_review.json` with:
    - `conversation_files`, `episodes`
    - `signal_strength_counts`, `lane_counts`
    - `emit_status_counts`, `lane_emit_status_counts`
  - keep per-episode review rows unchanged under `episodes`
  - keep confidence thresholds and case emission rules unchanged
- Why: Enables rapid lane-level triage and promotion decisions without manual
  aggregation over full review payloads.

## D-109: Harden OCR anchor matching for mixed split-letter tokens

- Date: `2026-03-30`
- Category: `eval_quality`
- Tags: `ocr_eval`, `anchor_matching`, `stability`, `strict_binary`
- Decision:
  - extend OCR rule matching so single-word anchors and forbidden words also
    match mixed split-letter outputs (for example `CHAT T IEST`, `GU ESS`)
  - preserve existing strict binary gate semantics and phrase-level constraints
  - add regression tests for mixed split required/forbidden matching
- Why: Removes deterministic false failures from OCR spacing artefacts while
  keeping gate strictness unchanged.

## D-110: Prioritise GPT-4o vision fine-tuning as first cookbook integration kernel

- Date: `2026-03-30`
- Category: `workflow_environment`
- Tags: `cookbook_queue`, `priority_pin`, `vqa`, `integration_order`
- Decision:
  - pin `Vision Fine-tuning on GPT-4o for Visual Question Answering` as the
    first item in the active cookbook integration queue
  - mirror the same priority pin in `CHARTER` and `RUNBOOK` so sequencing
    remains stable across session handoffs
- Why: Aligns cookbook execution order with current OCR/visual-grounding
  priorities and reduces drift from ad-hoc integration sequencing.

## D-111: Add transcript auto-fix/check tooling and end-of-day routine script

- Date: `2026-03-30`
- Category: `workflow_environment`
- Tags: `transcripts`, `format_consistency`, `daily_routine`, `deterministic_checks`
- Decision:
  - add curated transcript tooling:
    - `make transcript-fix` (`tools/fix_transcripts.py`)
    - `make transcript-check` (`tools/validate_transcripts.py`)
  - add one-command day-close routine:
    - `make eod` (`tools/end_of_day_routine.sh`)
  - day-close routine order is deterministic:
    1) transcript-fix
    2) transcript-check
    3) doctor-env
    4) lint-docs
    5) test
- Why: Keeps local transcript records consistently structured without manual
  drift, and standardises day-close validation into one repeatable command.

## D-112: Enforce streamline-first command surfaces with clean-run closure

- Date: `2026-03-30`
- Category: `workflow_environment`
- Tags: `operator_surface`, `command_hygiene`, `validation`, `drift_control`
- Decision:
  - keep one canonical make target per operator action
  - when command surfaces change, remove superseded aliases in the same change
  - avoid patch-layer compatibility additions unless explicitly approved
  - close runtime/tooling surface edits with clean runs:
    - `make doctor-env`
    - `make lint-docs`
    - `make test`
    - `make quality-gate-deterministic` when runtime/eval behaviour changed
- Why: Reduces stale-artifact drift, lowers operator ambiguity, and keeps
  runtime changes auditable through deterministic validation closure.

## D-113: Adopt stricter precision baseline for transcript OCR mining

- Date: `2026-03-31`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `precision_baseline`, `noise_reduction`, `strict_binary`
- Decision:
  - tighten askless handwriting promotion so medium confidence requires
    correction-overlap signal (not OCR framing alone, and not correction text
    that fails OCR anchor overlap)
  - set active transcript OCR baseline to precision-first output:
    `handwriting=14`, `typed=8`, `illustration=7` (`29` total)
  - keep previous `55`-case output as legacy reference for research comparison,
    not as active strict gate input
  - keep benchmark + stability lanes as strict binary gates
- Why: Removes framing-only conversational anchor leakage while preserving
  deterministic benchmark gate quality.

## D-114: Require correction-overlap for askless handwriting promotion

- Date: `2026-03-31`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `precision_baseline`, `anchor_overlap`, `strict_binary`
- Decision:
  - tighten askless handwriting promotion again:
    correction text must overlap transcription anchors (not just exist)
  - set active transcript OCR baseline to:
    `handwriting=10`, `typed=8`, `illustration=7` (`25` total)
  - keep legacy `55` and intermediate `29` outputs as reference-only
  - retain strict benchmark/stability lanes as release gates
- Why: Removes residual non-overlapping correction noise and restores clean
  full-lane diagnostic pass (`25/25`) without relaxing binary quality guards.

## D-115: Lock transcript OCR precision with correction-gated ask anchors and unstable-source quarantine

- Date: `2026-03-31`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `precision_hardening`, `source_quarantine`, `stability`
- Decision:
  - only extract ask-side correction phrases when correction signal is present
    (no unconditional ask-phrase promotion into correction anchors)
  - make handwriting hints token-bounded to avoid substring drift
    (for example `Polinko` no longer matching `ink`)
  - quarantine known unstable transcript sources from the active strict set:
    - `file_00000000b01871fdac46c44584b95d6a-sanitized.png`
    - `file_0000000047f871f7af65c1ce3955cc2e-sanitized.png`
  - set active transcript OCR precision baseline to:
    `handwriting=4`, `typed=11`, `illustration=6` (`21` total)
  - keep `55`/`29`/`25` outputs as legacy/reference only.
- Why: Removes conversational false positives and flaky micro-cases while
  preserving strict binary release gates with deterministic `21/21` stability.

## D-116: Filter low-confidence transcript review rows to OCR-signaled episodes only

- Date: `2026-03-31`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `noise_pruning`, `confidence_gating`, `precision_guard`
- Decision:
  - retain low-confidence rows in transcript miner review output only when OCR
    signal is present:
    `ocr_literal_intent_signal`, `ocr_framing_signal`, `correction_signal`, or
    `correction_overlap_signal`
  - treat explicit negated OCR phrasing as non-framing
    (`no ocr`, `not ocr`, `without ocr`, `no transcription`) so review rows
    are not retained from non-transcription assistant turns
  - keep emitted strict case baseline unchanged at:
    `handwriting=4`, `typed=11`, `illustration=6` (`21` total)
  - update review-noise baseline after rerun to:
    `episodes=172` (`high=7`, `medium=20`, `low=145`)
- Why: Reduces conversational review noise without relaxing strict binary gate
  criteria or changing emitted OCR benchmark cases.

## D-117: Split OCR evaluation into frozen lockset gate and high-fail growth lane

- Date: `2026-04-01`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `novel_case_growth`, `pass_from_fail`, `lockset_gate`
- Decision:
  - keep a frozen OCR lockset as the release gate (`must stay green`)
  - add a novel-growth OCR lane where high fail rates are expected and allowed
  - track pass-from-fail development metrics explicitly:
    `first_pass_fail_rate`, `fail_to_pass_conversion_rate`,
    `median_runs_to_pass`, and `unresolved_fail_age`
  - promote cases from growth lane into lockset only after repeated stable pass
- Why: Pass-only optimisation creates measurement noise; a split gate model
  preserves comparability while using failures as development signal.
- Authorship signal:
  - user hypothesis statement:
    "i think we need to allow for high fail rates. that starts tracking pass
    from fail"

## D-118: Remove backend API-key auth surface from active runtime

- Date: `2026-04-01`
- Category: `runtime_engineering`
- Tags: `auth_simplification`, `surface_reduction`, `tooling_hygiene`
- Decision:
  - remove `POLINKO_SERVER_API_KEY` and `POLINKO_SERVER_API_KEYS_JSON` from
    active config/runtime
  - remove API key enforcement from FastAPI endpoints
  - remove key/header assumptions from eval/client/perf tooling and runbook
- Why: This auth path is unused in the current local-first operating model and
  adds avoidable configuration and maintenance noise.

## D-119: Make OCR-forward split-lane model the primary eval design

- Date: `2026-04-01`
- Category: `eval_quality`
- Tags: `ocr_forward`, `lockset_gate`, `growth_lane`, `pass_from_fail`
- Decision:
  - set OCR as the primary reliability lane for current build phase
  - keep `lockset` as strict release gate (must remain green)
  - keep `growth` as fail-tolerant lane for novel-case expansion and
    pass-from-fail tracking
  - keep lockset and growth reporting distinct to avoid gate noise
  - add local notebook analysis starter as an operator aid:
    `output/jupyter-notebook/ocr-eval-live-filters-starter.ipynb`
- Why: This preserves deterministic release quality while still extracting
  useful learning signal from high-fail exploratory OCR cases.

## D-120: Operationalise growth-lane pass-from-fail metrics with a dedicated report surface

- Date: `2026-04-01`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `growth_lane`, `pass_from_fail`, `operator_surface`
- Decision:
  - add executable growth metrics tool:
    - `tools/eval_ocr_growth_metrics.py`
  - add canonical growth command + short alias:
    - `make eval-ocr-transcript-growth`
    - `make ocrgrowth`
  - write local growth reports to:
    - `.local/eval_reports/ocr_growth_metrics.json`
    - `.local/eval_reports/ocr_growth_metrics.md`
  - compute the D-117 metric set directly from run history:
    - `first_pass_fail_rate`
    - `fail_to_pass_conversion_rate`
    - `median_runs_to_pass`
    - `unresolved_fail_age`
- Why: Growth-lane metrics were policy-only; this makes them executable and
  reviewable without manual report forensics.

## D-121: Widen OCR growth lane with separate runnable case set and stability track

- Date: `2026-04-01`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `growth_lane`, `dataset_widening`, `pass_from_fail`
- Decision:
  - extend transcript miner output with a dedicated growth case set:
    - `.local/eval_cases/ocr_transcript_cases_growth.json`
  - keep lockset emission criteria unchanged; growth widening only affects the
    fail-tolerant lane
  - add growth-lane execution targets:
    - `make eval-ocr-transcript-cases-growth` (`make ocrwiden`)
    - `make eval-ocr-transcript-stability-growth` (`make ocrstablegrowth`)
  - route growth metrics to growth stability run history only
- Why: We need broader novel-case exposure for pass-from-fail signal while
  keeping release gate strict and stable.

## D-122: Materialise stable growth FAIL cohort as a first-class remediation input

- Date: `2026-04-01`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `growth_lane`, `fail_cohort`, `remediation_kernel`
- Decision:
  - add executable fail-cohort builder:
    - `tools/build_ocr_growth_fail_cohort.py`
  - add canonical command + short alias:
    - `make eval-ocr-growth-fail-cohort`
    - `make ocrfails`
  - emit cohort artefacts to local surfaces:
    - `.local/eval_cases/ocr_growth_fail_cohort.json`
    - `.local/eval_reports/ocr_growth_fail_cohort.md`
  - treat this cohort as the next-kernel input for precision-safe OCR hardening
    while keeping lockset gate unchanged
- Why: Growth widening increases failure signal volume; a deterministic fail
  cohort keeps remediation focused, reproducible, and separate from release
  gating.

## D-123: Add transient request retries to retrieval eval harness and quality gate path

- Date: `2026-04-01`
- Category: `eval_quality`
- Tags: `retrieval_eval`, `rate_limit_hardening`, `quality_gate`
- Decision:
  - add transient retry controls to `tools/eval_retrieval.py`:
    - `--request-retries`
    - `--request-retry-delay-ms`
  - retry on connection errors and transient HTTP statuses (`429`, `5xx`)
  - wire retry controls into `make eval-retrieval`,
    `make eval-retrieval-report`, and `make quality-gate`
  - add dedicated unit coverage for retry behaviour and parser defaults
- Why: Deterministic quality runs were producing avoidable false-red failures
  under short-lived API pressure; bounded retries reduce operational noise
  without relaxing case-level pass/fail logic.

## D-124: Add OCR fail-fast guard for sustained rate-limit streaks

- Date: `2026-04-01`
- Category: `eval_quality`
- Tags: `ocr_eval`, `rate_limit_hardening`, `operator_hygiene`
- Decision:
  - add `--max-consecutive-rate-limit-errors` to `tools/eval_ocr.py`
  - if enabled (`>0`), abort long OCR runs early when sustained `429` streaks
    occur
  - pass this control through `tools/eval_ocr_stability.py` so stability
    sequences inherit the same fail-fast behaviour
  - expose make-level knob:
    - `OCR_MAX_CONSEC_RATE_LIMIT_ERRORS` (default `3`)
  - keep summary/report compatibility while adding attempted/abort metadata
- Why: sustained provider-side `429` streaks consume runtime and quota without
  producing new signal; fail-fast behaviour preserves strict binary semantics
  while improving operator efficiency.

## D-125: Propagate OCR retry knobs to all eval make targets

- Date: `2026-04-01`
- Category: `eval_quality`
- Tags: `ocr_eval`, `retry_hardening`, `make_surface`
- Decision:
  - add make-level OCR eval retry controls:
    - `OCR_EVAL_OCR_RETRIES` (default `2`)
    - `OCR_EVAL_OCR_RETRY_DELAY_MS` (default `750`)
  - wire both controls into every `tools.eval_ocr` make target:
    - base OCR eval/report targets
    - handwriting eval targets
    - transcript lockset/growth single-run targets
    - quality-gate OCR step
  - keep strict binary pass/fail semantics unchanged; retries only absorb
    transient transport/provider pressure.
- Why: lockset and growth single-run commands were previously missing retry
  controls, causing avoidable red runs under short-lived `429` pressure.

## D-126: Constrain growth fail cohort to OCR-framed transcript episodes

- Date: `2026-04-01`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `growth_lane`, `fail_cohort`, `framing_gate`
- Decision:
  - extend `tools/build_ocr_growth_fail_cohort.py` with transcript-review
    linkage by `image_path`
  - add review-aware cohort controls:
    - `--review` (defaults to
      `.local/eval_cases/ocr_transcript_cases_review.json`)
    - `--require-ocr-framing`
  - enforce framing gate in canonical fail-cohort command surface:
    - `make eval-ocr-growth-fail-cohort`
    - `make ocrfails`
  - include cohort diagnostics for operator clarity:
    - `require_ocr_framing`
    - `skipped_non_framed`
    - per-case `framing_episode_count`
- Why: growth fail cohorts should remain OCR-specific remediation inputs. This
  avoids pulling non-framed/noisy failures into the hard-fail set while
  preserving strict binary gate semantics.

## D-127: Protect growth fail cohort from stale case-map joins

- Date: `2026-04-01`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `growth_lane`, `fail_cohort`, `stale_join_guard`
- Decision:
  - load canonical per-case metadata from stability run reports
    (`report_json`) when building fail cohorts
  - if growth case-map `image_path` for a case id does not match run-report
    `image_path`, skip that row and increment `skipped_case_map_mismatch`
  - add cohort diagnostics:
    - summary: `skipped_case_map_mismatch`
    - per-case: `run_must_contain_any`, `run_must_appear_in_order`
  - add lane fallback from linked review rows when growth lane is unknown
- Why: growth case ids can be regenerated while preserving id shape, which can
  silently misjoin stability history to new case definitions. The stale-join
  guard keeps fail cohorts trustworthy for remediation decisions.

## D-128: Stop stability replay after first sustained rate-limit abort

- Date: `2026-04-01`
- Category: `eval_runtime`
- Tags: `ocr_transcripts`, `stability`, `rate_limit`, `operator_efficiency`
- Decision:
  - add `--stop-on-rate-limit-abort` to `tools/eval_ocr_stability.py`
  - when enabled, stop remaining runs after first child report with
    `summary.aborted_due_to_rate_limit=true`
  - expose effective run window in stability output:
    - `runs_executed`
    - `runs_expected_for_stability`
  - enable this guard for all Makefile `eval_ocr_stability` entrypoints
- Why: under hard OCR `429` windows, replaying all requested runs produces no
  new signal and burns budget. Early stop preserves strict gates while reducing
  wasted retries and time-to-recovery.

## D-129: Keep `make ocr-data` offline-only

- Date: `2026-04-01`
- Category: `eval_ops`
- Tags: `ocr_transcripts`, `operator_surface`, `offline_workflow`
- Decision:
  - redefine `make ocr-data` to run offline data steps only:
    - `doctor-env`
    - `ocrmine`
    - `ocrdelta`
  - keep full online OCR replay path under
    `make ocr-notebook-workflow`
- Why: operators use `make ocr-data` for local dataset refresh and notebook prep.
  Mixing in live OCR eval/stability made the target fail under 429 windows and
  broke the expected offline workflow contract.

## D-130: Route high-signal unstable sources to growth lane only

- Date: `2026-04-02`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `growth_lane`, `source_quarantine`
- Decision:
  - keep `UNSTABLE_SOURCE_NAMES` excluded from strict transcript case set
  - allow unstable rows into growth lane only when signal is strong:
    - confidence is `medium` or `high`
    - at least 4 anchor terms
    - non-empty transcription phrases
    - OCR framing or correction signal present
  - mark such growth cases as `source_quarantine=true`
  - emit summary metric: `growth_quarantine_cases_written`
  - add OCR intent synonym support for `squibbles and bibbles`
- Why: unstable crops are too noisy for strict gating but still high-value for
  fail-heavy growth tracking. Growth-only quarantine preserves strict quality
  while increasing useful exposure for pattern discovery.

## D-131: Allow regex-only constraints in growth lane when anchors are empty

- Date: `2026-04-02`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `growth_lane`, `regex_constraints`, `fail_exposure`
- Decision:
  - when growth-lane candidates have no usable anchor/order terms, allow
    `must_match_regex` constraints derived from OCR transcription phrases
  - keep strict transcript set unchanged: regex-only routing applies to growth
    lane only
  - emit summary metric: `growth_regex_only_cases_written`
- Why: many low-confidence transcript rows still contain OCR-like phrase
  structure but collapse to zero anchor tokens after stopword/meta filtering.
  Regex-only growth constraints widen fail-heavy exposure without weakening
  strict gate semantics.

## D-132: Honor `Retry-After` in OCR eval retries

- Date: `2026-04-02`
- Category: `eval_runtime`
- Tags: `ocr`, `rate_limit`, `retry_after`, `operator_efficiency`
- Decision:
  - OCR eval request failures now preserve HTTP metadata via `OcrRequestError`
  - when retrying transient OCR failures, `HTTP 429` waits now honor
    `Retry-After` (if present) and use the max of:
    - configured `OCR_EVAL_OCR_RETRY_DELAY_MS`
    - header-derived wait seconds
- Why: fixed short retry delays under provider throttling burn attempts too
  quickly. Respecting `Retry-After` reduces wasted retry churn while preserving
  strict PASS/FAIL behavior.

## D-133: Enforce deterministic day-close background task shutdown

- Date: `2026-04-02`
- Category: `runtime_ops`
- Tags: `eod`, `task_hygiene`, `server`, `caffeinate`
- Decision:
  - extend `make eod` to include explicit shutdown step (`make eod-stop`) after
    validation checks
  - add `make eod-stop` to stop runtime background processes:
    - `make server-daemon-stop`
    - `make caffeinate-off-all`
  - add `make caffeinate-off-all` to stop both managed and matching unmanaged
    `caffeinate -d -i -m` processes
- Why: closing editor/app windows does not guarantee `caffeinate` or daemon
  processes exit. Deterministic shutdown prevents stale keep-awake and runtime
  task drift between days.

## D-134: Separate rate-limit blocked cases from fail cohort decisions

- Date: `2026-04-02`
- Category: `eval_observability`
- Tags: `ocr`, `growth_lane`, `rate_limit`, `cohort_quality`
- Decision:
  - `tools/build_ocr_growth_fail_cohort.py` now emits explicit rate-limit
    blocked case surfaces:
    - `summary.rate_limited_cases`
    - `summary.rate_limit_abort_runs`
    - `rate_limited_cases[]` list (ERROR-only, no PASS/FAIL decision yet)
  - fail cohort selection semantics remain unchanged:
    - only persistent FAIL decision cases enter `cases[]`
  - run report path resolution now checks repo-root-relative paths first to
    avoid stale joins when stability JSON stores `.local/...` report paths
- Why: under sustained OCR `429`, growth metrics can show zero selected fails
  while still being fully blocked. Explicit blocked-case telemetry keeps
  decision quality separate from decision availability and reduces false
  confidence during provider-pressure windows.

## D-135: Auto-start runtime daemon for direct OCR case eval commands

- Date: `2026-04-02`
- Category: `runtime_ops`
- Tags: `ocr`, `makefile`, `operator_hygiene`, `preflight`
- Decision:
  - direct OCR case eval targets now self-start `server-daemon` before running
    `tools.eval_ocr`:
    - `eval-ocr-transcript-cases`
    - `eval-ocr-transcript-cases-growth`
    - `eval-ocr-transcript-cases-handwriting`
    - `eval-ocr-transcript-cases-handwriting-benchmark`
    - `eval-ocr-transcript-cases-typed`
    - `eval-ocr-transcript-cases-typed-benchmark`
    - `eval-ocr-transcript-cases-illustration`
    - `eval-ocr-transcript-cases-illustration-benchmark`
  - semantics stay unchanged:
    - strict/growth gating logic is unchanged
    - `429`/retry/fail-fast behaviour is unchanged
- Why: operator runs should fail on OCR signal quality, not on avoidable local
  daemon preflight drift (`connection refused`).

## D-136: Record broad OCR-intent mining cue expansion

- Date: `2026-04-02`
- Category: `eval_quality`
- Tags: `ocr_transcripts`, `intent_mining`, `signal_coverage`, `precision_safe`
- Decision:
  - transcript miner OCR-intent pattern includes broad cue terms used in
    real session language:
    - `new drop`
    - `binareyes`
    - `scribbles and bibbles` / `squibbles and bibbles`
    - `peanut cursive`
    - `scratched out`
  - compact numeric entry markers are treated as valid OCR phrase content
    end-to-end:
    - preserved during framed/code-block transcription phrase extraction
    - used as valid tokens for anchor/ordered-term extraction
    - 24-hour compact time tokens (`HHMM`)
    - compact date-like tokens with year suffix (`...24`, `...25`, `...26`)
  - strict binary gate semantics are unchanged; this is mining-signal widening,
    not gate relaxation.
- Why: these cues are high-value, user-authored intent markers observed in the
  transcript corpus. Capturing them improves episode discovery and fail-from-pass
  learning surfaces without loosening release criteria.

## D-137: Add OCR eval pacing and post-429 cooldown controls

- Date: `2026-04-02`
- Category: `eval_runtime`
- Tags: `ocr`, `rate_limit`, `stability`, `operator_control`
- Decision:
  - add two explicit controls to `tools/eval_ocr.py`:
    - `--case-delay-ms`
    - `--rate-limit-cooldown-ms`
  - when a case errors with OCR rate-limit semantics (`HTTP 429`), apply
    cooldown as the max of:
    - configured `rate_limit_cooldown_ms`
    - header-derived `Retry-After` wait
  - plumb both controls through `tools/eval_ocr_stability.py` and Makefile
    stability targets (strict + growth + benchmark lanes).
- Why: retry-only handling is insufficient under sustained throttling.
  Explicit pacing/cooldown reduces abort churn and preserves deterministic
  binary gate behavior without relaxing PASS/FAIL criteria.

## D-138: Enrich OCR transcript review rows for analyst-facing queryability

- Date: `2026-04-02`
- Category: `eval_observability`
- Tags: `ocr_transcripts`, `review_rows`, `data_quality`, `db_viewer`
- Decision:
  - mined review episodes now include:
    - `query_text` (alias of ask text for direct filtering)
    - `expected_text` (preview from mined transcription phrases)
    - `skip_reason` (normalized reason when not emitted)
  - existing `emit_status`/confidence/lane semantics are unchanged.
- Why: analyst tools (DB Viewer/Data Wrangler) need high-signal columns for
  filtering and cohort inspection. These fields reduce manual reconstruction
  while keeping mining and gate logic stable.

## D-139: Surface fail-history cohort alongside persistent fails

- Date: `2026-04-02`
- Category: `eval_observability`
- Tags: `ocr_growth`, `fail_history`, `cohorting`, `rate_limit_resilience`
- Decision:
  - `tools/build_ocr_growth_fail_cohort.py` now emits two distinct cohorts:
    - `cases`: persistent fail cohort (existing strict semantics)
    - `fail_history_cases`: mixed-outcome cohort with at least one `FAIL` and
      one `PASS`
  - fail-history rows include conversion-state context:
    - `fail_to_pass_converted`
    - `first_status`
    - `latest_status`
  - summary now includes:
    - `fail_history_cases`
    - `fail_to_pass_cases`
    - `fail_history_lane_counts`
  - `make ocrfails` defaults are tuned for early-run visibility:
    - `OCR_FAIL_COHORT_MIN_RUNS=1`
    - `OCR_FAIL_COHORT_INCLUDE_UNSTABLE=true`
    - `OCR_FAIL_COHORT_REQUIRE_OCR_FRAMING=true`
- Why: strict persistent-fail selection can be empty during rate-limit-heavy
  or early growth runs. A separate fail-history surface preserves binary gate
  integrity while exposing high-value fail signals and conversion patterns for
  analyst review.

## D-140: Add focused fail-replay lane from growth cohorts

- Date: `2026-04-02`
- Category: `eval_runtime`
- Tags: `ocr_growth`, `remediation`, `subset_replay`, `operator_speed`
- Decision:
  - add `tools/build_ocr_focus_cases.py` to materialise a replay subset from:
    - persistent fail cohort (`cases`)
    - optional fail-history cohort (`fail_history_cases`)
  - add Make targets:
    - `make ocrfocuscases` -> build focused case set
    - `make eval-ocr-focus-stability` -> run stability on focused set only
    - `make ocrfocus` -> chain `ocrgrowth` + `ocrfails` + focused replay
  - focused lane defaults are paced and bounded for fail-first iteration:
    - `OCR_FOCUS_MAX_CASES=40`
    - `OCR_FOCUS_RUNS=1`
    - `OCR_FOCUS_CASE_DELAY_MS=1200`
    - `OCR_FOCUS_RATE_LIMIT_COOLDOWN_MS=12000`
    - `OCR_FOCUS_INCLUDE_FAIL_HISTORY=true`
- Why: full growth replays are expensive during provider throttling. A focused
  fail-derived subset gives faster remediation feedback while preserving binary
  gate semantics and existing lockset release rules.

## D-141: Add read-only runtime NULL audit command

- Date: `2026-04-02`
- Category: `eval_observability`
- Tags: `runtime_db`, `null_audit`, `operator_clarity`, `read_only`
- Decision:
  - add `tools/audit_runtime_nulls.py` and `make nulls` to report high-signal
    null surfaces in active runtime DBs:
    - `history.db` / `ocr_runs` (`source_message_id`, `result_message_id`)
    - `vector.db` / `message_vectors` (`message_id`, especially non-chat rows)
  - emit both machine and human outputs:
    - `.local/eval_reports/runtime_null_audit.json`
    - `.local/eval_reports/runtime_null_audit.md`
  - treat this as read-only observability (no DB lifecycle mutation commands).
- Why: repeated confusion around null-link columns is an observability gap.
  A deterministic audit surface clarifies expected nulls vs stale-link drift
  without reintroducing runtime DB lifecycle complexity.

## D-142: Add rate-limit backoff skip guard for focused replay

- Date: `2026-04-02`
- Category: `eval_runtime`
- Tags: `ocr_focus`, `rate_limit`, `backoff`, `call_budget`
- Decision:
  - add `tools/should_skip_ocr_run.py` as a deterministic preflight guard.
  - `make eval-ocr-focus-stability` now checks recent focus output:
    - if prior run aborted due to rate limits and is within
      `OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS`, skip replay.
  - control knobs:
    - `OCR_FOCUS_SKIP_RECENT_RATE_LIMIT=true|false`
    - `OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS=<seconds>`
- Why: repeated immediate replays under known provider throttle waste call
  budget and produce no new signal. Backoff skip preserves binary criteria
  while improving runtime efficiency.

## D-143: Stream OCR growth/stability command output in real time

- Date: `2026-04-02`
- Category: `eval_runtime`
- Tags: `ocr`, `operator_observability`, `run_feedback`, `growth_lane`
- Decision:
  - run growth/focus OCR replay commands with `PYTHONUNBUFFERED=1` in Makefile:
    - `eval-ocr-transcript-cases-growth`
    - `eval-ocr-transcript-cases-growth-batched`
    - `eval-ocr-transcript-stability-growth`
    - `eval-ocr-focus-stability`
  - no gate semantics, retries, or PASS/FAIL criteria were changed.
- Why: long OCR growth runs were operationally opaque during provider latency,
  which looked like hangs. Real-time stdout restores deterministic operator
  visibility without behavioural drift.

## D-144: Tighten growth-case miner to exclude metadata-framed low-confidence noise

- Date: `2026-04-02`
- Category: `eval_data`
- Tags: `ocr_growth`, `signal_quality`, `miner`, `precision`
- Decision:
  - expand miner token filtering in `tools/build_ocr_cases_from_export.py` to
    drop metadata-style anchor/order terms (for example: `page`, `partial`,
    `cropped`, `continuation`, `previous`, `updated`, `entry`, `more`).
  - tighten low-confidence growth inclusion rule:
    - include only when one of:
      - literal OCR intent signal
      - correction signal
      - OCR framing **and** OCR intent signal
    - OCR-framed-only rows without intent/correction are excluded from growth.
  - update miner regression tests in
    `tests/test_build_ocr_cases_from_export.py` to lock:
    - metadata token exclusion
    - stricter low-confidence growth gating
    - correction-led askless handwriting growth inclusion
- Why: growth lane had accumulated metadata-chatter rows that produced
  low-value failures unrelated to OCR capability. Tightening miner admission
  preserves fail-heavy evaluation while increasing diagnostic precision.

## D-145: Prune residual export-metadata tokens from growth anchors

- Date: `2026-04-02`
- Category: `eval_data`
- Tags: `ocr_growth`, `anchor_filtering`, `signal_quality`, `precision`
- Decision:
  - extend metadata token filtering in
    `tools/build_ocr_cases_from_export.py` to also exclude:
    `conversation`, `found`, `screenshot`, `html`.
  - extend miner regression coverage in
    `tests/test_build_ocr_cases_from_export.py` to lock those exclusions.
  - rerun growth alignment sequence after remine:
    - `make ocrstablegrowth`
    - `make ocrgrowth`
    - `make ocrfails`
  - refreshed aligned baseline:
    - growth stability: `29/39` pass, `10/39` fail, `0` errors
    - fail cohort (`require_ocr_framing=true`): `5` selected fail cases
- Why: residual export-descriptor tokens were still leaking into growth
  constraints and inflating low-value failure reasons. Pruning them preserves
  strict fail visibility while improving cohort diagnostic signal.

## D-146: Filter weak conversational anchor tokens from growth constraints

- Date: `2026-04-02`
- Category: `eval_data`
- Tags: `ocr_growth`, `anchor_terms`, `signal_quality`, `precision`
- Decision:
  - treat `chat` and `find` as weak anchor/order tokens in
    `tools/build_ocr_cases_from_export.py`.
  - extend miner unit coverage to ensure weak-token-only phrases are filtered.
  - rerun growth alignment sequence after remine:
    - `make ocrstablegrowth`
    - `make ocrgrowth`
    - `make ocrfails`
  - refreshed aligned baseline:
    - growth stability: `30/39` pass, `9/39` fail, `0` errors
    - fail cohort (`require_ocr_framing=true`): `4` selected fail cases
- Why: conversational tokens were producing low-value fail reasons unrelated to
  OCR difficulty. Filtering them keeps the growth lane fail-tolerant while
  increasing diagnostic utility of each failure.

## D-147: Drop UI error phrases from regex-only growth constraints

- Date: `2026-04-02`
- Category: `eval_data`
- Tags: `ocr_growth`, `regex_filter`, `signal_quality`, `precision`
- Decision:
  - suppress UI error phrases from regex pattern emission in
    `tools/build_ocr_cases_from_export.py`, specifically:
    - `conversation not found`
    - `chat html`
  - add miner regression tests in
    `tests/test_build_ocr_cases_from_export.py` for both phrases.
  - rerun growth alignment sequence after remine:
    - `make ocrmine`
    - `make ocrstablegrowth`
    - `make ocrgrowth`
    - `make ocrfails`
- Why: regex-only UI error rows were entering growth and consuming fail budget
  without improving OCR remediation signal.

## D-148: Skip UI-leading ordered tokens in growth fallback sequences

- Date: `2026-04-02`
- Category: `eval_data`
- Tags: `ocr_growth`, `ordered_terms`, `signal_quality`, `precision`
- Decision:
  - add `restore` and `deleted` to ordered-term fallback skip words in
    `tools/build_ocr_cases_from_export.py`.
  - keep anchor terms unchanged; this only removes brittle leading order
    constraints for UI-like phrase prefixes.
  - extend miner regression coverage in
    `tests/test_build_ocr_cases_from_export.py`.
  - rerun growth alignment sequence after remine:
    - `make ocrmine`
    - `make ocrstablegrowth`
    - `make ocrgrowth`
    - `make ocrfails`
- Why: UI-leading ordered constraints were causing false hard-fails in growth
  despite sufficient OCR signal in anchor terms.

## D-149: Require explicit OCR intent for low-confidence growth admission

- Date: `2026-04-02`
- Category: `eval_data`
- Tags: `ocr_growth`, `low_confidence`, `intent_gate`, `signal_quality`
- Decision:
  - tighten low-confidence growth admission in
    `tools/build_ocr_cases_from_export.py`:
    - include when one of:
      - literal OCR intent signal
      - askless handwriting overlap signal
      - OCR intent signal with correction/framing signal
    - exclude correction/framing-only rows without OCR intent.
  - add regression test to lock correction-without-intent exclusion in
    `tests/test_build_ocr_cases_from_export.py`.
  - rerun growth alignment sequence after remine:
    - `make ocrmine`
    - `make ocrstablegrowth`
    - `make ocrgrowth`
    - `make ocrfails`
    - `make ocrfocus`
  - refreshed aligned baseline:
    - growth cases: `28`
    - latest stability replay: `24/28` pass, `4/28` fail, `0` errors
    - fail cohort selection (`require_ocr_framing=true`): `0` selected cases
    - framed selection skips recorded: `skipped_non_framed=4`
- Why: non-OCR concept dialogue with incidental correction phrasing was
  contaminating growth with low-value fails. Intent-gating preserves
  fail-heavy evaluation while keeping the cohort remediation-focused.

## D-150: Rename transcript miner confidence schema to signal_strength

- Date: `2026-04-02`
- Category: `eval_data`
- Tags: `ocr_growth`, `schema`, `naming`, `signal_quality`
- Decision:
  - rename OCR transcript miner review/result schema keys:
    - per-episode field: `confidence` -> `signal_strength`
    - summary field: `confidence_counts` -> `signal_strength_counts`
    - CLI counters: `high_signal_strength`, `medium_signal_strength`,
      `low_signal_strength`
  - keep emit-status semantics unchanged (`skipped_low_confidence` remains as
    the status identifier for low-signal rows)
  - maintain backward-compatible readers in downstream tools:
    - `tools/report_ocr_case_mining_delta.py`
    - `tools/build_handwriting_benchmark_cases.py`
    - both now read `signal_strength` first, then legacy `confidence`
- Why: in this fail-tolerant OCR expansion phase, `signal_strength` is the
  correct semantic label for mining quality, while preserving status and reader
  compatibility avoids behavioural drift.

## D-151: Tighten illustration admission and drop brittle ordered constraints in growth lane

- Date: `2026-04-03`
- Category: `eval_data`
- Tags: `ocr_growth`, `signal_quality`, `constraint_hardening`, `stability`
- Decision:
  - tighten medium-signal illustration admission in
    `tools/build_ocr_cases_from_export.py`:
    - illustration rows now require anchor evidence plus at least one stronger
      OCR signal (`ocr_literal_intent_signal`, `correction_signal`,
      `correction_overlap_signal`, or `ocr_framing_signal`)
  - keep growth ordered constraints only for highest-signal rows:
    - clear `must_appear_in_order` for medium/low signal rows
    - clear `must_appear_in_order` for quarantined unstable-source rows
  - rerun alignment sequence:
    - `make ocrmine`
    - `make ocrstablegrowth`
    - `make ocrgrowth`
    - `make ocrfails`
    - `OCR_FAIL_COHORT_REQUIRE_OCR_FRAMING=false make ocrfails`
  - refreshed aligned baseline:
    - growth cases: `22`
    - growth stability: `21/22` pass, `1/22` fail, `0` errors
    - fail cohort (`require_ocr_framing=true`): `selected_fail_cases=0`
      with `skipped_non_framed=6`
    - diagnostic unframed cohort: `selected_fail_cases=1`
- Why: medium/quarantine ordered constraints were producing deterministic
  false-hard failures that did not add remediation value. This keeps growth
  fail-tolerant while preserving one meaningful residual fail signal.

## D-152: Remove residual growth false-fail idiom and stabilise no-memory response gating

- Date: `2026-04-03`
- Category: `eval_data`
- Tags: `ocr_growth`, `response_behaviour`, `determinism`, `quality_gate`
- Decision:
  - exclude idiomatic phrase `read it and weep` from OCR intent mining in
    `tools/build_ocr_cases_from_export.py` by tightening the `read it/this`
    regex branch.
  - add miner regression coverage in
    `tests/test_build_ocr_cases_from_export.py`:
    - `test_ask_regex_does_not_match_read_it_and_weep_idiom`
  - expand deterministic response-behaviour case phrase coverage in
    `docs/eval/cases/response_behaviour_eval_cases.json` for
    `no_memory_pretend_claim` to include explicit inability variants beyond
    `don't/do not have` (retain/store/remember forms).
  - rerun aligned validation + growth chain:
    - `make quality-gate-deterministic`
    - `CGPT_EXPORT_ROOT=/Users/tryskian/Library/CloudStorage/Dropbox/CGPT-DATA-EXPORT make ocrmine`
    - `make ocrstablegrowth`
    - `make ocrgrowth`
    - `make ocrfails`
    - `OCR_FAIL_COHORT_REQUIRE_OCR_FRAMING=false make ocrfails`
  - refreshed aligned baseline:
    - growth cases: `21`
    - growth stability: `21/21` pass, `0/21` fail, `0` errors
    - fail cohort (`require_ocr_framing=true`): `selected_fail_cases=0`
    - diagnostic unframed cohort: `selected_fail_cases=0`
- Why: the residual growth fail came from a non-OCR idiom being mined as OCR
  intent, and response-behaviour determinism was penalising valid explicit
  non-memory refusals that used retain/store/remember phrasing.

## D-153: Add OCR-to-safety bridge eval lane as deterministic non-gating diagnostic

- Date: `2026-04-02`
- Category: `eval_data`
- Tags: `ocr_safety`, `bridge_lane`, `determinism`, `diagnostic`
- Decision:
  - add dedicated OCR safety bridge case file:
    - `docs/eval/cases/ocr_safety_eval_cases.json`
  - add canonical commands:
    - `make eval-ocr-safety`
    - `make eval-ocr-safety-report`
  - extend deterministic response-behaviour harness with `--suite-id` so
    report/trace metadata remains lane-specific when sharing one evaluator.
  - include OCR safety report generation in `make eval-reports`.
  - keep this lane explicitly non-release-gating in current phase.
- Why: we need a measurable transfer check from OCR calibration into
  uncertainty/safety response behaviour without destabilising the strict
  release gate.
