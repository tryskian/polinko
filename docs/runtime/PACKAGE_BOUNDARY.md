<!-- @format -->

# Python Package Boundary

This page records the package-boundary migration contract for the beta refactor.
The packaging rail exists now; `config`, API, and core runtime implementation
are under `src/polinko/`.

## Current Tracked Shape

Tracked root runtime compatibility modules:

- `main.py`
  - compatibility launcher for `python main.py`
  - preserves project-virtualenv restart hints for direct launches
- `app.py`
  - lazy compatibility shim for legacy `python app.py`
- `server.py`
  - compatibility shim for `uvicorn server:app`
  - forwards module identity to `polinko.asgi`
- `config.py`
  - compatibility shim for legacy `from config import ...` imports
  - re-exports `AppConfig` and `load_config` from `polinko.config`
- `api/`
  - compatibility shims for legacy `api.*` imports
  - forwards module identity to `polinko.api.*`
  - exposes an explicit `__all__` list for supported legacy
    `from api import ...` imports
- `core/`
  - compatibility shims for legacy `core.*` imports
  - forwards module identity to `polinko.core.*`
  - exposes an explicit `__all__` list for supported legacy
    `from core import ...` imports

Tracked runtime packages currently live under `src/polinko/`; repo-local tools
remain rooted:

- `tools/`
  - repo-local operator, eval, report, render, and maintenance commands

Tracked packaging rail:

- `pyproject.toml`
  - package metadata and `src` layout configuration
  - installs the `polinko-chat` console script
  - includes packaged API static assets under `polinko.api`
- `src/polinko/__init__.py`
  - editable-install package identity
- `src/polinko/cli.py`
  - canonical CLI chat implementation
- `src/polinko/asgi.py`
  - canonical ASGI app construction and runtime-deps access
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

## Compatibility Audit

Current audit result:

- active runtime and tool imports should use `polinko.*`
- root compatibility imports are allowed only in the tracked shim layer and
  focused legacy-contract tests
- do not delete compatibility launchers or shims in this audit kernel

| Compatibility surface | Required by active references | Retire only after |
| --- | --- | --- |
| `main.py` | stable direct `python main.py` launcher and project-venv restart hints | direct root CLI launches are no longer supported |
| `app.py` | legacy `python app.py` launcher with lazy import behavior | local legacy callers have moved to `make chat`, `python -m polinko.cli`, or `polinko-chat` |
| `server.py` | stable `server:app` ASGI string used by Make defaults, server-daemon, local eval gates, Docker, and older scripts | operator, Docker, and eval defaults have an approved replacement ASGI string |
| `config.py` | legacy `from config import ...` imports | older local scripts have moved to `polinko.config` |
| `api/` | legacy `api.*` imports and supported `from api import ...` submodule imports | older local scripts have moved to `polinko.api.*` |
| `core/` | legacy `core.*` imports and supported `from core import ...` submodule imports | older local scripts have moved to `polinko.core.*` |

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
  - remains a thin compatibility launcher for direct `python main.py` usage
- `src/polinko/cli.py`
  - canonical CLI chat implementation
- `polinko-chat`
  - installed console-script entrypoint for the packaged CLI
- `src/polinko/asgi.py`
  - canonical ASGI app construction
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
   - root `server.py` currently forwards to `polinko.asgi`
4. Move or split `tools/` only after runtime imports and tests are stable.
5. Add a console-script entrypoint for the CLI before removing any root launcher.
   - current console script: `polinko-chat`

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
  - `polinko-chat`
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
