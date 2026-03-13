# Nautorus

Fresh scaffold baseline for the Nautorus build.

## Purpose

- Establish a clean trunk after Polinko-era complexity.
- Rebuild in small, validated slices.
- Keep evidence and decision traceability from day one.

## Archived Polinko Build

The legacy build is intentionally frozen and retained for reference:

- In this repo:
  - branch: `archive/polinko-full-build-2026-03-13`
  - tag: `polinko-build-frozen-2026-03-13`
  - frontend branch: `archive/polinko-frontend-2026-03-13`
  - frontend tag: `polinko-frontend-frozen-2026-03-13`
- Separate snapshot repo:
  - `https://github.com/tryskian/polinko-build-snapshot`

Frontend work from Polinko is frozen for historical reference. New UI
work should be rebuilt in OpenAI-native ecosystem flows.

## Quickstart

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `make test`
5. `make run`

## Repo Structure

- `nautorus/` core scaffold package
- `tests/` baseline test harness
- `docs/` control-plane docs
