# Polinko

Polinko is a local-first GPT assistant app with a FastAPI backend, CLI workflow,
and deterministic eval gates.

## Build Blocks

- Runtime and config: Python runtime with `.env`-driven config loading and
  required key validation (`OPENAI_API_KEY`).
- API backend: FastAPI app for chat, OCR/PDF ingest, retrieval search,
  feedback, and checkpoints, backed by SQLite persistence.
- Chat harness mode: optional deterministic fixture responses for smoke
  testing without model calls (`harness_mode=fixture`).
- UI eval adapter contract is documented in
  `docs/UI_EVAL_ADAPTER_CONTRACT.md` (TypeScript types + endpoint flow).
- Built-in local UI shell has been retired from active runtime. Use backend API
  docs + CLI for active operations.
- Legacy frontend context remains in `docs/live_archive/legacy_frontend/`.
- Eval and quality: deterministic and judge-based eval harnesses under
  `tools/`, plus one-command quality gating.
- Evidence and remediation: evidence indexing and metadata audit tooling with
  open/closed remediation tracking.
- Reference graph visualisation: markdown-native Mermaid graph generated from
  docs links (`make reference-graph`).
- Eval relationship visualisation: markdown-native Mermaid report generated
  from runtime eval data (`make eval-viz`).

## Quick Start

Run from repo root:

```bash
make doctor-env
make server
```

Open:

- `http://127.0.0.1:8000/docs` (backend OpenAPI)

Or open them via `make` targets:

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
1. Optional for UI harness smoke: set
   `POLINKO_CHAT_HARNESS_DEFAULT_MODE=fixture` to default chat requests to
   deterministic fixture mode.

Notes:

- `make` auto-selects interpreter in this order:
  `./polinko-repositioning-system/bin/python`, `./venv/bin/python`, `python3`.
- API key auth is optional for local dev (`POLINKO_SERVER_API_KEY`,
  `POLINKO_SERVER_API_KEYS_JSON`).

## Core Commands

Backend (canonical):

```bash
make server
```

Checks:

```bash
make test
make lint-docs
make backend-gate
make quality-gate
make quality-gate-deterministic
```

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

Single eval targets:

```bash
make eval-retrieval
make eval-file-search
make eval-ocr
make eval-ocr-recovery
make eval-style
make eval-hallucination
make eval-hallucination-deterministic
make eval-clip-ab
make eval-clip-ab-readiness
```

Report-generating variants:

```bash
make eval-retrieval-report
make eval-file-search-report
make eval-ocr-report
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
```

Exit-code semantics:

- `eval-retrieval` and `eval-file-search` return non-zero when cases fail.
- `eval-ocr`, `eval-ocr-recovery`, `eval-style`, `eval-hallucination`, and
  `eval-clip-ab` support strict failure mode (`--strict`) for non-zero gating.
- `make quality-gate` runs strict gating where applicable.

## Evidence and Reference Tooling

Evidence and metadata:

```bash
make evidence-index
make evidence-refresh
make portfolio-metadata-audit
```

Reference graph:

```bash
make reference-graph
```

Eval relationship graph (local runtime data):

```bash
make eval-viz
```

Default output path:

- `.local/visuals/eval_relationship_graph.md`

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
- `docs/live_archive/` live archive for legacy eval/frontend references

## CI

GitHub Actions runs:

- markdown lint (`README.md` + `docs/**/*.md`)
- Python test suite
