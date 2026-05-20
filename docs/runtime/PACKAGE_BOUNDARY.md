<!-- @format -->

# Python Package Boundary

This page records the package-boundary preflight for the beta refactor. It is a
contract for the next source-layout move, not the move itself.

## Current Tracked Shape

Tracked runtime Python currently has four root modules:

- `main.py`
  - canonical CLI chat entrypoint
- `app.py`
  - lazy compatibility shim for legacy `python app.py`
- `server.py`
  - FastAPI ASGI entrypoint
- `config.py`
  - environment loading and validation

Tracked runtime packages currently live at the repo root:

- `api/`
  - HTTP routes, middleware, app factory, manual-eval surfaces, and public
    portfolio data helpers
- `core/`
  - prompt, runtime, history, rate-limit, response parsing, and vector-store
    logic
- `tools/`
  - repo-local operator, eval, report, render, and maintenance commands

## Target Package Shape

The future import package should be `polinko` under `src/polinko/`.

Target placement:

- `src/polinko/config.py`
  - migrated from root `config.py`
- `src/polinko/api/`
  - migrated from root `api/`
- `src/polinko/core/`
  - migrated from root `core/`
- root `main.py`
  - remains a thin CLI launcher until a console-script entrypoint replaces it
- root `server.py`
  - remains the stable ASGI launcher for `uvicorn server:app`
- root `app.py`
  - remains only as the legacy lazy shim while local scripts still need it
- root `tools/`
  - remains repo-local operator tooling until the runtime package move is
    complete

## Migration Order

1. Add packaging metadata and editable-install coverage for `src/polinko/`.
2. Move `config.py`, `api/`, and `core/` under `src/polinko/`.
3. Rewrite internal imports to `polinko.*`.
4. Keep `main.py`, `server.py`, and `app.py` as compatibility launchers during
   the import rewrite.
5. Move or split `tools/` only after runtime imports and tests are stable.
6. Add a console-script entrypoint for the CLI before removing any root launcher.

## Guardrails

- Do not move files into `src/polinko/` in this preflight kernel.
- Do not change public operator commands:
  - `make chat`
  - `make server`
  - `make localhost`
  - `make server-daemon`
- Do not change ASGI import compatibility for `server:app`.
- Do not delete `app.py` while legacy `python app.py` compatibility is still
  documented.
- Do not package `tools/` into the runtime app before the core import boundary
  is stable.

## Validation

Before any future package-boundary move lands:

- focused entrypoint tests pass
- focused API smoke tests pass
- full unit suite passes
- docs and governance surfaces name the active compatibility boundary
- `make end` passes from clean synced `main`
