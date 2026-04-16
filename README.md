# Polinko

Polinko is a human-led, AI-assisted research and engineering project. It is a
repo-native AI evaluation lab and local-first GPT assistant app with a FastAPI
backend, CLI workflow, deterministic eval gates, OCR reliability loops, and
evidence-first documentation.

Current release lane: `beta v2.1 - Repo-as-Research`.

Snapshot label for this baseline: `polinko-build-snapshot-040426`.

## Research Project Boundary

This repository is the research project. Tracked README/docs, evals, tests,
runtime contracts, and diagrams are the canonical research documentation.

The public portfolio website is a lightweight about/contact doorway into the
work. Public-facing docs/copy should be derived separately from the canonical
repo docs rather than replacing them.

Polinko uses OpenAI Codex for repo-local engineering collaboration and OpenAI
Platform APIs for model-backed OCR, eval, retrieval, and runtime workflows.
Research direction, evidence interpretation, and publication decisions remain
human-authored.

## Research Notes

If you are reading Polinko as a research portfolio, start with the curated
public path:

- [Research Notes](docs/public/README.md) for the human-readable project map.
- [Method & Authorship](docs/public/METHOD.md) for the collaboration and
  responsibility boundary.
- [Hypothesis](docs/public/HYPOTHESIS.md) for what Polinko investigates.
- [Research](docs/public/RESEARCH.md) for how the proof is organised.
- [Diagrams](docs/public/DIAGRAMS.md) for Mermaid diagrams and curated visual
  evidence pointers.

The website should stay lean: identity, contact, and a link into this repo.
The repo carries the proof: docs, evals, tests, diagrams, and data contracts.
Notebook and query outputs stay local-only unless explicitly promoted.

Tracked governance/runtime docs are part of the working research archive and
continuity system. They are safe to track, but they are not the primary public
reading path.

## Confidentiality Note

This repository intentionally keeps proprietary/local research files untracked.
Folder skeletons are tracked for navigability, while sensitive lane contents
remain ignored via `.gitignore`.

## Build Blocks

- Runtime and config: Python runtime with `.env`-driven config loading and
  required key validation (`OPENAI_API_KEY`).
- API backend: FastAPI app for chat, OCR/PDF ingest, retrieval search,
  feedback, and checkpoints, backed by SQLite persistence.
- Chat harness mode: optional deterministic fixture responses for smoke testing
  without model calls (`harness_mode=fixture`).
- UI eval adapter spec is documented in
  `docs/runtime/RUNBOOK.md` (TypeScript types + endpoint flow).
- Eval and quality: deterministic and judge-based eval harnesses under
  `tools/`, plus one-command quality gating.
- Research-engineering stack: SQLite for local evidence stores, Docker and
  devcontainers for environment portability, Playwright for browser inspection
  and visual captures, Jupyter for local analysis, pytest/markdownlint/GitHub
  Actions for validation, and Make for repeatable operator workflows.
- Portfolio shell build surface:
  - local source scaffold: `frontend/` (ignored except `frontend/.gitkeep`)
  - local generated output: `ui/` (ignored except `ui/.gitkeep`)
  - tracked fallback: in-app about/contact HTML when `ui/index.html` is absent
  - runtime route: `GET /portfolio`
  - public scope: about/contact doorway

## Quick Start

Run from repo root:

```bash
make doctor-env
make server
```

Open:

- `http://127.0.0.1:8000/docs` (backend OpenAPI)

Or open it via `make` target:

```bash
make docs
make open-api-docs
```

## Setup

1. Use a local virtual environment (`./venv` or
   `./polinko-repositioning-system`).
1. Install Python deps: `make deps-install`.
1. Copy env file: `cp .env.example .env`.
1. Set `OPENAI_API_KEY` in `.env`.
1. Optional notebook/viz stack (local/private lane):
   `make notebook-setup`.
1. Optional for harness smoke: set
   `POLINKO_CHAT_HARNESS_DEFAULT_MODE=fixture` to default chat requests to
   deterministic fixture mode.

