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

CLI extras:
- `/reset` clears current CLI session memory/history
- `/export` writes transcript to `exports/<session>-<timestamp>.md`
- `/export path/to/file.txt` or `.json` for other formats

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

## Project Layout

- `app.py` CLI entrypoint
- `server.py` API entrypoint
- `api/` API implementation
- `core/` runtime logic
- `frontend/` Vite chat UI
- `tools/` local scripts
- `docs/` project docs

## Server-Side Chat History

The web UI now stores chat threads server-side (SQLite) instead of in browser local storage.

- `GET /chats` list chats
- `POST /chats` create a chat
- `GET /chats/{session_id}/messages` load a thread
- `POST /chats/{session_id}/notes` add internal preference note
- `POST /chats/{session_id}/deprecate` mark a chat as deprecated (hidden from default list)
- `PATCH /chats/{session_id}` rename a chat
- `DELETE /chats/{session_id}` delete a chat

Config:

- `POLINKO_HISTORY_DB_PATH` (default: `.polinko_history.db`)
- `POLINKO_DEPRECATE_ON_RESET` (default: `true`)

## UI Behavior

- Drawer-based chat list with `New chat`
- Per-chat thread loading from server history
- Session reset follows `POLINKO_DEPRECATE_ON_RESET`:
  - `true`: deprecate active chat and open a fresh one
  - `false`: clear active chat in-place
- Markdown + code block rendering for both user and assistant messages
- Small thinking animation before assistant responses render
- Silent preference notes via `/note ...` in the composer (stored server-side and applied silently)

## CI

GitHub Actions runs:

- unit tests on every push and PR
