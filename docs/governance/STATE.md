<!-- @format -->

# Project State

Last updated: 2026-06-27

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
  - Codex proactively records durable contract changes in the decision log
  - cleanup proceeds one kernel at a time from clean synced `main`
  - morning startup is a chat-first alignment pass: `make start` rehydrates,
    reports context, a kernel map, and any attention note, then waits for human
    alignment before implementation
- Public-facing surfaces remain derived from repo truth:
  - the root README now names the Polinko research model as staged for the
    next beta, replacing generic maintenance framing with a model-refactor
    status note
  - the root README includes a short refactor map that points readers to the
    public method and journey diagrams
  - the public status badge set distinguishes the Polinko research model,
    active model refactor, eval contract, research surface, and CI status
  - the root README points to public research docs, not local portfolio
    commands
  - portfolio source lives under `apps/portfolio/`, while tracked static output
    stays under `public/portfolio/`
  - `frontend` and `ui` are retired web-surface names; remaining Make/config
    references are compatibility aliases only
  - private portfolio mockups and screenshots stay in `docs/peanut/`
  - private portfolio mockups use `docs/peanut/assets/portfolio-mockups/`
  - ignore policy preserves only the current private portfolio mockup
    placeholder under `docs/peanut/assets/portfolio-mockups/`
  - promotion from private portfolio work to public docs requires explicit
    approval
- The eval contract is explicit and binary:
  - release outcomes are `pass` / `fail`
  - OCR case judgment remains `pass` / `fail`
  - OCR-ready candidate cleanup happens upstream of OCR judgment
