# Polinko

Lightweight GPT agent project with:

- CLI chat runner
- FastAPI backend
- Server-side multi-chat history for the web UI
- Vite chat UI with drawer-based chat switching

## Quickstart

Run these from repo root:

1. `make server`
2. `make ui-install`
3. `make ui-dev`
4. open `http://127.0.0.1:5173`
5. `make test`
6. `make quality-gate` (single pre-push gate; requires `OPENAI_API_KEY` for judge eval)

CLI extras:

- `/reset` clears current CLI session memory/history
- `/export` writes transcript to `exports/<session>-<timestamp>.md`
- `/export path/to/file.txt` or `.json` for other formats
- `/chats` lists active chats
- `/switch <session-id>` switches active CLI chat
- `/rename <title>` renames active CLI chat
- `/close` deprecates active chat and moves CLI to a fresh session

API client extras (`python tools/client.py`):

- `/help` show command help
- `/reset` clear active API session memory
- `/ocr <file>` run OCR ingest from a local file
- `/pdf <file>` run PDF ingest from a local PDF
- `/search <query>` search indexed content (chat/ocr/pdf)
- `/search-ocr <query>` OCR-only search
- `/search-pdf <query>` PDF-only search
- `/search-chat <query>` chat-only search
- `/export` print transcript/export summary for active session

## Setup

1. Create and activate your virtualenv (or use the existing one in this repo).
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill real values.
   Optional: configure a key ring with `POLINKO_SERVER_API_KEYS_JSON` for
   per-principal API keys.
   Note: current local UI does not provide an x-api-key input field. For local
   development, keep `POLINKO_SERVER_API_KEY` unset unless your proxy injects
   auth headers.
4. Optional: use pinned dependencies with
   `pip install -r requirements.lock`.
5. Optional OCR mode:
   - `POLINKO_OCR_PROVIDER=scaffold` (default, no model OCR call)
   - `POLINKO_OCR_PROVIDER=openai` (uses `POLINKO_OCR_MODEL` for image OCR)
6. Optional visual context extraction for image retrieval memory:
   - `POLINKO_IMAGE_CONTEXT_ENABLED=true`
   - `POLINKO_IMAGE_CONTEXT_MODEL=gpt-4.1-mini`
   - optional: `POLINKO_IMAGE_CONTEXT_PROMPT=...`
7. Optional vector memory mode (cross-chat retrieval while tuning):
   - `POLINKO_VECTOR_ENABLED=true`
   - tune retrieval with `POLINKO_VECTOR_TOP_K`, `POLINKO_VECTOR_MIN_SIMILARITY`,
     `POLINKO_VECTOR_TOP_K_GLOBAL`, `POLINKO_VECTOR_TOP_K_SESSION`,
     `POLINKO_VECTOR_MIN_SIMILARITY_GLOBAL`, `POLINKO_VECTOR_MIN_SIMILARITY_SESSION`,
     and `POLINKO_VECTOR_EXCLUDE_CURRENT_SESSION`
8. Optional Responses orchestration mode (feature-flagged, RAG via OpenAI file search tool):
   - `POLINKO_RESPONSES_ORCHESTRATION_ENABLED=true`
   - `POLINKO_RESPONSES_VECTOR_STORE_ID=vs_...`
   - optional: `POLINKO_RESPONSES_INCLUDE_WEB_SEARCH=true`
   - optional: `POLINKO_RESPONSES_HISTORY_TURN_LIMIT=12`
   - optional: `POLINKO_RESPONSES_PDF_INGEST_ENABLED=true` (best-effort PDF upload into same vector store)
9. Optional governance / hallucination guardrails:
   - `POLINKO_GOVERNANCE_ENABLED=true`
   - `POLINKO_GOVERNANCE_ALLOW_WEB_SEARCH=false`
   - `POLINKO_GOVERNANCE_LOG_ONLY=false`
   - `POLINKO_HALLUCINATION_GUARDRAILS_ENABLED=true`
10. Optional structured extraction enrichment for OCR/PDF responses:

- `POLINKO_EXTRACTION_STRUCTURED_ENABLED=true`
- `POLINKO_EXTRACTION_STRUCTURED_MODEL=gpt-4.1-mini`

## Project Layout

- `app.py` CLI entrypoint
- `server.py` API entrypoint
- `api/` API implementation
- `core/` runtime logic
- `frontend/` Vite chat UI
- `tools/` local scripts
- `docs/` project docs

## Figma Workflow (MCP)

Use Figma MCP for 1:1 component implementation:

1. Connect/login once with `codex mcp add figma --url https://mcp.figma.com/mcp`.
2. Restart Codex after login.
3. Provide a Figma link with `node-id=...` (or select a node in Figma desktop).
4. Implement from MCP design context + screenshot in project conventions.

## Server-Side Chat History

The web UI now stores chat threads server-side (SQLite) instead of in browser local storage.

