<!-- @format -->

# Response-Behaviour Stability Snapshot

Date: `2026-04-25`

## Purpose

This note records the tracked response-behaviour lane that keeps directness,
uncertainty, and bounded-claim behaviour inspectable in a deterministic eval
surface.

## Tracked Delta

Tracked artifacts for this lane:

- [response-behaviour-20260425-175025.json](../eval/beta_2_0/response-behaviour-20260425-175025.json)
- `docs/eval/beta_2_0/response_behaviour_eval_cases.json`

## Validation

- `make eval-response-behaviour-report`
- tracked snapshot:
  - `7/7` pass
  - `0` fail
  - deterministic evaluation mode

## Current Read

Response-behaviour stability is operationalized as a directness and
bounded-claim lane.

The tracked lane currently covers:

- no false action claims on repo change
- explicit uncertainty when context is missing
- no fake live claims without verification
- direct low-context greeting
- concise fact without wrapup
- no therapeutic roleplay overreach
- no memory pretend claim

The useful remaining signal is still the first case:
`no_false_action_claim_on_repo_change` failed on attempt one before recovering
on attempts two and three. That is a visible wobble, not an active failing
lane.

## Why This Matters

Polinko can show that direct and source-bound response behaviour is measured in
tracked evals, not left as an informal style preference.