Notes:

- `make` auto-selects interpreter in this order:
  `./polinko-repositioning-system/bin/python`, `./venv/bin/python`, `python3`.
- activate a local virtual environment shell with:
  `make venv` (alias: `make env`)
- short aliases for long-chain commands:
  `make ocrindex`, `make ocrmine`, `make ocrall`, `make ocrhand`,
  `make ocrtype`, `make ocrillu`, `make ocrstable`, `make ocrwiden`,
  `make ocrwidensync`,
  `make ocrstablegrowth`, `make ocrgrowth`, `make ocrfails`, `make gate`
- Batch-first OCR widening:
  `make ocrwiden` now runs the batched growth lane by default.
  Use `make ocrwidensync` for explicit synchronous fallback.
- OpenAI rate/budget quick openers:
  `make open-cost-console` (or `make open-limits`, `make open-usage`,
  `make open-billing`).
- notebook commands:
  `make notebook-setup`, `make notes` (aliases: `make notebook`, `make nb`)
- Python dependency lock strategy:
  - edit direct dependencies in `requirements.in`
  - regenerate the full lock with `make deps-lock`
  - install from `requirements.lock` with `make deps-install`

## Core Commands

Backend (canonical):

```bash
make server
```

Portfolio shell (canonical frontend flow):

```bash
make portfolio
```

Notebook viz (local/private, ignored output lane):

```bash
make notebook-setup
make notes
```

Local notebook workspace:

- `output/jupyter-notebook/`
- keep notebook outputs untracked unless explicitly promoted as curated
  evidence.

Checks:

```bash
make test
make lint-docs
make backend-gate
make quality-gate
make quality-gate-deterministic
```

Rate/credit hygiene:

- Rate limits (`RPM`/`TPM`) and spend/credits are separate controls.
- Keep interactive checks sync, and run heavy recurring OCR growth with
  `make ocrwiden` (batch-first).
- Watch these three dashboards regularly:
  - Limits (throughput)
  - Usage (token/cost burn)
  - Billing (payment/credits)

## API Surface

Health and metrics:

- `GET /health`
- `GET /metrics`

Chat and sessions:

- `POST /chat`
- `POST /session/reset`
- `GET /chats`
- `POST /chats`
- `GET /chats/{session_id}/messages`
- `PATCH /chats/{session_id}`
- `DELETE /chats/{session_id}`
- `POST /chats/{session_id}/deprecate`
- `GET /chats/{session_id}/export`

Feedback and checkpoints:

- `GET /chats/{session_id}/feedback`
- `POST /chats/{session_id}/feedback`
- `GET /chats/{session_id}/feedback/checkpoints`
- `POST /chats/{session_id}/feedback/checkpoints`

Memory and collaboration:

- `POST /chats/{session_id}/notes`
- `POST /chats/{session_id}/personalization`
- `GET /chats/{session_id}/personalization`
- `GET /chats/{session_id}/collaboration`
- `POST /chats/{session_id}/collaboration/handoff`

`POST /chat` optional harness fields:

- `harness_mode`: `live` (default) or `fixture`
- `fixture_output`: explicit output used only when `harness_mode=fixture`

Skills:

- `POST /skills/ocr`
- `POST /skills/pdf_ingest`
- `POST /skills/file_search`

Eval visualization and surfaces:

- `GET /viz/pass-fail` renders the local OCR fail-signal pulse.
- `GET /viz/pass-fail/data` returns the pulse payload.
- Default pulse source: strict OCR binary gate reports under `.local/eval_reports/`.
- Manual eval warehouse: `.local/runtime_dbs/active/manual_evals.db`
  (`make manual-evals-db`) for integrated Beta 1.0/current manual-eval rows.
- `GET /portfolio/sankey-data` returns the real-data portfolio evidence
  payload: Beta 1.0 manual eval rows from `manual_evals.db`, continuity
  bridge counts, and current OCR binary gate reports from `.local/eval_reports/`.
  It returns an explicit no-data state rather than decorative fallback when
  either source is missing.