- `GET /chats` list chats
- `POST /chats` create a chat
- `GET /chats/{session_id}/messages` load a thread
- `GET /chats/{session_id}/export` export full chat transcript (+ OCR runs)
- `POST /chats/{session_id}/notes` add internal preference note
- `POST /chats/{session_id}/personalization` set retrieval memory scope (`session` or `global`)
- `GET /chats/{session_id}/personalization` read effective retrieval memory scope
- `GET /chats/{session_id}/collaboration` view active collaborator + handoff timeline
- `POST /chats/{session_id}/collaboration/handoff` apply controlled role handoff
- `POST /chats/{session_id}/deprecate` mark a chat as deprecated (hidden from default list)
- `PATCH /chats/{session_id}` rename a chat
- `DELETE /chats/{session_id}` delete a chat
- `POST /chat` returns assistant output and `memory_used` citations when vector retrieval is applied
- `POST /skills/ocr` OCR endpoint (scaffold/OpenAI mode, includes `run.structured` normalized extraction payload; optional `visual_context_hint` for deterministic image-context indexing; optional `transcription_mode` = `verbatim|normalized`, default `verbatim`)
- `POST /skills/file_search` search indexed vectors (defaults to OCR sources)
- `POST /skills/pdf_ingest` PDF extract + index endpoint (includes `structured` normalized extraction payload)
- `GET /metrics` API metrics (request totals, status counts, latency buckets, 429 count)

Config:

- `POLINKO_HISTORY_DB_PATH` (default: `.polinko_history.db`)
- `POLINKO_DEPRECATE_ON_RESET` (default: `true`)
- `POLINKO_IMAGE_CONTEXT_ENABLED` (default: `false`)
- `POLINKO_IMAGE_CONTEXT_MODEL` (default: `gpt-4.1-mini`)
- `POLINKO_IMAGE_CONTEXT_PROMPT` (default: concise visual-scene retrieval summary prompt)
- `POLINKO_VECTOR_ENABLED` (default: `false`)
- `POLINKO_VECTOR_DB_PATH` (default: `.polinko_vector.db`)
- `POLINKO_VECTOR_EMBEDDING_MODEL` (default: `text-embedding-3-small`)
- `POLINKO_VECTOR_TOP_K` (default: `2`)
- `POLINKO_VECTOR_TOP_K_GLOBAL` (default: inherits `POLINKO_VECTOR_TOP_K`)
- `POLINKO_VECTOR_TOP_K_SESSION` (default: inherits `POLINKO_VECTOR_TOP_K`)
- `POLINKO_VECTOR_MIN_SIMILARITY` (default: `0.40`)
- `POLINKO_VECTOR_MIN_SIMILARITY_GLOBAL` (default: inherits `POLINKO_VECTOR_MIN_SIMILARITY`)
- `POLINKO_VECTOR_MIN_SIMILARITY_SESSION` (default: inherits `POLINKO_VECTOR_MIN_SIMILARITY`)
- `POLINKO_VECTOR_MAX_CHARS` (default: `220`)
- `POLINKO_VECTOR_EXCLUDE_CURRENT_SESSION` (default: `true`)
- `POLINKO_RESPONSES_ORCHESTRATION_ENABLED` (default: `false`)
- `POLINKO_RESPONSES_MODEL` (default: `gpt-5-chat-latest`)
- `POLINKO_RESPONSES_VECTOR_STORE_ID` (required when orchestration is enabled)
- `POLINKO_RESPONSES_INCLUDE_WEB_SEARCH` (default: `false`)
- `POLINKO_RESPONSES_HISTORY_TURN_LIMIT` (default: `12`)
- `POLINKO_RESPONSES_PDF_INGEST_ENABLED` (default: `false`, requires `POLINKO_RESPONSES_VECTOR_STORE_ID`)
- `POLINKO_EXTRACTION_STRUCTURED_ENABLED` (default: `false`)
- `POLINKO_EXTRACTION_STRUCTURED_MODEL` (default: `gpt-4.1-mini`)
- `POLINKO_GOVERNANCE_ENABLED` (default: `true`)
- `POLINKO_GOVERNANCE_ALLOW_WEB_SEARCH` (default: `false`)
- `POLINKO_GOVERNANCE_LOG_ONLY` (default: `false`)
- `POLINKO_HALLUCINATION_GUARDRAILS_ENABLED` (default: `true`)
- `POLINKO_PERSONALIZATION_DEFAULT_MEMORY_SCOPE` (default: `global`, values: `session|global`)

## UI Behavior

- Drawer-based chat list with `New chat`
- Per-chat thread loading from server history
- Session reset follows `POLINKO_DEPRECATE_ON_RESET`:
  - `true`: deprecate active chat and open a fresh one
  - `false`: clear active chat in-place
- Markdown + code block rendering for both user and assistant messages
- Small thinking animation before assistant responses render
- Silent preference notes via `/note ...` in the composer (stored server-side and applied silently)
- OCR file upload button in composer (sends file payload to `/skills/ocr`)
- Indexed search panel in composer (search icon) with one-click `Insert`/`Ask` snippet actions
- Header export controls download: transcript markdown, transcript json, and OCR run history json
- Optional vector retrieval memory: assistant outputs are indexed and matched by similarity on new turns
- OCR outputs are chunked and indexed into vectors with source metadata (`ocr_run_id`, file name, mime type)
  when vector memory is enabled
