<!-- @format -->

# Beta 2.2 Stability Soak (2026-05-09)

## Purpose

This note records the first one-hour deterministic quality soak after the
style-gate instability pass on `nonperformative_working_style_contract`.

The goal was not to get a pretty one-off live pass. The goal was to see whether
the old dominant style pressure still controlled the broader `Beta 2.2` gate.

## Run

- target: `quality-gate-deterministic`
- duration: `3685s`
- cycles: `21`
- pass cycles: `19`
- fail cycles: `2`

Previous broad soak on the same beta gate had finished at:

- `11/21` pass
- `10/21` fail

with `nonperformative_working_style_contract` dominating the failure surface.

## What Changed

- the style lane stayed clean across the soak
- both failing cycles still passed the tracked style surface:
  - `14/14`
- the old dominant style case did not reappear as the broad gate driver

The local style-case adjustment lives in the local eval lane under
`docs/eval/**`. The tracked repo delta for this kernel is the helper-test
coverage plus the resulting state sync.

## Remaining Failure Pressure

The two failing cycles landed in different uncertainty-boundary cases:

- cycle `10`
  - hallucination lane
  - `uncertainty_required_no_relationship_motive_guess`
- cycle `20`
  - response-behaviour lane
  - `explicit_uncertainty_when_context_missing`

That means the remaining pressure is no longer style drift. It is uncertainty
contract precision across two related lanes.

## Read

This is a meaningful `Beta 2.2` shift:

- co-reasoning style stress is now stable enough that it no longer dominates the
  broad gate
- the next stability kernel should target uncertainty-boundary behaviour, not
  return to style farming
- operator burden remains a real thin lane, but it is not the current broad-gate
  pressure point

## Why It Matters

This is the kind of progress Polinko is meant to show:

- not just a passing targeted eval
- a change in what the broad gate actually fails on

The soak did not make the beta fully clean. It did make the repo more truthful
about where the real remaining pressure sits.
