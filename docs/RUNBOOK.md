# Runbook

## Rotate API Keys

1. Update `.env` with new `OPENAI_API_KEY`.
2. If used, rotate `POLINKO_SERVER_API_KEY` and/or update `POLINKO_SERVER_API_KEYS_JSON`.
3. Restart running API/CLI processes.

## Reset Local Session Memory

1. Stop running processes.
2. Remove local DB files:
   - `.polinko_memory.db`
   - `.polinko_memory.db-shm` (if present)
   - `.polinko_memory.db-wal` (if present)
3. Start app again (`make chat` or `make server`).

## Evaluate Prompt Stability

1. Run `make eval`.
2. If failures appear, inspect `configs/golden_prompts.json` and prompt text in `core/prompts.py`.

## Run API Tests

1. Run `make test`.
2. Fix failures before merging.

## Common Connection Error

Symptom:

- `FAIL: connection error` during eval or chat.

Checks:

1. Confirm internet access and no firewall/VPN block.
2. Confirm `OPENAI_API_KEY` is set in `.env` (and set as GitHub Actions secret `OPENAI_API_KEY` for CI eval).
3. Retry command after a short wait.
