<!-- @format -->

# Runbook

## Rotate API Keys

1. Update `.env` with new `OPENAI_API_KEY`.
2. If used, rotate `POLINKO_SERVER_API_KEY` and/or update
   `POLINKO_SERVER_API_KEYS_JSON`.
3. Restart running API/CLI processes.

## Reset Local Session Memory

1. Stop running processes.
2. Remove local DB files:
   - `.polinko_memory.db`
   - `.polinko_memory.db-shm` (if present)
   - `.polinko_memory.db-wal` (if present)
   - `.polinko_history.db`
   - `.polinko_history.db-shm` (if present)
   - `.polinko_history.db-wal` (if present)
   - `.polinko_vector.db` (if present)
   - `.polinko_vector.db-shm` (if present)
   - `.polinko_vector.db-wal` (if present)
3. Start app again (`make chat` or `make server`).

## Reset One Chat Session (API)

1. Set mode in `.env`:
   - `POLINKO_DEPRECATE_ON_RESET=true` (tuning mode)
   - `POLINKO_DEPRECATE_ON_RESET=false` (clear in-place mode)
2. Send `POST /session/reset` with `{"session_id":"your-chat-id"}`.
3. If needed, force deprecate regardless of env:
   `{"session_id":"your-chat-id","deprecate":true}`.
4. Deprecated chats are hidden from default `GET /chats`.
5. To include them for review: `GET /chats?include_deprecated=true`.
6. A non-deprecating reset clears both:
   - conversation memory in `.polinko_memory.db`
   - persisted chat messages in `.polinko_history.db`
   - vector memories for that session in `.polinko_vector.db` (when enabled)
7. Deprecation/reset is chat lifecycle state management, not model-weights
   training or a direct runtime penalty signal.

## Chat History API

- `GET /chats` list chats
- `POST /chats` create chat
- `GET /chats/{session_id}/messages` load chat messages
- `GET /chats/{session_id}/export` export transcript (+ OCR runs)
- `POST /chats/{session_id}/notes` add internal preference note
- `POST /chats/{session_id}/personalization` set retrieval memory scope
  (`session` or `global`)
- `GET /chats/{session_id}/personalization` read effective retrieval memory
  scope
- `GET /chats/{session_id}/collaboration` view active collaborator + handoff
  timeline
- `POST /chats/{session_id}/collaboration/handoff` apply active role handoff
- `POST /chats/{session_id}/deprecate` deprecate a chat
- `PATCH /chats/{session_id}` rename chat
- `DELETE /chats/{session_id}` delete chat and clear memory
- `POST /chat` returns `memory_used` citations (vector snippets + source
  metadata) when retrieval is used
- `POST /skills/ocr` run OCR (scaffold or OpenAI mode, includes
  `run.structured`; optional `transcription_mode=verbatim|normalized`)
- `POST /skills/pdf_ingest` extract and index PDF text into vector memory
  (includes `structured`)
- `POST /skills/file_search` search indexed vector content (OCR/chat sources)
- `GET /metrics` request counters, status counts, latency buckets, rate-limit
  totals

Hash fields in responses:

- `messages[*].content_sha256` is a deterministic SHA-256 hash of message
  content.
- `export.transcript_sha256` is a deterministic SHA-256 fingerprint over ordered
  message lineage + content hashes.

## OCR Provider Toggle

1. In `.env`, set:
   - `POLINKO_OCR_PROVIDER=scaffold` for fallback mode (default)
   - `POLINKO_OCR_PROVIDER=openai` for model OCR
2. Optional OCR settings:
   - `POLINKO_OCR_MODEL` (default `gpt-4.1-mini`)
   - `POLINKO_OCR_PROMPT` (custom extraction prompt)
   - `POLINKO_IMAGE_CONTEXT_ENABLED` (default `false`, best-effort visual-scene
     extraction for retrieval)
   - `POLINKO_IMAGE_CONTEXT_MODEL` (default `gpt-4.1-mini`)
   - `POLINKO_IMAGE_CONTEXT_PROMPT` (custom visual context prompt)