- Polinko is entering the next method beta from a frozen Beta 2.3 snapshot:
  - fail-first evaluation is the active posture
  - active maintenance kernels prioritise runtime/script hygiene and
    docs/tooling alignment; OCR-specific work is treated as a parked research
    lane to resume intentionally when that lane reopens
  - Beta 2.3 evidence is frozen under `docs/eval/beta_2_3/`
  - `pre-Beta 2.4` is staged as the next research-model contract
  - the next model-contract review must preserve the original positive
    instruction shape by describing the behaviours the model should produce as
    the primary contract
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
  - startup/runtime smoke defaults to isolated localhost port and `/tmp`
    database paths per run, while explicit `SMOKE_PORT`, `SMOKE_BASE_URL`, and
    smoke DB path overrides remain available for fixed-endpoint debugging
  - local eval gates resolve the checkout root before starting their fresh
    local server or launching gate modules, so subdirectory invocation uses the
    same packaged runtime surface as Make execution; direct invocation without
    `PYTHON` prefers the repo `.venv` interpreter when available
  - core background runner lifecycle is script-owned for `caffeinate`,
    `server-daemon`, `eval-sidecar`, and `portfolio-mockups`; Make targets
    delegate start, status, and stop actions to helper scripts with repo-owned
    PID/log handling, and direct runner invocation uses the shared
    `tools/python_runtime.sh` interpreter rail for detached launchers
  - `caffeinate` command and match-pattern config are paired in Make so status
    and closeout cleanup inspect the same wake-lock shape that start launches
  - `server-daemon` adopts matching local `uvicorn server:app` processes on
    start, reports matching servers without PID files on status, and stops
    matching servers during closeout recovery
  - `server-daemon` trusts managed PID files only when the live PID matches
    the configured Polinko `uvicorn` app; stale PID files that point to
    unrelated live processes are cleaned without stopping the unrelated process
  - `eval-sidecar` reports missing current-file drift on start/status and still
    stops the repo-managed PID during closeout
  - `eval-sidecar` trusts managed PID files only when the live PID matches the
    `tools.eval_sidecar run` process shape; stale PID files that point to
    unrelated live processes are cleaned without stopping the unrelated process
  - `portfolio-mockups` treats a reachable mockup URL without a PID file as a
    lifecycle issue: matching local `http.server` processes are adopted, while
    unmanaged reachable ports fail loudly
  - `portfolio-mockups` trusts managed PID files only when the live PID matches
    the configured mockup `http.server` process shape; stale PID files that
    point to unrelated live processes are cleaned without stopping the
    unrelated process
  - manual eval health, feedback, overlay, OCR retry, and reclassification Make
    targets keep their public names while routing through a single
    `MANUAL_EVALS_DB_HEALTH_COMMAND` entrypoint and shared Make helper
  - surface Make targets and config keep public entrypoints at
    `makefiles/surfaces.mk` and `makefiles/config/surfaces.mk`, while
    role-owned fragments live under matching `makefiles/*/surfaces/`
    directories
  - eval Make config keeps the public entrypoint at
    `makefiles/config/evals.mk`, while role-owned fragments live under
    `makefiles/config/evals/` for quality gates, OCR case sources, eval
    sidecar, OCR runners, and report workflows
  - runtime Make targets keep the public entrypoint at
    `makefiles/runtime.mk`, while role-owned fragments live under
    `makefiles/runtime/` for core lifecycle, server-daemon, local URL helpers,
    OpenAI account helpers, keep-awake, and privacy guard surfaces
  - check Make targets keep the public entrypoint at `makefiles/checks.mk`,
    while role-owned fragments live under `makefiles/checks/` for tests,
    Python static analysis, docs/rendering, runtime audits, and local
    developer helpers
  - build Make targets keep the public entrypoint at `makefiles/build.mk`,
    while role-owned fragments live under `makefiles/build/` for CI
    aggregation, dependency lock/install flows, package checks, and security
    gates
  - eval report wrappers resolve the checkout root before writing default
    report paths or launching report modules, so direct script execution and
    Make execution share the same report-output base
  - `make path-leak-audit-local` is an actionable local runtime-config audit:
    it checks hidden/editor/container config surfaces without failing on
    ignored manual-eval evidence bundles that intentionally retain source paths,
    and it validates VS Code task/config shape plus retired local doc/config
    tokens
  - `make privacy-local-on` installs the current machine-local handoff exclude
    pattern; tracked docs stay visible, while `make privacy-local-off` can
    clear any legacy docs skip-worktree state left by the older helper
    behaviour
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
  - `make manual-evals-feedback-source-context` prints read-only
    source-history context for selected open feedback rows using
    `schema_version=polinko.manual_eval_feedback_source_context.v1`; it
    defaults to the `grounding_source_verification` fail slice and does not
    mutate feedback, OCR rows, eval rows, or source history
  - `make manual-evals-feedback-decision-draft` writes a local ignored
    feedback-decision draft for the current source-context slice using
    `schema_version=polinko.manual_eval_feedback_decision_draft.v1`; it
    defaults to `.local/manual_eval_decisions/feedback_decision.json`, refuses
    overwrite unless `FORCE=1`, preserves source-context fingerprints, and
    does not mutate feedback, OCR rows, eval rows, the warehouse, or source
    history
  - `make manual-evals-feedback-decision-preview` reads a local
    human-reviewed decision through `DECISION_PATH=<path>` without mutation,
    validates it against the current source-context slice, and emits
    `schema_version=polinko.manual_eval_feedback_decision_preview.v1`
  - local feedback decision packets can record `keep_open` as the active
    evidence posture for overlay-assisted OCR hypothesis rows that have no
    exact OCR retry execution target; those rows remain hypothesis pressure
    until a real OCR comparison lane exists with attached overlay/source image
    context
  - `make manual-evals-overlay-comparison-readiness` prints a read-only
    overlay/OCR comparison readiness packet for selected overlay-assisted OCR
    hypothesis rows, using
    `schema_version=polinko.manual_eval_overlay_ocr_comparison_readiness.v1`
  - the readiness packet can read a local ignored overlay/source image context
    index at `.local/manual_eval_decisions/overlay_source_context_index.json`
    or `OVERLAY_SOURCE_INDEX_PATH=<path>`; index entries use
    `schema_version=polinko.manual_eval_overlay_source_context_index.v1` and
    must match the current source-context fingerprint before they make a row
    ready
  - overlay/OCR comparison readiness packets expose source context,
    source-image candidates, exact blockers, and payload-only previews before
    any OCR run, feedback closure, eval write, source-history mutation, or
    warehouse mutation
  - `make manual-evals-overlay-source-index-draft` writes a local ignored
    fillable overlay/source image context index from the current readiness
    slice using
    `schema_version=polinko.manual_eval_overlay_source_context_index_draft.v1`
  - `make manual-evals-overlay-source-index-validate` validates the local
    index against the current readiness packet using
    `schema_version=polinko.manual_eval_overlay_source_context_index_validation.v1`
  - overlay source-index drafts preserve feedback IDs, source sessions,
    message IDs, and source-context fingerprints, and require human-reviewed
    local source image paths before readiness can become ready
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
  - the manual-eval health CLI is decomposed by responsibility:
    `tools/manual_evals_db_health.py` is the thin parser/router entrypoint,
    while CLI contracts, parser construction, output handling, feedback
    dispatch, OCR retry dispatch, and shared dispatch helpers live in focused
    `tools/manual_eval_cli_*` modules; parser construction now keeps
    `tools/manual_eval_cli_parser.py` as the stable facade while shared,
    feedback, and OCR retry argument-family helpers live in focused parser
    modules; parser boolean flag registration now reuses the shared parser
    helper while preserving public option order, with option-order and
    coordinator-order contract tests, and
    manual-eval CLI contract aliases now keep
    `tools/manual_eval_cli_contracts.py` as the stable public facade while
    grouped feedback, overlay, OCR retry, and shared contract modules own the
    underlying schema/default aliases with a focused export-order test; OCR
    retry dispatch now keeps `tools/manual_eval_cli_ocr_retry_dispatch.py` as
    the stable coordinator while selection/source planning, execution, and
    feedback-closure command bodies live in lifecycle-owned dispatch modules
    with a focused group-order contract test; OCR retry dispatch default
    filters now live in `tools/manual_eval_cli_dispatch_support.py` and are
    reused by execution and selection dispatch so the default `partial` /
    `ocr_retry_evidence` command contract has one source; feedback dispatch
    now keeps
    `tools/manual_eval_cli_feedback_dispatch.py` as the stable coordinator
    while reclassify, source-context, overlay, decision, and open-feedback
    command bodies live in focused dispatch modules with a focused
    group-order contract test; feedback dispatch command-family filtering now
    reuses the shared support helper for default filters and positive limits;
    feedback and OCR retry dispatch paths now reuse the shared support helper
    for local artifact path normalization; guarded error-default finish calls
    now reuse the shared support helper while preserving explicit status
    mappings; OCR retry dispatch report-builder argument expansion now reuses
    the shared support helper for retry defaults, positive limits, and
    optional artifact IDs; filtered feedback dispatch report-builder argument
    expansion now reuses the shared support helper for default filters and
    positive limits; OCR retry selection post-feedback read-only report
    dispatch now uses a local command table for route order, report builders,
    formatters, and path/artifact argument shape; feedback reclassify
    dispatch now uses a local command table for route order, builders,
    formatters, no-context defaults, plan/confirm/backup path handling, and
    preview/apply status mappings; feedback overlay dispatch now uses a local
    command table for route order, report builders, formatters, overlay
    defaults, source-index path handling, output/force handling, and direct
    versus guarded finish semantics; feedback decision dispatch now uses a
    local command table for route order, report builders, formatters, feedback
    decision defaults, output/force handling, decision-path handling, and
    guarded finish semantics; OCR retry feedback-closure dispatch now uses a
    local command table for route order, report builders, formatters, run-dir
    handling, backup-dir handling, confirmation tokens, backup/restore roots,
    direct preview finish semantics, and guarded apply/report/restore finish
    semantics; the thin health/router entrypoint now has focused contract
    coverage for route order, short-circuit behavior, health fallback, and
    explicit guarded-mutation marker coverage
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
  - devcontainer setup resolves the git top-level before creating `.venv`
    and installing root or portfolio dependencies; venv creation uses the
    configurable `POLINKO_DEVCONTAINER_BOOTSTRAP_PYTHON` bootstrap interpreter,
    then pip installs run through the created venv Python
  - devcontainer VS Code settings use repo-owned Ruff and mypy tooling from
    `.venv`
  - Python dependencies use `requirements.in` plus generated
    `requirements.txt`, matching pip-tools and Dependabot conventions
  - `make deps-lock` and `make deps-lock-check` use the same explicit
    pip-tools backtracking resolver
  - Python security tooling and pins are tracked through `requirements.in` plus
    generated `requirements.txt`; current refreshed pins include
    `pip-audit==2.10.0`, `PyJWT==2.13.0`, `pip==26.1.2`, and `pypdf==6.13.3`
  - root Node security locks are tracked through `package-lock.json`; current
    refreshed transitive pins include `undici==7.28.0`
  - GitHub CI runs on pull requests and on pushes to `main`; feature-branch
    pushes rely on the pull-request gate to avoid duplicate red runs, and CI
    plus dependency-review workflows cancel superseded runs when a newer commit
    arrives
  - GitHub CI and dependency-review workflows use explicit read-only repository
    token permissions
  - Dependabot routine and security updates are grouped by ecosystem so Python,
    root npm, portfolio npm, and GitHub Actions updates stay below GitHub's open
    PR queue limits
  - local dependency refreshes are explicit through `make refresh-deps` before
    rerunning `make security-checks`
  - shell helper hygiene is explicit through `make scripts-check`, which
    verifies tracked `tools/*.sh` shebangs, strict modes, shell parser syntax,
    sourced helper contracts, and root-helper coverage for executable operator
    scripts
  - runtime risk-surface coverage is explicit through `make risk-scan`, which
    verifies that known high-risk runtime, script, CI, runner, and local
    configuration surfaces remain visible in tracked docs and Make gates,
    including the lightweight pre-commit hook contract
  - runtime tool reference coverage is explicit through unit tests, which
    verify that active Make, CI, runtime, docs, and tooling references point to
    existing `tools/*.py` and `tools/*.sh` helpers, and that tracked runtime,
    script, docs, and config references to tracked helpers have direct test
    visibility
  - Make Python helper targets use the configured `$(PYTHON)` interpreter for
    repo-local checks, including `make pycheck`
  - direct runtime shell wrappers share `tools/python_runtime.sh`, so explicit
    `PYTHON` wins, repo `.venv` is preferred for direct invocation, and
    `python3` remains the final fallback
  - local runtime config coverage is explicit through
    `make local-runtime-config-check`, which validates VS Code and
    devcontainer config shape, rejects retired local doc references, guards
    retired VS Code extension recommendation drift, and runs through
    `make ci-docs`
  - operator alias coverage is explicit through `make operator-alias-check`,
    which keeps `manual-evals-*` targets paired with their `manualdb-*`
    compatibility aliases and keeps parked OCR eval aliases out of automatic
    startup, closeout, and CI dependencies
  - `make ci-docs` runs `make path-leak-check`, `make scripts-check`,
    `make local-runtime-config-check`, `make risk-scan`,
    `make operator-alias-check`, `make startup-contracts-check`, and
    `make lint-docs`; `make end` also runs `make path-leak-check`,
    `make scripts-check`, `make risk-scan`, and `make operator-alias-check`
    before longer style, type, test, and security gates
  - public diagram renderers use source-first, write-if-changed behaviour:
    Mermaid SVGs use the diagram manifest, and the D3 Evidence Sankey renders
    through a temporary SVG before replacing the tracked artefact
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
  - `make end` is the canonical closeout target; `make eod` remains a
    compatibility alias only
  - `make caffeinate` launches the managed wake-lock process in a detached
    child session through the configured Python launcher
  - `make caffeinate-status`, `make decaffeinate`, and `make end` operate on
    the repo-owned PID without adopting unrelated user wake-lock processes
  - repo-managed caffeinate writes metadata for PID ownership and repo activity
    state so status can distinguish `ACTIVE`, `QUIET`, `STALE`, and `OFF`
  - high-traffic lifecycle and validation Make targets update repo activity
    metadata without changing wake-lock ownership
  - `make caffeinate-off-all` is repo-scoped by default; global matching-process
    cleanup requires explicit operator opt-in
  - `make end-stop` closes the core background runner family:
    `eval-sidecar`, `portfolio-mockups`, `server-daemon`, and repo-managed
    `caffeinate`, then prints status for each family member
  - background runner scripts launch detached child processes through
    `tools/launch_detached_process.py` after resolving the checkout root
    through `tools/repo_root.sh`, while each runner keeps its own liveness,
    adoption, status, and stop logic
  - `tools/launch_detached_process.py` stops a started child process if the
    PID file cannot be written, so failed starts do not leave unmanaged
    background processes behind
  - VS Code keeps `make start` available as a manual task; folder-open
    bootstrap is retired so startup stays chat-led
  - `make doctor-env` reports both the active interpreter path and its source
    label, so repo `.venv`, override, and host fallback paths are visible
    during startup
  - local URL helpers such as `make docs`, `make open-api-docs`, and
    `make viz` print the target URL by default instead of launching a browser
  - explicit browser launch remains available through `make docs-open`,
    `make open-api-docs-browser`, `make viz-open`, `make open-viz`, and
    `make portfolio-open`; those system-launch paths route through
    `tools/open_local_url.sh`
  - base OCR transcript case and stability workflows now use the same shared
    case guard as growth, focus, and transcript-lane OCR wrappers, so missing
    and empty case-file handling stays consistent before eval runners launch
  - OCR intake, focus, growth, case-guard, and transcript workflow entrypoints
    resolve the checkout root before using default local paths, sourcing guard
    helpers, or delegating to eval runners, so direct script execution behaves
    like Make and subdirectory invocation
  - OCR report workflow/build wrappers resolve the checkout root before
    validating local report inputs or launching report-builder modules, so
    direct script execution behaves like Make and subdirectory invocation
  - direct OCR eval runner wrappers resolve the checkout root before starting
    the server daemon or launching eval modules, and direct invocation without
    `PYTHON` uses the shared `tools/python_runtime.sh` repo `.venv` fallback
  - direct OCR growth eval runner wrappers use the same checkout-root and repo
    `.venv` fallback contract before starting the server daemon or launching
    growth eval modules
