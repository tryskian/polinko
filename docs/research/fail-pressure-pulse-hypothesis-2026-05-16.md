<!-- @format -->

# Fail-Pressure Pulse Hypothesis

Date: `2026-05-16`

## Boundary

This is a hypothesis-only method note for non-OCR evals.

It does not change OCR.

It proposes a different unit of judgment for bounded non-OCR runs:

- the run is the binary unit
- the items are evidence inside the run
- the run verdict is `PASS` or `FAIL`

Current beta rollout may start in language, but the same method can also apply
to logic-heavy runs such as Huemiliator.

## Claim

Non-OCR evals should run as bounded pulses under fail pressure when run-level
shape matters more than single-row replay.

- start small:
  - around `15` rows
- treat the pulse as the unit that carries the verdict
- treat the rows as evidence inside the pulse:
  - anchor
  - counted seam
  - excluded noise[^excluded-noise-taxonomy]
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

## Exclusion Controls

- raw pulse count stays visible
- counted pulse count stays visible
- every excluded item needs a narrow reason
- excluded items stay reviewable after the pulse
- a pulse verdict should always be readable against both:
  - the raw pulse
  - the counted pulse

## Scope

- non-OCR evals
- useful for language and logic-heavy runs where shortcut pressure, commentary
  drift, or seam density matter more than single case replay

## What This Would Change

- binary judgment would move from the row to the pulse
- counted seam density would matter more than isolated wins
- exclusion review would become part of pulse hygiene
- larger non-OCR batches would have to earn themselves through stabilized
  smaller pulses

[^excluded-noise-taxonomy]: If this hypothesis graduates into procedure,
  excluded noise should use a tight shared reason taxonomy so pulse cleanup
  stays auditable.
