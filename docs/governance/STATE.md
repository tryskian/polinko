<!-- @format -->

# Project State

Last updated: 2026-05-21

## Current Truth

- Backend-first runtime remains canonical:
  - FastAPI API + chat-facing manual eval workbench endpoints are active
    execution and manual-eval surfaces
  - ASGI app construction lives in `src/polinko/asgi.py`
  - root `server.py` remains the `uvicorn server:app` compatibility shim
  - CLI chat implementation lives in `src/polinko/cli.py`
  - `make chat`, `polinko-chat`, and root `main.py` launch the packaged CLI
  - legacy root `app.py` has been retired after the deprecation/removal
    preflight found no active tracked or focused local ignored-lane launcher
    usage
  - Python package-boundary contract is documented; `config`, API,
    and core runtime implementation now live under `src/polinko/`
  - `pyproject.toml` and `src/polinko/` provide the editable-install rail for
    the runtime package
  - legacy root `config.py` has been retired after the legacy-import preflight
    found no active tracked or focused local ignored-lane root import usage
  - legacy root `api/` has been retired after the legacy-import preflight
    found no active tracked or focused local ignored-lane root import usage
  - legacy root `core/` has been retired after the legacy-import preflight
    found no active tracked or focused local ignored-lane root import usage
  - the package-boundary audit confirms active `src/` and `tools/` Python
    imports use `polinko.*`, while remaining root compatibility surfaces are
    launchers only
  - the entrypoint compatibility contract maps `make chat`, `python main.py`,
    `polinko-chat`, `make server`, `make localhost`, `make server-daemon`,
    local eval gates, and Docker to their packaged CLI or ASGI implementation
    paths
  - the root launcher readiness audit records `server.py` as not
    retirement-ready
    while `server:app` remains active in Docker, Make defaults, server-daemon,
    and local eval gates
  - `app.py`, `config.py`, root `api/`, and root `core/` are retired;
    remaining root launcher retirement work stays surface-specific and must
    preserve manual eval and operator workflows
  - prompt and runtime behaviour stay minimal and deterministic
  - notebooks, local evidence databases, `/chat`, and `/chats/*` remain active
    because they feed manual evals, feedback, checkpoints, exports, and
    runtime history
  - notebook workspace defaults to `.local/notebooks/`, keeping manual eval
    notebooks in the local evidence lane by default
- The repository is the research object:
  - tracked docs, code, tests, and reports are canonical truth
  - public-facing writing is the derived publication layer from repo truth
  - local/private material stays in `docs/peanut/`
- Refactor method is human-led:
  - the human lead owns scope, method, acceptance, and go/no-go decisions
  - Codex owns implementation, validation, Git/PR flow, and hygiene execution
  - cleanup proceeds one kernel at a time from clean synced `main`
- Public-facing surfaces remain derived from repo truth:
  - the root README now points to public research docs, not local portfolio
    commands
  - portfolio source lives under `apps/portfolio/`, while tracked static output
    stays under `public/portfolio/`
  - `frontend` and `ui` are retired web-surface names; remaining Make/config
    references are compatibility aliases only
  - private portfolio mockups and screenshots stay in `docs/peanut/`
  - private portfolio mockups use `docs/peanut/assets/portfolio-mockups/`
  - promotion from private portfolio work to public docs requires explicit
    approval
- The eval contract is explicit and binary:
  - release outcomes are `pass` / `fail`
  - OCR case judgment remains `pass` / `fail`
  - OCR-ready candidate cleanup happens upstream of OCR judgment
