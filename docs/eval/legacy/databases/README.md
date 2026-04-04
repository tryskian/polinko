# Legacy Databases

Legacy database snapshots are expected in this lane when recovered.

## Current Scan Result

- No legacy `.db` files are present in tracked repo paths.
- Snapshot check (`polinko_snapshot/main`, commit `fc8de944f61caf2cd688990a59d26c8ddff28c83`)
  also contains no tracked `.db` files.
- Only active runtime DBs are present:
  - `.local/runtime_dbs/active/history.db`
  - `.local/runtime_dbs/active/memory.db`
  - `.local/runtime_dbs/active/vector.db`
  - `.local/runtime_dbs/active/eval_viz.db`

## Placement Rule

- If legacy DB snapshots are restored, place metadata/docs references here.
- Keep raw DB files local-only unless explicitly approved for tracking.

## Wiring References (Recovered from Cleanup Archive)

- `.archive/live_archive/legacy_coordination/POLINKO_WORKFLOW_peanut_refs_pre_move.md`
  - DB path map for:
    - `history.db`
    - `memory.db`
    - `vector.db`
    - `eval_viz.db`
  - query-oriented sections:
    - `A) history.db`
    - `B) memory.db`
    - `C) vector.db`
    - `D) eval_viz.db`
