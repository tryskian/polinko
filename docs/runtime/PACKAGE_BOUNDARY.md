<!-- @format -->

# Python Package Boundary

This page records the package-boundary migration contract for the beta refactor.
The packaging rail exists now; `config`, API, and core runtime implementation
are under `src/polinko/`. The legacy root `app.py` launcher is retired. The
legacy root `config.py` import shim is retired. The legacy root `api/` import
shims are retired. The legacy root `core/` import shims are retired.

## Current Tracked Shape

Tracked root runtime compatibility modules:

- `main.py`
  - compatibility launcher for `python main.py`
  - preserves project-virtualenv restart hints for direct launches
- `server.py`
  - compatibility shim for `uvicorn server:app`
  - forwards module identity to `polinko.asgi`

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
- remaining root compatibility imports are allowed only in the tracked shim
  layer and focused legacy-contract tests
- compatibility launcher and shim retirement must happen through
  surface-specific kernels with evidence
- active `server:app` references still exist in Docker, Make runtime defaults,
  server-daemon startup, and local eval gate startup
- the legacy `app.py` launcher is retired; use `make chat`, `python -m
  polinko.cli`, `polinko-chat`, or root `main.py` for CLI chat launches
- the legacy root `config.py` import shim is retired; use `polinko.config`
  imports
- the legacy root `api/` import shims are retired; use `polinko.api.*`
  imports
- the legacy root `core/` import shims are retired; use `polinko.core.*`
  imports

| Compatibility surface | Required by active references | Retire only after |
| --- | --- | --- |
| `main.py` | stable direct `python main.py` launcher and project-venv restart hints | direct root CLI launches are no longer supported |
| `server.py` | stable `server:app` ASGI string used by Make defaults, server-daemon, local eval gates, Docker, and older scripts | operator, Docker, and eval defaults have an approved replacement ASGI string |

### Readiness Snapshot: 2026-05-20

This snapshot records the current retirement posture after the root-shim
reference audit.

| Surface | Current evidence | Retirement posture |
| --- | --- | --- |
| `main.py` | root CLI launcher is still a stable direct operator entrypoint and preserves project-venv restart hints | keep until direct `python main.py` launches are intentionally deprecated |
| `app.py` | no active tracked code caller before removal; focused local ignored-lane search found no legacy launcher usage | retired in a separate deprecation/removal kernel |
| `server.py` | `server:app` remains the default ASGI string in Make, Docker, server-daemon, and local eval gates | not retirement-ready |
| `config.py` | active `src/` and `tools/` imports use `polinko.config`; focused local ignored-lane search found no legacy root import usage | retired in a separate deprecation/removal kernel |
| `api/` | active `src/` and `tools/` imports use `polinko.api.*`; focused local ignored-lane search found no legacy root import usage | retired in a separate deprecation/removal kernel |
| `core/` | active `src/` and `tools/` imports use `polinko.core.*`; focused local ignored-lane search found no legacy root import usage | retired in a separate deprecation/removal kernel |

Retired root launchers:

- `app.py`
  - removed after the deprecation/removal preflight found no active tracked
    caller and no focused local ignored-lane launcher usage
  - replacement launchers are `make chat`, `python -m polinko.cli`,
    `polinko-chat`, and root `main.py`

Retired root import shims:

- `config.py`
  - removed after the legacy-import preflight found no active tracked caller
    and no focused local ignored-lane import usage
  - replacement imports use `polinko.config`
- `api/`
  - removed after the legacy-import preflight found no active tracked caller
    and no focused local ignored-lane import usage
  - replacement imports use `polinko.api.*`
- `core/`
  - removed after the legacy-import preflight found no active tracked caller
    and no focused local ignored-lane import usage
  - replacement imports use `polinko.core.*`

## Target Package Shape

The future runtime import package should be `polinko` under `src/polinko/`.

Target placement:

- `src/polinko/config.py`
  - canonical config implementation
- `src/polinko/api/`
  - canonical API implementation
- `src/polinko/core/`
  - canonical core runtime implementation
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
- Do not reintroduce root `config.py`; use `polinko.config`.
- Do not reintroduce root `api/`; use `polinko.api.*`.
- Do not reintroduce root `core/`; use `polinko.core.*`.
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
  compatibility launchers are stable.

## Validation

Before any future package-boundary move lands:

- `make package-install-check` passes
- focused entrypoint tests pass
- focused API smoke tests pass
- full unit suite passes
- docs and governance surfaces name the active compatibility boundary
- `make end` passes from clean synced `main`
