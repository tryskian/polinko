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

## Chat History API

- `GET /chats` list chats
- `POST /chats` create chat
- `GET /chats/{session_id}/messages` load chat messages
- `POST /chats/{session_id}/notes` add internal preference note
- `POST /chats/{session_id}/deprecate` deprecate a chat
- `PATCH /chats/{session_id}` rename chat
- `DELETE /chats/{session_id}` delete chat and clear memory

## Run API Tests

1. Run `make test`.
2. Fix failures before merging.

## Common Connection Error

Symptom:

- `connection error` during chat.

Checks:

1. Confirm internet access and no firewall/VPN block.
2. Confirm `OPENAI_API_KEY` is set in `.env`.
3. If auth is enabled, confirm `POLINKO_SERVER_API_KEY` or `POLINKO_SERVER_API_KEYS_JSON`
   is configured consistently with your client/proxy.
4. Retry command after a short wait.
