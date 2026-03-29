<!-- @format -->

# Project State

## Current Status

- Prompt/runtime is intentionally minimal and aligned with the original `try.py` behaviour.
- CLI agent loop works with persistent SQLite memory (`.local/runtime_dbs/active/memory.db`) and
  `/reset`.
- Backend API is running with:
  - `GET /health`
  - `GET /metrics`
  - `POST /chat`
  - `POST /session/reset`
  - `POST /skills/ocr`
  - `POST /skills/file_search`
  - `GET /chats/{session_id}/export`
  - `GET /chats/{session_id}/collaboration`
  - `POST /chats/{session_id}/collaboration/handoff`
- API includes:
  - startup config validation
  - optional API key auth (single key or key ring principals)
  - structured request/chat logs
  - in-process request metrics (`requests_total`, status counts, latency buckets, 429 count)
  - rate limiting + `Retry-After` on 429
  - periodic stale bucket cleanup in the in-memory limiter
  - per-chat personalization memory scope (`session` vs `global`)
  - `/chat` retrieval citations via `memory_used` when vector memory contributes context
  - deterministic harness override for smoke tests:
    `harness_mode=fixture` (+ optional `fixture_output`)
  - env-level harness default:
    `POLINKO_CHAT_HARNESS_DEFAULT_MODE=live|fixture`
  - canonical UI eval adapter contract:
    `docs/eval/UI_EVAL_ADAPTER_CONTRACT.md`
- Legacy frontend implementation remains archived in
  `.archive/live_archive/legacy_frontend/`.
- OpenAI developer docs MCP server is now configured for Codex/VS Code usage:
  - endpoint: `https://developers.openai.com/mcp`
  - workspace wiring: `.vscode/mcp.json`
- Figma/UI parity work is deprecated for current cycle; execution focus is backend retrieval, OCR, and file-search reliability.
- Quality gate is implemented and passing locally via `make quality-gate`:
  - unit tests
  - retrieval eval (`12/12`)
  - file-search eval (`5/5`, including image-context smoke)
  - OCR eval strict (`6/6`)
  - style eval strict (`6/6`)
  - hallucination eval strict (`6/6`)
- Latest local report baseline (March 6, 2026) is green:
  - `make eval-ocr-report` PASS
  - `make eval-file-search-report` PASS
  - `make eval-style-report` PASS
  - `make eval-hallucination-report` PASS
  - `make eval-retrieval-report` PASS
- Latest focused validation cycle (March 15, 2026) is green:
  - strict style eval: `style-strict-20260315-180637.json` (`11/11` PASS)
  - file-search report: `file-search-20260315-181109.json` (`5/5` PASS)
  - CLIP A/B report: `clip-ab-20260315-180942.json` (`delta=+1.000`)
  - CLIP readiness: `GO` on latest pair
    (`clip-ab-20260315-143219.json`, `clip-ab-20260315-180942.json`)
  - runtime regression signal: `make test` (`154` tests PASS)
- Status checkpoint (March 17, 2026):
  - project is in late build-hardening phase (not early scaffold phase)
  - core runtime + binary eval flow are stable and merged on `main`
  - remaining work is concentrated in backlog triage, eval UX hardening, and
    final portfolio evidence packaging
- Binary eval policy checkpoint (March 21, 2026):
  - gate logic remains strict `PASS`/`FAIL` for deterministic release decisions
  - `em_dash_style` is currently a hard-fail signal to set the style baseline
  - human nuance stays in notes/transcripts for diagnosis, not gate computation
- Rubric simplification checkpoint (March 22, 2026):
  - active UI rubric is now two explicit dimensions:
    `style` and `hallucination_risk` (each `pass`/`fail`)
  - optional style penalties are split:
    - `default_style` = soft penalty
    - `em_dash_style` = hard penalty
  - response status remains stream-based (`pass: ...`, `fail: ...`,
    `penalty: ...`) so nuanced signals persist without collapsing into one label
  - operator gate remains binary: any hard fail signal is treated as a fail for
    that response
