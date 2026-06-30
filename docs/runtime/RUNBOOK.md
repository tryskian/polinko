<!-- @format -->

# Runbook

## When to Read This

Use this doc for operator procedure.

- `docs/governance/CHARTER.md`
  - durable rules and role split
- `docs/runtime/ARCHITECTURE.md`
  - stable system shape
- `docs/runtime/SURFACE_IA.md`
  - web surface path roles and planned directory renames
- `docs/runtime/RUNTIME_SURFACE_MAP.md`
  - current operator surface map for startup, closeout, background runners,
    CI, and eval tooling
- `docs/governance/STATE.md`
  - tracked current truth
- local `docs/peanut/governance/SESSION_HANDOFF.md`
  - active kernel and next-session carryover

## Branch, Worktree, and Scope Policy

1. Canonical repo root is the repo root printed by `make start`.
   Tracked docs should not hard-code machine-local repo paths.
2. Default workflow is one feature branch per change set:
   - `git switch -c codex/bigbrain/<task-name>`
3. Start edits from a feature branch.
4. Use a worktree only when you need parallel active implementation tracks.
5. Keep one logical task per branch; merge or close before starting the next.
6. Use worktrees for parallel code changes.
7. Use parallel agents only for bounded analysis after architecture,
   acceptance criteria, and rubric constraints are explicit.

## Command Surface Rule

1. Keep one atomic command per operator action.
2. Keep operator thinking in procedure and keep wrapper targets mechanical.
3. Procedure lives in this runbook.
4. Mechanical checks live in `make` targets.

## Morning Startup Ritual

1. Run:
   - `make start`
   - startup includes a GitHub health attention pass before local runtime
     checks
2. Read in this order from the printed rehydrate prompt:
   - `docs/governance/CHARTER.md`
   - `docs/governance/STATE.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/runtime/ARCHITECTURE.md`
   - local `docs/peanut/governance/SESSION_HANDOFF.md` if present
3. Confirm execution location:
   - printed repo root and host vs devcontainer mode
   - GitHub health attention, if printed
4. Confirm active branch:
   - `git branch --show-current`
5. If on `main`, create or switch to a feature branch before edits.
6. Reply in the morning ritual before implementation:
   - context: printed repo root, host vs devcontainer mode, active branch, clean `main` or feature branch, and runtime health
   - kernel map: likely lanes from current docs/state, with one
     recommended first kernel
   - startup note: one small issue or risk only if something needs attention
7. Treat the reply as the chat-first alignment pass.
8. Wait for human alignment before implementation.
9. After alignment, run one active kernel at a time and stop before broadening.

## Environment Doctor

1. Run:
   - `make doctor-env`
2. It checks:
   - Python path
   - venv
   - package imports
   - shell setup
3. Resolve actionable issues before runtime or eval work.

## Inspect-First Rule

1. If a file, path, screenshot, log, report, or transcript is named, inspect
   it before interpretation.
2. Use source evidence as the basis for interpretation.
3. State inspection status plainly.

## Command Ownership

1. Human lead owns:
   - objective
   - scope
   - acceptance criteria
   - meaning-level trade-offs
   - go/no-go decisions
2. Engineer owns:
   - implementation
   - validation
   - command execution
   - Git and PR flow
   - proactive hygiene
3. Default mode is execution-first:
   - do the work directly when asked

## Protected Main PR Flow

1. Work on a feature branch.
2. Commit locally.
3. Run the PR readiness gate:
   - `make pr-preflight`
4. Push the branch.
5. Open a PR to `main`.
6. Wait for required checks.
7. Merge through the protected-main flow.
8. Sync local `main`:
   - `git switch main`
   - `git pull --ff-only`
9. Final local repo state must be clean and synced with `origin/main`.

## End-of-Day Ritual

1. Run the literal closeout routine from clean synced `main`:
   - `make end`
2. If you need companion checks as standalone checks, run:
   - `make end-docs-check`
   - `make end-git-check`
   - `make git-prune-stale-refs`
3. Update tracked current truth and local handoff before stopping.

## Local-Only Docs Policy

1. `docs/peanut/` is the local-only lane.
2. Use it for:
   - transcripts
   - theory
   - design refs
   - working notes
   - operator handoff
