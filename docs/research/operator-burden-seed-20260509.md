<!-- @format -->

# Operator Burden Seed Snapshot

Date: `2026-05-09`

## Boundary

This is the first tracked operator-burden row surface.

It is intentionally narrow:

- human-owned
- row-local
- binary first gate
- explicit post-fail `retain` / `evict`

It is not a large automated eval family yet.

## Seeded Rows

### `ob-rd-001` Direct mapping collapsed into advisory commentary

- Source lineage:
  - local experiment `R-D`
  - local operator note:
    - `docs/peanut/research/experiment_R-D_operator_burden_shift_2026-03-28.md`
- Task shape:
  - direct mapping
- Expected boundary:
  - `match A to B`
  - no style interpretation
  - no qualitative reframing
  - clear binary decision
- Observed pattern:
  - qualitative critique replaced direct mapping
  - hedging and fuzzy percentages replaced decision clarity
- Verdict:
  - `fail`
- Post-fail disposition:
  - `retain`
- Why retained:
  - this is real in-scope burden evidence, not a malformed case

### `ob-rd-002` Sparse-control contract preserved execution clarity

- Source lineage:
  - tracked decision `D-158`
  - local primary-source transcript:
    - `docs/peanut/transcripts/co_reasoning/13_pattern_learning_over_prescriptive_instruction_2026-04-03.md`
- Task shape:
  - sparse-control execution
- Expected boundary:
  - objective + hard acceptance checks + example signals
  - no advisory overload
- Observed pattern:
  - assistant accepted the sparse-control contract
  - execution stayed tied to objective and checks
  - extra prescriptive overhead was avoided
- Verdict:
  - `pass`

## Current Read

- operator burden is no longer only a hypothesis note
- it now has a tracked seed surface with contrast:
  - `1` retained fail row
  - `1` pass row
- export-backed cue widening now surfaces:
  - `9` candidate conversations
  - `8` conversation families
- the lane is still thin
- the next work is row expansion from the widened backlog, not bigger
  automation

## Why This Matters

This gives Polinko a real non-OCR thin lane that matches the Beta 2.2 contract:

- `pass` / `fail`
- then, if `fail`, `retain` / `evict`

That is a better starting point than pretending operator burden is ready for a
full automated runner before the evidence surface is mature enough.