## UI Shell Access

- `GET /` redirects to `GET /portfolio`.
- `GET /portfolio` serves the local generated portfolio scaffold when present,
  or a tracked in-app about/contact fallback when `ui/index.html` is absent:
  - current interaction model is pinned-stage stepping
  - current local frontend implementation uses a stacked SVG evidence-map
    FPO at `frontend/src/stacked-evidence-map-fpo.svg`
  - the FPO is an implementation placeholder only; `/portfolio/sankey-data`
    still loads and exposes real-data readiness state
  - public portfolio direction is about/contact; evidence visualizations remain
    repo research instruments
  - flat SVG/D3 Sankey or alluvial view remains the accessibility,
    reduced-motion, performance, and direct-inspection fallback
  - visual weights are normalized for readability across Beta 1.0 and current
    totals; labels/tooltips retain actual source counts
  - WebGL interaction should be drag-to-rotate only; do not capture
    wheel/trackpad gestures inside the canvas
  - no weird headlines, dashboard cards, placeholder copy, invented overlays,
    decorative fake data, or fake/decorative FPO evidence panels
  - explicit no-data behavior when real local sources are unavailable
- frontend shell build contract:
  - `frontend/` and `ui/` are local-only working directories with tracked
    `.gitkeep` placeholders
  - edit source in `frontend/` when the local frontend scaffold is present
  - generate served shell with `make portfolio-build` (writes ignored output to
    `ui/`)
  - use `make portfolio` for the canonical rebuild + serve + system-browser
    open workflow when local frontend source is present; `make rebuild` and
    `make portfolio-rebuild` are aliases for the same human-facing path
  - use `make portfolio-playwright` only for Codex/debug inspection in the
    repo Playwright session; it opens a Playwright tab instead of using the
    human-facing browser command
  - do not hand-edit built files under `ui/`; regenerate them from local
    `frontend/`
- Playwright CLI captures should use the repo wrapper so snapshots/screenshots
  are grouped by local day under `docs/peanut/assets/screenshots/playwright`.
  Use `make pwcli ARGS="open <url>"` for the deterministic default flow; this
  writes a deterministic repo-local config (`.local/logs/playwright/cli.config.json`)
  and uses a fixed default
  session (`polinko`) when no session is provided. Example output path:
  `docs/peanut/assets/screenshots/playwright/DD-MM-YY`.
  Optional explicit session override:
  `make pwcli ARGS="--session <name> open <url>"`.
  Run `make playwright-snapshot-dir` to print the active folder. If passing an
  explicit `--filename`, keep it under that dated folder.

## CLI Modes

Local CLI runner:

```bash
make chat
```

API client:

```bash
python tools/client.py --base-url http://127.0.0.1:8000 --session-id local-dev
```

`tools/client.py` commands:

- `/help`
- `/reset`
- `/ocr [--mode verbatim|normalized] <file>`
- `/pdf <file>`
- `/search <query>`
- `/search-ocr <query>`
- `/search-pdf <query>`
- `/search-chat <query>`
- `/export`

## Eval Harnesses

OCR-forward lane model:

- `lockset` lane: strict release gate (must stay green)
- `growth` lane: fail-tolerant novel-case lane for pass-from-fail tracking

Single eval targets:

```bash
make eval-retrieval
make eval-file-search
make eval-ocr
make eval-ocr-handwriting
make eval-ocr-recovery
make eval-style
make eval-hallucination
make eval-hallucination-deterministic
make eval-clip-ab
make eval-clip-ab-readiness
```

Retrieval retry controls (for transient 429/5xx or connection errors):

```bash
make eval-retrieval RETRIEVAL_REQUEST_RETRIES=2 RETRIEVAL_REQUEST_RETRY_DELAY_MS=750
```

OCR fail-fast control (abort early on sustained 429 streaks):

```bash
make eval-ocr OCR_MAX_CONSEC_RATE_LIMIT_ERRORS=3
```

OCR eval retry controls (for transient OCR 429/5xx or connection errors):

