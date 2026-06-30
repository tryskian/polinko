<!-- @format -->

# Python Package Boundary

This page records the package-boundary contract for the beta refactor.
The packaging rail exists now; `config`, API, and core runtime implementation
live under `src/polinko/`. The active root Python modules are `main.py` and
`server.py`, both as compatibility launchers.

## Current Tracked Shape

Tracked root compatibility launchers:

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
  - canonical HTTP routes, middleware, app factory, manual-eval surfaces,
    evidence visualisation helpers, and packaged API static assets
- `src/polinko/core/`
  - canonical prompt, runtime, history, rate-limit, response parsing, and
    vector-store logic
- `tools/check_package_install.py`
  - verifies editable-install metadata, package import identity, and packaged
    API static assets

## Current Boundary

Current audit result:

- active runtime and tool imports use `polinko.*`
- root compatibility surfaces are launchers only
- CLI chat launches through `make chat`, `python -m polinko.cli`,
  `polinko-chat`, or root `main.py`
- config imports use `polinko.config`
- API imports use `polinko.api.*`
- core runtime imports use `polinko.core.*`
- `server:app` is the active ASGI compatibility string in Docker, Make
  runtime defaults, server-daemon startup, and local eval gate startup
- future launcher changes happen through surface-specific kernels with
  evidence

| Compatibility surface | Active references | Change after |
| --- | --- | --- |
| `main.py` | stable direct `python main.py` launcher and project-venv restart hints | an approved replacement exists for direct root CLI launches |
| `server.py` | stable `server:app` ASGI string used by Make defaults, server-daemon, local eval gates, Docker, and older scripts | operator, Docker, and eval defaults have an approved replacement ASGI string |

## Entrypoint Compatibility Contract

The current root runtime files are compatibility launchers. Runtime
implementation lives under `src/polinko/`.

| Operator path | Stable target | Canonical implementation |
| --- | --- | --- |
| `make chat` | `$(PYTHON) -m polinko.cli` through `CLI_ENTRYPOINT` | `polinko.cli.main` |
| `python main.py` | root compatibility launcher with project-venv restart hints | lazy import of `polinko.cli.main` |
| `polinko-chat` | installed console script | `polinko.cli:main` |
| `make server` / `make localhost` | `uvicorn server:app` through `ASGI_APP` | root `server.py` forwarding to `polinko.asgi` |
| `make server-daemon` | repo-managed daemon using `ASGI_APP` | `tools/run_server_daemon.sh` defaulting to `server:app` |
| local eval gates | fresh local server using `ASGI_APP` | `tools/run_local_eval_gate.sh` defaulting to `server:app` |
| Docker CMD | `uvicorn server:app` | root `server.py` forwarding to `polinko.asgi` |

Changing the CLI target requires updating the Make runtime config, root
`main.py`, `pyproject.toml`, the package-install check, and focused entrypoint
tests in the same kernel. Changing the ASGI target requires updating Docker,
Make runtime config, server-daemon startup, local eval gates, API smoke
expectations, and this package-boundary contract in the same kernel.

## Package Shape

The runtime import package is `polinko` under `src/polinko/`.

Current placement:

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
  - includes read-only local evidence inventory commands such as
    `tools/report_ocr_lane_inventory.py`

## Remaining Order

1. Keep packaging metadata and editable-install coverage green.
2. Keep active runtime imports on `polinko.*`.
3. Keep `main.py` and `server.py` as compatibility launchers.
   - root `server.py` currently forwards to `polinko.asgi`
4. Move or split `tools/` only after runtime imports and tests are stable.
5. Keep `polinko-chat` as the installed console-script entrypoint.

## Boundary Requirements

- Runtime modules stay under `src/polinko/`.
- Config imports use `polinko.config`.
- API imports use `polinko.api.*`.
- Core runtime imports use `polinko.core.*`.
- Public operator commands stay stable:
  - `make chat`
  - `polinko-chat`
  - `make server`
  - `make localhost`
  - `make server-daemon`
- ASGI compatibility stays on `server:app` while Docker, Make runtime defaults,
  server-daemon startup, and local eval gates use that string.
- CLI chat launchers stay on `make chat`, `python -m polinko.cli`,
  `polinko-chat`, and root `main.py`.
- `tools/` stays repo-local until a tooling split is explicitly approved.
- Local evidence inventory and operator tooling stay repo-local unless a later
  tooling split is explicitly approved.

## Validation

Before any future package-boundary move lands:

- `make package-install-check` passes
- focused entrypoint tests pass
- focused API smoke tests pass
- full unit suite passes
- docs and governance surfaces name the active compatibility boundary
- `make end` passes from clean synced `main`