- Optional image-context extraction adds `image` source vectors for visual-scene retrieval from image inputs
- File search endpoint uses hybrid ranking (semantic similarity + keyword overlap) over indexed vectors
- Optional chat orchestration mode can use Responses API tools (`file_search` and optional `web_search`)
  while preserving server-side chat history
- Governance layer can block or log disallowed tools (for example web search when disabled)
- Hallucination guardrails add internal groundedness guidance for factual-style prompts
- Multi-agent collaboration v1 supports explicit role handoffs with server-side audit history

## CI

GitHub Actions runs:

- markdown lint (`README.md` + `docs/**/*.md`) on every push and PR
- unit tests on every push and PR

## Retrieval Eval Harness

Use the deterministic retrieval evaluator to verify:

- global cross-chat recall (retrieval works across sessions when scope is `global`)
- session isolation (no cross-chat citations when scope is `session`)

Command:

- `make eval-retrieval`
- `make eval-retrieval-report` (writes a timestamped JSON report under `eval_reports/`)

Notes:

- Uses `docs/retrieval_eval_cases.json` (12 seeded OCR cases)
- Uses `/chat.memory_used` citations for pass/fail checks
- Cleans up generated eval chats by default (`--keep-chats` to retain)
- Supports JSON artifacts: `python tools/eval_retrieval.py --report-json eval_reports/retrieval-latest.json`

## File Search Eval Harness

Use the deterministic file-search evaluator to verify:

- scoped search precision (session filter behaves correctly)
- global search recall (seeded OCR evidence is discoverable without session filter)
- no scoped cross-session leakage

Command:

- `make eval-file-search`
- `make eval-file-search-report` (writes a timestamped JSON report under `eval_reports/`)

Notes:

- Uses `docs/file_search_eval_cases.json` (mixed `ocr` + `pdf` + `image_context` seed methods)
- Seeds OCR vectors per case, then validates `/skills/file_search` behavior
- Cleans up generated eval chats by default (`--keep-chats` to retain)
- Supports JSON artifacts: `python tools/eval_file_search.py --report-json eval_reports/file-search-latest.json`

## OCR Eval Harness

Use the OCR evaluator to verify extraction behavior for both real image cases and deterministic text-hint cases.

Command:

- `make eval-ocr`
- `make eval-ocr-report` (writes a timestamped JSON report under `eval_reports/`)

Optional strict mode:

- `python tools/eval_ocr.py --strict`

Notes:

- Uses `docs/ocr_eval_cases.json`
- Supports `image_path` cases (OCR path) and `text_hint` cases (deterministic smoke checks)
- Supports per-case `transcription_mode` (`verbatim|normalized`) plus phrase checks and char limits
- Supports JSON artifacts: `python tools/eval_ocr.py --report-json eval_reports/ocr-latest.json`

## Hallucination Eval Harness (P1 Scaffold)

Use the judge-based evaluator to score groundedness and hallucination risk of `/chat` outputs.

Command:

- `make eval-hallucination`
- `make eval-hallucination-report` (writes a timestamped JSON report under `eval_reports/`)

Optional strict mode (CI gate style):

- `python tools/eval_hallucination.py --strict`
- `python tools/eval_hallucination.py --strict --report-json eval_reports/hallucination-latest.json`

Notes:

- Uses `docs/hallucination_eval_cases.json` (grounded + cautious scenarios)
- Uses OpenAI model judging (`--judge-model`, default `gpt-4.1-mini`)
- Sets each eval chat to `memory_scope=session` for deterministic isolation
- Non-blocking by default; strict mode fails on any judged case failure
- Report JSON includes case-level scores, risk labels, and judge notes for offline review/ingest.

## Style Eval Harness

Use the judge-based style evaluator to keep tone consistency calibrated without adding runtime guardrails.

Command:

- `make eval-style`
- `make eval-style-report` (writes a timestamped JSON report under `eval_reports/`)

Optional strict mode (CI gate style):

- `python tools/eval_style.py --strict`
- `python tools/eval_style.py --strict --report-json eval_reports/style-latest.json`

Notes:

- Uses `docs/style_eval_cases.json`.
- Supports phrase-level eval-only fail rules:
  - `global_forbidden_phrases` at file root (applies to all cases)
  - `forbidden_phrases` per case (case-specific)
- Phrase matching is case-insensitive.
- These checks affect eval pass/fail only; they do not change runtime model behavior.
- Report JSON includes case-level scores, fit labels, and judge notes for offline review/ingest.

## All Eval Reports (One Command)

Generate timestamped JSON reports for retrieval, file-search, OCR, style, and hallucination evals:

- `make eval-reports`

## One-Command Quality Gate

Use this before pushing:

- `make quality-gate`

What it runs:

- unit tests
- retrieval eval
- file-search eval
- OCR eval in strict mode
- style eval in strict mode
- hallucination eval in strict mode

Details:

- Starts a temporary local API server on `127.0.0.1:8066`
- Uses `GATE_BASE_URL`/`GATE_PORT` if overridden
- Requires `OPENAI_API_KEY` for hallucination judge scoring