- Polinko is entering the next method beta from a frozen Beta 2.3 snapshot:
  - fail-first evaluation is the active posture
  - Beta 2.3 evidence is frozen under `docs/eval/beta_2_3/`
  - `pre-Beta 2.4` is staged as the next research-model contract
  - the discarded run-level rollup hypothesis is not being carried forward
  - non-OCR lanes stay source-first rather than run-verdict-first
  - the manual eval workbench, including notebooks, local evidence databases,
    `/chat`, `/chats/*`, and runtime history, remains source evidence for that
    contract
  - manual eval workbench evidence rows link feedback to matching OCR
    source/result messages when a case link exists, rather than treating the
    latest OCR run in a session as the judged case
  - `/viz/pass-fail` also uses feedback-to-result message matching for manual
    eval rows, so run-specific chart rows do not borrow unrelated session
    feedback
  - active eval visualization labels use source-first monitor wording rather
    than retired run-level rollup labels
  - source-first manual eval payloads expose `summary_unit` for lane-summary
    wording; the temporary `rollup_unit` compatibility alias was retired after
    a tracked and local consumer audit found no active dependency
  - source-first manual eval payloads expose
    `schema_version=polinko.manual_eval_source_first.v1`; generated
    `manual_evals.db` metadata exposes
    `schema_version=polinko.manual_evals_db.v1`
  - `make api-smoke` includes non-browser checks for `/manual-evals/surface`
    and `/viz/pass-fail/data` so source-first schema and summary-unit drift is
    caught in the startup/runtime smoke path
  - `/manual-evals/surface` and `/viz/pass-fail/data` expose read-only
    `data_freshness` status for the local manual eval warehouse so stale,
    schema-old, unknown, or missing source data is visible without rebuilding
    local databases
  - `data_freshness` compares source history counts against the manual eval
    import scope, so idle chats outside feedback/checkpoint/OCR evidence do
    not make a freshly rebuilt warehouse stale
  - `make manual-evals-db-status` prints terminal-native freshness without
    mutating local databases, while `make manual-evals-db` preserves an
    existing warehouse under `.local_archive/manual-evals-db-refresh-*` before
    rebuilding and prints the post-refresh status
  - `make manual-evals-db-health` reports read-only source-quality signals for
    the current warehouse, including source coverage, missing image assets,
    missing image debt by source family, feedback-to-result links, open
    feedback debt by outcome, and session evidence mix
  - `make manual-evals-feedback-actionables` prints a read-only row-level list
    and JSON export for open manual-eval feedback using
    `schema_version=polinko.manual_eval_feedback_actionables.v1`
  - `make manual-evals-feedback-cohorts` prints read-only action cohorts for
    open manual-eval feedback using
    `schema_version=polinko.manual_eval_feedback_cohorts.v1`
  - open feedback actionables and cohorts can be narrowed with
    `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, and `LIMIT=<n>` Make variables;
    cohort filtering remains read-only and uses explicit `recommended_action`
    labels
  - `make manual-evals-no-context-reclassify-preview` previews
    overlay-hypothesis OCR feedback rows that have no same-session OCR context
    and whose source response asked for new image evidence, using
    `schema_version=polinko.manual_eval_no_context_feedback_reclassify.v1`
  - `make manual-evals-no-context-reclassify-apply` requires
    `CONFIRM=manual-evals-no-context-reclassify`, keeps matching feedback rows
    open as overlay-assisted OCR hypothesis evidence, writes a backup under
    `.local_archive/manual-evals-feedback-no-context-*`, and limits mutation
    to feedback `recommended_action`, `action_taken`, and `updated_at`
  - `make manual-evals-feedback-reclassify-preview` reads a local
    human-reviewed plan through `PLAN_PATH=<path>` without mutation, using
    `schema_version=polinko.manual_eval_feedback_reclassify.v1`
  - `make manual-evals-feedback-reclassify-apply` requires
    `PLAN_PATH=<path>` and `CONFIRM=manual-evals-feedback-reclassify`, keeps
    matching feedback rows open, writes a backup under
    `.local_archive/manual-evals-feedback-reclassify-*`, and limits mutation
    to feedback `recommended_action`, `action_taken`, and `updated_at`
  - `make manual-evals-ocr-retry-candidates` prints a read-only OCR retry
    candidate packet for selected open feedback, grouped by source session and
    latest same-session OCR run, using
    `schema_version=polinko.manual_eval_ocr_retry_candidates.v2`
  - OCR retry candidate packets expose read-only readiness flags for ambiguous
    same-session OCR context and missing explicit feedback-to-result links
    before any reruns
  - `make manual-evals-ocr-retry-source-verification` prints a read-only
    source-verification packet for selected OCR retry candidates, using
    `schema_version=polinko.manual_eval_ocr_retry_source_verification.v1`
  - OCR retry source-verification packets expose feedback note/action text,
    candidate source image names, OCR run IDs, OCR previews, readiness flags,
    and exact not-confirmed reasons before any rerun or feedback closure
  - `make manual-evals-ocr-retry-source-provenance` prints a read-only
    source-history provenance packet for selected OCR retry candidates, using
    `schema_version=polinko.manual_eval_ocr_retry_source_provenance.v1`
  - OCR retry source-provenance packets expose source-history feedback message
    presence plus exact OCR source/result message IDs when they are already
    present in the warehouse; context-only OCR rows remain not exact links
  - `make manual-evals-ocr-retry-input-packet` prints a read-only OCR retry
    input packet for selected OCR retry candidates, using
    `schema_version=polinko.manual_eval_ocr_retry_input_packet.v1`
  - OCR retry input packets expose feedback IDs, source sessions, source image
    names, resolved image status, OCR run IDs, feedback source-message
    previews, and exact-link blocker state before any rerun or feedback
    closure
  - `make manual-evals-ocr-retry-rerun-manifest` prints a read-only OCR retry
    source-artifact selection manifest for selected OCR retry inputs, using
    `schema_version=polinko.manual_eval_ocr_retry_rerun_manifest.v1`
  - OCR retry rerun manifests expose source image names, OCR run IDs,
    resolution status, thumbnail dimensions, OCR previews, feedback
    source-message previews, and the separate feedback-closure blocker state
    before any rerun, curation, or feedback closure
  - `make manual-evals-ocr-retry-rerun-plan` prints a read-only OCR retry
    rerun plan for selected source artifacts, using
    `schema_version=polinko.manual_eval_ocr_retry_rerun_plan.v1`
  - OCR retry rerun plans expose stable source artifact IDs, feedback IDs,
    source sessions, OCR run IDs, source image names, resolved source paths,
    thumbnail dimensions, source previews, and payload-only command previews;
    `ARTIFACT_IDS=<artifact_id>` narrows the preview without running OCR,
    closing feedback, writing live evals, or mutating the warehouse
  - `make manual-evals-ocr-retry-selection-review` prints a read-only OCR retry
    source-artifact shortlist for human selection, using
    `schema_version=polinko.manual_eval_ocr_retry_selection_review.v1`
  - OCR retry selection reviews collapse duplicate source image artifacts from
    rerun plans, expose feedback IDs, OCR run IDs, source image names,
    thumbnail dimensions, source previews, and candidate payload previews, then
    keep the human disposition explicit as `rerun_input`, `curated_case`, or
    `context_only` before any OCR rerun, feedback closure, live eval write, or
    warehouse mutation
  - `make manual-evals-ocr-retry-selection-template` prints a read-only OCR
    retry human-selection template for the source-artifact shortlist, using
    `schema_version=polinko.manual_eval_ocr_retry_selection_template.v1`
  - OCR retry selection templates expose shortlist IDs, feedback IDs,
    candidate artifact IDs, OCR run IDs, source image names, thumbnail
    dimensions, source previews, and fillable decision fields that default to
    `selected_action=undecided`, without running OCR, closing feedback,
    writing live evals, or mutating the warehouse
  - `make manual-evals-ocr-retry-selection-draft` writes a local ignored OCR
    retry human-selection draft from the current source-artifact shortlist,
    using
    `schema_version=polinko.manual_eval_ocr_retry_selection_decision_draft.v1`
  - OCR retry selection drafts default to
    `.local/manual_eval_decisions/ocr_retry_selection_draft.json`, refuse to
    overwrite without `FORCE=1`, preserve shortlist IDs, candidate artifact
    IDs, source provenance, and template fingerprints, and remain local input
    for the validator and apply-preview gates without running OCR, closing
    feedback, writing live evals, or mutating the warehouse
  - `make manual-evals-ocr-retry-selection-validate` validates a local OCR
    retry human-selection JSON against the current source-artifact shortlist,
    using
    `schema_version=polinko.manual_eval_ocr_retry_selection_validation.v1`
  - OCR retry selection validation accepts compact decision lists or filled
    selection templates, requires `rerun_input`, `curated_case`, or
    `context_only`, verifies selected artifact IDs against the matching
    shortlist item, flags missing/stale/duplicate decisions, and remains
    read-only without running OCR, closing feedback, writing live evals, or
    mutating the warehouse
  - `make manual-evals-ocr-retry-selection-apply-preview` prints a read-only
    would-apply preview from a valid local OCR retry decision JSON, using
    `schema_version=polinko.manual_eval_ocr_retry_selection_apply_preview.v1`
  - OCR retry selection apply previews require validation `state=ok` before
    emitting would-apply payloads, split valid decisions by `rerun_input`,
    `curated_case`, and `context_only`, preserve selected artifact provenance,
    and keep pending/stale/duplicate/mismatched selections as blockers without
    running OCR, closing feedback, writing live evals, or mutating the
    warehouse
  - `make manual-evals-ocr-retry-execution-readiness` prints a read-only OCR
    retry execution-readiness report from a valid local decision JSON, using
    `schema_version=polinko.manual_eval_ocr_retry_execution_readiness.v1`
  - OCR retry execution readiness requires apply-preview `state=ok`, checks
    selected `rerun_input` and `curated_case` artifacts for existing source
    files and payload-only command previews
  - `make manual-evals-ocr-retry-execute` is the local-bundle OCR retry
    executor; it requires `SELECTION_PATH=<path>` plus
    `CONFIRM=ocr-retry-execute`, recomputes validation/apply-preview/readiness
    in-process, writes ignored run bundles under
    `.local/manual_eval_runs/ocr_retry/`, and does not close feedback, write
    live eval rows, refresh `manual_evals.db`, or mutate the warehouse
  - `make manual-evals-ocr-retry-execution-report` inspects one local OCR retry
    execution bundle with `RUN_DIR=<path>`, using
    `schema_version=polinko.manual_eval_ocr_retry_execution_report.v1`
  - OCR retry execution bundle reports are read-only, hide source file paths in
    terminal output, and check bundle files, run ID alignment,
    request/response counts, provider failure status, stop reasons, and the
    no-warehouse-mutation boundary before closure or any warehouse gate
  - `make manual-evals-ocr-retry-feedback-closure-preview` previews feedback
    closure from one inspected OCR retry execution bundle with
    `RUN_DIR=<path>`, using
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_preview.v1`
  - OCR retry feedback-closure previews group successful responses by feedback
    ID, mark mixed provider status as `attention`, and remain read-only: they
    do not close feedback, write action-taken text, refresh `manual_evals.db`,
    write eval rows, or mutate the warehouse
  - `make manual-evals-ocr-retry-feedback-closure-apply` applies OCR retry
    feedback closure from one inspected local execution bundle only when
    `RUN_DIR=<path>` and `CONFIRM=ocr-retry-feedback-closure-apply` are
    provided, the execution-bundle report and feedback-closure preview are
    both `ok`, every preview item is `ready`, and every target feedback row is
    still open
  - OCR retry feedback-closure apply writes a backup-first copy of the current
    manual eval warehouse under
    `.local_archive/manual-evals-feedback-closure-apply-<timestamp>/`, emits
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`,
    and limits mutation to feedback `status`, `action_taken`, and `updated_at`
  - `make manual-evals-ocr-retry-feedback-closure-apply-report` verifies the
    local apply summary with `RUN_DIR=<path>`, using
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1`
  - OCR retry feedback-closure apply reports are read-only and verify backup
    DB integrity, backup feedback rows still open, active feedback rows closed,
    and action-taken text present
  - `make manual-evals-ocr-retry-feedback-closure-restore-preview` inspects one
    apply backup with `BACKUP_DIR=<path>`, using
    `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_restore.v1`
  - `make manual-evals-ocr-retry-feedback-closure-restore` requires
    `BACKUP_DIR=<path>` and `CONFIRM=ocr-retry-feedback-closure-restore`,
    writes a pre-restore backup under
    `.local_archive/manual-evals-feedback-closure-restore-<timestamp>/`, then
    restores the whole manual eval warehouse from the verified apply backup
  - `docs/runtime/OCR_RETRY_EXECUTION_GATE.md` defines the local-bundle OCR
    retry executor boundary, including rollback and failure handling
  - manual eval warehouse rebuilds resolve OCR source images from extracted
    files first across private screenshot roots, tracked `docs/eval/`
    snapshots, the Dropbox screenshot sync root, and local export roots, then
    matching files inside `.zip` archives under configured image roots;
    archive-backed thumbnails are built without extracting files into the repo
  - the remaining unresolved image assets after the Dropbox screenshot root are
    text fixtures and stay historical source-name debt until curated source
    files are promoted
  - generated trace artifacts from manual submissions use manual eval workbench
    names, not `ui` names
  - co-reasoning is the first promoted non-OCR lane
  - uncertainty-boundary, hallucination-boundary, retrieval, and
    response-behaviour surfaces are operationalized
  - operator burden remains the active thin lane
  - no additional non-OCR lane currently meets promotion criteria
  - the lane map is current, and the research surface remains open
  - OCR remains one mature method lane inside the broader project
  - OCR is stabilized on the current image set, with broader
    generalization pressure as the next kernel
  - live eval execution is pinned until an explicit resume decision; the
    current OCR work surface is read-only inventory plus guarded local-bundle
    retry execution
  - OCR intake now uses transcript-mined episodes plus OCR-ready
    generalization candidates
  - `make ocr-inventory` prints a read-only map of tracked OCR cases plus
    local case, report, manual-eval DB, and notebook paths
  - `make ocr-inventory-json` exposes the same OCR evidence map in JSON,
    including source JSON shape and list-count metadata when available
  - OCR inventory freshness flags local case/report files as `current`,
    `stale`, `unknown`, or `missing` from existing `generated_at` metadata
  - OCR verdicts stay `pass` / `fail` under that broader intake
