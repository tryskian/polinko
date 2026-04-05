# Polinko

Polinko is a local-first GPT assistant app with a FastAPI backend, CLI workflow,
and deterministic eval gates.

Current release lane: `beta v2.0`.

Snapshot label for this baseline: `polinko-build-snapshot-040426`.

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
1. Install Python deps: `pip install -r requirements.txt`.
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

## Core Commands

Backend (canonical):

```bash
make server
```

Notebook viz (local/private):

```bash
make notebook-setup
make notes
```

Starter notebook:

- `output/jupyter-notebook/ocr-eval-live-filters-starter.ipynb`
  (live filters/sliders + instant chart/table updates).

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
- `docs/` architecture, runbook, decisions, state
- `.archive/live_archive/` live archive for legacy eval/frontend references

## CI

GitHub Actions runs:

- markdown lint (`README.md` + `docs/**/*.md`)
- Python test suite
