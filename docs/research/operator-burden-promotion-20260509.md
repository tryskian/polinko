<!-- @format -->

# Operator Burden Row Promotion (2026-05-09)

## Purpose

This note records the first row-promotion pass after the operator-burden miner
was widened around export-native control-contract language.

The goal was to turn the widened backlog into judged row-local evidence instead
of letting it stay as a candidate list only.

## Promoted Rows

Added to `docs/eval/beta_2_0/operator_burden_rows.json`:

- `ob-rd-003`
  - `pass`
  - raw pull preserved no-commentary retrieval boundary
- `ob-rd-004`
  - `pass`
  - protocol lock preserved no-commentary execution
- `ob-rd-005`
  - `fail`
  - `retain`
  - direct-pull request had to correct interpretive rundown drift
- `ob-rd-006`
  - `pass`
  - exact-as-provided preference preserved low-burden document handling
- `ob-rd-007`
  - `fail`
  - `evict`
  - archive-quoted raw-pull clone should be removed from distinct row evidence

## Current Row Surface

The tracked operator-burden surface now holds:

- rows: `7`
- pass: `4`
- fail: `3`
- retained fail: `2`
- evict: `1`

## Read

This is a better thin-lane shape than the initial seed:

- there is now more than one pass-side control anchor
- there is now more than one retained fail anchor
- the retained fail pressure is still about interpretive or advisory drift, not
  about runtime fragility
- the contract now has a real `evict` example instead of only described
  semantics
- duplicate archive-quoted raw-pull matches can now be evicted upstream instead
  of being promoted as fake new evidence

That means the next operator-burden step is still:

- promote more rows from the widened backlog
- keep the lane human-owned and row-local
- do not jump to a larger automated runner yet

## Why It Matters

This makes operator burden more legible as a real Polinko lane.

It is no longer just:

- one manual failure note
- one contrast pass row
- one mined backlog

It is now a small judged surface with repeated shape:

- exact retrieval and protocol-lock cases can pass cleanly
- interpretive drift remains retainable fail pressure when it pulls execution
  away from direct work
- archive-quoted duplicate matches can be evicted when they are not distinct
  operator-burden evidence
