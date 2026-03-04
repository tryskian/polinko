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
- Frontend includes indexed search UI in composer (`Search` toggle with `Insert`/`Ask` actions).
- Figma/UI parity work is intentionally paused; current execution focus is backend retrieval, OCR, and file-search reliability.
- Quality gate is implemented and passing locally via `make quality-gate`:
  - unit tests (`119`)
  - retrieval eval (`12/12`)
  - file-search eval (`5/5`, including image-context smoke)
  - OCR eval strict (`6/6`)
  - style eval strict (`6/6`)
  - hallucination eval strict (`6/6`)
- Hallucination judge evaluation now supports configurable judge credentials and
  base URL (`--judge-api-key-env`, `--judge-base-url`) so OpenAI-compatible
  judge backends (including Braintrust gateways) can be wired without runtime
  behavior changes.
- Hallucination score gating now supports configurable minimum threshold via
  `HALLUCINATION_MIN_ACCEPTABLE_SCORE`; report-based calibration helper is
  available through `make calibrate-hallucination-threshold`.
- P2 CLIP experiment scaffolding has started with
  `make eval-clip-ab` (baseline mixed-source vs image-prioritized proxy arm).
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
- Evidence indexing now tracks FAIL remediation lifecycle with
  `recommended_action`, `action_taken`, `status`, and optional PASS-linked
  closure metadata.
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
- AWS deployment is intentionally paused and AWS scripts were removed from the
  repo.

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
