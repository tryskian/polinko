<!-- @format -->

# Operator Burden Signal Shape (2026-05-12)

## Purpose

This note records the next earned operator-burden move after the first seeded
rows and the export-backed miner widening pass.

The question was no longer "can we find more operator-burden cases?" The
question was:

- does the current backlog still earn distinct row promotion?
- or is the right move to make the existing thin lane more legible instead of
  inflating it with duplicates?

## Current Tracked Surface

The row-local lane currently holds:

- `4` pass anchors
- `2` retained fail rows
- `1` evicted fail row

That is enough to show real repeated shape:

- low-burden execution can hold under sparse-control, raw-pull, protocol-lock,
  and exact-output boundaries
- real fail pressure still comes from interpretive or advisory drift
- duplicate archive-quoted matches can be evicted instead of being promoted as
  fake new evidence

## Current Backlog Read

The current top export-backed slice is mostly duplicate family pressure, not
new task-shape pressure.

The remaining visible candidates mostly map back to rows already represented:

- raw-pull / no-commentary clones map back to:
  - `ob-rd-003`
  - `ob-rd-007`
- protocol-lock / no-commentary execution maps back to:
  - `ob-rd-004`
- direct-pulls instead of interpretation maps back to:
  - `ob-rd-005`
- exact-as-provided preference maps back to:
  - `ob-rd-006`

So the current slice does **not** earn more row promotion.

## Earned Delta

This kernel therefore changes the lane shape in a different way:

- the report surface now shows pass anchors, not only retained/evicted failures
- the public diagram surface now has an operator-burden signal-shape diagram
- the tracked docs now say directly that the current top slice is
  duplicate-heavy

That is a better use of the lane than raising row counts with clone evidence.

## Why It Matters

This is real progress because it makes the thin lane readable as a research
instrument.

Operator burden now shows:

- what clean low-burden control surfaces look like
- what retained fail pressure still looks like
- what should be evicted upstream
- and when to stop farming more rows from the same family shape

That keeps the lane aligned with the Beta 2.2 contract:

- `pass` / `fail`
- then, after `fail`, `retain` / `evict`

It also keeps the next move honest:

- wait for a distinct task shape
- or improve visibility
- but do not pretend duplicate backlog families are fresh evidence
