<!-- @format -->

# Project State

## Current Status

- Prompt/runtime is intentionally minimal and aligned with legacy `try.py` behaviour.
- CLI agent loop works with persistent SQLite memory (`.polinko_memory.db`) and
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
- Frontend now exposes per-chat personalization memory scope control in the header.
- Frontend includes OCR upload wiring that posts to `/skills/ocr` and appends extracted text to the active chat.
- Frontend image attachments now support paste-to-attach, client-side downsize/compression, per-chat persistence across chat switches/page reloads, and OCR follow-up turns that reuse the latest persisted image batch when no new image is attached.
- Frontend chat drawer now includes eval review queue controls:
  sort (`recent`, `unreviewed`, `fail_ratio`) plus `unreviewed only` filter for
  faster checkpoint triage.
- Frontend now includes a quick triage snapshot panel (unreviewed totals,
  chats-needing-review, high-fail count, priority list) and a header export
  action for full checkpoint rollup JSON (`Download eval triage rollup`).
- Frontend includes indexed search UI in composer (`Search` toggle with `Insert`/`Ask` actions).
- OpenAI developer docs MCP server is now configured for Codex/VS Code usage:
  - endpoint: `https://developers.openai.com/mcp`
  - workspace wiring: `.vscode/mcp.json`
- Figma/UI parity work is intentionally paused; current execution focus is backend retrieval, OCR, and file-search reliability.
- Quality gate is implemented and passing locally via `make quality-gate`:
  - unit tests (`134`)
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
  - feedback save now supports mixed stream checkpoints
    (simultaneous positive and negative rubric tags on one response)
  - UI status line now renders separate streams (`pass: ...` and `fail: ...`)
    instead of forcing a single top-level label
  - checkpoint rollups now count `pass_count` and `fail_count` independently;
    `other_count` only tracks rows with neither stream set
  - API/frontend/tests were updated together to avoid state drift between
    rubric UI and saved checkpoint payloads
- Docs hygiene checkpoint (March 21, 2026):
  - deprecated pilot/comms docs are archive-only and removed from active
    runbook/state/handoff references
  - archived docs are hidden from explorer/search to reduce active-workflow
    clutter
  - `docs/PEANUT_TOOLING_REF.md` remains visible for day-to-day operator use
- Raw evidence cleanup checkpoint (March 22, 2026):
  - legacy hybrid/OpenAI eval artifacts were moved from active
    `docs/portfolio/raw_evidence` paths to
    `docs/portfolio/archive/2026-03-22-raw-evidence-legacy`
  - active evidence flow remains PASS/FAIL/MIXED/INBOX under
    `docs/portfolio/raw_evidence`
  - archive naming now follows date-prefixed pattern
    `docs/portfolio/archive/YYYY-MM-DD-...` for consistent cataloging
- Safety certainty checkpoint (March 21, 2026):
  - captured transcript + peanut-reference framing in
    `docs/transcripts/safety_certainty_and_inference_notes_2026-03-21.md`
    (unsupported certainty = fail; uncertainty + grounded recovery = pass)
- Latest audit checkpoint (March 20, 2026):
  - `make doctor-env`: healthy
  - `make lint-docs`: pass
  - `ruff check .`: pass
  - `mypy .`: pass (`58` source files)
  - `make test`: pass (`175` tests)
  - tooling import fallback debt removed in eval/pilot helpers
    (canonical `tools.*` imports only)
- Eval runs no longer produce ambiguous generic `New chat` helper rows in the
  UI; generated eval chats now use deterministic session-id titles when
  retained.
- Parallel eval report orchestration is now available:
  - command: `make eval-reports-parallel`
  - tool: `tools/eval_parallel_orchestrator.py`
  - artifact: `eval_reports/parallel-<run_id>.json` plus per-suite logs/reports
- Playwright smoke E2E now validates retry-variant lineage behavior end-to-end
  (assistant variant creation, `Variant X of Y` controls, and no duplicate user
  prompt rows in the rendered thread).
- Hallucination judge evaluation now supports configurable judge credentials and
  base URL (`--judge-api-key-env`, `--judge-base-url`) so OpenAI-compatible
  judge backends (including Braintrust gateways) can be wired without runtime
  behavior changes.
- Hallucination score gating now supports configurable minimum threshold via
  `HALLUCINATION_MIN_ACCEPTABLE_SCORE`; report-based calibration helper is
  available through `make calibrate-hallucination-threshold`.
- Calibration tie-break now prefers the strictest threshold among equal-metric
  candidates, preventing under-conservative recommendations from all-pass
  datasets.
- P2 CLIP experiment scaffolding has started with
  `make eval-clip-ab` (baseline mixed-source vs image-prioritized proxy arm).
