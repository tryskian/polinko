<!-- @format -->

# Surface IA

This page maps current operator-facing surface names during the beta refactor.
It is about path roles, not visual direction.

## Active Surfaces

- API runtime:
  - `server:app`
  - `GET /health`
  - `GET /`
  - `GET /viz/pass-fail`
  - `GET /viz/pass-fail/data`
- Manual eval workbench:
  - `POST /chat`
  - `/chats/*`
  - `/manual-evals/surface`
  - `.local/runtime_dbs/active/manual_evals.db`
  - `.local/runtime_dbs/active/history.db`
- Notebook workspace:
  - `make notes`
  - `make notebook`
  - `make nb`
  - `.local/notebooks/`
- Public diagram evidence:
  - `docs/public/diagrams/`
  - `tools/render_public_d3_diagrams.py`
  - `src/polinko/api/evidence_sankey.py`

## Quarantined Surfaces

The deprecated portfolio app, static output, preview/mockup helpers, and
Netlify config are preserved for porting under:

- `.archive/quarantine/portfolio-2026-06-29/`

The old active surfaces are intentionally not wired into Make, FastAPI,
Dependabot, devcontainer setup, pre-commit excludes, or runtime risk scans:

- `apps/portfolio/`
- `public/portfolio/`
- `/portfolio`
- `/assets`
- `make portfolio`
- `make portfolio-open`
- `make portfolio-build`
- `make portfolio-install`
- `make portfolio-mockups`
- archived portfolio static builder helper
- archived portfolio mockup runner helper
- `netlify.toml`

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

Read-only OCR inventory is a tooling companion to the workbench:

- `make ocr-inventory`
- `make ocr-inventory-json`

It inspects local evidence shape and freshness without moving chat-facing
routes or executing eval lanes.

Generated trace artifacts from workbench submissions use manual-eval workbench
names:

- tool name: `manual_eval_workbench/eval_submission`
- trace type: `manual_eval_workbench_submission`

## Guardrails

- Do not move chat-facing manual eval routes as part of web-surface cleanup.
- Do not reintroduce `frontend/`, `ui/`, `apps/portfolio/`, or
  `public/portfolio/` as active standalone web surfaces.
- Do not promote private `docs/peanut/` work into public docs without an
  explicit promotion decision.
- Do not introduce generated artifacts or docs that name the manual eval
  workbench as `ui`.
