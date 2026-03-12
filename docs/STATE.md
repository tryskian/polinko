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
- Frontend image attachments now support paste-to-attach, client-side downsize/compression, and per-chat persistence across chat switches and page reloads.
- Frontend includes indexed search UI in composer (`Search` toggle with `Insert`/`Ask` actions).
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
- Eval runs no longer produce ambiguous generic `New chat` helper rows in the
  UI; generated eval chats now use deterministic session-id titles when
  retained.
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
- CLIP go/no-go criterion is now explicit (two consecutive runs with
  `cases_count >= 4`, proxy `any_rate >= 0.90`, delta `>= 0.50`, zero
  errors/skips) before integration escalation.
- Automated CLIP readiness gate is available via
  `make eval-clip-ab-readiness`; it inspects the latest two report artifacts
  and returns explicit `GO`/`NO-GO` against the D-040 threshold.
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
- Eval feedback submissions are now append-logged for all outcomes
  (`PASS`/`PARTIAL`/`FAIL`) to
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

## Known Constraints

- Network-dependent API calls may fail in restricted environments (handled as
  503 in API / friendly error in CLI).
- Cloud deployment automation is intentionally paused and previous AWS scripts
  were removed from the repo; Azure is the preferred target when deployment
  work resumes.
- Dependabot PR `#13` (`openai-agents==0.11.1`) is blocked until OpenAI SDK pin
  is raised first (`openai>=2.26.0` via PR `#5`); merge order matters.

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
   - Offline eval/CI scaffold is implemented; next calibrate thresholds and enable branch protections.
7. Multimodal retrieval A/B with CLIP embeddings [P2]
   - Evaluate against current embeddings path after OCR/PDF retrieval baseline is stable.

## Final Action Plan (Current)

1. Lock baseline and keep Runner path stable as default.
2. Implement governance and hallucination guardrails (tool policy + groundedness guidance).
3. Build Multi-Agent Portfolio Collaboration v1 with controlled role handoffs. (Completed)
4. Expand context engineering for personalization (session-local vs global preference memory). (Completed v1)
5. Add PDF RAG and structured extraction contracts (Structured Outputs first).
6. Optimize with prompt caching and formal eval loops before fine-tuning data prep.
