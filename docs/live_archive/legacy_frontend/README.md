# Legacy Frontend Reference

This lane records UI context that is no longer an active execution surface.

## Current role

- `frontend/` has been removed from the active repository surface.
- Backend API + CLI + eval tooling are the canonical active surfaces.

## Reference entry points

- historical frontend snapshots are retained through Git history and this lane's
  archive notes.

## Rules

- Do not use frontend behaviour as authoritative eval evidence.
- Any UI maintenance must not drift binary gate contracts.
- Document material UI archival decisions in `docs/DECISIONS.md`.
