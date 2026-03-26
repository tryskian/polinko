# Build Audit Log

Purpose: inspect the existing build block-by-block in execution order, fix concrete drift, and keep a fresh-path baseline without a hard reset.

## Block 1: README (entry surface)

Status: complete

Actions:

- Rewrote `README.md` into current-state build blocks.
- Removed duplicated/stale eval narrative sections.
- Aligned command lists with live `Makefile` targets and API routes.

Validation:

- `npx markdownlint-cli2 README.md` pass.

## Block 2: Makefile target wiring

Status: complete

Actions:

- Audited all `$(PYTHON) -m tools.*` modules referenced by `Makefile`.
- Found a fresh-clone gremlin: `eval-cleanup` depended on local-only script.
- Patched `eval-cleanup` to skip gracefully when `tools/cleanup_eval_chats.py` is missing.

Validation:

- `make eval-cleanup` pass.

## Block 3: Local lint parity with CI

Status: complete

Actions:

- Found drift: local `make lint-docs` did not lint `README.md`, while CI does.
- Updated root `package.json`:
  - `lint:docs` from `markdownlint-cli2 docs/**/*.md`
  - to `markdownlint-cli2 README.md docs/**/*.md`

Validation:

- `make lint-docs` pass.

## Block 4: Runtime sanity checks

Status: complete

Validation:

- `make doctor-env` pass.
- `make test` pass (`162` tests).
- `make ui-build` pass.

## Block 5: API contract surface audit

Status: complete

Actions:

- Diffed live FastAPI routes in `api/app_factory.py` against README endpoint documentation.
- Confirmed route coverage parity for health, chat/session, feedback/checkpoints,
  skills, and collaboration endpoints.

Validation:

- route-diff check: no contract mismatch after method normalisation.

## Block 6: Eval harness contract audit

Status: complete

Actions:

- Verified CLI surfaces for eval modules (`--help` checks).
- Documented non-zero semantics in `README.md`.
- Added automated guard checks via `tools/audit_build_blocks.py`
  and `make build-audit`.

Validation:

- `make quality-gate-deterministic` pass (tests + retrieval + file-search + OCR
  strict + style strict + hallucination strict deterministic).

## Block 7: Evidence pipeline audit

Status: complete

Actions:

- Executed full evidence refresh flow (`index` + metadata strict audit).
- Confirmed summary reporting and triage override handling run without failures.

Validation:

- `make evidence-refresh` pass (`errors=0`, `warnings=1`, summary emitted).

## Block 8: Human reference pipeline audit

Status: complete

Actions:

- Rebuilt local human reference database from current local corpus.
- Queried latest entries to confirm query/read path and category mapping.

Validation:

- `make human-reference-db` pass.
- `make human-reference-latest` pass.

## Block 9: CI and Docker audit

Status: complete

Actions:

- Confirmed local markdown lint now matches CI scope (`README.md` + `docs/**/*.md`).
- Built production image and ran live `/health` smoke against container runtime.

Validation:

- `make lint-docs` pass.
- `make docker-build` pass.
- container smoke check pass (`GET /health` -> `{\"status\":\"ok\"}`).

## Next Blocks (in order)

1. Docs propagation:
   update `RUNBOOK`, `STATE`, `SESSION_HANDOFF`, `DECISIONS` only for material deltas from the completed blocks.
