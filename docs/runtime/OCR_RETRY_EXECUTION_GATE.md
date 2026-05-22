<!-- @format -->

# OCR Retry Execution Gate

Status: `implemented-local-bundle`

This page defines the OCR retry execution gate. The gate is active only as a
guarded local-bundle writer. It can assemble and execute selected OCR retry
requests, but it does not close feedback, write live eval rows, refresh
`manual_evals.db`, or mutate the manual eval warehouse.

## Current Boundary

- The OCR retry execution Make target exists only as a guarded local-bundle
  writer.
- `manual-evals-ocr-retry-execute` writes only ignored local run bundles.
- No feedback row is closed by this gate.
- No live eval row is written by this gate.
- No manual eval warehouse mutation happens from this gate.

Feedback closure, live eval writes, and warehouse mutation remain separate
follow-up gates.

## Command Shape

The command is explicit and hard to run by accident:

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
  - default: `.local/manual_eval_runs/ocr_retry/`
- optional OCR provider:
  - `OCR_PROVIDER=scaffold`
  - `OCR_PROVIDER=openai`
  - default follows `POLINKO_OCR_PROVIDER`, falling back to `scaffold`

`scaffold` is provider-safe and records stub responses for binary images.
Use `OCR_PROVIDER=openai` only when live OCR calls are intentionally approved.

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

The implementation writes only a local execution bundle:

- `.local/manual_eval_runs/ocr_retry/<run_id>/manifest.json`
- `.local/manual_eval_runs/ocr_retry/<run_id>/requests.jsonl`
- `.local/manual_eval_runs/ocr_retry/<run_id>/responses.jsonl`
- `.local/manual_eval_runs/ocr_retry/<run_id>/summary.json`

The bundle records:

- source selection path
- source decision fingerprint
- readiness schema version
- selected artifact IDs
- source file paths and request metadata
- OCR provider and model configuration
- response status and extracted text preview
- per-item success or failure
- zero warehouse mutation state

The implementation must not close feedback, write live eval rows, or refresh
`manual_evals.db`. Those are separate follow-up gates.

## Inspection Target

Generated execution bundles are inspected before any follow-up mutation gate:

- `make manual-evals-ocr-retry-execution-report`
- alias: `make manualdb-ocr-retry-execution-report`
- required input: `RUN_DIR=<path>`
- JSON schema:
  `schema_version=polinko.manual_eval_ocr_retry_execution_report.v1`

The report target is read-only. It reads the bundle files, verifies that they
stay under the run directory, checks schema versions, run ID alignment,
request/response counts, response status counts, stop reasons, and the
local-bundle mutation boundary. Terminal output hides source file paths and
prints only the run ID, directory name, counts, and blocker/warning summary.

Report states:

- `ok`: bundle is structurally valid and all responses succeeded.
- `attention`: bundle is structurally valid but contains provider failures or
  skipped requests.
- `error`: bundle structure, alignment, or mutation boundary is invalid.

## Feedback-Closure Preview

Closure remains non-mutating. The current follow-up target previews only:

- `make manual-evals-ocr-retry-feedback-closure-preview`
- alias: `make manualdb-ocr-retry-feedback-closure-preview`
- required input: `RUN_DIR=<path>`
- JSON schema:
  `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_preview.v1`

The feedback-closure preview target is read-only. It first runs the execution
bundle inspection gate, then groups successful OCR retry responses by feedback
ID. It proposes which feedback rows would be closeable, marks mixed provider
status as `attention`, and blocks when the bundle inspection has structural or
mutation-boundary errors.

The preview does not write feedback status, action-taken text, live eval rows,
or `manual_evals.db`. It also keeps terminal output path-safe by printing run
ID, directory name, feedback counts, and closure item states only.

## Feedback-Closure Apply Gate

The feedback-closure apply target is implemented as a backup-first local
warehouse writer.

It is exposed through:

- target:
  - `make manual-evals-ocr-retry-feedback-closure-apply`
  - alias: `make manualdb-ocr-retry-feedback-closure-apply`
- required inputs:
  - `RUN_DIR=<path>`
  - `CONFIRM=ocr-retry-feedback-closure-apply`
- JSON schema:
  `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`
- required preconditions:
  1. execution bundle report returns `state=ok`
  2. feedback-closure preview returns `state=ok`
  3. every preview item has `state=ready`
  4. every target feedback row is still open in the current manual eval
     warehouse
  5. the current manual eval warehouse is backed up before any write

The backup must copy the current warehouse to a timestamped path under:

- `.local_archive/manual-evals-feedback-closure-apply-<timestamp>/`

The apply gate may update only the feedback rows named by the preview:

- `status`
- `action_taken`
- `updated_at`

It blocks without a backup or mutation when confirmation is missing, the bundle
or preview is not `ok`, the target feedback rows are missing, or any target
feedback row is no longer open. It must not write live eval rows, run OCR,
refresh `manual_evals.db`, mutate OCR run rows, or infer new source links. It
writes a local apply summary beside the run bundle and includes the backup
path, updated feedback IDs, skipped feedback IDs, and restore command guidance.

Rollback for the apply gate is database restore:

1. Stop any local server using the manual eval warehouse.
2. Copy the backup DB from
   `.local_archive/manual-evals-feedback-closure-apply-<timestamp>/` back over
   `.local/runtime_dbs/active/manual_evals.db`.
3. Re-run `make manual-evals-db-health` and
   `make manual-evals-ocr-retry-feedback-closure-preview RUN_DIR=<path>`.

## Rollback Story

Rollback is local-file cleanup:

1. Remove the generated run bundle under `.local/manual_eval_runs/ocr_retry/`.
2. Keep the original `SELECTION_PATH` unchanged.
3. Re-run `make manual-evals-ocr-retry-execution-readiness` to confirm the
   source selection still resolves.

Any additional database mutation gate must add backup-first behavior under
`.local_archive/` before mutation and document restore steps in this file.

## Failure Handling

The command fails closed:

- missing confirmation token: exit non-zero before any provider call
- validation/apply-preview/readiness not ready: exit non-zero before any
  provider call
- missing source file: exit non-zero before any provider call
- partial provider failure: write the local run bundle and mark failed items,
  but do not close feedback or mutate the warehouse
- rate limit or provider outage: stop remaining items and write a summary with
  retry-after/backoff evidence when available

## Validation Contract

The implementation includes tests proving:

- readiness is recomputed from current source truth
- missing confirmation blocks before provider calls
- `context_only` selections do not run OCR
- missing source files block before provider calls
- partial failures write local evidence only
- no feedback closure or manual eval warehouse mutation happens in the first
  execution implementation