- Eval stream checkpoint (March 21, 2026):
  - feedback save supports simultaneous positive and negative rubric streams on
    one response
  - UI status line now renders separate streams (`pass: ...` and `fail: ...`)
    instead of forcing a single top-level label
  - checkpoint rollups now count `pass_count` and `fail_count` independently;
    `non_binary_count` is expected to remain `0` and is treated as an integrity signal
  - checkpoint API responses now expose explicit fail-closed `gate_outcome`
    (`pass`/`fail`) derived from checkpoint counts
  - API/tests were updated together to avoid state drift between rubric
    semantics and saved checkpoint payloads
- Binary contract hard-cut checkpoint (March 26, 2026):
  - feedback outcomes are strict `pass`/`fail` at API and storage boundaries
  - legacy `tags`-only feedback payload compatibility is removed
  - checkpoint responses use `non_binary_count` (no active `other_count` label)
  - no migration helper is part of active workflow; data outside contract is a repair task
- Post-merge eval + reference checkpoint (March 25, 2026):
  - PR `#71` merged to `main` (`a60bf15`) with backend/API/test sync
  - checkpoint and feedback APIs preserve binary gate behaviour
  - document-link relationship indexing model was established for reference flow
- Docs hygiene checkpoint (March 21, 2026):
  - deprecated pilot/comms docs are archive-only and removed from active
    runbook/state/handoff references
  - archived docs are hidden from explorer/search to reduce active-workflow
    clutter
  - `docs/peanut/refs/PEANUT_TOOLING_REF.md` remains visible for day-to-day
    operator use
- Git-native retention checkpoint (March 27, 2026):
  - archive-folder workflow removed from active operations
    (`make eval-reset-baseline` removed)
  - eval trace default output moved to
    `eval_reports/eval_trace_artifacts.jsonl`
  - tracked-state retention is now explicitly Git-native
    (no additional archive folder layer required)
- Live archive checkpoint (March 27, 2026):
  - added tracked live archive lane: `.archive/live_archive/`
  - lane split is explicit:
    - `.archive/live_archive/legacy_eval/`
    - `.archive/live_archive/legacy_frontend/`
    - `.archive/live_archive/legacy_human_reference/`
  - archive lane is reference-only and non-authoritative for active runtime
    gate decisions
- Docs straggler cleanup checkpoint (March 28, 2026):
  - deprecated top-level coordination docs moved into:
    - `.archive/live_archive/legacy_coordination/`
  - active top-level docs now stay focused on current runtime/eval operations
    and research workflow
- Eval docs canonical naming checkpoint (March 27, 2026):
  - renamed `docs/EVAL_V2_SPEC.md` -> `docs/eval/EVAL_SPEC.md`
  - renamed `docs/EVAL_V2_BACKEND_MAP.md` -> `docs/eval/EVAL_BACKEND_MAP.md`
  - binary policy semantics are documented in
    `docs/eval/BINARY_EVAL_LOGIC_REFINEMENT.md`
- EOD docs confidentiality merge checkpoint (March 25, 2026):
  - PR `#72` merged to `main` (`2a6f575`)
  - runbook + ignore policy now treats non-build internal docs as local-only
    by default
  - session handoff is aligned to the merged cleanup baseline for next-day
    startup
- Branch protection checkpoint (March 25, 2026):
  - `main` remains protected (PR + required checks)
  - active implementation now runs through task branches merged back to `main`
  - no special-purpose `eval-rubric` branch/ruleset is active
- Safety certainty checkpoint (March 21, 2026):
  - captured transcript + peanut-reference framing in
    `docs/peanut/transcripts/safety_certainty_and_inference_notes_2026-03-21.md`
    (unsupported certainty = fail; uncertainty + grounded recovery = pass)
- Reasoning Loops diagnostic checkpoint (March 22, 2026):
  - captured transcript + structured interpretation in the March 22 diagnostic
    transcript under `docs/peanut/transcripts/`
  - preserves the “pattern is strategy, not the other way around” framing for
    future rubric and reasoning-behaviour analysis
- Latest audit checkpoint (March 25, 2026):
  - `make doctor-env`: healthy
  - `make lint-docs`: pass
  - backend regression tests: `make test` pass (`162` tests)