- Branch protection on `main` remains active:
  - PR required
  - strict status checks enabled
  - squash-only merge
- Development setup and dependency gates are aligned to canonical paths:
  - devcontainer setup creates `.venv`
  - devcontainer VS Code settings use repo-owned Ruff and mypy tooling from
    `.venv`
  - Python dependencies use `requirements.in` plus generated
    `requirements.txt`, matching pip-tools and Dependabot conventions
  - Dependabot Python/`pyproject.toml` version update jobs are currently
    blocked by GitHub's "cannot open any more pull requests" limit and should
    be triaged by reducing or merging the open dependency PR queue before
    treating the pyproject lane as healthy
  - portfolio Node setup uses `apps/portfolio/`
  - root and portfolio npm locks both have audit and Dependabot coverage
  - portfolio installs prefer `npm ci` when a lockfile is present
  - pre-commit runs lightweight repo-owned Ruff and markdownlint checks, while
    mypy remains a CI/closeout gate and Pyright remains advisory
- The type-check gate is explicit and scoped:
  - `make type-check` runs mypy against active `src/` and `tools/` Python
    code
  - frozen eval snapshots, local `docs/peanut` material, and untyped tests are
    excluded from the type-check gate
  - `make ci-python-type-check`, GitHub CI, and `make end` enforce the same
    scoped mypy surface
  - Pyright is repo-owned as an advisory/editor check:
    `make pyright-check` runs the pinned root Node dependency against
    `pyrightconfig.json`, but mypy remains the required CI and closeout gate