- Latest P2 expanded run (2026-03-10, run `20260310-125230`) used 4
  image-context cases and showed stable proxy uplift:
  - baseline mixed any-hit: `0.0`
  - image-priority proxy any-hit: `1.0`
  - delta (`proxy - baseline`): `+1.0`
  - errors/skipped: `0/0` in both arms
- Latest CLIP readiness pair (2026-03-15) is green:
  - `20260315-143219`: PASS (`cases=4`, `proxy_any_rate=1.000`,
    `delta=+1.000`, `errors=0`, `skipped=0`)
  - `20260315-180942`: PASS (`cases=4`, `proxy_any_rate=1.000`,
    `delta=+1.000`, `errors=0`, `skipped=0`)
- Latest readiness decision (2026-03-15): `GO`.
- CLIP go/no-go criterion is now explicit (two consecutive runs with
  `cases_count >= 4`, proxy `any_rate >= 0.90`, delta `>= 0.50`, zero
  errors/skips) before integration escalation.
- Minimal CLIP proxy integration slice is now implemented behind feature flag:
  - `POLINKO_CLIP_PROXY_FILE_SEARCH_ENABLED` (default `false`)
  - `POST /skills/file_search` now accepts
    `retrieval_profile=clip_proxy_image_only`
  - disabled profile requests return `409` (explicit, reversible rollout)
  - enabled profile forces image-only retrieval path without changing default
    mixed-source behavior.
- Automated CLIP readiness gate is available via
  `make eval-clip-ab-readiness`; it inspects the latest two report artifacts
  and returns explicit `GO`/`NO-GO` against the D-040 threshold.
- Active operating mode is local-first glue-code + manual eval workflow, with
  runtime `/chat` behavior unchanged.
- Collaboration policy checkpoint (March 21, 2026):
  - human judgment sets architecture/rubric first
  - multi-agent/parallel workflows are applied only after constraints are
    explicit and validation remains deterministic
- `make hallucination-gate` now provides a dedicated strict hallucination gate
  run with managed local server startup; CI includes optional Braintrust gate
  wiring when repository vars/secrets are configured.
- Docker smoke is validated locally (`make docker-build` + `make docker-run` +
  `/health` probe).
- Devcontainer Docker connectivity is stabilized with Docker-outside-of-Docker
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
  `docs/ocr_recovery_eval_cases.json`.
- Evidence indexing now tracks FAIL remediation lifecycle with
  `recommended_action`, `action_taken`, `status`, and optional PASS-linked
  closure metadata.
- Adaptive runtime note selection now applies decay-weighted feedback scoring,
  near-duplicate suppression, and a max of two active notes, with note-change
  events logged as `adaptive_style_notes_updated` to prevent prompt/input
  over-indexing.
- Eval feedback submissions are now append-logged for binary outcomes
  (`PASS`/`FAIL`) to
  `docs/portfolio/raw_evidence/INBOX/eval_submissions.jsonl`, with quick
  latest-view command: `make eval-inbox`.
- Hallucination eval cases now include an interpersonal motive-guess regression
  guard (`cautious_no_relationship_motive_guess`) to catch speculative
  relationship attribution and enforce uncertainty-forward responses.
- Co-reasoning interaction guidance is now documented with a dedicated eval
  reference and PASS/FAIL mapping:
  - `docs/research/co_reasoning_eval_reference.md`
- Style eval cases now include co-reasoning stress scenarios for
  constraint-retention, meta-shift handling, anti-mimicry adaptation, and
  grounding-under-abstraction checks.
- Portfolio metadata audit tooling is available (`make portfolio-metadata-audit`)
  and validates evidence-index + evidence-log metadata completeness.
- Integration tests exist and pass locally (`tests/test_api.py`).
- Collaboration v1 supports explicit agent-role handoffs per chat with audit history.

## Key Files

- Prompt version + active prompt: `core/prompts.py`
- CLI chat runner: `app.py`
- Backend entrypoint: `server.py`
- API app factory + routes: `api/app_factory.py`
- Frontend app: `frontend/`
- Architecture guide: `docs/ARCHITECTURE.md`
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

`Read docs/CHARTER.md, docs/STATE.md, and docs/DECISIONS.md. Summarize current status in 5 bullets, list top risks, and execute the single highest-leverage next step. Preserve prompt behavior rules.`

## Suggested Next Steps

1. Calibrate Braintrust hallucination judge gate thresholds and enable CI gate with production vars/secrets.
2. Add Structured Outputs for OCR/file extraction payloads to increase reliability and testability.
3. Add image-understanding-with-RAG flow for mixed OCR + visual context retrieval.
4. Add ELT-style batch extraction pipeline (OCR alternative path) for large archive ingestion.
5. Resume Figma/UI parity after backend retrieval/OCR/file-search milestones are stable.
6. Add model-graders evaluation loop after retrieval quality and schema stability are locked.
7. Continue local-first eval hardening and checkpoint hygiene, with explicit
   archive/reset cycles between rubric revisions.

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
