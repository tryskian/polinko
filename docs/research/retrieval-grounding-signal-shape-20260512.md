<!-- @format -->

# Retrieval Grounding Signal Shape (2026-05-12)

## Purpose

This note records the next earned visibility step for Polinko's retrieval
grounding surfaces.

The retrieval and file-search lanes were already green, but they were still
mostly visible as old pass counts rather than as a current structured proof
surface.

This kernel refreshes both tracked artifacts and makes the retrieval lane
readable as current evidence instead of inherited baseline.

## Current Tracked Surface

Fresh tracked artifacts:

- [retrieval-20260512-190149.json](../eval/beta_2_0/retrieval-20260512-190149.json)
- [file-search-20260512-190149.json](../eval/beta_2_0/file-search-20260512-190149.json)

Current results:

- retrieval:
  - total: `12`
  - pass: `12`
  - fail: `0`
  - global miss: `0`
  - session leak: `0`
- file search:
  - total: `5`
  - pass: `5`
  - fail: `0`
  - scoped miss: `0`
  - global miss: `0`
  - scoped leak: `0`

## Lane Shape

The visible retrieval-grounding surface now has two complementary branches:

- retrieval recall branch
  - global recall from seeded evidence
  - session isolation
  - no cross-session leak
  - source-bound recall phrases
- file-search branch
  - scoped search hit
  - global search hit
  - no scoped distractor leak
  - mixed source methods:
    - OCR
    - PDF
    - image-context

That is a better public read than "retrieval passes" because it shows what
kind of grounding is actually being enforced.

## Current Read

The important result is not just that the lane is green.

The lane now visibly shows that Polinko is enforcing retrieval grounding in two
different ways:

- memory-style recall must stay source-bound and leak-free
- file-search recall must stay scoped, recoverable, and source-type aware

There is no active failure pressure in this lane right now.

## Why It Matters

This is real method progress because retrieval grounding is now readable as a
current proof surface:

- current tracked artifacts match current repo truth
- the lane has a visible two-branch structure
- the console can point to a current retrieval-grounding note for both the
  retrieval and file-search cards

That makes retrieval easier to read as a live Polinko lane rather than a quiet
background green check.