3. Restart API after changing provider settings.
4. If vector memory is enabled, OCR outputs are chunked and indexed
   automatically with OCR metadata.

## File Search (Vector Index)

1. Ensure vector memory is enabled (`POLINKO_VECTOR_ENABLED=true`) and restart
   API.
2. Index content first (for example via `POST /skills/ocr`).
3. Search with `POST /skills/file_search`:
   - required: `query`
   - optional: `session_id` to scope results to one chat
   - optional: `limit` (default `5`, max `20`)
   - optional: `source_types` (`["ocr"]`, `["chat"]`, or both)
4. Results include similarity, keyword score, combined score, snippet, and
   source metadata.
5. `source_types` now supports `ocr`, `chat`, `pdf`, and `image`.

## PDF Ingest (Vector Index)

1. Ensure vector memory is enabled (`POLINKO_VECTOR_ENABLED=true`) and restart
   API.
2. Ensure PDF parser dependency is available:
   - `pip install pypdf`
3. Ingest with `POST /skills/pdf_ingest`:
   - required: `data_base64` (PDF bytes)
   - optional: `session_id`, `source_name`, `mime_type` (`application/pdf`)
   - optional: `attach_to_chat` (default `true`)
4. Search indexed PDF chunks with `POST /skills/file_search` and
   `source_types: ["pdf"]`.
5. Optional: enable best-effort upload into your OpenAI Responses vector store:
   - `POLINKO_RESPONSES_PDF_INGEST_ENABLED=true`
   - Requires `POLINKO_RESPONSES_VECTOR_STORE_ID=vs_...`

## Vector Memory Toggle

1. In `.env`, set:
   - `POLINKO_VECTOR_ENABLED=true` to enable retrieval memory
2. Optional vector settings:
   - `POLINKO_VECTOR_DB_PATH` (default `.polinko_vector.db`)
   - `POLINKO_VECTOR_EMBEDDING_MODEL` (default `text-embedding-3-small`)
   - `POLINKO_VECTOR_TOP_K` (default `2`)
   - `POLINKO_VECTOR_MIN_SIMILARITY` (default `0.40`)
   - `POLINKO_VECTOR_MAX_CHARS` (default `220`)
   - `POLINKO_VECTOR_EXCLUDE_CURRENT_SESSION` (default `true`)
3. Restart API after changing vector settings.
4. Chat retrieval currently uses chat-response vectors for tone consistency;
   OCR/image vectors are stored with metadata for search/retrieval workflows.

## Responses Orchestration Toggle (RAG)

1. In `.env`, set:
   - `POLINKO_RESPONSES_ORCHESTRATION_ENABLED=true`
   - `POLINKO_RESPONSES_VECTOR_STORE_ID=vs_...`
2. Optional settings:
   - `POLINKO_RESPONSES_MODEL` (default `gpt-5-chat-latest`)
   - `POLINKO_RESPONSES_INCLUDE_WEB_SEARCH` (`true`/`false`)
   - `POLINKO_RESPONSES_HISTORY_TURN_LIMIT` (default `12`)
   - `POLINKO_RESPONSES_PDF_INGEST_ENABLED` (`true`/`false`, requires vector
     store id)
3. Restart API after changing orchestration settings.
4. Default behavior remains unchanged when orchestration is disabled.

## Structured Extraction Enrichment

1. In `.env`, set:
   - `POLINKO_EXTRACTION_STRUCTURED_ENABLED=true`
2. Optional model override:
   - `POLINKO_EXTRACTION_STRUCTURED_MODEL=gpt-4.1-mini`
3. Restart API after changing extraction settings.
4. When enabled, OCR/PDF endpoints attempt a strict JSON-schema normalization
   pass for extraction metadata and gracefully fall back to deterministic local
   shaping if unavailable.

## Governance + Hallucination Guardrails

1. In `.env`, set:
   - `POLINKO_GOVERNANCE_ENABLED=true`
   - `POLINKO_HALLUCINATION_GUARDRAILS_ENABLED=true`