- Test and runtime resource hygiene is explicit:
  - sqlite connections are closed through explicit lifecycle handling
  - tests reject direct `with sqlite3.connect(...)` usage so Python 3.14
    ResourceWarning noise stays out of `make test`
- Runtime lifecycle controls are repo-managed:
  - `make caffeinate` launches the managed wake-lock process in a detached
    child session through the configured Python launcher
  - `make caffeinate-status`, `make decaffeinate`, and `make end` operate on
    the repo-owned PID without adopting unrelated user wake-lock processes
  - local URL helpers such as `make docs`, `make open-api-docs`, and
    `make viz` print the target URL by default instead of launching a browser
  - explicit browser launch remains available through `make docs-open`,
    `make open-api-docs-browser`, `make viz-open`, and `make open-viz`
- Local operator tooling follows a reusable non-mutating contract:
  - `docs/runtime/LOCAL_TOOLING.md` records the repo-local pattern for tools
    that materialize ignored local input, validate it, preview application, and
    execute only through a separate explicit follow-up gate
  - required knobs include an ignored local default path, explicit path
    override, no-overwrite default, `FORCE=1`, deterministic
    `schema_version`, source fingerprints, validation command, and
    apply-preview command
  - the OCR retry decision draft flow is the current reference instance, but
    the reusable contract is local input, validation, and apply-preview before
    any execution gate
