<!-- @format -->

# Python Package Boundary

This page records the package-boundary migration contract for the beta refactor.
The packaging rail exists now; `config`, API, and core runtime implementation
are under `src/polinko/`.

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
- `api/`
  - compatibility shims for legacy `api.*` imports
  - forwards module identity to `polinko.api.*`
- `core/`
  - compatibility shims for legacy `core.*` imports
  - forwards module identity to `polinko.core.*`

Tracked runtime packages currently live under `src/polinko/`; repo-local tools
remain rooted:

- `tools/`
  - repo-local operator, eval, report, render, and maintenance commands

Tracked packaging rail:

- `pyproject.toml`
  - package metadata and `src` layout configuration
  - includes packaged API static assets under `polinko.api`
- `src/polinko/__init__.py`
  - editable-install package identity
- `src/polinko/config.py`
  - canonical environment loading and validation implementation
- `src/polinko/api/`
  - canonical HTTP routes, middleware, app factory, manual-eval surfaces, public
    portfolio data helpers, and packaged API static assets
- `src/polinko/core/`
  - canonical prompt, runtime, history, rate-limit, response parsing, and
    vector-store logic
- `tools/check_package_install.py`
  - verifies editable-install metadata, package import identity, and packaged
    API static assets

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
  - remains repo-local operator tooling unless a later tooling split is
    explicitly approved

## Migration Order

1. Keep packaging metadata and editable-install coverage green.
2. Keep active runtime imports on `polinko.*`.
3. Keep `main.py`, `server.py`, and `app.py` as compatibility launchers during
   the import rewrite.
4. Move or split `tools/` only after runtime imports and tests are stable.
5. Add a console-script entrypoint for the CLI before removing any root launcher.

## Guardrails

- Do not move runtime modules into `src/polinko/` before the editable-install
  rail is green.
- Keep root `config.py` as a compatibility shim until older local scripts have
  moved off `from config import ...`.
- Keep root `api/` as compatibility shims until older local tests and scripts
  have moved off `api.*` imports.
- Keep root `core/` as compatibility shims until older local tests and scripts
  have moved off `core.*` imports.
- Do not change public operator commands:
  - `make chat`
  - `make server`
  - `make localhost`
  - `make server-daemon`
- Do not change ASGI import compatibility for `server:app`.
- Do not delete `app.py` while legacy `python app.py` compatibility is still
  documented.
- Do not package `tools/` into the runtime app before runtime imports and
  compatibility shims are stable.

## Validation

Before any future package-boundary move lands:

- `make package-install-check` passes
- focused entrypoint tests pass
- focused API smoke tests pass
- full unit suite passes
- docs and governance surfaces name the active compatibility boundary
- `make end` passes from clean synced `main`
