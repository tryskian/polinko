# Legacy Human Reference (Archived)

This lane preserves the previous SQLite-based human-reference workflow for
traceability only.

## Status

- Archived from active operations.
- Non-authoritative for runtime or eval gate decisions.
- Replaced by markdown-native graph visualisation:
  - `make reference-graph`
  - output: `docs/REFERENCE_GRAPH.md`

## Archived Materials

- `HUMAN_REFERENCE_DB.md`
- previous helper scripts:
  - `docs/live_archive/legacy_human_reference/build_human_reference_db.py`
  - `docs/live_archive/legacy_human_reference/query_human_reference.py`

## Rule

Do not use archived human-reference DB outputs as release evidence for active
build decisions.
