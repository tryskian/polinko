<!-- @format -->

# OCR Retry Execution Gate

Status: `designed-only`

This page defines the future OCR retry execution gate. It is not an active run
command. The current executable surface remains read-only through
`make manual-evals-ocr-retry-execution-readiness`.

## Current Boundary

- No OCR retry execution Make target exists yet.
- No OCR rerun happens from this design note.
- No feedback row is closed from this design note.
- No live eval row is written from this design note.
- No manual eval warehouse mutation happens from this design note.

The next implementation kernel may add an execution command only after this
contract is reviewed from clean `main`.

## Proposed Command Shape

The future command should be explicit and hard to run by accident:

- target:
  - `make manual-evals-ocr-retry-execute`
  - alias: `make manualdb-ocr-retry-execute`
- required inputs:
  - `SELECTION_PATH=<path>`
  - `CONFIRM=ocr-retry-execute`
- optional narrowing:
  - `ARTIFACT_IDS=<artifact_id[,artifact_id...]>`
  - `LIMIT=<n>`
  - `OUTCOME=<outcome>`
  - `COHORT=<cohort_id>`
- optional output:
  - `EXECUTION_DIR=<path>`
  - default should be an ignored local lane under
    `.local/manual_eval_runs/ocr_retry/`

The command must recompute readiness inside the same process. It must not trust
a stale readiness JSON copied from a prior run.

## Required Preconditions

Execution is allowed only when all of these are true:

1. `SELECTION_PATH` exists and points to a local decision JSON file.
2. selection validation reports `state=ok`.
3. selection apply-preview reports `state=ok`.
4. execution readiness reports `state=ready`.
5. every selected `rerun_input` or `curated_case` artifact has:
   - a stable artifact ID
   - an existing source file
   - payload inputs with `operation=ocr_retry_rerun_or_case_curation`
   - a payload-only command preview
6. at least one executable item exists.
7. the operator provided the exact confirmation token.

`context_only` decisions stay non-executing. They can be included in the
selection file for bookkeeping, but the execution command must not run OCR for
them.

## First Mutation Target

The first implementation should write only a local execution bundle:

- `.local/manual_eval_runs/ocr_retry/<run_id>/manifest.json`
- `.local/manual_eval_runs/ocr_retry/<run_id>/requests.jsonl`
- `.local/manual_eval_runs/ocr_retry/<run_id>/responses.jsonl`
- `.local/manual_eval_runs/ocr_retry/<run_id>/summary.json`

The bundle should record:

- source selection path
- source decision fingerprint
- readiness schema version
- selected artifact IDs
- source file paths
- OCR provider and model configuration
- request payload metadata
- response status and extracted text preview
- per-item success or failure
- zero warehouse mutation state

The first implementation must not close feedback, write live eval rows, or
refresh `manual_evals.db`. Those are separate follow-up gates.

## Rollback Story

For the first implementation, rollback is local-file cleanup:

1. Remove the generated run bundle under `.local/manual_eval_runs/ocr_retry/`.
2. Keep the original `SELECTION_PATH` unchanged.
3. Re-run `make manual-evals-ocr-retry-execution-readiness` to confirm the
   source selection still resolves.

If a later kernel adds database mutation, that kernel must add backup-first
behavior under `.local_archive/` before mutation and document restore steps in
this file.

## Failure Handling

The future command should fail closed:

- missing confirmation token: exit non-zero before any provider call
- validation/apply-preview/readiness not ready: exit non-zero before any
  provider call
- missing source file: exit non-zero before any provider call
- partial provider failure: write the local run bundle and mark failed items,
  but do not close feedback or mutate the warehouse
- rate limit or provider outage: stop remaining items and write a summary with
  retry-after/backoff evidence when available

## Validation Contract

The implementation kernel that adds execution must include tests proving:

- readiness is recomputed from current source truth
- missing confirmation blocks before provider calls
- `context_only` selections do not run OCR
- missing source files block before provider calls
- partial failures write local evidence only
- no feedback closure or manual eval warehouse mutation happens in the first
  execution implementation

Until those tests and the command exist, OCR retry execution remains designed
but not runnable.