- Build block audit checkpoint (March 26, 2026):
  - README was refreshed to current build blocks and live API surface
  - local lint now matches CI scope (`README.md` + `docs/**/*.md`)
  - new guard command is available: `make build-audit`
  - `eval-cleanup` now skips cleanly when local-only helper script is absent
  - full deterministic gate cycle passed: `make quality-gate-deterministic`
  - evidence pipeline passed: `make evidence-refresh`
  - Docker smoke passed:
    `make docker-build` + container `/health` probe
- UI archive checkpoint (March 27, 2026):
  - legacy `frontend/` folder removed from active repository surface
  - canonical surfaces are API + CLI + deterministic eval tooling
  - historical UI context is retained via live archive docs + Git history
- Human-reference archive checkpoint (March 27, 2026):
  - SQLite human-reference DB/query workflow moved to archive-only status
  - canonical visual surface is markdown-native `make reference-graph`
- Runtime DB lifecycle checkpoint (March 27, 2026):
  - runtime DB defaults moved to `.local/runtime_dbs/active/`
  - local DB lifecycle commands are retired during wiring lock
    (docs/tests remain the active contract surface)
  - no root-level `.polinko_*.db` files are part of the active surface
- Minimal-config benchmark checkpoint (March 27, 2026):
  - canonical benchmark spec added:
    - `docs/benchmarks/MINIMAL_CONFIG_BENCHMARK_SPEC.md`
  - benchmark compares three phases:
    - minimal-config CLI baseline
    - traditional eval stack
    - binary eval stack
  - evaluation axes are fixed to quality, decision clarity, iteration speed,
    and maintenance overhead
- Benchmark verdict checkpoint (March 28, 2026):
  - A/B/C moved from provisional to decision-ready status:
    - A: `PASS` (baseline anchor)
    - B: `FAIL` (traditional complexity underperformed)
    - C: `PASS` (binary current target)
  - `H-001` is currently supported for product direction
  - next benchmark-derived backend priority is operation-binding diagnostics
    (`benchmark D`) as deterministic implementation slices
- Wiring lock checkpoint (March 27, 2026):
  - runtime DB provisioning is intentionally paused until eval wiring sign-off
  - no fresh `.polinko_*.db` or `.human_reference.db` files are active in
    repository root during this phase
  - canonical wiring source is `docs/eval/EVAL_WIRING_SPEC.md` and associated
    contract docs/tests
- Runtime DB doc-contract checkpoint (March 28, 2026):
  - active docs no longer reference retired local DB commands
    (`db-reset`, `db-archive`, `db-visuals`)
  - `make build-audit` now fails on reintroduction of those command tokens in
    active docs
- Transcript-backed OCR mining checkpoint (March 29, 2026):
  - merged PR `#110` adds export indexing + transcript OCR case mining:
    - `tools/index_cgpt_export.py`
    - `tools/build_ocr_cases_from_export.py`
  - canonical local commands:
    - `make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
    - `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
    - `make eval-ocr-transcript-cases`
  - local outputs are untracked under `.local/eval_cases/`
  - latest transcript-case run is green (`1/1` PASS) with strict OCR gating
- Eval relationship visual checkpoint (March 28, 2026):
  - local eval data visualisation now has a canonical navigation-first report:
    - command: `make eval-viz`
    - builder: `tools/build_eval_relationship_graph.py`
    - output: `.local/visuals/eval_relationship_graph.md` (local-only)
  - report includes:
    - schema ER diagram
    - session topology graph
    - linked session directory + per-session relationship maps
    - per-session message/feedback/checkpoint tables + tag frequency
- Visual tooling track checkpoint (March 28, 2026):
  - Mermaid remains canonical for active operator visuals and docs-native
    versioning
  - D3.js interactive visualisation is pinned as a deferred track for later UI
    iteration (not active in current runtime/docs gate path)
- UI shell retirement checkpoint (March 28, 2026):
  - active `ui/` folder and `/ui` route are removed from runtime surface
  - canonical active surfaces are backend API + CLI
  - historical frontend context remains in `.archive/live_archive/legacy_frontend/`
