<!-- @format -->

# Python Package Boundary

This page records the package-boundary migration contract for the beta refactor.
The packaging rail exists now; `config`, API, and core runtime implementation
are under `src/polinko/`. The legacy root `app.py` launcher has been retired
after an explicit deprecation/removal preflight.

## Current Tracked Shape

Tracked root runtime compatibility modules:

- `main.py`
  - compatibility launcher for `python main.py`
  - preserves project-virtualenv restart hints for direct launches
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
- compatibility launcher and shim retirement must happen through
  surface-specific kernels with evidence
- active `server:app` references still exist in Docker, Make runtime defaults,
  server-daemon startup, and local eval gate startup
- the legacy `app.py` launcher is retired; use `make chat`, `python -m
  polinko.cli`, `polinko-chat`, or root `main.py` for CLI chat launches

| Compatibility surface | Required by active references | Retire only after |
| --- | --- | --- |
| `main.py` | stable direct `python main.py` launcher and project-venv restart hints | direct root CLI launches are no longer supported |
| `server.py` | stable `server:app` ASGI string used by Make defaults, server-daemon, local eval gates, Docker, and older scripts | operator, Docker, and eval defaults have an approved replacement ASGI string |
| `config.py` | legacy `from config import ...` imports | older local scripts have moved to `polinko.config` |
| `api/` | legacy `api.*` imports and supported `from api import ...` submodule imports | older local scripts have moved to `polinko.api.*` |
| `core/` | legacy `core.*` imports and supported `from core import ...` submodule imports | older local scripts have moved to `polinko.core.*` |

### Readiness Snapshot: 2026-05-20

This snapshot records the current retirement posture after the root-shim
reference audit.

| Surface | Current evidence | Retirement posture |
| --- | --- | --- |
| `main.py` | root CLI launcher is still a stable direct operator entrypoint and preserves project-venv restart hints | keep until direct `python main.py` launches are intentionally deprecated |
| `app.py` | no active tracked code caller before removal; focused local ignored-lane search found no legacy launcher usage | retired in a separate deprecation/removal kernel |
| `server.py` | `server:app` remains the default ASGI string in Make, Docker, server-daemon, and local eval gates | not retirement-ready |
| `config.py` | active `src/` and `tools/` imports use `polinko.config`; legacy root imports remain confined to focused compatibility tests | keep until local legacy import support is intentionally dropped |
| `api/` | active `src/` and `tools/` imports use `polinko.api.*`; legacy root imports remain confined to focused compatibility tests | keep until local legacy import support is intentionally dropped |
| `core/` | active `src/` and `tools/` imports use `polinko.core.*`; legacy root imports remain confined to focused compatibility tests | keep until local legacy import support is intentionally dropped |

Retired root launchers:

- `app.py`
  - removed after the deprecation/removal preflight found no active tracked
    caller and no focused local ignored-lane launcher usage
  - replacement launchers are `make chat`, `python -m polinko.cli`,
    `polinko-chat`, and root `main.py`

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
- root `tools/`
  - remains repo-local operator tooling unless a later tooling split is
    explicitly approved

## Migration Order

1. Keep packaging metadata and editable-install coverage green.
2. Keep active runtime imports on `polinko.*`.
3. Keep `main.py` and `server.py` as compatibility launchers during the import
   rewrite.
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
- Do not reintroduce root `app.py`; use `make chat`, `python -m polinko.cli`,
  `polinko-chat`, or root `main.py`.
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
