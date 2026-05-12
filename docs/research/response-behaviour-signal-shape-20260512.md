<!-- @format -->

# Response-Behaviour Signal Shape (2026-05-12)

## Purpose

This note records the next earned visibility step for Polinko's
response-behaviour lane.

The lane was already green, but the visible tracked surface was still an older
April snapshot and a short eval note. Repo truth had moved forward; the lane
needed a fresh tracked artifact and a clearer public shape showing what kinds
of behaviour boundaries are actually being enforced.

## Current Tracked Surface

Fresh tracked response-behaviour snapshot:

- [response-behaviour-20260512-195350.json](../eval/beta_2_0/response-behaviour-20260512-195350.json)

Current result:

- total cases: `7`
- pass: `7`
- fail: `0`
- attempts per case: `3`
- minimum pass attempts required: `2`

## Lane Shape

The visible response-behaviour lane now has two branches:

- verification and uncertainty boundaries
  - no false action claim on repo change
  - explicit uncertainty when context is missing
  - no fake live claim without verification
  - no memory-pretend claim
- interaction-shape boundaries
  - direct low-context greeting
  - concise fact without wrap-up
  - no therapeutic roleplay overreach

That is a better public read than "response behaviour passes" because it shows
the concrete behaviour constraints the lane is testing.

## Current Read

The important result is not only the pass count.

The lane now visibly shows that Polinko is holding two different surfaces at
once:

- verification discipline under missing or unverifiable context
- concise non-performative interaction shape under low-context or emotionally
  loaded prompts

The old repo-action wobble did not recur in this fresh tracked run.

## Why It Matters

This is real method progress because the response-behaviour lane is now
readable as a current proof surface:

- the tracked snapshot matches current repo truth
- the lane has a visible internal structure
- the evidence console can point to a current signal note instead of only the
  older April snapshot note

That makes response behaviour easier to read as a live Polinko lane rather than
an inherited baseline report.
