# Polinko

Lightweight GPT agent project with:

- CLI chat runner
- FastAPI backend
- Server-side multi-chat history for the web UI

## Quickstart

Run these from repo root:

1. `make server`
2. `make ui-install`
3. `make ui-dev`
4. open `http://127.0.0.1:5173`
5. `make test`

## Setup

1. Create and activate your virtualenv (or use the existing one in this repo).
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill real values.
   Optional: configure a key ring with `POLINKO_SERVER_API_KEYS_JSON` for
   per-principal API keys.
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
- `PATCH /chats/{session_id}` rename a chat
- `DELETE /chats/{session_id}` delete a chat

Config:

- `POLINKO_HISTORY_DB_PATH` (default: `.polinko_history.db`)

## CI

GitHub Actions runs:

- unit tests on every push and PR
