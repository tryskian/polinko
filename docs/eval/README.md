<!-- @format -->

# Eval Evidence Map

This folder is the tracked eval evidence lane.

Use it when you need:

- beta-era context
- case files and report snapshots
- the shortest path from eval artifacts to public proof

![Polinko evidence sankey](../public/diagrams/polinko-evidence-sankey.svg)

## Beta Meanings

- `beta_1_0`
  - binary-transition era
  - manual and screenshot-backed evaluation still carries real evidence weight
- `beta_2_0`
  - binary-operational era
  - flatter case/report structure and repeatable eval commands
- `beta_2_3`
  - frozen method-boundary snapshot for next-beta cleanup
  - OCR generalization pressure starts from the stabilized current-image base
  - tracked summary points to curated notes and evidence, with raw export
    material promoted only after explicit curation
- `pre-Beta 2.4`
  - staged research-model contract before the next evidence folder is cut
  - the discarded run-level rollup hypothesis is not being carried forward
  - row and case evidence remain source-bound before lane-level summaries
  - manual eval workbench sources stay canonical inputs

Beta 1.0, Beta 2.0, Beta 2.3, and pre-Beta 2.4 should be read by role.
Beta 1.0 explains the transition into binary evals. Beta 2.0 shows the
operationalized lane. Beta 2.3 freezes the current method read before the
next beta work starts. Pre-Beta 2.4 names the next source-first
research-model contract.

## Current Canonical Surfaces

The manual eval workbench is the human-judged research workspace. It includes
notebooks, local evidence databases, chat artifacts, feedback, checkpoints,
notes, exports, and runtime history.

- notebook workspace:
  - `make notes`
  - aliases: `make notebook`, `make nb`
  - default local path: `.local/notebooks/`
