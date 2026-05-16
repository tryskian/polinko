<!-- @format -->

# Language Pulse Hypothesis

Date: `2026-05-16`

## Boundary

This is a hypothesis-only method note for language evals.

It does not change OCR.

It proposes a different unit of judgment for language runs:

- the run is the binary unit
- the items are evidence inside the run
- the run verdict is `PASS` or `FAIL`

## Claim

Language evals should run as bounded pulses under fail pressure.

- start small:
  - around `15` rows
- treat the pulse as the unit that carries the verdict
- treat the rows as evidence inside the pulse:
  - anchor
  - counted seam
  - excluded noise
- grow pulse size only after the passing shape starts to stabilize

## Why

- fail pressure at the root deters shortcut-seeking
- small pulses keep judging cheap and fresh
- row evidence still stays inspectable
- one lucky row cannot make the whole run look healthier than it is

## Proposed Judgment Shape

- judge item evidence first:
  - anchor
  - counted seam
  - excluded noise
- remove excluded noise from the real pulse count
- judge the pulse after evidence cleanup:
  - more counted seams than anchors: `FAIL`
  - more anchors than counted seams: `PASS`
  - tie: `FAIL`

## Scope

- language evals only
- not OCR
- useful where shortcut pressure and commentary drift matter more than single
  case replay

## What This Would Change

- binary judgment would move from the row to the pulse
- counted seam density would matter more than isolated wins
- larger language batches would have to earn themselves through stabilized
  smaller pulses
