<!-- @format -->

# Python Package Boundary

This page records the package-boundary migration contract for the beta refactor.
The packaging rail exists now; `config` is the first runtime module moved under
`src/polinko/`.

## Current Tracked Shape

Tracked root runtime compatibility modules:

- `main.py`
  - canonical CLI chat entrypoint
- `app.py`
  - lazy compatibility shim for legacy `python app.py`
- `server.py`
  - FastAPI ASGI entrypoint
- `config.py`
  - compatibility shim for legacy `from config import ...` imports
  - re-exports `AppConfig` and `load_config` from `polinko.config`

Tracked runtime packages currently live at the repo root:

- `api/`
  - HTTP routes, middleware, app factory, manual-eval surfaces, and public
    portfolio data helpers
- `core/`
  - prompt, runtime, history, rate-limit, response parsing, and vector-store
    logic
- `tools/`
  - repo-local operator, eval, report, render, and maintenance commands

Tracked packaging rail:

- `pyproject.toml`
  - package metadata and `src` layout configuration
- `src/polinko/__init__.py`
  - editable-install package identity
- `src/polinko/config.py`
  - canonical environment loading and validation implementation
- `tools/check_package_install.py`
  - verifies editable-install metadata and package import identity

## Target Package Shape

The future runtime import package should be `polinko` under `src/polinko/`.

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

1. Keep packaging metadata and editable-install coverage green.
2. Move `api/` and `core/` under `src/polinko/`.
3. Rewrite remaining internal imports to `polinko.*`.
4. Keep `main.py`, `server.py`, and `app.py` as compatibility launchers during
   the import rewrite.
5. Move or split `tools/` only after runtime imports and tests are stable.
6. Add a console-script entrypoint for the CLI before removing any root launcher.

## Guardrails

- Do not move runtime modules into `src/polinko/` before the editable-install
  rail is green.
- Keep root `config.py` as a compatibility shim until older local scripts have
  moved off `from config import ...`.
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

- `make package-install-check` passes
- focused entrypoint tests pass
- focused API smoke tests pass
- full unit suite passes
- docs and governance surfaces name the active compatibility boundary
- `make end` passes from clean synced `main`
