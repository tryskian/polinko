<!-- @format -->

# Surface IA

This page maps the web and portfolio-adjacent directory names before the next
rename kernel. It is intentionally about path roles, not visual direction.

## Current Paths

- `frontend/`
  - Vite source app for the public portfolio doorway.
  - Builds into the tracked static output directory.
  - Used by `FRONTEND_DIR`, `portfolio-build`, `frontend-build`, and
    `tools/build_portfolio_static.py`.
- `ui/`
  - Tracked static build output for the portfolio doorway.
  - Served by FastAPI:
    - `/portfolio` returns `ui/index.html`.
    - `/assets` mounts `ui/assets/`.
  - Copied into `output/netlify/` by `tools/build_portfolio_static.py`.
- `/portfolio`
  - Public route and operator workflow.
  - Not a source directory.
- `docs/peanut/assets/tumbles/portfolio/`
  - Private local portfolio mockup lane.
  - Stays private unless explicitly promoted.

## Target Names

- `apps/portfolio/`
  - Recommended target for the Vite source app now stored in `frontend/`.
  - Rationale: this is a named app surface, not a generic frontend.
- `public/portfolio/`
  - Recommended target for the tracked static output now stored in `ui/`.
  - Rationale: this is deployable public static output, not source UI.
- `docs/peanut/assets/portfolio-mockups/`
  - Recommended target for private mockup assets now stored in
    `docs/peanut/assets/tumbles/portfolio/`.
  - Rationale: the path should say what the assets are and keep the private
    lane obvious.

## Move Order

1. Introduce explicit `PORTFOLIO_APP_DIR` and `PORTFOLIO_STATIC_DIR` variables
   while keeping the current paths.
2. Move `ui/` to `public/portfolio/` and update FastAPI static serving,
   Netlify build copy, and Vite output.
3. Move `frontend/` to `apps/portfolio/` and update Make, Vite, npm, and
   build-script references.
4. Move private mockups from `docs/peanut/assets/tumbles/portfolio/` to
   `docs/peanut/assets/portfolio-mockups/`.
5. Keep public routes and operator target names stable during the moves:
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