```bash
make eval-ocr OCR_EVAL_OCR_RETRIES=2 OCR_EVAL_OCR_RETRY_DELAY_MS=750
```

Report-generating variants:

```bash
make eval-retrieval-report
make eval-file-search-report
make eval-ocr-report
make eval-ocr-handwriting-report
make eval-ocr-recovery-report
make eval-style-report
make eval-hallucination-report
make eval-clip-ab-report
make eval-reports
make eval-reports-parallel
```

Auxiliary eval tooling:

```bash
make backfill-eval-traces
make calibrate-hallucination-threshold
make cgpt-export-index
make ocr-cases-from-export
make eval-ocr-transcript-cases
make eval-ocr-transcript-cases-growth
make eval-ocr-transcript-cases-handwriting
make eval-ocr-transcript-cases-typed
make eval-ocr-transcript-cases-illustration
make eval-ocr-transcript-stability
make eval-ocr-transcript-stability-growth
make eval-ocr-transcript-growth
```

Exit-code semantics:

- `eval-retrieval` and `eval-file-search` return non-zero when cases fail.
- `eval-ocr`, `eval-ocr-recovery`, `eval-style`, `eval-hallucination`, and
  `eval-clip-ab` support strict failure mode (`--strict`) for non-zero gating.
- `make quality-gate` runs strict gating where applicable.
- handwriting lane:
  - expects a local cases file at `.local/eval_cases/ocr_handwriting_eval_cases.json`
    (override via `OCR_HANDWRITING_CASES=<path>`).
  - cases should use real `image_path` entries (no `text_hint`).
  - requires `POLINKO_OCR_PROVIDER=openai` for true image OCR behaviour.

Transcript-backed OCR mining lane:

- index a local ChatGPT export (local-only artifacts):
  - `make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
- mine transcript-backed OCR cases from correction/confirmation turns:
  - `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
- run OCR eval against mined transcript cases:
  - `make eval-ocr-transcript-cases`
  - `make eval-ocr-transcript-cases-handwriting`
  - `make eval-ocr-transcript-cases-typed`
  - `make eval-ocr-transcript-cases-illustration`
- run OCR decision-stability replay on mined transcript cases:
  - `make eval-ocr-transcript-stability OCR_STABILITY_RUNS=3`
- default local outputs:
  - `.local/eval_cases/cgpt_export_attachment_index.json`
  - `.local/eval_cases/ocr_transcript_cases_all.json`
  - `.local/eval_cases/ocr_handwriting_from_transcripts.json`
  - `.local/eval_cases/ocr_typed_from_transcripts.json`
  - `.local/eval_cases/ocr_illustration_from_transcripts.json`
  - `.local/eval_cases/ocr_transcript_cases_review.json`
  - `.local/eval_reports/ocr_transcript_stability.json`
  - `.local/eval_reports/ocr_stability_runs/`

Eval interpretation rules:

- FAIL pressure is first-class research signal; pass-only summaries are not
  sufficient for eval observability.
- Manual eval notes remain a human interpretation layer and may capture
  qualitative issues such as factuality, tone, usefulness, or whimsy delivered
  as fact.
- Transcripts, screenshots, and raw reports are source evidence; decisions are
  the binding interpretation layer over that evidence.

## Docker Smoke Test

```bash
make docker-build
make docker-run
```

Defaults:

- image: `polinko:dev`
- host port: `8000` (`DOCKER_PORT` override)
- env file: `.env` (`ENV_FILE` override)

## Project Layout

- `app.py` CLI entrypoint
- `server.py` API entrypoint
- `api/` API implementation
- `core/` runtime logic
- `tools/` operational and eval scripts
- `tests/` unit and integration tests
- `docs/public/` public-facing guide layer derived from canonical docs
- `docs/` architecture, runbook, decisions, state
- `docs/eval/` beta lanes and active eval cases

## CI

GitHub Actions runs:

- markdown lint (`README.md` + `docs/**/*.md`)
- Python test suite