2. Optional governance controls:
   - `POLINKO_GOVERNANCE_ALLOW_WEB_SEARCH=false` (blocks web search tool when
     false)
   - `POLINKO_GOVERNANCE_LOG_ONLY=false` (set `true` to allow but log policy
     violations)
3. Restart API after changing governance settings.
4. Guardrails operate as internal guidance only; they do not alter API response
   schema.

## Multi-Agent Collaboration v1

1. Apply a handoff:
   - `POST /chats/{session_id}/collaboration/handoff`
   - body:
     - `to_agent_id` (required)
     - `to_role` (required)
     - `objective` (optional)
     - `reason` (optional)
2. Inspect current collaboration state:
   - `GET /chats/{session_id}/collaboration`
3. Handoffs are server-side audited and included in a per-chat timeline.
4. During `/chat`, active collaboration context is injected internally (not
   shown to users).

## Personalization Memory Scope

1. Set default scope in `.env`:
   - `POLINKO_PERSONALIZATION_DEFAULT_MEMORY_SCOPE=global` (cross-chat
     retrieval)
   - or `session` (same-chat retrieval only)
2. Override per chat:
   - `POST /chats/{session_id}/personalization`
   - body: `{"memory_scope":"session"}` or `{"memory_scope":"global"}`
3. Inspect effective per-chat scope:
   - `GET /chats/{session_id}/personalization`
   - returns explicit override if present, otherwise current default scope.
4. This affects retrieval memory selection during `/chat` while keeping response
   schema unchanged.

## Run API Tests

1. Run `make test`.
2. Fix failures before merging.

## Run One-Command Quality Gate

1. Ensure `.env` includes `OPENAI_API_KEY` (judge eval requires it).
2. Run `make quality-gate`.
3. If startup fails, inspect `/tmp/polinko-quality-gate.log`.
4. Optional overrides:
   - `make quality-gate GATE_PORT=8099`
   - `make quality-gate GATE_BASE_URL=http://127.0.0.1:8099`

## Run Retrieval Eval

1. Ensure API is running locally (`make server`).
2. Run `make eval-retrieval`.
3. Optional:
   - custom endpoint:
     `python tools/eval_retrieval.py --base-url http://127.0.0.1:8000`
   - retain generated eval chats: `python tools/eval_retrieval.py --keep-chats`
   - write JSON report:
     `python tools/eval_retrieval.py --report-json eval_reports/retrieval-latest.json`
   - one-command report run: `make eval-retrieval-report`

## Run File Search Eval

1. Ensure API is running locally (`make server`).
2. Run `make eval-file-search`.
3. Optional:
   - custom endpoint:
     `python tools/eval_file_search.py --base-url http://127.0.0.1:8000`
   - retain generated eval chats:
     `python tools/eval_file_search.py --keep-chats`
   - write JSON report:
     `python tools/eval_file_search.py --report-json eval_reports/file-search-latest.json`
   - one-command report run: `make eval-file-search-report`
4. Cases:
   - uses `docs/file_search_eval_cases.json` (OCR + PDF + optional image-context
     smoke test)
   - image-context case is skipped automatically when
     `POLINKO_IMAGE_CONTEXT_ENABLED=false`

## Run OCR Eval

1. Ensure API is running locally (`make server`).
2. Run `make eval-ocr`.
3. Optional:
   - custom endpoint:
     `python tools/eval_ocr.py --base-url http://127.0.0.1:8000`
   - show extracted text: `python tools/eval_ocr.py --show-text`
   - strict fail on any failed case: `python tools/eval_ocr.py --strict`
   - retain generated eval chats: `python tools/eval_ocr.py --keep-chats`
   - write JSON report:
     `python tools/eval_ocr.py --report-json eval_reports/ocr-latest.json`
   - one-command report run: `make eval-ocr-report`