3. Tracked docs remain canonical project truth.
4. Keep local-only files in the local lane and keep tracked repo truth in the
   tracked docs surface.

## Local Tooling Policy

1. Use `docs/runtime/LOCAL_TOOLING.md` for local operator tooling that prepares
   human decisions, inspects local evidence, or prepares high-impact eval
   inputs.
2. Keep preparation separate from execution:
   - generate ignored local input
   - validate that input against current source truth
   - preview application as a read-only would-apply step
   - execute only through a separate explicit follow-up gate
3. Use read-only inventory/status tools before eval refreshes when local
   evidence state is unclear.
4. Required knobs include an ignored default output path, explicit path
   override, no-overwrite default, `FORCE=1`, deterministic `schema_version`,
   validation command, and apply-preview command.
5. Preparation and inventory tools must not launch a browser, run OCR, close
   feedback, write live eval rows, or mutate the manual eval warehouse.

## Active Kernel Validation

1. Use focused checks during active refactor kernels:
   - touched unit tests
   - `make scripts-check` for script changes
   - `make local-runtime-config-check` for VS Code task/config changes
   - `make risk-scan` for runtime map, Make gate, CI, runner, startup/closeout,
     or local configuration surface changes
   - `make operator-command-check` for manual eval or OCR operator command changes
   - `make lint-docs` for docs changes
   - `git diff --check`
2. Use `make end-preflight` when the kernel is broad enough to need the full
   branch-local quality suite.
3. End each kernel summary with the recommended next kernel.
4. Reserve `make end` for real session closeout only.

## Atomic Commands

- `make doctor-env`
  - environment health check
- `make caffeinate`
  - validate repo-managed wake-lock config and start the wake lock
- `make caffeinate-status`
  - validate repo-managed wake-lock config and report wake-lock/activity status
- `make decaffeinate`
  - validate repo-managed wake-lock config and stop the wake lock
- `make decaffeinate-status`
  - report closeout wake-lock status
- `make api-smoke`
  - live backend smoke check with isolated default localhost port and DB paths
- `make manual-evals-db-status`
  - print read-only manual eval warehouse freshness without rebuilding
- `make manual-evals-db`
  - back up the existing manual eval warehouse, rebuild it from configured
    history sources, and print the post-refresh freshness status
- `make manual-evals-db-health`
  - print read-only manual eval warehouse source-quality signals
- `make ocr-inventory`
  - print read-only OCR lane inventory, including tracked cases, local
    cases/reports, manual-eval DB paths, notebook paths, row-source counts,
    and freshness state from existing metadata
- `make ocr-inventory-json`
  - print the same OCR inventory as JSON
  - use `FRESHNESS_DAYS=<days>` to adjust the freshness threshold
- `make manual-evals-feedback-actionables`
  - print read-only row-level open feedback actionables for manual triage
- `make manual-evals-feedback-cohorts`
  - print read-only open feedback action cohorts for manual triage
- `make manual-evals-feedback-actionables COHORT=ocr_retry_evidence`
  - print read-only row-level actionables for one selected cohort
  - combine with `OUTCOME=<outcome>` and `LIMIT=<n>` for smaller manual
    triage slices
