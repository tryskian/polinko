<!-- @format -->

# Uncertainty-Boundary Stability Kernel (2026-05-09)

## Purpose

This note records the `Beta 2.2` stability kernel that followed the first
one-hour soak where the broad gate no longer failed on style drift.

The next narrow question was whether the remaining broad-gate pressure in:

- `uncertainty_required_no_relationship_motive_guess`
- `explicit_uncertainty_when_context_missing`

was coming from tracked matcher limits, from local case-anchor drift, or from a
real model-regression seam.

## Tracked Runtime Changes

The tracked repo delta for this kernel is narrow and behavioural:

- [tools/eval_response_behaviour.py](../../tools/eval_response_behaviour.py)
  - required phrase matching now accepts short token-gap variants instead of
    only exact contiguous substrings
- [tools/eval_hallucination.py](../../tools/eval_hallucination.py)
  - forbidden-phrase detection now ignores clearly negated evidence framing such
    as `no clear evidence` and `not enough evidence`
- targeted coverage was added in:
  - [tests/test_eval_response_behaviour.py](../../tests/test_eval_response_behaviour.py)
  - [tests/test_eval_hallucination.py](../../tests/test_eval_hallucination.py)

## Local Eval-Lane Clarifications

Two local eval-case clarifications were also required under ignored
`docs/eval/**` surfaces:

- `explicit_uncertainty_when_context_missing`
  - widened anchor families to accept correct variants such as `no saved
    record`, `stored notes`, and `nothing was saved`
- `co_reasoning_not_summary_mode`
  - widened the local co-reasoning anchor family so the deterministic gate
    accepts natural variants like `shared process`, `prefab`, `preset`, and
    `fixed frame`

Those local clarifications are real evidence about case design, but they are not
part of the tracked repo delta.

## Current Read

Current checkpoint:

- a fresh `make quality-gate-deterministic` rerun passed cleanly
- a restarted deterministic sidecar soak was then run for `2695s`
- stopped clean for EOD at:
  - `14/14` pass cycles
  - `0` fail cycles
  - `0` recurring failure signals

That is enough to say the uncertainty-boundary kernel is behaving like a real
stability pass rather than another one-off live green.

It is not yet a full one-hour closure, because the run was stopped early for
end-of-day wind-down.

## Why This Matters

This kernel matters for the beta read because it clears two different kinds of
false pressure:

- tracked matcher seams that were rejecting correct uncertainty behaviour
- local case-anchor seams that were too literal for natural co-reasoning output

If the next slice finishes a full one-hour soak cleanly, `Beta 2.2` moves from
`style pressure retired, uncertainty now dominant` to `broad gate currently
holding across style, uncertainty, and co-reasoning`.