- Proactive ownership checkpoint (March 26, 2026):
  - engineer execution mode is action-first and proactive by default
  - technical hygiene/drift-control slices are executed without reminder
  - user prompts are reserved for approvals and material trade-offs
- Human-managed co-reasoning checkpoint (March 26, 2026):
  - human remains work-management authority in reasoning loops
  - human controls objective/scope/acceptance + go/no-go cutlines
  - engineer executes proactive implementation/hygiene within that frame
- Eval runs no longer produce ambiguous generic `New chat` helper rows in the
  UI; generated eval chats now use deterministic session-id titles when
  retained.
- Parallel eval report orchestration is now available:
  - command: `make eval-reports-parallel`
  - tool: `tools/eval_parallel_orchestrator.py`
  - artifact: `eval_reports/parallel-<run_id>.json` plus per-suite logs/reports
- Playwright smoke E2E now validates retry-variant lineage behaviour end-to-end
  (assistant variant creation, `Variant X of Y` controls, and no duplicate user
  prompt rows in the rendered thread).
- Hallucination judge evaluation now supports configurable judge credentials and
  base URL (`--judge-api-key-env`, `--judge-base-url`) so OpenAI-compatible
  judge backends (including Braintrust gateways) can be wired without runtime
  behaviour changes.
- Hallucination score gating now supports configurable minimum threshold via
  `HALLUCINATION_MIN_ACCEPTABLE_SCORE`; report-based calibration helper is
  available through `make calibrate-hallucination-threshold`.
- Calibration tie-break now prefers the strictest threshold among equal-metric
  candidates, preventing under-conservative recommendations from all-pass
  datasets.
- P2 CLIP experiment scaffolding has started with
  `make eval-clip-ab` (baseline hybrid-source vs image-prioritized proxy arm).
- Latest P2 expanded run (2026-03-10, run `20260310-125230`) used 4
  image-context cases and showed stable proxy uplift:
  - baseline hybrid any-hit: `0.0`
  - image-priority proxy any-hit: `1.0`
  - delta (`proxy - baseline`): `+1.0`
  - errors: `0` in both arms
- Latest CLIP readiness pair (2026-03-15) is green:
  - `20260315-143219`: PASS (`cases=4`, `proxy_any_rate=1.000`,
    `delta=+1.000`, `errors=0`)
  - `20260315-180942`: PASS (`cases=4`, `proxy_any_rate=1.000`,
    `delta=+1.000`, `errors=0`)
- Latest readiness decision (2026-03-15): `GO`.
- CLIP go/no-go criterion is now explicit (two consecutive runs with
  `cases_count >= 4`, proxy `any_rate >= 0.90`, delta `>= 0.50`, zero errors)
  before integration escalation.
- Minimal CLIP proxy integration slice is now implemented behind feature flag:
  - `POLINKO_CLIP_PROXY_FILE_SEARCH_ENABLED` (default `false`)
  - `POST /skills/file_search` now accepts
    `retrieval_profile=clip_proxy_image_only`
  - disabled profile requests return `409` (explicit, reversible rollout)
  - enabled profile forces image-only retrieval path without changing default
    hybrid-source behaviour.
- Automated CLIP readiness gate is available via
  `make eval-clip-ab-readiness`; it inspects the latest two report artifacts
  and returns explicit `GO`/`NO-GO` against the D-040 threshold.
- Active operating mode is local-first glue-code + manual eval workflow, with
  runtime `/chat` behaviour unchanged.
- Collaboration policy checkpoint (March 21, 2026):
  - human judgment sets architecture/rubric first
  - multi-agent/parallel workflows are applied only after constraints are
    explicit and validation remains deterministic
- Reasoning Loops collaboration checkpoint (March 26, 2026):
  - `Reasoning Loops` is the canonical human-AI collaboration model term
  - imagineer leads hypotheses/theory framing + eval operation
  - engineer leads implementation/tooling/validation + execution recommendations
- Inspect-first checkpoint (March 26, 2026):
  - when context is noisy/ambiguous, execution pauses for inspection before
    cleanup/refactor
  - deprecated context stays in archive paths and does not drive active contracts
  - directed precision mode is active for scoped changes to avoid unusable
    summary-first outputs