- integrated manual-eval warehouse:
  - `.local/runtime_dbs/active/manual_evals.db`
  - rebuild with `make manual-evals-db`
  - DB metadata exposes `schema_version=polinko.manual_evals_db.v1`
  - API surfaces expose read-only `data_freshness` status before any rebuild
  - freshness source counts use the same evidence-bearing import scope as the
    rebuild command
  - inspect freshness without mutation with `make manual-evals-db-status`
  - refreshes preserve the previous warehouse under
    `.local_archive/manual-evals-db-refresh-*` before rebuilding
  - inspect warehouse health with `make manual-evals-db-health`
  - health output breaks remaining missing-image debt down by source family
  - health output breaks open feedback debt down by era/outcome and known OCR
    evidence relationships without inferring links
  - list open feedback row actionables with
    `make manual-evals-feedback-actionables`
  - JSON actionables export uses
    `schema_version=polinko.manual_eval_feedback_actionables.v1`
  - summarize open feedback row actionables by cohort with
    `make manual-evals-feedback-cohorts`
  - JSON cohort export uses
    `schema_version=polinko.manual_eval_feedback_cohorts.v1`
  - drill into a selected cohort without mutation with
    `make manual-evals-feedback-actionables COHORT=ocr_retry_evidence`
  - combine `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, and `LIMIT=<n>` for
    terminal-native manual triage filters
  - inspect source-history context for selected open feedback rows with
    `make manual-evals-feedback-source-context`
  - JSON source-context export uses
    `schema_version=polinko.manual_eval_feedback_source_context.v1`
  - write a local ignored feedback-decision draft without mutation with
    `make manual-evals-feedback-decision-draft`
  - JSON decision-draft files default to
    `.local/manual_eval_decisions/feedback_decision.json` and use
    `schema_version=polinko.manual_eval_feedback_decision_draft.v1`
  - preview a local human-reviewed feedback decision without mutation with
    `make manual-evals-feedback-decision-preview DECISION_PATH=<path>`
  - JSON decision-preview export uses
    `schema_version=polinko.manual_eval_feedback_decision_preview.v1`
  - decision previews validate the selected feedback row against the current
    source-context slice and print the future gate/mutation boundary only
  - inspect overlay/OCR comparison readiness without mutation with
    `make manual-evals-overlay-comparison-readiness`
  - JSON overlay/OCR readiness export uses
    `schema_version=polinko.manual_eval_overlay_ocr_comparison_readiness.v1`
  - overlay readiness packets expose source context, source-image candidates,
    exact blockers, and payload-only previews before any OCR comparison run
  - preview overlay-hypothesis OCR feedback rows that have no same-session OCR
    context and whose source response asked for new image evidence with
    `make manual-evals-no-context-reclassify-preview`
  - apply that reclassification with
    `make manual-evals-no-context-reclassify-apply
    CONFIRM=manual-evals-no-context-reclassify`
  - overlay reclassification preserves the row as overlay-assisted OCR
    hypothesis evidence, keeps feedback open, writes a backup under
    `.local_archive/manual-evals-feedback-no-context-*`, and limits mutation
    to feedback `recommended_action`, `action_taken`, and `updated_at`
  - JSON overlay reclassification export uses
    `schema_version=polinko.manual_eval_no_context_feedback_reclassify.v1`
  - preview a local human-reviewed feedback reclassification plan with
    `make manual-evals-feedback-reclassify-preview PLAN_PATH=<path>`
  - apply that plan with
    `make manual-evals-feedback-reclassify-apply PLAN_PATH=<path>
    CONFIRM=manual-evals-feedback-reclassify`
  - plan-based feedback reclassification keeps rows open, writes a backup
    under `.local_archive/manual-evals-feedback-reclassify-*`, and limits
    mutation to feedback `recommended_action`, `action_taken`, and
    `updated_at`
  - JSON feedback reclassification export uses
    `schema_version=polinko.manual_eval_feedback_reclassify.v1`
  - inspect the first OCR retry candidate packet without mutation with
    `make manual-evals-ocr-retry-candidates`
  - JSON OCR retry candidate export uses
    `schema_version=polinko.manual_eval_ocr_retry_candidates.v2`
  - OCR retry candidate packets expose read-only readiness flags for
    ambiguous same-session OCR context and missing explicit feedback-to-result
    links before any reruns
  - verify selected OCR retry source candidates without mutation with
    `make manual-evals-ocr-retry-source-verification`
  - JSON OCR retry source-verification export uses
    `schema_version=polinko.manual_eval_ocr_retry_source_verification.v1`
  - source-verification packets include feedback note/action text, candidate
    source image names, OCR run IDs, OCR previews, and readiness flags
  - exact not-confirmed reasons are included without inferring links
  - drill into source-history message provenance without mutation with
    `make manual-evals-ocr-retry-source-provenance`
  - JSON OCR retry source-provenance export uses
    `schema_version=polinko.manual_eval_ocr_retry_source_provenance.v1`
  - source-provenance packets expose source-history feedback message presence
    and exact OCR source/result message IDs when they are already present,
    while preserving context-only OCR rows as not exact links
  - build a concrete OCR retry input packet without mutation with
    `make manual-evals-ocr-retry-input-packet`
  - JSON OCR retry input-packet export uses
    `schema_version=polinko.manual_eval_ocr_retry_input_packet.v1`
  - input packets expose feedback IDs, source sessions, source image names,
    resolved image status, OCR run IDs, feedback source-message previews, and
    exact-link blocker state before any rerun or feedback closure
  - build a concrete OCR retry source-artifact selection manifest without
    mutation with `make manual-evals-ocr-retry-rerun-manifest`
  - JSON OCR retry rerun-manifest export uses
    `schema_version=polinko.manual_eval_ocr_retry_rerun_manifest.v1`
  - rerun manifests expose source image names, OCR run IDs, resolution status,
    thumbnail dimensions, OCR previews, feedback source-message previews, and
    the separate feedback-closure blocker state before any rerun, curation, or
    feedback closure
  - build a payload-only OCR retry rerun plan without mutation with
    `make manual-evals-ocr-retry-rerun-plan`
  - JSON OCR retry rerun-plan export uses
    `schema_version=polinko.manual_eval_ocr_retry_rerun_plan.v1`
  - rerun plans expose stable source artifact IDs, feedback IDs, source
    sessions, OCR run IDs, source image names, resolved source paths,
    thumbnail dimensions, source previews, and payload-only command previews;
    `ARTIFACT_IDS=<artifact_id>` narrows the preview without running OCR or
    mutating the warehouse
  - build a human-selection OCR retry shortlist without mutation with
    `make manual-evals-ocr-retry-selection-review`
  - JSON OCR retry selection-review export uses
    `schema_version=polinko.manual_eval_ocr_retry_selection_review.v1`
  - selection reviews collapse duplicate source image artifacts from rerun
    plans and expose feedback IDs, OCR run IDs, source image names, thumbnail
    dimensions, source previews, candidate payload previews, and explicit
    dispositions: `rerun_input`, `curated_case`, or `context_only`
  - build a human-selection template without mutation with
    `make manual-evals-ocr-retry-selection-template`
  - JSON OCR retry selection-template export uses
    `schema_version=polinko.manual_eval_ocr_retry_selection_template.v1`
  - selection templates expose shortlist IDs, candidate artifact IDs, source
    previews, and fillable decision fields that default to
    `selected_action=undecided`
  - materialize a local fillable human-selection draft with
    `make manual-evals-ocr-retry-selection-draft`
  - JSON OCR retry selection-draft files use
    `schema_version=polinko.manual_eval_ocr_retry_selection_decision_draft.v1`
  - selection drafts are written to a local ignored lane by default, preserve
    shortlist IDs, candidate artifact IDs, source provenance, and template
    fingerprints, and remain blocked from execution until the validator and
    apply-preview gates pass
  - template fingerprints stay in the draft payload for local stale-input
    review
  - validate local OCR retry human-selection JSON without mutation with
    `make manual-evals-ocr-retry-selection-validate`
  - JSON OCR retry selection-validation export uses
    `schema_version=polinko.manual_eval_ocr_retry_selection_validation.v1`
  - selection validation accepts compact decision lists or filled selection
    templates, requires `rerun_input`, `curated_case`, or `context_only`,
    verifies selected artifact IDs against the matching shortlist item, and
    flags missing/stale/duplicate decisions before any OCR execution surface
  - preview local OCR retry decision application without mutation with
    `make manual-evals-ocr-retry-selection-apply-preview`
  - JSON OCR retry selection-apply preview export uses
    `schema_version=polinko.manual_eval_ocr_retry_selection_apply_preview.v1`
  - apply previews require validation `state=ok` before emitting would-apply
    payloads, split decisions by `rerun_input`, `curated_case`, and
    `context_only`, and keep validation blockers visible before any OCR
    execution surface
  - check OCR retry execution readiness without mutation with
    `make manual-evals-ocr-retry-execution-readiness`
  - JSON OCR retry execution-readiness export uses
    `schema_version=polinko.manual_eval_ocr_retry_execution_readiness.v1`
  - execution-readiness reports require apply-preview `state=ok`, verify
    selected artifact source-file existence and payload-only command previews,
    and keep execution in a separate explicit follow-up gate
  - inspect local OCR retry execution bundles without mutation with
    `make manual-evals-ocr-retry-execution-report RUN_DIR=<path>`
  - JSON OCR retry execution-bundle reports use
    `schema_version=polinko.manual_eval_ocr_retry_execution_report.v1`
  - execution-bundle reports verify files, run IDs, request/response counts,
    provider failure status, stop reasons, and the no-warehouse-mutation
    boundary before feedback closure or any warehouse mutation
  - preview OCR retry feedback closure without mutation with
    `make manual-evals-ocr-retry-feedback-closure-preview RUN_DIR=<path>`
  - JSON OCR retry feedback-closure previews use
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_preview.v1`
  - feedback-closure previews group successful OCR retry responses by feedback
    ID and keep feedback status, action-taken text, eval rows, and
    `manual_evals.db` unchanged
  - apply OCR retry feedback closure with
    `make manual-evals-ocr-retry-feedback-closure-apply RUN_DIR=<path>
    CONFIRM=ocr-retry-feedback-closure-apply`
  - JSON OCR retry feedback-closure apply reports use
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`
  - feedback-closure apply is backup-first and limits mutation to feedback
    `status`, `action_taken`, and `updated_at`
  - verify OCR retry feedback closure after apply without mutation with
    `make manual-evals-ocr-retry-feedback-closure-apply-report RUN_DIR=<path>`
  - JSON OCR retry feedback-closure apply-report exports use
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1`
  - apply-report verifies backup DB integrity, backup feedback rows still open,
    active feedback rows closed, and action-taken text present
  - preview OCR retry feedback-closure restore without mutation with
    `make manual-evals-ocr-retry-feedback-closure-restore-preview
    BACKUP_DIR=<path>`
  - restore OCR retry feedback closure only with
    `make manual-evals-ocr-retry-feedback-closure-restore BACKUP_DIR=<path>
    CONFIRM=ocr-retry-feedback-closure-restore`
  - JSON OCR retry feedback-closure restore exports use
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_restore.v1`
  - restore writes a pre-restore backup under
    `.local_archive/manual-evals-feedback-closure-restore-<timestamp>/` before
    restoring the whole manual eval warehouse from the verified apply backup
  - image resolution checks extracted files first across private screenshot
    roots, tracked `docs/eval/` snapshots, the Dropbox screenshot sync root,
    and local export roots, then matching files inside `.zip` archives under
    configured image roots
  - remaining unresolved text fixtures are historical source-name debt unless
    their seed files are explicitly curated as source files
- active chat artifacts:
  - `POST /chat`
  - `/chats/*`
  - includes feedback, checkpoints, notes, exports, and personalization rows
- raw current runtime source:
  - `.local/runtime_dbs/active/history.db`
- live strict-gate observability plus tracked lane snapshots:
  - `.local/eval_reports/`
  - `/viz/pass-fail`
  - `/viz/pass-fail/data`

Manual evals and strict OCR gate reports answer different questions:

- manual evals capture human judgment and qualitative notes from the manual
  eval workbench
- manual feedback evidence rows link to the matching source/result message
  when a case link exists; session context alone is not promoted into an OCR
  case link
- `/viz/pass-fail` uses the same source-first match when it turns manual
  feedback into evaluated rows; raw OCR status stays raw when feedback belongs
  to a different result message
- `/manual-evals/surface` and `/viz/pass-fail/data` expose the shared
  source-first payload as
  `schema_version=polinko.manual_eval_source_first.v1`
- OCR gate reports preserve binary fail pressure
- `/viz/pass-fail` keeps the live chart on the active window and uses tracked
  eval files to keep the wider lane map visible below it
- tracked lane cards now expose direct links to:
  - the underlying tracked artifact
  - the promoted research note when that lane has one

Do not flatten one into the other.

## Tracked Gate Contract

- OCR gate reports stay strictly `pass` / `fail`
- OCR candidate cleanup happens upstream of eval:
  - malformed candidates
  - duplicate candidates
  - known-bad inputs
- non-OCR lanes can still use richer staged or thin-lane method surfaces where
  the research question is not simple extraction correctness
- judge detail and qualitative notes can enrich a report, but they do not
  create a third OCR gate state
- thin new lanes can begin as row-local human `pass` / `fail` evidence before
  larger automation
- run-level verdicts are not canonical rollups for the active manual eval
  workbench

## What Is Tracked Here

### Beta 1.0

- curated historical evidence under `docs/eval/beta_1_0/`
- archived build snapshot material under
  `docs/eval/beta_1_0/build_snapshot_polinko-incase/`
- role in the evidence map:
  - left-side/legacy evidence for the Sankey payload

### Beta 2.0

- active-era case files and report snapshots under `docs/eval/beta_2_0/`
- includes OCR, OCR recovery, OCR safety, hallucination, retrieval, file
  search, style, response behaviour, CLIP A/B, and operator burden
- append-only eval trace artifacts stay local under `eval_reports/`; they are
  not auto-promoted into the tracked beta surface
- current non-OCR promoted lane lives in the tracked style surface for
  co-reasoning reliability
- current thin-lane operator burden surface lives in:
  - `docs/eval/beta_2_0/operator_burden_rows.json`
  - summarize with:
    - `make operator-burden-report`
    - the summary now surfaces:
      - pass anchors
      - retained failures
      - evicted failures
  - widen candidate rows locally with:
    - `python3 -m tools.build_behaviour_backlog_from_export --export-root /abs/path/to/CGPT-DATA-EXPORT`
- role in the evidence map:
  - right-side/current evidence for the Sankey payload

### Beta 2.3

- frozen method-boundary snapshot under `docs/eval/beta_2_3/`
- source boundary:
  - `2026-05-16`
- snapshot role:
  - preserve the current Beta 2.3 read before broad cleanup/refactor work
  - record high-level OCR generalization intake counts
  - point to the tracked research notes and prior operational evidence files
  - hand off into the staged pre-Beta 2.4 research-model contract
- entry points:
  - [Beta 2.3 eval snapshot](./beta_2_3/README.md)
  - [Beta 2.3 snapshot manifest](./beta_2_3/research_snapshot_manifest.json)
  - [Pre-Beta 2.4 research model contract](../research/pre-beta-2-4-research-model-contract-2026-05-19.md)

## What Stays Local

- live runtime databases under `.local/runtime_dbs/active/`
- archived runtime databases under `.local/runtime_dbs/archive/`
- export-mined candidate backlogs under `.local/eval_cases/`
- full Beta 1.0 local snapshot databases and runtime state
- private exports, scratch screenshots, and raw local audit material

Do not commit the full Beta 1.0 snapshot wholesale. Promote only curated
evidence or explicitly approved artifacts.

## Interpretation Rule

- compare Beta 1.0 and Beta 2.0 by role, not by artifact neatness
- treat transcripts, screenshots, and raw reports as source evidence
- let decisions and public notes interpret the evidence, not replace it