- `make manual-evals-feedback-source-context`
  - print read-only source-history context for selected open feedback rows
  - defaults to the `grounding_source_verification` fail slice
  - combine with `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, and `LIMIT=<n>`
    for explicit manual triage slices
  - emits `schema_version=polinko.manual_eval_feedback_source_context.v1`
- `make manual-evals-feedback-decision-draft`
  - write a local ignored decision draft for the selected feedback slice
  - accepts `DRAFT_PATH=<path>` and `FORCE=1`
  - emits `schema_version=polinko.manual_eval_feedback_decision_draft.v1`
  - stays local-only without OCR, feedback closure, eval writes, warehouse
    mutation, or source-history mutation
- `make manual-evals-feedback-decision-preview DECISION_PATH=<path>`
  - preview a local human-reviewed decision for the selected feedback slice
  - validates the row against current source-context evidence
  - emits `schema_version=polinko.manual_eval_feedback_decision_preview.v1`
  - stays read-only and prints the future gate/mutation boundary only
  - use `keep_open` for overlay-assisted OCR hypothesis rows that have no exact
    OCR retry execution target; they remain active evidence pressure until a
    real OCR comparison lane exists with attached overlay/source image context
- `make manual-evals-overlay-comparison-readiness`
  - print read-only overlay/OCR comparison readiness for selected
    overlay-assisted OCR hypothesis rows
  - combine with `COHORT=ocr_overlay_hypothesis`, `OUTCOME=<outcome>`, and
    `LIMIT=<n>` for explicit manual triage slices
  - pass `OVERLAY_SOURCE_INDEX_PATH=<path>` to attach a local ignored
    overlay/source image context index; the default index path is
    `.local/manual_eval_decisions/overlay_source_context_index.json`
  - require matching source-context fingerprints before indexed images make a
    row ready
  - expose source context, source-image candidates, exact blockers, and
    payload-only previews before any OCR run, feedback closure, eval write, or
    warehouse mutation
  - emits
    `schema_version=polinko.manual_eval_overlay_ocr_comparison_readiness.v1`
- `make manual-evals-overlay-source-index-draft`
  - write a local ignored overlay/source image context index draft for the
    selected readiness slice
  - accepts `DRAFT_PATH=<path>` and `FORCE=1`
  - writes `.local/manual_eval_decisions/overlay_source_context_index.json` by
    default
  - emits
    `schema_version=polinko.manual_eval_overlay_source_context_index_draft.v1`
  - draft entries preserve the current feedback ID, source session, message
    ID, and source-context fingerprint
  - fill in human-reviewed local source image paths before validation
- `make manual-evals-overlay-source-index-validate`
  - validate the local ignored overlay/source image context index against the
    current readiness packet
  - accepts `OVERLAY_SOURCE_INDEX_PATH=<path>`
  - emits
    `schema_version=polinko.manual_eval_overlay_source_context_index_validation.v1`
  - reuse readiness blockers for stale fingerprints and missing local source
    image paths
  - stays read-only before any OCR run, feedback closure, eval write, or
    warehouse mutation
- `make manual-evals-no-context-reclassify-preview`
  - preview overlay-hypothesis OCR feedback rows that have no same-session OCR
    context and whose source response asked for new image evidence
  - emits
    `schema_version=polinko.manual_eval_no_context_feedback_reclassify.v1`
- `make manual-evals-no-context-reclassify-apply
  CONFIRM=manual-evals-no-context-reclassify`
  - keeps matching feedback rows open while moving them out of executable OCR
    retry work into overlay-assisted OCR hypothesis evidence
  - writes a backup under `.local_archive/manual-evals-feedback-no-context-*`
    before mutating feedback `recommended_action`, `action_taken`, and
    `updated_at`
- `make manual-evals-feedback-reclassify-preview PLAN_PATH=<path>`
  - preview a local human-reviewed feedback reclassification plan
  - emits `schema_version=polinko.manual_eval_feedback_reclassify.v1`
- `make manual-evals-feedback-reclassify-apply PLAN_PATH=<path>
  CONFIRM=manual-evals-feedback-reclassify`
  - keeps feedback rows open while moving them between explicit manual-eval
    action cohorts
  - writes a backup under
    `.local_archive/manual-evals-feedback-reclassify-*` before mutating
    feedback `recommended_action`, `action_taken`, and `updated_at`
- `make manual-evals-ocr-retry-candidates`
  - print the read-only OCR retry candidate packet for the default
    `ocr_retry_evidence` partial slice
  - combine with `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, and `LIMIT=<n>`
    for explicit manual triage slices
  - use readiness flags to distinguish exact feedback-to-result links from
    same-session OCR context before reruns
- `make manual-evals-ocr-retry-source-verification`
  - print the read-only OCR retry source-verification packet for the default
    `ocr_retry_evidence` partial slice
  - combine with `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, and `LIMIT=<n>`
    for explicit manual triage slices
  - use feedback notes/actions, source image names, OCR previews, readiness
    flags, and exact confirmation blockers before reruns or feedback closure
- `make manual-evals-ocr-retry-source-provenance`
  - print the read-only OCR retry source-history provenance packet for the
    default `ocr_retry_evidence` partial slice
  - combine with `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, and `LIMIT=<n>`
    for explicit manual triage slices
  - use source-history feedback message presence and exact OCR source/result
    message IDs already present in the warehouse before reruns or closure