- `make hallucination-gate` now provides a dedicated strict hallucination gate
  run with managed local server startup; CI includes optional Braintrust gate
  wiring when repository vars/secrets are configured.
- Docker smoke is validated locally (`make docker-build` + `make docker-run` +
  `/health` probe).
- Devcontainer Docker connectivity is stabilised with Docker-outside-of-Docker
  support and UI-side Docker extension routing for reliable `Containers` view.
- Local IDE interpreter-path drift is now documented and resolved:
  host workspaces should not pin Python to container-built Linux venv binaries;
  use host interpreter auto-discovery (or explicit host Python) on macOS.
- Local environment doctor is available via `make doctor-env` for interpreter,
  import, and `zsh` completion checks.
- Python static analysis is now repo-scoped and stable:
  - `mypy.ini` is the single source of truth for mypy checks
  - workspace diagnostics run in `workspace` scope and use repo mypy config
  - generated/venv and high-noise test shim paths are excluded from default
    mypy reporting to keep signals actionable
- OCR supports a provider flag:
  - `POLINKO_OCR_PROVIDER=scaffold` (default fallback)
  - `POLINKO_OCR_PROVIDER=openai` (image OCR via OpenAI model)
- OCR supports optional `visual_context_hint` for deterministic image-context indexing
  (useful for eval seeding and controlled ingest).
- Optional Responses API orchestration mode is implemented behind feature flags:
  - `POLINKO_RESPONSES_ORCHESTRATION_ENABLED`
  - `POLINKO_RESPONSES_VECTOR_STORE_ID`
  - optional web search + history-turn tuning flags
- File-search API responses now include explicit backend path metadata:
  `backend`, `fallback_reason`, and `candidate_count`.
- Hallucination eval harness now isolates each eval case in session-local scope to reduce cross-case memory bleed and improve determinism.
- Runtime session layer now uses managed SQLite session cleanup so cross-thread
  handles are closed deterministically (prevents late sqlite `ResourceWarning`
  noise in strict test runs).
- Eval harnesses support JSON report artifacts via `--report-json`
  (hallucination, style, retrieval, file-search, OCR).
- OCR ambiguity/recovery eval harness is available via
  `make eval-ocr-recovery` with case template
  `docs/eval/cases/ocr_recovery_eval_cases.json`.
- Evidence indexing now tracks FAIL remediation lifecycle with
  `recommended_action`, `action_taken`, `status`, and optional PASS-linked
  closure metadata.
- Adaptive runtime note selection now applies decay-weighted feedback scoring,
  near-duplicate suppression, and a max of two active notes, with note-change
  events logged as `adaptive_style_notes_updated` to prevent prompt/input
  over-indexing.
- Eval feedback/checkpoint state is persisted in SQLite only; no active
  `raw_evidence` intake file logging remains in runtime.
- Hallucination eval cases now include an interpersonal motive-guess regression
  guard (`uncertainty_required_no_relationship_motive_guess`) to catch speculative
  relationship attribution and enforce uncertainty-forward responses.
- Co-reasoning interaction guidance is now documented with a dedicated eval
  reference and PASS/FAIL mapping:
  - `docs/peanut/research/co_reasoning_eval_reference.md`
- Style eval cases now include co-reasoning stress scenarios for
  constraint-retention, meta-shift handling, anti-mimicry adaptation, and
  grounding-under-abstraction checks.
- Portfolio metadata audit tooling is available (`make portfolio-metadata-audit`)
  and validates evidence-index + evidence-log metadata completeness.
- Integration tests exist and pass locally (`tests/test_api.py`).
- Collaboration v1 supports explicit agent-role handoffs per chat with audit history.

## Portfolio Timeline Snapshot (March 28, 2026)

- Engineering build completion estimate: `65-75%`
- Portfolio package completion estimate: `40-50%`
- Overall project completion estimate (apply-ready target): `55-65%`
- Remaining horizon at current pace: `3-5 weeks`
- Milestone sequence:
  - `1-2 weeks`: backend hardening + eval flow stability + minimal operator surface
  - `1-2 weeks`: benchmark cycles + evidence tables/figures + findings lock
  - `~1 week`: final case-study/research-paper assembly for portfolio handoff

