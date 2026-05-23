<!-- @format -->

# Local Tooling Contract

This page names the reusable local-tooling pattern established during the beta
refactor. It is a repo-local contract for Polinko's future operator tools. It
is not a shared package.

## Contract Shape

Local operator tools that prepare human decisions or high-impact eval inputs
must separate preparation from execution:

1. Generate ignored local input.
2. Validate that local input against current source truth.
3. Preview the application without mutation.
4. Execute only through a separate explicit follow-up gate.

The first three stages are safe to add as local tooling. The fourth stage needs
its own approval and validation kernel.

Read-only inventory and status tools are also local tooling. They may inspect
tracked and ignored local evidence, summarize freshness, and print JSON for
operator review, but they must not execute evals, run OCR, launch browsers, or
mutate local data.

## Required Knobs

Every tool that materializes local operator input must expose:

- an ignored default output path under `.local/` or another approved local-only
  lane
- an explicit output or input path override, such as `DRAFT_PATH=<path>` or
  `SELECTION_PATH=<path>`
- no-overwrite behavior by default
- a deliberate `FORCE=1` override for replacing an existing local draft
- a deterministic `schema_version`
- source provenance or fingerprints that let validators reject stale input
- a validation command that reports blockers without mutating data
- an apply-preview command that prints the would-apply payloads only after
  validation passes

## Mutation Boundary

Preparation tools must not:

- launch a browser
- run OCR
- close feedback
- write live eval rows
- mutate the manual eval warehouse
- infer source links that are not present in current source truth

Execution tools may be added only as explicit follow-up gates. They must state
their mutation target, reuse the validator, and keep a preview path available.

## Manual Feedback Decision Packets

Manual feedback decision packets are local operator inputs, not warehouse
updates. The workflow is:

1. Inspect the open feedback slice with source-context tooling.
2. Write an ignored local decision draft.
3. Fill the draft with one of the allowed actions:
   - `keep_open`
   - `reclassify`
   - `close_feedback`
4. Preview the filled decision against the current source-context fingerprints.
5. Add a separate explicit gate only when a future mutation is approved.

For overlay-assisted OCR hypothesis rows, `keep_open` is the default evidence
posture when the row has no exact OCR retry execution target. Those rows remain
active hypothesis pressure until there is a real OCR comparison lane with
attached overlay/source image context. A decision preview can record that local
human-reviewed posture without running OCR, closing feedback, writing eval rows,
or mutating the manual eval warehouse.

The OCR retry execution gate is documented in
`docs/runtime/OCR_RETRY_EXECUTION_GATE.md`. It writes local ignored run bundles
only and keeps feedback closure, live eval writes, and warehouse mutation out
of scope.

## Current Polinko Instance

The current OCR retry human-selection flow is the reference instance for
operator input tooling:

- `make manual-evals-ocr-retry-selection-draft`
  - writes ignored local input to
    `.local/manual_eval_decisions/ocr_retry_selection_draft.json`
  - accepts `DRAFT_PATH=<path>` and `FORCE=1`
  - emits
    `schema_version=polinko.manual_eval_ocr_retry_selection_decision_draft.v1`
- `make manual-evals-ocr-retry-selection-validate`
  - reads local operator decisions through `SELECTION_PATH=<path>`
  - rejects missing, stale, duplicate, or mismatched selections
  - stays read-only
- `make manual-evals-ocr-retry-selection-apply-preview`
  - reads the same local operator decisions
  - emits would-apply payloads only when validation reports `state=ok`
  - stays read-only
- `make manual-evals-ocr-retry-execution-readiness`
  - reads the same local operator decisions
  - checks whether selected `rerun_input` and `curated_case` artifacts have
    existing source files and payload-only command previews
  - emits
    `schema_version=polinko.manual_eval_ocr_retry_execution_readiness.v1`
  - stays read-only and does not run OCR, close feedback, write eval rows, or
    mutate the manual eval warehouse
- `make manual-evals-ocr-retry-execute`
  - requires `SELECTION_PATH=<path>` and `CONFIRM=ocr-retry-execute`
  - recomputes validation, apply-preview, and execution readiness in-process
  - writes local ignored run bundles under `.local/manual_eval_runs/ocr_retry/`
  - does not close feedback, write eval rows, refresh `manual_evals.db`, or
    mutate the manual eval warehouse
- `make manual-evals-ocr-retry-execution-report`
  - reads one local ignored run bundle through `RUN_DIR=<path>`
  - emits
    `schema_version=polinko.manual_eval_ocr_retry_execution_report.v1`
  - checks bundle files, run ID alignment, request/response counts, provider
    failure status, stop reasons, and the no-warehouse-mutation boundary
  - stays read-only and hides source file paths from terminal output