- Documentation roles are explicit:
  - `CHARTER` holds durable rules
  - `STATE` holds tracked current truth
  - `RUNBOOK` holds operator procedure
  - `ARCHITECTURE` holds stable system shape
  - `PACKAGE_BOUNDARY` holds the Python package-boundary contract
  - `make package-install-check` verifies the editable-install rail
  - local `SESSION_HANDOFF` holds the active slice
  - `make end` now mirrors the legacy `make eod` closeout routine directly

## Active Priorities

1. Keep the public doorway stable and credible.
2. Keep tracked research docs compact and non-duplicative.
3. Keep the promoted non-OCR lane visible as the broader proof surface grows.
4. Keep operator-burden and related thin-lane work grounded in real evidence
   and distinct lane signal.
5. Keep OCR moving from current-set stability into generalization pressure.
6. Keep cleanup/refactor work anchored to the frozen Beta 2.3 baseline.
7. Keep exploring new seams without forcing promotion before the signal earns
   it.

## Canonical Sources

- Rules:
  - `docs/governance/CHARTER.md`
- Current truth:
  - `docs/governance/STATE.md`
- Procedure:
  - `docs/runtime/RUNBOOK.md`
- Structure:
  - `docs/runtime/ARCHITECTURE.md`
- Local tooling contract:
  - `docs/runtime/LOCAL_TOOLING.md`
- Durable history:
  - `docs/governance/DECISIONS.md`
- Active local carryover:
  - `docs/peanut/governance/SESSION_HANDOFF.md`

## Validation Baseline

- `make doctor-env`
- `make api-smoke`
- `make ruff-check`
- `make ruff-format-check`
- `make lint-docs`
- `make package-install-check`
- `make type-check`
- `make test`
- `make security-checks`
- `make ci` when checking the local equivalent of GitHub CI job targets
- `make end`
- `make end-docs-check` when validating current-truth freshness explicitly
- `make end-git-check` after merge and sync
