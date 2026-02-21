# Frontend (Vite)

## Dev

From repo root:

1. `make server`
2. `make ui-install`
3. `make ui-dev`
4. open `http://127.0.0.1:5173`

## Build

From repo root:

1. `make ui-build`

## Backend Config

Set in `.env`:

- `OPENAI_API_KEY`
- `POLINKO_MEMORY_DB_PATH` (optional)
- `POLINKO_HISTORY_DB_PATH` (optional)

Optional:

- `POLINKO_SERVER_API_KEY`
- `POLINKO_SERVER_API_KEYS_JSON`

Note:

- The current UI does not include an x-api-key input control.
- If server API key auth is enabled, inject `x-api-key` upstream (proxy) or keep
  API key auth unset for local UI development.

## UI Features

- Server-side chat history (`/chats` endpoints)
- Drawer chat list and `New chat`
- Per-chat restore on load
- Markdown + code rendering for both user/assistant
- Thinking animation before responses render