4. Cases:
   - default cases file: `docs/ocr_eval_cases.json`
   - supports image cases (`image_path`) and deterministic text-hint cases
     (`text_hint`)
   - optional per-case controls:
     - `transcription_mode` (`verbatim` or `normalized`)
     - `must_contain`, `must_contain_any`, `must_not_contain`
     - `min_chars`, `max_chars`, `case_sensitive`

## Run Hallucination Eval (Judge-Based)

1. Ensure API is running locally (`make server`).
2. Ensure `OPENAI_API_KEY` is set in `.env` (judge model call).
3. Run `make eval-hallucination`.
4. Optional strict mode:
   - `python tools/eval_hallucination.py --strict`
5. Optional tuning:
   - choose model:
     `python tools/eval_hallucination.py --judge-model gpt-4.1-mini`
   - retain generated chats: `python tools/eval_hallucination.py --keep-chats`
   - write JSON report:
     `python tools/eval_hallucination.py --report-json eval_reports/hallucination-latest.json`
   - one-command report run: `make eval-hallucination-report`
6. Eval isolation behavior:
   - Each generated eval chat is set to `memory_scope=session` to reduce
     cross-chat retrieval noise.

## Run Style Eval (Judge-Based)

1. Ensure API is running locally (`make server`).
2. Ensure `OPENAI_API_KEY` is set in `.env` (judge model call).
3. Run `make eval-style`.
4. Optional strict mode:
   - `python tools/eval_style.py --strict`
5. Optional tuning:
   - choose model: `python tools/eval_style.py --judge-model gpt-4.1-mini`
   - retain generated chats: `python tools/eval_style.py --keep-chats`
   - write JSON report:
     `python tools/eval_style.py --report-json eval_reports/style-latest.json`
   - one-command report run: `make eval-style-report`
6. Eval-only phrase fail rules (no runtime behavior changes):
   - `docs/style_eval_cases.json` root `global_forbidden_phrases` applies to all
     cases
   - per-case `forbidden_phrases` applies only to that case
   - phrase checks are case-insensitive

## Generate All Eval Reports

1. Ensure API is running locally (`make server`).
2. Ensure `OPENAI_API_KEY` is set in `.env` (judge eval reports require it).
3. Run `make eval-reports`.
4. Reports are written under `eval_reports/` with timestamped filenames.

## Export CLI Transcript

1. Run `make chat`.
2. In CLI, use `/export` for default markdown export.
3. Optional custom path/format: `/export exports/session.txt` or
   `/export exports/session.json`.
4. CLI chat management:
   - `/chats` list active chats
   - `/switch <session-id>` switch chat
   - `/rename <title>` rename current chat
   - `/close` deprecate current chat and create a fresh session

## API Client (`tools/client.py`)

1. Run `python tools/client.py --session-id local-dev`.
2. Useful commands:
   - `/help`
   - `/reset`
   - `/ocr path/to/image.png`
   - `/ocr --mode normalized path/to/image.png`
   - `/pdf path/to/file.pdf`
   - `/search your query`
   - `/search-ocr your query`
   - `/search-pdf your query`
   - `/search-chat your query`
   - `/export`

## Export From UI

1. Open a chat in the web UI.
2. Use header controls to download:
   - transcript markdown (`.md`)
   - transcript json (`.json`)
   - OCR run history json (`.ocr-runs.json`)

## Common Connection Error

Symptom:

- `connection error` during chat.

Checks:

1. Confirm internet access and no firewall/VPN block.
2. Confirm `OPENAI_API_KEY` is set in `.env`.
3. If auth is enabled, confirm `POLINKO_SERVER_API_KEY` or
   `POLINKO_SERVER_API_KEYS_JSON` is configured consistently with your
   client/proxy.
4. Retry command after a short wait.

## Figma MCP Design Fetch Troubleshooting

Symptom:

- Figma tools return: `You currently have nothing selected.`

Checks:

1. Confirm Figma MCP is connected and authenticated.
2. If using Figma desktop workflow, select the target frame/layer before fetch.
3. If using URL workflow, ensure the link includes a valid `node-id` and retry.
4. Restart Codex after first-time MCP login to refresh tool availability.
