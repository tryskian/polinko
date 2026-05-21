<!-- @format -->

# Surface IA

This page maps web, portfolio, and manual eval workbench names during the beta
refactor. It is intentionally about path roles, not visual direction.

## Current Paths

- `apps/portfolio/`
  - Current default for `PORTFOLIO_APP_DIR`.
  - Vite source app for the public portfolio doorway.
  - Builds into the tracked static output directory.
  - `FRONTEND_DIR` is a legacy compatibility override only.
- `public/portfolio/`
  - Current default for `PORTFOLIO_STATIC_DIR`.
  - Tracked static build output for the portfolio doorway.
  - Served by FastAPI:
    - `/portfolio` returns `public/portfolio/index.html`.
    - `/assets` mounts `public/portfolio/assets/`.
  - Copied into `output/netlify/` by `tools/build_portfolio_static.py`.
- `/portfolio`
  - Public route and operator workflow.
  - Not a source directory.
- `docs/peanut/assets/portfolio-mockups/`
  - Private local portfolio mockup lane.
  - Stays private unless explicitly promoted.

## Current Path Contract

- `PORTFOLIO_APP_DIR` names the Vite source app path.
- `PORTFOLIO_STATIC_DIR` names the tracked static output path.
- `POLINKO_PORTFOLIO_APP_DIR` carries the source path into Python build
  helpers.
- `POLINKO_PORTFOLIO_STATIC_DIR` carries the static output path into Vite,
  Python build helpers, and FastAPI serving.
- `FRONTEND_DIR` remains supported as a legacy override feeding
  `PORTFOLIO_APP_DIR` when the canonical variable is not set directly.
  New docs, scripts, and operators should prefer `PORTFOLIO_APP_DIR`.
- `ui/` was the old tracked static output path. Do not reintroduce it for
  portfolio output.
- `frontend/` was the old Vite source app path. Do not reintroduce it for
  portfolio source.
- Public target names stay stable:
  - `make portfolio`
  - `make portfolio-install`
  - `make portfolio-build`
- Legacy aliases remain runnable but are compatibility-only:
  - `make portfolio-app-install`
  - `make frontend-install`
  - `make frontend-build`

## Completed Renames

- `apps/portfolio/`
  - Vite source app moved from `frontend/`.
  - Rationale: this is a named app surface, not a generic frontend.
- `docs/peanut/assets/portfolio-mockups/`
  - Private mockup assets moved from
    `docs/peanut/assets/tumbles/portfolio/`.
  - Rationale: the path should say what the assets are and keep the private
    lane obvious.

## Manual Eval Workbench

The manual eval workbench is the human-judged research workspace, not an
automated eval runner and not the discarded run-level rollup path.

It includes:

- notebooks launched by:
  - `make notes`
  - `make notebook`
  - `make nb`
- local notebook workspace:
  - `.local/notebooks/`
- local evidence databases:
  - `.local/runtime_dbs/active/manual_evals.db`
  - `.local/runtime_dbs/active/history.db`
- chat-facing manual eval surfaces:
  - `POST /chat`
  - `/chats/*`
- feedback, checkpoints, notes, exports, and runtime history

Automated eval reports, strict OCR gates, and tracked beta snapshots remain
separate eval evidence lanes.

Generated trace artifacts from workbench submissions use manual-eval workbench
names:

- tool name: `manual_eval_workbench/eval_submission`
- trace type: `manual_eval_workbench_submission`

## Stability Contract

- Public routes and canonical operator target names stay stable:
  - `/portfolio`
  - `/assets`
  - `make portfolio`
  - `make portfolio-install`
  - `make portfolio-build`
  - `make portfolio-mockups`
- Compatibility aliases stay runnable during the migration but should not be
  used as new IA names:
  - `make portfolio-app-install`
  - `make frontend-install`
  - `make frontend-build`

## Guardrails

- Do not move chat-facing manual eval routes as part of this surface rename.
- Do not delete tracked static output unless a replacement deploy output is
  already served and tested.
- Do not promote private `docs/peanut/` mockups into public docs without an
  explicit promotion decision.
- Do not introduce new generated artifacts or docs that name the manual eval
  workbench as `ui`.