- `make manual-evals-ocr-retry-input-packet`
  - print the read-only OCR retry input packet for the default
    `ocr_retry_evidence` partial slice
  - combine with `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, and `LIMIT=<n>`
    for explicit manual triage slices
  - use verified source candidates plus source-history provenance to prepare
    rerun/case-curation inputs without closing feedback or mutating the
    warehouse
- `make manual-evals-ocr-retry-rerun-manifest`
  - print the read-only OCR retry source-artifact selection manifest for the
    default `ocr_retry_evidence` partial slice
  - combine with `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, and `LIMIT=<n>`
    for explicit manual triage slices
  - use resolved source artifacts, thumbnail dimensions, OCR previews, and
    feedback source-message previews as the go/no-go surface before any rerun,
    curation, feedback closure, or warehouse mutation
- `make manual-evals-ocr-retry-rerun-plan`
  - print the read-only OCR retry rerun plan and payload preview for the
    default `ocr_retry_evidence` partial slice
  - combine with `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, `LIMIT=<n>`, and
    `ARTIFACT_IDS=<artifact_id>` for explicit manual source-artifact selection
  - use stable source artifact IDs, feedback IDs, OCR run IDs, resolved source
    paths, thumbnail dimensions, and source previews to inspect exact
    payload-only command previews before any OCR rerun, curation, feedback
    closure, or warehouse mutation
- `make manual-evals-ocr-retry-selection-review`
  - print the read-only OCR retry source-artifact shortlist for the default
    `ocr_retry_evidence` partial slice
  - combine with `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, `LIMIT=<n>`, and
    `ARTIFACT_IDS=<artifact_id>` for explicit manual source-artifact review
  - use grouped source image identities, feedback IDs, OCR run IDs, thumbnail
    dimensions, source previews, and candidate payload previews to choose
    `rerun_input`, `curated_case`, or `context_only` before any OCR rerun,
    curation, feedback closure, or warehouse mutation
