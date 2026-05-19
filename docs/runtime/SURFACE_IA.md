<!-- @format -->

# Surface IA

This page maps the web and portfolio-adjacent directory names during the beta
refactor. It is intentionally about path roles, not visual direction.

## Current Paths

- `frontend/`
  - Current default for `PORTFOLIO_APP_DIR`.
  - Vite source app for the public portfolio doorway.
  - Builds into the tracked static output directory.
  - `FRONTEND_DIR` remains a compatibility override for the same path.
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
- `docs/peanut/assets/tumbles/portfolio/`
  - Private local portfolio mockup lane.
  - Stays private unless explicitly promoted.

## Current Path Contract

- `PORTFOLIO_APP_DIR` names the Vite source app path.
- `FRONTEND_DIR` remains supported as the legacy default for
  `PORTFOLIO_APP_DIR`.
- `PORTFOLIO_STATIC_DIR` names the tracked static output path.
- `POLINKO_PORTFOLIO_APP_DIR` carries the source path into Python build
  helpers.
- `POLINKO_PORTFOLIO_STATIC_DIR` carries the static output path into Vite,
  Python build helpers, and FastAPI serving.
- `ui/` was the old tracked static output path. Do not reintroduce it for
  portfolio output.
- Public target names stay stable:
  - `make portfolio`
  - `make portfolio-build`
  - `make frontend-build`

## Target Names

- `apps/portfolio/`
  - Recommended target for the Vite source app now stored in `frontend/`.
  - Rationale: this is a named app surface, not a generic frontend.
- `docs/peanut/assets/portfolio-mockups/`
  - Recommended target for private mockup assets now stored in
    `docs/peanut/assets/tumbles/portfolio/`.
  - Rationale: the path should say what the assets are and keep the private
    lane obvious.

## Move Order

1. Move `frontend/` to `apps/portfolio/` and update Make, Vite, npm, and
   build-script references.
2. Move private mockups from `docs/peanut/assets/tumbles/portfolio/` to
   `docs/peanut/assets/portfolio-mockups/`.
3. Keep public routes and operator target names stable during the moves:
   - `/portfolio`
   - `/assets`
   - `make portfolio`
   - `make portfolio-build`
   - `make frontend-build`
   - `make portfolio-mockups`

## Guardrails

- Do not move chat workbench routes as part of this surface rename.
- Do not delete tracked static output unless a replacement deploy output is
  already served and tested.
- Do not promote private `docs/peanut/` mockups into public docs without an
  explicit promotion decision.
