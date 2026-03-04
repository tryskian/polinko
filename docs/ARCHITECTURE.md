# Architecture

## Folder Map

- `app.py`  
  CLI chat entrypoint.
- `config.py`  
  Environment loading + validation.
- `server.py`  
  API entrypoint (creates FastAPI app).
- `api/`  
  HTTP layer and app factory.
- `core/`  
  Agent runtime logic (prompt, session, rate limit helpers).
- `frontend/`
  Vite frontend chat UI.
- `tools/`  
  Local utility scripts (API client, env doctor, eval/report utilities).
- `tests/`  
  Automated tests.
- `docs/`  
  Project docs, state, decisions, handoff.

## Runtime Flow

1. `server.py` loads config from `config.py`.
2. `server.py` calls `api.app_factory.create_app(...)`.
3. `api/app_factory.py` wires routes, middleware, auth, rate limiting, and runtime deps.
4. Runtime behavior comes from `core/` modules.

## Placement Rules

- New API endpoints or middleware: `api/`
- New model/prompt/runtime behavior: `core/`
- New frontend code: `frontend/`
- New local scripts/one-off utilities: `tools/`
- New status/process documentation: `docs/`
- Keep root limited to entrypoints + top-level project files.

## Common Commands

- Environment doctor: `make doctor-env`
- Tests: `make test`
- Quality gate: `make quality-gate` (or `make quality-gate-deterministic`)
- CLI chat: `make chat`
- Local API server: `make server`
- Frontend dev: `make ui-dev`
- Docker smoke: `make docker-build` then `make docker-run`