- `make manual-evals-ocr-retry-selection-template`
  - print the read-only OCR retry human-selection template for the default
    `ocr_retry_evidence` partial slice
  - combine with `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, `LIMIT=<n>`, and
    `ARTIFACT_IDS=<artifact_id>` for explicit manual source-artifact review
  - use shortlist IDs, candidate artifact IDs, source previews, and fillable
    `selected_action=undecided` fields to prepare local human decisions before
    any OCR rerun, curation, feedback closure, or warehouse mutation
- `make manual-evals-ocr-retry-selection-draft`
  - write a local ignored OCR retry human-selection draft for the default
    `ocr_retry_evidence` partial shortlist
  - combine with `DRAFT_PATH=<path>`, `FORCE=1`, `COHORT=<cohort_id>`,
    `OUTCOME=<outcome>`, `LIMIT=<n>`, and `ARTIFACT_IDS=<artifact_id>` for
    explicit local decision files
  - default output is
    `.local/manual_eval_decisions/ocr_retry_selection_draft.json`; existing
    files are not overwritten unless `FORCE=1`
  - fill the draft locally, then validate it with
    `make manual-evals-ocr-retry-selection-validate SELECTION_PATH=<path>`
    before any apply preview or execution surface
- `make manual-evals-ocr-retry-selection-validate`
  - validate local OCR retry human decisions against the current default
    `ocr_retry_evidence` partial shortlist without mutating eval data
  - combine with `SELECTION_PATH=<path>`, `COHORT=<cohort_id>`,
    `OUTCOME=<outcome>`, `LIMIT=<n>`, and `ARTIFACT_IDS=<artifact_id>` for
    explicit manual source-artifact review
  - use `rerun_input`, `curated_case`, or `context_only` decisions plus
    selected artifact IDs to catch missing, stale, duplicate, or mismatched
    selections before any OCR rerun, curation, feedback closure, live eval
    write, or warehouse mutation
- `make manual-evals-ocr-retry-selection-apply-preview`
  - print a read-only would-apply plan from a valid local OCR retry selection
    JSON without mutating eval data
  - combine with `SELECTION_PATH=<path>`, `COHORT=<cohort_id>`,
    `OUTCOME=<outcome>`, `LIMIT=<n>`, and `ARTIFACT_IDS=<artifact_id>` for
    explicit manual source-artifact review
  - require selection validation `state=ok` before payload previews are
    emitted; otherwise inspect the validation blockers and keep the preview
    blocked
  - use the split by `rerun_input`, `curated_case`, and `context_only` to
    inspect would-apply payloads before any OCR rerun, curation, feedback
    closure, live eval write, or warehouse mutation
- `make manual-evals-ocr-retry-execution-readiness`
  - print a read-only execution-readiness report from the same local OCR retry
    selection JSON without mutating eval data
  - combine with `SELECTION_PATH=<path>`, `COHORT=<cohort_id>`,
    `OUTCOME=<outcome>`, `LIMIT=<n>`, and `ARTIFACT_IDS=<artifact_id>` for
    explicit manual source-artifact review
  - require selection apply-preview `state=ok`, then check selected
    `rerun_input` and `curated_case` artifacts for existing source files and
    payload-only command previews
  - use this as the final read-only readiness gate before a separate explicit
    execution kernel; OCR execution, feedback closure, live eval writes, and
    manual eval warehouse mutation stay in separate gates
- OCR retry execution:
  - `docs/runtime/OCR_RETRY_EXECUTION_GATE.md`
  - `make manual-evals-ocr-retry-execute`
  - requires `SELECTION_PATH=<path>` plus
    `CONFIRM=ocr-retry-execute`
  - recomputes validation, apply-preview, and execution readiness in-process
  - writes only a local ignored execution bundle under
    `.local/manual_eval_runs/ocr_retry/`
  - leaves feedback, live eval rows, `manual_evals.db`, and the manual eval
    warehouse unchanged
- OCR retry execution bundle inspection:
  - `make manual-evals-ocr-retry-execution-report RUN_DIR=<path>`
  - reads one local ignored execution bundle while OCR execution and eval data
    remain unchanged
  - reports `ok`, `attention`, or `error` after checking files, run IDs,
    request/response counts, provider failure status, stop reasons, and the
    warehouse mutation boundary
- OCR retry feedback-closure preview:
  - `make manual-evals-ocr-retry-feedback-closure-preview RUN_DIR=<path>`
  - reads one inspected local execution bundle while feedback and eval data
    remain unchanged
  - groups OCR retry responses by feedback ID, proposes closeable feedback
    items only as preview data, and marks mixed provider status as `attention`
- OCR retry feedback-closure apply:
  - `make manual-evals-ocr-retry-feedback-closure-apply RUN_DIR=<path>
    CONFIRM=ocr-retry-feedback-closure-apply`
  - requires `RUN_DIR=<path>` plus
    `CONFIRM=ocr-retry-feedback-closure-apply`
  - emits
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`
  - runs as a backup-first gate by copying
    `.local/runtime_dbs/active/manual_evals.db` under
    `.local_archive/manual-evals-feedback-closure-apply-<timestamp>/` before
    any feedback row update
  - applies only feedback `status`, `action_taken`, and `updated_at` updates
    after the execution-bundle report and feedback-closure preview are both
    `ok`
- OCR retry feedback-closure apply report:
  - `make manual-evals-ocr-retry-feedback-closure-apply-report RUN_DIR=<path>`
  - reads the local apply summary as a read-only report
  - emits
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1`
  - verifies active feedback rows are closed and backup feedback rows remain
    open before any manual restore decision
- OCR retry feedback-closure restore:
  - `make manual-evals-ocr-retry-feedback-closure-restore-preview
    BACKUP_DIR=<path>`
  - previews restore readiness as a read-only gate
  - `make manual-evals-ocr-retry-feedback-closure-restore BACKUP_DIR=<path>
    CONFIRM=ocr-retry-feedback-closure-restore`
  - emits
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_restore.v1`
  - writes a pre-restore backup under
    `.local_archive/manual-evals-feedback-closure-restore-<timestamp>/`, then
    restores the whole manual eval warehouse from the verified apply backup
