<!-- @format -->

# Retrieval Grounding Snapshot

Date: `2026-03-28`

## Purpose

This note records the tracked retrieval-grounding surface that keeps retrieval
and file-search claims source-bound and inspectable inside Beta 2.0.

## Tracked Delta

Tracked artifacts for this lane:

- [retrieval-20260328-184111.json](../eval/beta_2_0/retrieval-20260328-184111.json)
- [file-search-20260328-184143.json](../eval/beta_2_0/file-search-20260328-184143.json)
- [retrieval_eval_cases.json](../eval/beta_2_0/retrieval_eval_cases.json)
- `docs/eval/beta_2_0/file_search_eval_cases.json`

## Validation

- `make eval-retrieval-report`
- `make eval-file-search-report`
- retrieval report:
  - `12/12` pass
  - `0` global miss
  - `0` leak
- file-search report:
  - `5/5` pass
  - `0` scoped miss
  - `0` global miss
  - `0` scoped leak

## Current Read

Retrieval grounding is operationalized across two connected surfaces:

- retrieval eval proves global recall plus session isolation
- file-search eval proves scoped and global lookup across OCR, PDF, and image
  context sources

The tracked lane currently covers:

- OCR-seeded cross-session recall
- session isolation without cross-session leak
- scoped file-search hits
- PDF-grounded lookup
- image-context smoke

## Why This Matters

Polinko can now claim inspectable retrieval grounding with explicit leak and
miss counters instead of treating retrieval as a hidden capability claim.

This lane is operationalized and stable. It does not currently need a new
promotion step because the visible pressure is elsewhere.