- Local operator tooling follows a reusable non-mutating contract:
  - `docs/runtime/LOCAL_TOOLING.md` records the repo-local pattern for tools
    that materialize ignored local input, validate it, preview application, and
    execute only through a separate explicit follow-up gate
  - `make repo-search` is the routine active-surface search helper; it keeps
    maintenance searches focused on implementation, runtime/research docs,
    tests, and operator scripts without flooding the operator with transcript,
    archive, generated-output, or long governance-log lanes
  - `make repo-search-full` is the explicit source/evidence search helper for
    cases where private transcripts, frozen eval snapshots, or long governance
    history are the active source
  - shell bootstrap and operator helpers resolve the checkout root through
    `tools/repo_root.sh` so startup, closeout, clean-main git checks,
    devcontainer setup, local privacy guard, OCR workflow/orchestrator wrappers,
    and Playwright snapshot scripts share one audited root-discovery path
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
  - `make end-docs-check` verifies `STATE` and local `SESSION_HANDOFF` date
    freshness; when local `SESSION_HANDOFF` exists, it must also mention the
    current commit so a same-date but stale handoff cannot pass closeout

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
- `make risk-scan`
- `make local-runtime-config-check`
- `make operator-alias-check`
- `make package-install-check`
- `make type-check`
- `make test`
- `make security-checks`
- `make ci` when checking the local equivalent of GitHub CI job targets
- `make pr-preflight` before publishing PRs that need the CI-equivalent gate
  plus whitespace diff check
- `make end`
- `make end-docs-check` when validating current-truth freshness explicitly
- `make end-git-check` as the standalone clean-main check
- `make git-prune-stale-refs` after merged or deleted PR branches leave stale
  `origin/*` remote-tracking refs