- `make docs`
  - start or reuse the local server and print the API docs URL
- `make docs-open`
  - start or reuse the local server and launch the API docs URL in the system
    browser
- `make viz`
  - start or reuse the local server and print the PASS/FAIL viz URL
- `make viz-open`
  - start or reuse the local server and launch the PASS/FAIL viz URL in the
    system browser
- `make end`
  - literal closeout routine from clean synced `main`: docs freshness,
    transcript fix/check, doctor, script/path checks, risk-scan, operator command
    checks, Python style/type checks, docs lint, tests, security checks,
    `make end-stop`, and final clean-main Git check
- `make end-docs-check`
  - verifies `STATE` and local `SESSION_HANDOFF` were refreshed today
  - when local `SESSION_HANDOFF` exists, verifies it names the current short
    commit so same-date stale handoffs fail closeout
- `make security-checks`
  - local Python and root Node dependency audits
  - Python audit tooling is installed from `requirements.txt`, not side-loaded
    in CI
- `make refresh-deps`
  - refreshes the local Python environment and root npm lock after Dependabot
    or dependency metadata changes
- `make package-install-check`
  - install the root package editable without dependencies and verify package
    metadata/import identity
- `make lint-docs`
  - docs lint
- `make scripts-check`
  - validates tracked shell helper shebangs, strict modes, sourced helper
    contracts, and root-helper coverage for executable operator scripts
- repo activity heartbeat
  - common lifecycle, validation, and runtime operator work Make targets mark
    repo activity before running their work
  - current background-runner start/stop targets that own local process state
    mark repo activity before lifecycle work begins
  - activity marking updates caffeinate activity metadata only; wake-lock PID
    ownership stays unchanged
  - pure status/read-only targets report state while preserving activity
    freshness
- `make local-runtime-config-check`
  - validates VS Code task/config shape, extension recommendation drift, and
    devcontainer config/setup-script drift through
    `tools.check_local_runtime_config`
- `make risk-scan`
  - validates that known high-risk runtime, script, CI, runner, and local
    configuration surfaces remain visible in tracked docs and Make gates
- `make operator-command-check`
  - validates canonical manual eval commands and parked OCR eval shortcut
    boundaries
- `make startup-contracts-check`
  - validates startup and active-kernel runtime doc contracts
- `make ruff-check`
  - Python lint
- `make ruff-format-check`
  - Python format check
- `make type-check`
  - mypy check for active `src/` and `tools/` Python surfaces
- `make test`
  - test suite
- `make ci`
  - local aggregate of the named GitHub CI job targets:
    `ci-docs`, `ci-python-style`, `ci-python-type-check`, `ci-package`,
    `ci-test`, `ci-python-security`, and `ci-node-security`
- `make build-hygiene`
  - PR-safe build hygiene gate that runs `doctor-env`, `transcript-check`,
    `make ci`, and `git diff --check`
- `make pr-preflight`
  - local PR readiness command for `make build-hygiene`
- `make github-health`
  - read-only GitHub helper that reports `gh` auth state, recent failed
    workflow runs, open PR check state, and the next useful `gh` command

Dependency maintenance:

1. Merge grouped Dependabot PRs before single-package duplicates.
2. Close duplicate single-package PRs once the grouped PR contains the same
   bump.
3. Run `make refresh-deps` after syncing `main`.
4. Run `make security-checks`.
5. Finish with `make end` on clean synced `main`.

- `make openai-account-summary`
  - print OpenAI organization costs and usage from the Admin API
  - requires `OPENAI_ADMIN_KEY` or `OPENAI_ADMIN_KEY_ENV=<env_name>`
- `make openai-costs`
  - print OpenAI organization cost totals
- `make openai-usage`
  - print OpenAI organization usage totals
- `make openai-limits OPENAI_PROJECT_ID=<project_id>`
  - print OpenAI project rate limits
- `make end-git-check`
  - standalone clean-main closeout check; `make end` runs it as the final
    closure gate
- `make git-prune-stale-refs`
  - prunes stale `origin/*` remote-tracking refs after merged or deleted PR
    branches without deleting local branches
