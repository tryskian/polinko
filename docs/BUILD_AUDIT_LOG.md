# Build Audit Log (2026-03-27)

Purpose: confirm active build surfaces are clean, artifact-free, and matched to current docs/contracts.

## Scope

- Legacy human-reference + workbench artifacts
- Make targets vs tools
- Root/hidden noise (DB files, caches)

## Findings & Remediations

- Removed runtime DB scripts/targets during wiring lock; no local DB commands remain.
- Deleted lingering root DB artifacts (`.polinko_history.db`, `.polinko_vector.db`); none remain in repo.
- Pruned workbench legacy: removed `tools/workbench_server.py` and Make target.
- Archived human-reference tooling: moved `build_human_reference_db.py`, `query_human_reference.py`, `human_reference_queries.sql` to `docs/live_archive/legacy_human_reference/` and updated references.
- Updated ignores to cover remaining runtime artefact noise only.
- `tools/audit_build_blocks.py` checks removal of legacy targets; `python -m tools.audit_build_blocks` passes.

## Validation

- `python -m tools.audit_build_blocks` (pass)
- `python -m unittest tests/test_config.py` (pass)
- `ruff check tools/manage_local_dbs.py config.py tests/test_config.py` (pass)
- `python -m unittest tests/test_config.py tests/test_eval_trace_artifacts.py` (pass)

## Folder-by-folder audit pass (2026-03-27)

- `api/`: clean active runtime/API surface.
- `core/`: clean active runtime logic surface.
- `tests/`: clean; no legacy-target regressions.
- `tools/`: removed orphaned legacy helper `tools/import_transcripts.py`; active tools all referenced.
- `docs/`: updated active docs for archive/reset DB lifecycle and benchmark framing; legacy SQL is archive-only under `docs/live_archive/legacy_human_reference/`.
- root artefacts: no `.db`/`.sqlite` files present; only archive SQL remains in live archive.

## Outstanding

- None identified; working tree holds unstaged cleanup changes ready to commit.
