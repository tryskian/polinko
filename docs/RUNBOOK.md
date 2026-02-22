# Runbook

## Rotate API Keys

1. Update `.env` with new `OPENAI_API_KEY`.
2. If used, rotate `POLINKO_SERVER_API_KEY` and/or update `POLINKO_SERVER_API_KEYS_JSON`.
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
3. If needed, force deprecate regardless of env: `{"session_id":"your-chat-id","deprecate":true}`.
4. Deprecated chats are hidden from default `GET /chats`.
5. To include them for review: `GET /chats?include_deprecated=true`.
6. A non-deprecating reset clears both:
   - conversation memory in `.polinko_memory.db`
   - persisted chat messages in `.polinko_history.db`
   - vector memories for that session in `.polinko_vector.db` (when enabled)

## Chat History API

- `GET /chats` list chats
- `POST /chats` create chat
- `GET /chats/{session_id}/messages` load chat messages
- `GET /chats/{session_id}/export` export transcript (+ OCR runs)
- `POST /chats/{session_id}/notes` add internal preference note
- `POST /chats/{session_id}/deprecate` deprecate a chat
- `PATCH /chats/{session_id}` rename chat
- `DELETE /chats/{session_id}` delete chat and clear memory
- `POST /skills/ocr` run OCR (scaffold or OpenAI mode)
- `POST /skills/file_search` search indexed vector content (OCR/chat sources)
- `GET /metrics` request counters, status counts, latency buckets, rate-limit totals

## OCR Provider Toggle

1. In `.env`, set:
   - `POLINKO_OCR_PROVIDER=scaffold` for fallback mode (default)
   - `POLINKO_OCR_PROVIDER=openai` for model OCR
2. Optional OCR settings:
   - `POLINKO_OCR_MODEL` (default `gpt-4.1-mini`)
   - `POLINKO_OCR_PROMPT` (custom extraction prompt)
3. Restart API after changing provider settings.
4. If vector memory is enabled, OCR outputs are chunked and indexed automatically with OCR metadata.

## File Search (Vector Index)

1. Ensure vector memory is enabled (`POLINKO_VECTOR_ENABLED=true`) and restart API.
2. Index content first (for example via `POST /skills/ocr`).
3. Search with `POST /skills/file_search`:
   - required: `query`
   - optional: `session_id` to scope results to one chat
   - optional: `limit` (default `5`, max `20`)
   - optional: `source_types` (`["ocr"]`, `["chat"]`, or both)
4. Results include similarity, keyword score, combined score, snippet, and source metadata.

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
4. Chat retrieval currently uses chat-response vectors for tone consistency; OCR vectors are stored with
   metadata for search/retrieval workflows.

## Run API Tests

1. Run `make test`.
2. Fix failures before merging.

## Export CLI Transcript

1. Run `make chat`.
2. In CLI, use `/export` for default markdown export.
3. Optional custom path/format: `/export exports/session.txt` or `/export exports/session.json`.
4. CLI chat management:
   - `/chats` list active chats
   - `/switch <session-id>` switch chat
   - `/rename <title>` rename current chat
   - `/close` deprecate current chat and create a fresh session

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
3. If auth is enabled, confirm `POLINKO_SERVER_API_KEY` or `POLINKO_SERVER_API_KEYS_JSON`
   is configured consistently with your client/proxy.
4. Retry command after a short wait.
