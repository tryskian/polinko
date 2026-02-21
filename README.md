# Polinko

Lightweight GPT agent project with:

- CLI chat runner
- FastAPI backend
- Prompt regression checks

## Quickstart

Run these from repo root:

1. `make chat`
2. `make server`
3. `make eval`
4. `make test`

Data leverage commands (from normalized ledger exports):

1. `make build-eval-seed LEDGER_INPUT=path/to/transcript_turns.csv`
2. `make build-memory-facts LEDGER_INPUT=path/to/transcript_turns.csv`

## Setup

1. Create and activate your virtualenv (or use the existing one in this repo).
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill real values.
   Optional: configure a key ring with `POLINKO_SERVER_API_KEYS_JSON` for
   per-principal API keys.
4. Optional: use pinned dependencies with
   `pip install -r requirements.lock`.

## Project Layout

- `app.py` CLI entrypoint
- `server.py` API entrypoint
- `api/` API implementation
- `core/` runtime logic
- `tools/` local scripts
- `configs/` regression cases
- `docs/` project docs

## CI

GitHub Actions runs:

- unit tests on every push and PR
- regression eval when `OPENAI_API_KEY` repository secret is configured