- `make manual-evals-ocr-retry-feedback-closure-preview`
  - reads the same local ignored run bundle through `RUN_DIR=<path>`
  - emits
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_preview.v1`
  - groups successful OCR retry responses by feedback ID and previews which
    feedback rows would be closeable
  - stays read-only and does not close feedback, write action-taken text,
    refresh `manual_evals.db`, write eval rows, or mutate the warehouse
- `make manual-evals-ocr-retry-feedback-closure-apply`
  - reads the same local ignored run bundle through `RUN_DIR=<path>`
  - requires `CONFIRM=ocr-retry-feedback-closure-apply`
  - emits
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`
  - requires execution-bundle and feedback-closure preview state `ok`
  - writes a backup-first warehouse copy before any feedback row update
  - mutates only feedback `status`, `action_taken`, and `updated_at`
- `make manual-evals-ocr-retry-feedback-closure-apply-report`
  - reads the local apply summary through `RUN_DIR=<path>`
  - emits
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1`
  - verifies backup DB integrity, backup feedback rows still open, active
    feedback rows closed, and action-taken text present
  - stays read-only and does not restore, reopen, close, or mutate warehouse
    rows
- `make manual-evals-ocr-retry-feedback-closure-restore-preview`
  - reads one apply backup through `BACKUP_DIR=<path>`
  - emits
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_restore.v1`
  - verifies backup integrity, backup-open rows, and active closed apply
    markers without mutation
- `make manual-evals-ocr-retry-feedback-closure-restore`
  - reads one apply backup through `BACKUP_DIR=<path>`
  - requires `CONFIRM=ocr-retry-feedback-closure-restore`
  - writes a pre-restore backup under
    `.local_archive/manual-evals-feedback-closure-restore-<timestamp>/`
  - restores the whole manual eval warehouse from the verified apply backup
- `make manual-evals-no-context-reclassify-preview`
  - previews overlay-hypothesis OCR feedback rows that have no same-session
    OCR context and whose source response asked for new image evidence
  - emits
    `schema_version=polinko.manual_eval_no_context_feedback_reclassify.v1`
  - stays read-only
- `make manual-evals-no-context-reclassify-apply`
  - requires `CONFIRM=manual-evals-no-context-reclassify`
  - writes a backup-first warehouse copy under
    `.local_archive/manual-evals-feedback-no-context-*`
  - keeps feedback rows open as overlay-assisted OCR hypothesis evidence while
    mutating only feedback
    `recommended_action`, `action_taken`, and `updated_at`
- `make manual-evals-feedback-reclassify-preview`
  - reads a local human-reviewed reclassification plan through
    `PLAN_PATH=<path>`
  - emits `schema_version=polinko.manual_eval_feedback_reclassify.v1`
  - stays read-only
- `make manual-evals-feedback-decision-draft`
  - writes a local ignored feedback decision draft to
    `.local/manual_eval_decisions/feedback_decision.json`
  - accepts `DRAFT_PATH=<path>` and `FORCE=1`
  - preserves source-context fingerprints for preview-time stale-input checks
  - emits `schema_version=polinko.manual_eval_feedback_decision_draft.v1`
- `make manual-evals-feedback-decision-preview`
  - reads a local human-reviewed feedback decision through
    `DECISION_PATH=<path>`
  - validates the decision against the current source-context slice
  - emits `schema_version=polinko.manual_eval_feedback_decision_preview.v1`
  - stays read-only and prints only the future gate/mutation boundary
- `make manual-evals-feedback-reclassify-apply`
  - reads the same local plan through `PLAN_PATH=<path>`
  - requires `CONFIRM=manual-evals-feedback-reclassify`
  - writes a backup-first warehouse copy under
    `.local_archive/manual-evals-feedback-reclassify-*`
  - keeps feedback rows open while mutating only feedback
    `recommended_action`, `action_taken`, and `updated_at`

The current OCR lane inventory is the reference instance for read-only local
evidence inspection:

- `make ocr-inventory`
  - prints tracked OCR cases, local case inputs, local reports, manual-eval DB
    paths, and notebook paths without running OCR or mutating data
  - reports JSON shape, row-source counts, and freshness state from existing
    `generated_at` metadata
- `make ocr-inventory-json`
  - emits the same inventory as JSON for scripts or manual review
  - accepts `FRESHNESS_DAYS=<days>` through the same Make surface

## Adoption Rule

Future Polinko tooling should adopt the contract, not the OCR-specific
implementation. The reusable part is the operator workflow:

- local ignored input
- explicit path override
- no-overwrite default
- `FORCE=1` override
- deterministic schema version
- source fingerprints
- validation before preview
- preview before execution

Keep new local tooling repo-local. Extract shared code only after repeated
Polinko behavior proves the shared boundary is obvious.

## Active Evidence Surfaces

This contract preserves the active manual-eval evidence surfaces:

- `/chat`
- `/chats/*`
- notebooks launched by `make notes`, `make notebook`, and `make nb`
- local notebook workspace under `.local/notebooks/`
- local evidence databases under `.local/runtime_dbs/active/`
- `/viz/pass-fail`
- read-only OCR inventory through `make ocr-inventory` and
  `make ocr-inventory-json`

Local tooling can prepare decisions for those surfaces, but it must not mutate
them without a separate explicit execution gate.