## Key Files

- Prompt version + active prompt: `core/prompts.py`
- CLI chat runner: `app.py`
- Backend entrypoint: `server.py`
- API app factory + routes: `api/app_factory.py`
- Architecture guide: `docs/runtime/ARCHITECTURE.md`
- API tests: `tests/test_api.py`
- Local API client: `tools/client.py`
- Environment doctor: `tools/doctor_env.py`
- Evidence index builder: `tools/build_evidence_index.py`
- Portfolio metadata auditor: `tools/audit_portfolio_metadata.py`
- Hallucination threshold calibrator: `tools/calibrate_hallucination_threshold.py`
- CLIP A/B eval harness: `tools/eval_clip_ab.py`
- Parallel eval orchestrator: `tools/eval_parallel_orchestrator.py`

## Known Constraints

- Network-dependent API calls may fail in restricted environments (handled as
  503 in API / friendly error in CLI).
- Cloud deployment automation is intentionally paused and previous AWS scripts
  were removed from the repo; Azure is the preferred target when deployment
  work resumes.
- Dependabot PR `#13` (`openai-agents==0.11.1`) is blocked until OpenAI SDK pin
  is raised first (`openai>=2.26.0` via PR `#5`); merge order matters.
- Style eval strict gate is currently sensitive to model-output drift on low
  context greeting/mimicry rubric cases; keep it monitored as a quality signal,
  but treat as non-runtime-regression unless corroborated by API/unit failures.

## Resume Prompt (For New Chats)

Use this in a new chat:

`Read docs/governance/CHARTER.md, docs/governance/STATE.md, and docs/governance/DECISIONS.md. Summarise current status in 5 bullets, list top risks, and execute the single highest-leverage next step. Preserve prompt behaviour rules.`

## Suggested Next Steps

1. Execute benchmark `D` (operation-binding diagnostics) and map outcomes to one
   deterministic backend slice (next slice after harness mode is diagnostics telemetry).
2. Keep binary gate semantics strict (`pass`/`fail`) and keep diagnostic richness
   outside gate arithmetic.
3. Maintain archive-first runtime DB posture during wiring lock (no local DB
   lifecycle command paths).
4. Continue local-first deterministic validation (`make build-audit`,
   `make lint-docs`, `make test`, `make quality-gate-deterministic`) at each
   milestone.
5. Keep benchmark outputs product-supportive by converting findings into
   explicit implementation priorities.

## Cookbook Roadmap (Prioritized)

These are mapped from the OpenAI cookbook items and ordered for this project:

1. Doing RAG on PDFs using File Search in the Responses API
   - Best immediate fit with current vector + file search architecture.
2. Structured Outputs
   - Highest leverage for stable extraction/indexing contracts.
3. Image Understanding with RAG
   - Extends OCR and supports richer multimodal retrieval.
4. Data Extraction and Transformation in ELT Workflows (GPT-4o OCR alternative)
   - Best when moving from single-chat flows to batch ingestion jobs.
5. Exploring Model Graders for Reinforcement Fine-Tuning
   - Most useful once eval criteria and production traces are mature.
6. Custom LLM-as-Judge hallucination checks (Braintrust) [P1]
   - Offline eval/CI scaffold is implemented; calibrate thresholds and keep
     branch protections strict.
7. Multimodal retrieval A/B with CLIP embeddings [P2]
   - Evaluate against current embeddings path after OCR/PDF retrieval baseline is stable.

## Final Action Plan (Current)

1. Lock baseline and keep Runner path stable as default.
2. Keep governance + hallucination guardrails hardened in local runtime.
3. Maintain multi-agent collaboration API contract already implemented.
4. Continue eval UX/rubric simplification with deterministic checkpoint output.
5. Keep OCR/file-search/retrieval quality loops green before expansion work.
6. Preserve local-first workflow and avoid deprecated hybrid pilot paths.
