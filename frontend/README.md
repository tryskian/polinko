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
- `NAUTORUS_MEMORY_DB_PATH` (optional)
- `NAUTORUS_HISTORY_DB_PATH` (optional)
- `NAUTORUS_DEPRECATE_ON_RESET` (optional, default `true`)

Optional:

- `NAUTORUS_SERVER_API_KEY`
- `NAUTORUS_SERVER_API_KEYS_JSON`

Legacy compatibility:

- `POLINKO_*` env keys remain supported as fallback.

Note:

- The current UI does not include an x-api-key input control.
- If server API key auth is enabled, inject `x-api-key` upstream (proxy) or keep
  API key auth unset for local UI development.

## UI Features

- Server-side chat history (`/chats` endpoints)
- Drawer chat list and `New chat`
- Per-chat restore on load
- Reset button starts a fresh chat; deprecate-vs-clear behavior is controlled by `NAUTORUS_DEPRECATE_ON_RESET`
- Markdown + code rendering for both user/assistant
- Thinking animation before responses render
- Silent preference notes with `/note your guidance here`
