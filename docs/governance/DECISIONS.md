# Decisions Log

## Taxonomy

- `Category` values:
  - `runtime_engineering`
  - `eval_quality`
  - `collaboration_method`
  - `evidence_governance`
  - `workflow_environment`
  - `research_experiment`
- `Tags`:
  - lowercase snake_case labels for quick filtering

## Entry Criteria

Add an entry only when the change is durable and still governs the repo.

Good fits:

- collaboration model or control rights
- repo workflow rules
- runtime or eval contract changes
- evidence handling rules
- documentation governance rules

Keep temporary wrapper churn, wording tweaks, branch-local cleanup,
one-off debugging moves, and current-session handoff facts in the local handoff
or branch history instead.

## Entry Style

- keep entries short and operational
- one durable decision per entry
- use one category
- use 3 to 5 tags
- keep `Decision` and `Why` tight

## D-001: Backend-first runtime remains canonical

- Date: `2026-05-15`
- Category: `runtime_engineering`
- Tags: `backend_first`, `api_cli`, `presentation_boundary`
- Decision: FastAPI API plus CLI remain the execution surfaces, and
  presentation layers stay aligned with runtime and eval policy.
- Why: This keeps system behavior anchored in the backend and prevents surface
  work from changing the contract.

## D-002: The repository is the research object

- Date: `2026-05-15`
- Category: `evidence_governance`
- Tags: `repo_native`, `canonical_truth`, `public_derivation`
- Decision: Tracked docs, code, tests, and reports are canonical project
  truth, while public-facing writing serves as the derived publication layer
  from repo truth.
- Why: This keeps the source of truth stable and prevents publication surfaces
  from drifting into fake authority.

## D-003: Binary release gate stays primary

- Date: `2026-05-15`
- Category: `eval_quality`
- Tags: `binary_gate`, `retain_evict`, `lane_contract`
- Decision: Release outcomes remain `pass` / `fail`. Broader manual and
  non-OCR lanes may still use `retain` / `evict` after `fail` as upstream case
  curation, but OCR case judgment stays strict `PASS / FAIL` per `D-013`.
- Why: This keeps the release gate legible while preserving a clean
  distinction between binary judgment and the narrower curation surfaces that
  still matter outside OCR.

## D-004: Failure is primary signal

- Date: `2026-05-15`
- Category: `evidence_governance`
- Tags: `fail_first`, `signal_quality`, `pressure_visibility`
- Decision: Unresolved failure pressure stays visible through pass-rate
  reporting and summary framing.
- Why: The project is meant to inspect real behavior and expose pressure
  points clearly.

## D-005: `docs/peanut` is the local-only lane

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `local_only`, `private_lane`, `operator_notes`
- Decision: `docs/peanut/` is the local-only lane for transcripts, theory,
  design refs, working notes, and operator handoff.
- Why: This preserves a clean boundary between tracked project truth and
  private exploratory material.

## D-006: Clean synced `main` is the tracked stop state

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `protected_main`, `squash_pr`, `stop_state`
- Decision: Tracked truth should end on clean synced `main` through feature
  branches, PR checks, and squash merges.
- Why: This keeps local and remote tracked truth aligned.

## D-007: Document roles are explicit and non-overlapping

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `docs_roles`, `non_duplication`, `current_truth`
- Decision: `CHARTER` holds durable rules, `STATE` holds tracked current
  truth, `RUNBOOK` holds procedure, `ARCHITECTURE` holds system shape, and
  local `SESSION_HANDOFF` holds the active slice.
- Why: This keeps the docs stack legible and prevents overlap drift.

## D-008: Startup is an operator procedure backed by atomic commands

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `startup`, `operator_contract`, `atomic_commands`
- Decision: Startup is executed as an operator procedure backed by atomic
  commands and real rehydration.
- Why: The discipline lives in the thinking contract and the real
  rehydration pass.

## D-009: Reset the docs stack through focused replaces and a durable ledger

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `docs_reset`, `focused_replace`, `downsizing`, `current_truth`
- Decision: Reset the tracked docs stack by replacing each core doc with a
  smaller single-purpose version, then record the durable outcome in a compact
  decisions ledger.
- Why: The stack had drifted into overlapping warehouse surfaces where
  procedure, current truth, structure, and active carryover were duplicating
  each other and wrapper rituals were standing in for operator discipline.
- How:
  1. Create a local reset workspace under
     `docs/peanut/doc_resets/2026-05-15-live-doc-copies/`.
  2. Rewrite each copy from zero so every doc has one job.
  3. Remove negative and prohibition-style phrasing so the docs state what to
     do directly.
  4. Focused-replace tracked `RUNBOOK.md`, `STATE.md`, `ARCHITECTURE.md`, and
     `CHARTER.md` one file at a time with direct validation after each replace.
  5. Reset the local `SESSION_HANDOFF.md` so it carries only active local
     carryover.
  6. Replace tracked `DECISIONS.md` last with the durable ledger version.
- Diff Counts:
  - tracked `RUNBOOK.md`: `139 insertions`, `1435 deletions`
  - tracked `STATE.md`: `46 insertions`, `173 deletions`
  - tracked `ARCHITECTURE.md`: `60 insertions`, `94 deletions`
  - tracked `CHARTER.md`: `37 insertions`, `70 deletions`
  - local `SESSION_HANDOFF.md`: `38 insertions`, `93 deletions`
  - tracked `DECISIONS.md`: `101 insertions`, `4504 deletions`

## D-010: Thin non-OCR lanes promote only on distinct recurring method signal

- Date: `2026-05-16`
- Category: `research_experiment`
- Tags: `non_ocr`, `lane_promotion`, `thin_lane`, `signal_quality`
- Decision: Keep thinner non-OCR lanes in row-local or export-backed form until
  they show distinct task-shape pressure, recurring seam shape, and a real
  method consequence.
- Why: This keeps duplicate-heavy backlog from being mistaken for progress and
  makes promoted lanes earn tracked surface area.

## D-011: Stabilized OCR surfaces advance by generalization pressure

- Date: `2026-05-16`
- Category: `research_experiment`
- Tags: `ocr`, `generalization`, `stability`, `signal_quality`
- Decision: Once OCR is stabilized on the current image set, the next OCR
  kernel should apply generalization pressure through new visual conditions
  under the same eval contract.
- Why: Same-image stability is a real method gain, but it does not justify a
  broader claim until the lane holds under changed image conditions.

## D-012: OCR generalization intake uses both transcript and OCR-ready sources

- Date: `2026-05-16`
- Category: `research_experiment`
- Tags: `ocr`, `generalization`, `intake`, `candidate_curation`
- Decision: Beta 2.3 OCR intake now combines transcript-mined OCR episodes
  with a separate OCR-ready generalization candidate surface, then cuts a
  bounded review slice from that wider pool.
- Why: A failed mining attempt showed that transcript-only intake could hide a
  real OCR-ready image when the surrounding exchange was not phrased as a
  transcription task. The method needed a second intake surface so broader OCR
  pressure stays visible instead of disappearing behind the older miner gate.

## D-013: OCR case judgment stays strictly PASS / FAIL

- Date: `2026-05-16`
- Category: `research_experiment`
- Tags: `ocr`, `pass_fail`, `generalization`, `candidate_curation`
- Decision: Keep OCR case judgment strictly `PASS / FAIL`, even under broader
  generalization pressure. Use OCR-ready candidate curation upstream of eval,
  not as a second verdict layer inside OCR.
- Why: For OCR, the research signal is whether the extraction is right or
  wrong. That strict binary has already yielded high-signal results. Broader
  intake is useful, but it should widen the candidate surface before eval
  rather than muddy the OCR verdict contract itself.

## D-014: Freeze beta evidence before broad cleanup

- Date: `2026-05-19`
- Category: `evidence_governance`
- Tags: `beta_snapshot`, `eval_evidence`, `docs_sync`, `cleanup`
- Decision: When a method beta becomes the baseline for next-beta work, freeze
  its curated research and evidence read under `docs/eval/<beta>/` before broad
  refactor or cleanup work starts.
- Why: This gives cleanup work a stable evidence baseline and keeps current
  truth readable after the live research surface moves on.

## D-015: Normalize the CLI entrypoint before deeper refactors

- Date: `2026-05-19`
- Category: `architecture`
- Tags: `entrypoints`, `ia`, `build`, `cli`
- Decision: Make `main.py` the canonical CLI chat entrypoint, keep `server.py`
  as the FastAPI ASGI entrypoint, and retain `app.py` only as a compatibility
  launcher while build and docs surfaces converge on the new name.
- Why: Entry points are part of the repo information architecture. Normalizing
  them first lets later refactors work from clear runtime boundaries without
  changing API behaviour.

## D-016: Route GitHub CI through named Make targets

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `ci`, `validation`, `parity`
- Decision: Represent each required GitHub CI job with a named Make target
  (`ci-docs`, `ci-test`, `ci-python-security`, `ci-node-security`) and have
  Actions call those targets instead of duplicating command bodies.
- Why: The Makefile is currently the operator command router. Giving CI the
  same named entrypoints reduces drift between local validation and protected
  branch checks before larger Makefile decomposition starts.

## D-017: Preserve the default Make entrypoint explicitly

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `entrypoints`, `operator_surface`, `refactor`
- Decision: Declare `.DEFAULT_GOAL := chat` and keep phony declarations grouped
  by target family as the Makefile is refactored.
- Why: Large Makefiles should not rely on target ordering to define their
  default command. Making the default explicit preserves the existing
  no-argument `make` behavior while letting CI and other target families move
  independently.

## D-018: Extract Makefile families through include files

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `modularity`, `ci`, `dependencies`
- Decision: Move coherent Make target families into `makefiles/*.mk` fragments,
  starting with build, dependency, CI, and security targets in
  `makefiles/build.mk`.
- Why: The root Makefile should stay as the operator router and shared variable
  surface while large recipe families move into focused include files. This
  keeps target names stable for operators and CI while reducing root-file size
  and making later family-level refactors easier to review.

## D-019: Keep validation targets in a checks include

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `validation`, `checks`, `modularity`
- Decision: Move local validation, transcript, docs-render, path-leak,
  pre-commit, and `act` check targets into `makefiles/checks.mk` while keeping
  their public target names unchanged.
- Why: Validation targets are shared by local operator routines and CI-backed
  build targets. A dedicated checks include keeps that contract visible without
  burying it in the root operator router or mixing it into dependency/security
  recipes.

## D-020: Keep runtime controls in an operator include

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `runtime`, `operator_surface`, `modularity`
- Decision: Move CLI, lifecycle, server-daemon, browser-open, status,
  keep-awake, and local privacy targets into `makefiles/runtime.mk` while
  keeping their public target names unchanged.
- Why: Runtime controls are an operator surface, not eval or build logic. A
  dedicated runtime include keeps start/end and local machine controls visible
  while letting the root Makefile stay focused on shared variables, includes,
  and the remaining families still awaiting extraction.

## D-021: Keep local product surfaces in a dedicated include

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `portfolio`, `manual_evals`, `notebooks`, `modularity`
- Decision: Move notebook, manual eval database, portfolio/frontend,
  portfolio mockup, and Playwright helper targets into
  `makefiles/surfaces.mk` while keeping their public target names unchanged.
- Why: These targets operate local product and evaluation surfaces rather than
  build, validation, runtime lifecycle, or research eval logic. A dedicated
  surfaces include keeps manual eval and portfolio workflows active and visible
  while reducing root Makefile load without renaming directories yet.

## D-022: Keep eval and quality gates in a dedicated include

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `evals`, `quality_gate`, `modularity`
- Decision: Move OCR mining aliases, eval runners, API/eval smoke, eval
  sidecar, hallucination gate, and quality-gate targets into
  `makefiles/evals.mk` while keeping their public target names unchanged.
- Why: Eval and quality-gate targets are active research and release-pressure
  surfaces. A dedicated include keeps that contract visible as one family
  without mixing it into the root shared variable surface or non-eval
  container/performance checks.

## D-023: Keep external ops checks in a dedicated include

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `ops`, `containers`, `modularity`
- Decision: Move external smoke, container build/run, and filesystem/container
  scan targets into `makefiles/ops.mk` while keeping their public target names
  unchanged.
- Why: These targets depend on external operator tooling such as `k6`, Trivy,
  and Docker. A dedicated ops include keeps those optional checks available
  without leaving recipe bodies in the root Makefile after the build, check,
  runtime, product-surface, and eval families have been extracted.

## D-024: Map surface directories before renaming them

- Date: `2026-05-19`
- Category: `architecture`
- Tags: `ia`, `portfolio`, `frontend`, `static_assets`, `refactor`
- Decision: Record the current and target roles for portfolio source, static
  output, public routes, and private mockup assets in
  `docs/runtime/SURFACE_IA.md` before moving directories.
- Why: `frontend/`, `ui/`, and the private portfolio mockup path are ambiguous
  names with different runtime responsibilities. Mapping the roles first keeps
  the later move sequence reviewable and protects the chat workbench and manual
  eval routes from being swept into a portfolio rename.

## D-025: Name portfolio source and static directories explicitly

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `ia`, `portfolio`, `makefile`, `static_assets`, `refactor`
- Decision: Introduce `PORTFOLIO_APP_DIR` and `PORTFOLIO_STATIC_DIR`, backed
  by `POLINKO_PORTFOLIO_APP_DIR` and `POLINKO_PORTFOLIO_STATIC_DIR` for Python
  and Vite surfaces, while preserving the current `frontend/` and `ui/` paths
  and public target names. Keep `FRONTEND_DIR` as a legacy override feeding the
  new source-app default.
- Why: The next directory moves should be mechanical path changes, not coupled
  runtime rewrites. Naming source and output responsibilities first keeps the
  portfolio build, FastAPI static serving, and Netlify helper aligned.

## D-026: Move tracked portfolio output under public

- Date: `2026-05-19`
- Category: `architecture`
- Tags: `ia`, `portfolio`, `static_assets`, `public`, `refactor`
- Decision: Move the tracked portfolio static output from `ui/` to
  `public/portfolio/`, and make `PORTFOLIO_STATIC_DIR` default to that path.
  Keep `/portfolio`, `/assets`, `make portfolio`, `make portfolio-build`, and
  `make frontend-build` stable.
- Why: The output directory is deployable public static content, not source
  UI. Moving it under `public/portfolio/` makes the runtime role explicit while
  preserving operator and browser-facing entrypoints.

## D-027: Stage pre-Beta 2.4 as the research model contract

- Date: `2026-05-19`
- Category: `evidence_governance`
- Tags: `pre_beta`, `research_model`, `fail_pressure`, `manual_evals`,
  `pulse`
- Decision: Stage `pre-Beta 2.4` as the next method contract. OCR remains
  case-level `pass` / `fail` under generalization pressure. Non-OCR lanes may
  use bounded pulse-level `PASS` / `FAIL` with row evidence labels, while
  manual eval and chat workbench sources remain canonical evidence inputs.
- Why: Beta 2.3 froze lane evidence before cleanup. The next beta needs a
  named contract for how evidence rolls up from source artifacts to row labels,
  pulse verdicts, and eventual method claims.
- Current disposition: Superseded by `D-028`.

## D-028: Do not carry fail-pressure pulses into pre-Beta 2.4

- Date: `2026-05-19`
- Category: `evidence_governance`
- Tags: `pre_beta`, `research_model`, `fail_pressure`, `manual_evals`,
  `source_first`
- Decision: Treat the fail-pressure pulse hypothesis as historical method
  evidence, not the pre-Beta 2.4 forward path. Pre-Beta 2.4 stays
  source-first: active chat workbench artifacts, manual eval rows, row/case
  judgments, exclusions, and lane summaries carry the research model before
  any method claim is promoted.
- Why: The pulse shape did not work properly as a stable research surface. The
  next beta needs evidence rollup that preserves manual evals and row/case
  judgment without forcing a pulse-level verdict.

## D-029: Move portfolio source into a named app path

- Date: `2026-05-19`
- Category: `architecture`
- Tags: `ia`, `portfolio`, `frontend`, `mockups`, `refactor`
- Decision: Move the Vite portfolio source app from `frontend/` to
  `apps/portfolio/`, and move private portfolio mockup placeholders from
  `docs/peanut/assets/tumbles/portfolio/` to
  `docs/peanut/assets/portfolio-mockups/`. Keep `/portfolio`, `/assets`,
  `make portfolio`, `make portfolio-build`, `make frontend-build`, and
  `make portfolio-mockups` stable.
- Why: `frontend/` and the old mockup path described implementation shape
  rather than surface ownership. The new paths make portfolio source and
  private mockups explicit while leaving browser and operator entrypoints
  unchanged.

## D-030: Keep lifecycle aliases as target aliases

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `lifecycle`, `aliases`, `operator_surface`
- Decision: Keep `end` as the canonical closeout target and make `eod` and
  `end-preflight` dependency aliases. Keep keep-awake aliases pointed at their
  canonical targets instead of repeating recursive recipes.
- Why: Operator command names stay stable, while the Makefile has one recipe
  source for each lifecycle action.

## D-031: Keep shared Make configuration in a config include

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `config`, `modularity`, `operator_surface`
- Decision: Move shared Make variables into `makefiles/config.mk`, loaded
  before the target-family includes, while keeping root `Makefile` focused on
  the default goal and include order.
- Why: Target families now live in focused includes. Moving shared defaults
  into a config include removes the last large root-file block without
  changing operator or CI command names.

## D-032: Make portfolio naming canonical while preserving frontend aliases

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `portfolio`, `frontend`, `aliases`, `ia`
- Decision: Make `PORTFOLIO_APP_DIR` default directly to `apps/portfolio/`
  and add `make portfolio-install` as the canonical install target. Preserve
  `FRONTEND_DIR`, `make portfolio-app-install`, `make frontend-install`, and
  `make frontend-build` as compatibility aliases.
- Why: The physical source and static directories now have explicit names.
  The command/config surface should foreground portfolio ownership while
  keeping older operator commands and overrides working during the beta
  cleanup.

## D-033: Prefer dependency edges for internal Make wrapper chains

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `dry_run`, `dependencies`, `operator_surface`
- Decision: Express internal Make wrapper chains as prerequisites or
  target-specific variable assignments when the chain does not require shell
  control flow. Avoid embedding recursive `$(MAKE)` calls inside
  backslash-continued operator shell recipes.
- Why: Recursive Make lines are executed under `make -n`. Dependency edges keep
  dry-runs observational for common operator targets and reduce accidental
  build, server, browser, or keep-awake side effects.

## D-034: Delegate shell-controlled eval workflows to tool scripts

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `evals`, `dry_run`, `workflow`
- Decision: Keep public eval Make targets stable, but delegate ordered
  workflows that need shell guards plus internal target sequencing to versioned
  scripts under `tools/`. Use focused helper scripts for shared eval setup such
  as ensuring the server daemon after case validation passes.
- Why: `make -n` executes recursive `$(MAKE)` recipe lines. Script delegation
  keeps dry-runs observational while preserving guard order, skip behavior, and
  existing eval target names.

## D-035: Keep Ruff in CI and closeout gates

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `ci`, `ruff`, `validation`
- Decision: Add `ci-python-style` as the named Python style gate, backed by
  `ruff-check` and `ruff-format-check`, and run it from both GitHub CI and the
  local `make end` closeout routine.
- Why: The formatter baseline is only durable if the standard local and remote
  gates reject style drift before broad refactor work continues.

## D-036: Split Make configuration by responsibility

- Date: `2026-05-19`
- Category: `build_system`
- Tags: `makefile`, `config`, `modularity`, `ia`
- Decision: Keep `makefiles/config.mk` as the stable shared configuration
  entrypoint, but move family-specific defaults into focused
  `makefiles/config/*.mk` includes.
- Why: The root Makefile and target-family includes are already decomposed.
  Splitting the remaining config monolith makes ownership clearer while
  preserving the public Make target and override contract.

## D-037: Split eval Make targets by role

- Date: `2026-05-20`
- Category: `build_system`
- Tags: `makefile`, `evals`, `modularity`, `ia`
- Decision: Keep `makefiles/evals.mk` as the stable eval-family entrypoint,
  but move aliases, core eval suites, gates, OCR intake, and OCR runner targets
  into focused `makefiles/evals/*.mk` includes.
- Why: Eval targets are active research surfaces. Splitting the large eval
  target file by role keeps the command contract visible while making future
  research-lane changes smaller and easier to validate.

## D-038: Keep OCR report preflights in workflow scripts

- Date: `2026-05-20`
- Category: `build_system`
- Tags: `makefile`, `ocr`, `reports`, `workflow`
- Decision: Keep the OCR report builder as the suite-to-Python command router,
  and move report-target preflight checks into a focused OCR report workflow
  script. Public report target and alias names remain stable.
- Why: Report targets need shell-controlled file and directory checks before
  builder execution. Keeping that control flow in a script makes the OCR Make
  fragment smaller while preserving dry-run visibility and failure guidance.

## D-039: Keep no-fix audit exceptions narrow and visible

- Date: `2026-05-20`
- Category: `security`
- Tags: `pip-audit`, `dependencies`, `pyjwt`, `no-fix`
- Decision: Keep the Python dependency audit gate active, but explicitly ignore
  `PYSEC-2025-183` / `CVE-2025-45768` while it remains a disputed PyJWT
  advisory with no released fixed version. Keep the exception as a named
  Make-config value rather than hiding or disabling `pip-audit`.
- Why: PyJWT is only present transitively through `mcp`, and Polinko has no
  direct JWT use. A narrow ignore keeps closeout usable while preserving failure
  pressure for any other dependency advisory.

## D-040: Keep dev environment setup aligned with canonical paths

- Date: `2026-05-20`
- Category: `build_system`
- Tags: `devcontainer`, `dependencies`, `portfolio`, `lockfiles`
- Decision: Devcontainer setup, portfolio install/build targets, and Node
  dependency checks use `.venv`, `apps/portfolio/`, lockfile-first `npm ci`,
  and explicit root plus portfolio audit/update coverage.
- Why: The repo no longer uses `frontend/` or a custom-named repositioning
  virtualenv as active setup surfaces. Aligning setup with canonical paths keeps
  local, container, and CI dependency behavior deterministic.

## D-041: Keep source-first workbench payloads free of run-level rollups

- Date: `2026-05-20`
- Category: `evidence_governance`
- Tags: `pre_beta`, `manual_evals`, `eval_workbench`, `source_first`
- Decision: The active manual-eval and pass/fail visualization payloads expose
  the allowed source-first chain only: source artifact, row/case judgment,
  lane summary, and repeated lane signal as the promotion gate. They do not
  expose broken run-level rollup fields as rejected active contract members.
- Why: The discarded rollup shape collided with eval runs and made the
  workbench contract look like it still had an active alternate method. The
  live workbench should preserve manual eval workbench evidence without
  carrying that method residue forward.

## D-042: Name the manual eval workbench as the human-judged workspace

- Date: `2026-05-20`
- Category: `surface_ia`
- Tags: `manual_evals`, `notebooks`, `databases`, `workbench`, `ia`
- Decision: Use `manual eval workbench` for the human-judged research
  workspace. It includes notebooks, local evidence databases, chat artifacts,
  feedback, checkpoints, notes, exports, and runtime history. Automated eval
  reports and strict OCR gates stay separate eval evidence lanes.
- Why: The active manual workflow uses notebooks and databases as well as chat
  artifacts. Naming the full workspace prevents the workbench from being
  mistaken for either a chat-only surface or the discarded run-level rollup
  path.

## D-043: Freeze app.py as a lazy compatibility shim

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `entrypoints`, `cli`, `compatibility`, `ia`
- Decision: Keep `main.py` as the canonical CLI entrypoint and keep `app.py`
  only as a lazy compatibility shim for legacy `python app.py` launches.
  Importing `app` must not import or initialize the full CLI runtime.
- Why: The repo has converged on `main.py` and `make chat` for active operator
  use, but removing `app.py` would break older local scripts. A lazy shim keeps
  backward compatibility without preserving `app.py` as an active runtime
  surface.

## D-044: Preflight the Python package boundary before moving imports

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `python`, `package_boundary`, `src_layout`, `imports`
- Decision: Treat `src/polinko/` as the target runtime package shape, but keep
  this kernel as a preflight only. Root `main.py`, `server.py`, and `app.py`
  stay compatibility launchers while `config.py`, `api/`, and `core/` are the
  future runtime-package move set. Root `tools/` remains repo-local operator
  tooling until runtime imports are stable.
- Why: Moving the import tree without an explicit boundary would risk broad
  behavior drift across the API, CLI, eval scripts, and tests. The preflight
  gives the next kernel a reviewed target shape before any file move happens.

## D-045: Add the editable-install rail before moving runtime imports

- Date: `2026-05-20`
- Category: `build_system`
- Tags: `python`, `packaging`, `src_layout`, `editable_install`
- Decision: Add `pyproject.toml`, a minimal `src/polinko/` package scaffold,
  and `make package-install-check` before moving `config.py`, `api/`, or
  `core/` under the package namespace. CI exercises the editable install in
  the Python test job.
- Why: The source-layout move needs a working package install path before
  imports are rewritten. Keeping the scaffold identity-only gives the next
  kernel an install rail without changing runtime behavior.

## D-046: Move config into the Python package first

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `python`, `config`, `src_layout`, `compatibility`
- Decision: Make `src/polinko/config.py` the canonical config implementation
  and keep root `config.py` as a compatibility shim that re-exports
  `AppConfig` and `load_config`. Active runtime imports use `polinko.config`.
- Why: Config is the narrowest runtime boundary to move first. It proves the
  package path in real runtime code while preserving older local imports during
  the broader `api/` and `core/` migration.

## D-047: Move API implementation into the Python package

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `python`, `api`, `src_layout`, `compatibility`
- Decision: Make `src/polinko/api/` the canonical API implementation package
  and keep root `api/` as compatibility shims for legacy `api.*` imports.
  Active runtime imports use `polinko.api.*`.
- Why: The API package is the next runtime boundary after config. Moving it
  proves app construction, manual eval workbench routes, public portfolio
  helpers, and packaged API static assets through the source-layout import path
  while preserving older scripts and tests during the remaining `core/`
  migration.

## D-048: Move core runtime into the Python package

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `python`, `core`, `src_layout`, `compatibility`
- Decision: Make `src/polinko/core/` the canonical core runtime package and
  keep root `core/` as compatibility shims for legacy `core.*` imports. Active
  runtime imports use `polinko.core.*`.
- Why: Core contains the runtime behaviour, prompt versioning, persistence,
  rate limiting, response parsing, and vector-store helpers. Moving it after
  config and API completes the runtime package boundary while preserving older
  local scripts and tests until the root compatibility layer can be retired.

## D-049: Package the CLI implementation behind stable launchers

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `python`, `cli`, `entrypoints`, `src_layout`, `compatibility`
- Decision: Make `src/polinko/cli.py` the canonical CLI chat implementation,
  add the `polinko-chat` console script, and keep root `main.py` plus `app.py`
  as compatibility launchers. `make chat` runs the packaged CLI with
  `python -m polinko.cli`; `server.py` remains the stable `server:app` ASGI
  surface.
- Why: The runtime package boundary is now stable for config, API, and core.
  Moving the CLI implementation into the package keeps the root entrypoint
  layer thin while preserving existing operator commands and legacy direct
  launches.

## D-050: Package ASGI app construction behind server compatibility

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `python`, `asgi`, `entrypoints`, `src_layout`, `compatibility`
- Decision: Make `src/polinko/asgi.py` the canonical ASGI app construction
  module and keep root `server.py` as a compatibility shim for `uvicorn
  server:app`. The shim forwards module identity to `polinko.asgi` so existing
  tests and local scripts can keep using `server.app`, `server.Runner`, and
  `server.get_runtime_deps()`.
- Why: The API implementation is already packaged under `polinko.api`. Moving
  ASGI construction into the package removes another active runtime body from
  the repo root without changing the protected server import string or manual
  eval workbench behavior.

## D-051: Keep audited root shims compatibility-only

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `python`, `package_boundary`, `compatibility`, `imports`
- Decision: Keep root `main.py`, `app.py`, `server.py`, `config.py`, `api/`,
  and `core/` as an audited compatibility layer. Active `src/` and `tools/`
  Python imports use `polinko.*`; future shim retirement requires a separate
  approved kernel after operator defaults and legacy local callers are
  accounted for.
- Why: The runtime package boundary is stable, but direct CLI launches,
  `server:app`, and legacy local imports still protect operator and eval
  workflows. An explicit audit keeps compatibility visible without allowing
  active code to drift back to root imports.

## D-052: Close SQLite connections explicitly

- Date: `2026-05-20`
- Category: `runtime_engineering`
- Tags: `sqlite`, `tests`, `resource_lifecycle`, `python314`
- Decision: Do not use `sqlite3.connect(...)` directly as a context manager in
  repo code or tests. Use an explicit close path, such as
  `contextlib.closing(...)`, and make commits explicit when setup data must be
  persisted.
- Why: Python 3.14 surfaces unclosed sqlite connections as `ResourceWarning`.
  Explicit lifecycle handling keeps test output clean without changing the
  manual-eval or runtime database contract.

## D-053: Launch managed caffeinate in a detached session

- Date: `2026-05-20`
- Category: `workflow_environment`
- Tags: `caffeinate`, `startup`, `pid_lifecycle`, `host_shell`
- Decision: `make caffeinate` launches the repo-managed wake-lock process
  through the configured Python launcher in a detached child session, then
  records only that process PID. Public targets stay `make caffeinate`,
  `make caffeinate-status`, `make decaffeinate`, and `make end`.
- Why: Non-interactive host shells can clean up ordinary background children
  when the command session exits. A detached session lets status and closeout
  observe and stop the same repo-owned wake-lock process reliably.

## D-054: Treat frontend and UI names as legacy compatibility only

- Date: `2026-05-20`
- Category: `surface_ia`
- Tags: `portfolio`, `frontend`, `manual_evals`, `compatibility`, `ia`
- Decision: New surface references use portfolio app/static and manual eval
  workbench names. `FRONTEND_DIR`, `make portfolio-app-install`,
  `make frontend-install`, and `make frontend-build` remain compatibility
  aliases only, with canonical portfolio targets preferred. New eval trace
  artifacts use `manual_eval_workbench/...` labels instead of `ui/...`.
- Why: `frontend` and `ui` describe implementation shape, not surface
  ownership. Keeping aliases avoids breaking older commands while preventing
  stale names from re-entering active docs and generated artifacts.

## D-055: Record the refactor method as human-led

- Date: `2026-05-20`
- Category: `governance`
- Tags: `human_led`, `refactor`, `method`, `decision_log`, `kernel_flow`
- Human-led: The human lead made the scope decision to refactor Polinko after
  freezing the Beta 2.3 evidence baseline, using a one-kernel-at-a-time method
  that preserves manual eval workbench behavior and validates each kernel
  through PR, merge, and closeout gates.
- Decision: Decision entries that materially shape method, scope, acceptance,
  or go/no-go should preserve the human-led source of that decision. Engineering
  implementation details can remain in the ordinary `Decision` / `Why` form
  when they do not change the human-led method boundary.
- Why: The refactor is not an agent-discovered cleanup project; it is a
  human-led method choice with Codex executing implementation, validation, and
  Git flow. Recording that authorship keeps the governance ledger aligned with
  the charter working model.

## D-056: Use Dependabot-visible Python lockfile naming

- Date: `2026-05-20`
- Category: `dependency_management`
- Tags: `dependabot`, `pip_tools`, `lockfiles`, `ci`, `python`
- Human-led: The human lead surfaced the failing Dependabot `requirements.in`
  update signal from GitHub during the refactor pass.
- Decision: Keep `requirements.in` as the direct-dependency input and use the
  generated `requirements.txt` as the pip-tools lockfile consumed by CI,
  Docker, devcontainer setup, `pip-audit`, and `make deps-lock-check`.
- Why: GitHub Dependabot's pip/pip-compile support recognizes standard
  requirements text files. Keeping the generated output as `requirements.lock`
  made Dependabot PRs update only the input file while Polinko's CI correctly
  rejected the stale compiled output. The standard naming preserves strict
  lockfile validation without requiring a weaker security gate.

## D-057: Enforce a scoped Python type-check gate

- Date: `2026-05-20`
- Category: `build_validation`
- Tags: `mypy`, `ci`, `make`, `python`, `type_checking`
- Decision: Add `make type-check` and `make ci-python-type-check` as the
  canonical mypy gate for active `src/` and `tools/` Python surfaces. Exclude
  frozen eval snapshots, local `docs/peanut` material, and tests from the
  typed gate, and run the gate in GitHub CI plus `make end`.
- Why: The mypy 2.1 upgrade was safe, but the repo had no enforceable
  type-check surface: repo-wide invocation collided with frozen eval snapshots,
  while active `src`/`tools` code had existing type drift. A scoped gate matches
  the package-boundary refactor and catches real runtime/tooling drift without
  treating archived evidence as live source.

## D-058: Keep Pyright repo-owned and advisory

- Date: `2026-05-20`
- Category: `build_validation`
- Tags: `pyright`, `node_tooling`, `make`, `editor`, `type_checking`
- Decision: Pin Pyright in the root Node tooling manifest and expose it through
  `make pyright-check` for editor/static-analysis parity, while keeping mypy as
  the required Python type-check gate in CI and closeout.
- Why: `pyrightconfig.json` is tracked repo configuration, so the executable
  should be repo-owned rather than dependent on a global install. Keeping it
  advisory avoids adding a second required type gate while still making the
  editor surface reproducible.

## D-059: Keep local URL helpers non-launching by default

- Date: `2026-05-20`
- Category: `workflow_environment`
- Tags: `browser_launch`, `make`, `operator_targets`, `local_runtime`
- Human-led: The human lead asked to avoid browser-launching workflows because
  running Codex and VS Code together is already CPU-heavy on the local machine.
- Decision: `make docs`, `make open-api-docs`, and `make viz` print local URLs
  by default. Browser launch is explicit through `make docs-open`,
  `make open-api-docs-browser`, `make viz-open`, `make open-viz`, or
  `LOCAL_BROWSER_LAUNCH=system`.
- Why: URL printing preserves operator access without forcing a browser process
  into every local inspection flow. Explicit launch aliases keep the old
  capability available when it is intentionally needed.

## D-060: Audit root shim retirement readiness before deletion

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `package_boundary`, `compatibility`, `root_shims`, `asgi`, `refactor`
- Decision: Treat root launchers and shim packages as an audited compatibility
  layer until each surface has explicit retirement evidence. `server.py`
  remains not retirement-ready while `server:app` is active in Docker, Make
  defaults, server-daemon, and local eval gates. `app.py` is closest to
  retirement because tracked active code has no caller beyond the shim and
  compatibility tests, but deletion still requires a separate deprecation or
  removal kernel.
- Why: The package boundary is stable enough to audit, but deleting root
  compatibility based on cleanliness alone would risk operator, container, or
  local legacy workflows. Readiness should be proved surface-by-surface.

## D-061: Retire the legacy root app.py launcher

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `entrypoints`, `compatibility`, `cli`, `package_boundary`
- Decision: Remove root `app.py` after the deprecation/removal preflight found
  no active tracked code caller and no focused local ignored-lane launcher
  usage. CLI chat launchers are `make chat`, `python -m polinko.cli`,
  `polinko-chat`, and root `main.py`.
- Why: Keeping a compatibility launcher with no observed caller preserves
  ambiguity at the repo root. Removing it tightens the package-boundary surface
  while leaving the active CLI and `server:app` operator paths unchanged.

## D-062: Retire the legacy root config.py import shim

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `config`, `compatibility`, `imports`, `package_boundary`
- Decision: Remove root `config.py` after the legacy-import preflight found no
  active tracked code caller and no focused local ignored-lane root import
  usage. Runtime and tooling imports use `polinko.config`.
- Why: Config is already canonical under the packaged runtime. Removing the
  unused root shim reduces import ambiguity while preserving the active API,
  CLI, manual eval workbench, and `server:app` surfaces.

## D-063: Retire the legacy root api package shims

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `api`, `compatibility`, `imports`, `package_boundary`
- Decision: Remove root `api/` after the legacy-import preflight found no
  active tracked code caller and no focused local ignored-lane root import
  usage. Runtime and tooling imports use `polinko.api.*`.
- Why: API implementation is already canonical under the packaged runtime.
  Removing the unused root shims reduces import ambiguity while preserving the
  active ASGI, manual eval workbench, public portfolio data, CLI, and
  `server:app` surfaces.

## D-064: Retire the legacy root core package shims

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `core`, `compatibility`, `imports`, `package_boundary`
- Decision: Remove root `core/` after the legacy-import preflight found no
  active tracked code caller and no focused local ignored-lane root import
  usage. Runtime and tooling imports use `polinko.core.*`.
- Why: Core runtime logic is already canonical under the packaged runtime.
  Removing the unused root shims reduces import ambiguity while preserving the
  active API, CLI, manual eval workbench, and `server:app` surfaces.

## D-065: Consolidate the Python package boundary around root launchers

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `python`, `package_boundary`, `root_launchers`, `imports`
- Decision: Treat `src/polinko/` as the runtime import boundary. Root
  `app.py`, `config.py`, `api/`, and `core/` stay retired and guarded against
  reintroduction; root `main.py` and `server.py` remain the only root
  compatibility surfaces.
- Why: The import-shim migration is complete. Consolidating the contract
  reduces root-level ambiguity while preserving the two launch paths that still
  protect operator, Docker, and local eval workflows.

## D-066: Treat entrypoint compatibility as an explicit audit surface

- Date: `2026-05-20`
- Category: `architecture`
- Tags: `entrypoints`, `compatibility`, `asgi`, `cli`, `operator_surface`
- Human-led: The human lead chose to continue the refactor one kernel at a
  time after the package-boundary consolidation, with manual eval and operator
  workflows preserved.
- Decision: Keep operator entrypoints mapped explicitly: `make chat`,
  `python main.py`, and `polinko-chat` reach `polinko.cli`; `make server`,
  `make localhost`, `make server-daemon`, local eval gates, and Docker continue
  through `server:app` until an approved replacement ASGI string exists.
- Why: Launchers are now the remaining root compatibility layer. Treating them
  as a tested audit surface prevents cleanup from silently changing active
  operator or eval paths.

## D-067: Keep manual eval evidence rows linked by source message

- Date: `2026-05-20`
- Category: `eval_quality`
- Tags: `manual_evals`, `source_first`, `evidence_rows`, `workbench`
- Decision: Manual eval workbench evidence rows link feedback to an OCR case
  only when the feedback message matches that OCR run's result message.
  Session context alone is not enough to promote the latest OCR run into the
  judged case link.
- Why: A source-first workbench has to preserve the actual artifact-to-judgment
  chain. In sessions with multiple OCR runs, linking feedback to the latest
  session OCR run can misstate what the human judgment applied to.

## D-068: Keep eval viz feedback rows on result-message provenance

- Date: `2026-05-20`
- Category: `eval_quality`
- Tags: `manual_evals`, `eval_viz`, `source_first`, `provenance`
- Decision: `/viz/pass-fail` manual feedback rows and run-specific OCR rows use
  feedback only when `feedback.message_id` matches the OCR run's
  `result_message_id`. The manual eval DB also indexes the feedback-message and
  OCR-result-message columns used for that join.
- Why: The visualization is an operator decision surface. Borrowing feedback
  from another OCR run in the same session can make the chart imply a human
  judgment applied to an artifact that was never judged.

## D-069: Use monitor wording for active eval visualization

- Date: `2026-05-20`
- Category: `eval_quality`
- Tags: `eval_viz`, `manual_evals`, `source_first`, `terminology`
- Human-led: The human lead retired the pulse direction because it did not
  work properly and collided with eval runs.
- Decision: Active runtime and operator visualization labels use
  source-first monitor wording for `/viz/pass-fail`. Historical pulse wording
  stays only where it documents the rejected hypothesis or frozen beta
  evidence.
- Why: `/viz/pass-fail` is still an active manual-eval and OCR inspection
  surface. Its labels should not imply that the discarded run-level rollup
  method is still live.

## D-070: Add source-first summary-unit naming to workbench payloads

- Date: `2026-05-20`
- Category: `eval_quality`
- Tags: `manual_evals`, `source_first`, `payload_contract`, `compatibility`
- Decision: Manual eval workbench source-first payloads expose
  `summary_unit=lane_summary` as the active field name and keep the existing
  `rollup_unit` field as a compatibility alias. The live eval monitor displays
  summary-unit wording.
- Why: The active workbench should describe lane summaries without reviving
  run-level rollup language, but local/manual consumers should not break during
  the refactor.
- Current disposition: Superseded by `D-071`.

## D-071: Retire the source-first rollup compatibility alias

- Date: `2026-05-20`
- Category: `eval_quality`
- Tags: `manual_evals`, `source_first`, `payload_contract`, `compatibility`
- Decision: Remove `rollup_unit` from active source-first manual eval payloads.
  `summary_unit=lane_summary` is the only active lane-summary field.
- Why: A tracked and local compatibility audit found no active notebook,
  `.local`, or `docs/peanut` workbench consumer of `rollup_unit`. Keeping the
  alias would preserve retired rollup wording after the source-first contract
  had already moved on.

## D-072: Version source-first manual eval payload boundaries

- Date: `2026-05-20`
- Category: `eval_quality`
- Tags: `manual_evals`, `source_first`, `payload_contract`, `schema_version`
- Decision: Source-first manual eval payloads expose
  `schema_version=polinko.manual_eval_source_first.v1`, and generated
  `manual_evals.db` metadata exposes
  `schema_version=polinko.manual_evals_db.v1`.
- Why: `/manual-evals/surface` and `/viz/pass-fail/data` share the source-first
  object as an active manual-eval contract boundary. Adding explicit version
  markers makes future payload migrations visible without changing existing
  source-first evidence behavior.

## D-073: Cover manual eval source-first data in API smoke

- Date: `2026-05-20`
- Category: `runtime`
- Tags: `api_smoke`, `manual_evals`, `source_first`, `eval_viz`
- Decision: `make api-smoke` checks `/manual-evals/surface` and
  `/viz/pass-fail/data` without launching a browser. The smoke validates the
  shared source-first `schema_version`, `summary_unit=lane_summary`, and the
  absence of the retired `rollup_unit` alias.
- Why: These endpoints are active manual-eval evidence surfaces. Keeping them
  in the startup/runtime smoke path catches contract drift before manual eval
  workbench use.

## D-074: Surface manual eval warehouse freshness read-only

- Date: `2026-05-20`
- Category: `eval_quality`
- Tags: `manual_evals`, `freshness`, `source_first`, `eval_viz`
- Decision: `/manual-evals/surface` and `/viz/pass-fail/data` expose a
  read-only `data_freshness` block that labels the manual eval warehouse as
  `current`, `stale`, `unknown`, or `missing` from existing metadata and source
  history DB counts/timestamps.
- Why: Manual eval work can continue with stale local evidence, but the
  workbench must make stale, schema-old, or missing source data visible without
  silently rebuilding local databases or launching browser surfaces.

## D-075: Compare freshness against manual eval import scope

- Date: `2026-05-20`
- Category: `eval_quality`
- Tags: `manual_evals`, `freshness`, `import_scope`, `local_evidence`
- Decision: `data_freshness` source counts compare against the same import
  scope used by `make manual-evals-db`: sessions count only when they have
  feedback, checkpoint, or OCR evidence, and metadata exclude-prefixes are
  honored.
- Why: Idle chats can exist in source history without belonging to the manual
  eval warehouse. A freshly rebuilt warehouse should not remain stale because
  raw source tables contain non-imported chat rows.

## D-076: Make manual eval warehouse refresh backup-first

- Date: `2026-05-20`
- Category: `operator_workflow`
- Tags: `manual_evals`, `freshness`, `backup`, `makefile`, `local_evidence`
- Decision: `make manual-evals-db` and the explicit
  `make manual-evals-db-refresh` alias copy an existing manual eval warehouse
  into `.local_archive/manual-evals-db-refresh-*` before rebuilding and print
  the read-only freshness status afterward. `make manual-evals-db-status`
  provides the same freshness status without mutating local databases.
- Why: Manual eval warehouse refreshes are local evidence maintenance. The
  operator should be able to inspect freshness before rebuilding and preserve
  the previous warehouse automatically when the refresh does mutate it.

## D-077: Report manual eval warehouse health read-only

- Date: `2026-05-20`
- Category: `operator_workflow`
- Tags: `manual_evals`, `health`, `source_quality`, `local_evidence`,
  `makefile`
- Decision: `make manual-evals-db-health` reports read-only manual eval
  warehouse health from the integrated local DB, including source coverage,
  image resolution, feedback status, feedback-to-result linking, and session
  evidence mix. The target distinguishes freshness from source-quality
  attention so a current warehouse can still expose unresolved evidence gaps.
- Why: The refreshed warehouse can be current while still carrying missing
  images, open feedback, or unlinked feedback evidence. Operators need a
  terminal-native health report before deciding whether a later cleanup kernel
  should reconcile evidence or leave it as historical context.

## D-078: Resolve manual eval images from local export archives

- Date: `2026-05-20`
- Category: `operator_workflow`
- Tags: `manual_evals`, `image_resolution`, `local_evidence`, `archives`
- Decision: The manual eval warehouse builder resolves OCR source images from
  matching files inside `.zip` archives under the configured image roots after
  checking extracted files first. Archive-backed rows store a
  `zip_path::member` reference and build thumbnails from the archived bytes
  without extracting files into the repo.
- Why: The missing-image audit showed that a material portion of the current
  unresolved OCR evidence exists locally inside ChatGPT export archives rather
  than extracted directories. The builder should use that local evidence
  directly while keeping the live warehouse refresh backup-first and explicit.

## D-079: Resolve manual eval images from tracked eval snapshots

- Date: `2026-05-20`
- Category: `operator_workflow`
- Tags: `manual_evals`, `image_resolution`, `docs_eval`, `local_evidence`
- Decision: The manual eval warehouse builder includes `docs/eval/` in the
  default OCR source-image roots, after private peanut screenshot roots and
  before loose home-directory export roots. Tracked eval snapshot images are
  therefore resolved as curated evidence before the builder falls back to
  uncurated local export folders and archives.
- Why: The missing-image audit found screenshot assets already present under
  the tracked Beta 1.0 eval snapshot. Curated eval evidence should not remain
  invisible to the integrated warehouse or be counted as absent historical
  evidence.

## D-080: Resolve manual eval screenshots from Dropbox sync roots

- Date: `2026-05-20`
- Category: `operator_workflow`
- Tags: `manual_evals`, `image_resolution`, `screenshots`, `local_evidence`
- Decision: The manual eval warehouse builder includes the macOS Dropbox
  screenshot sync folder in the default OCR source-image roots. The root is
  checked as a narrow screenshot folder before loose home-directory export
  roots.
- Why: The bounded missing-image audit found exact local matches for every
  remaining unresolved screenshot asset in that synced screenshot folder. The
  remaining unresolved image assets after this root are text fixtures, which
  are historical source-name debt until their seed files are explicitly
  curated as source files.

## D-081: Classify manual eval missing-image debt by source family

- Date: `2026-05-20`
- Category: `operator_workflow`
- Tags: `manual_evals`, `health`, `source_quality`, `local_evidence`
- Decision: `make manual-evals-db-health` breaks unresolved image debt down by
  source family in addition to printing total missing asset and OCR-run counts.
  The report must make the remaining text-fixture debt visible without mutating
  the warehouse or rerunning broad filesystem audits.
- Why: Screenshot recovery is closed for the current warehouse. The remaining
  unresolved assets are historical text fixture source names, so the health
  surface should make that boundary explicit before future refactor kernels
  decide whether to curate seed files or leave the names as historical debt.

## D-082: Classify manual eval open feedback debt read-only

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `health`, `feedback`, `local_evidence`
- Decision: `make manual-evals-db-health` breaks open feedback debt down by
  era and outcome, including affected session counts, note coverage,
  recommended-action coverage, action-taken coverage, explicit OCR-result
  links, and same-session OCR presence. The report stays read-only. It does
  not infer feedback-to-OCR links by broad heuristics.
- Why: Open manual eval feedback is actionable only when the next operator can
  see what work is queued and what evidence relationship is known. Same-session
  OCR presence is useful triage context, but it is not the same as an explicit
  result-message link.

## D-083: List manual eval open feedback actionables read-only

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `feedback`, `triage`, `local_evidence`, `makefile`
- Decision: `make manual-evals-feedback-actionables` prints a read-only row
  list of open manual-eval feedback for triage. The terminal report and JSON
  export expose `schema_version=polinko.manual_eval_feedback_actionables.v1`,
  feedback row identity, source session/message identity, note and
  recommended-action fields, and OCR context split between explicit
  result-message links and same-session OCR presence.
- Why: The health summary shows open feedback debt exists, but curation needs
  row-level evidence before any warehouse mutation or closure. A read-only
  actionables list lets the operator inspect queued work without guessing
  feedback-to-OCR relationships or changing the local evidence database.

## D-084: Cohort manual eval open feedback actionables read-only

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `feedback`, `triage`, `local_evidence`, `makefile`
- Decision: `make manual-evals-feedback-cohorts` prints read-only cohorts for
  open manual-eval feedback actionables. The terminal report and JSON export
  expose `schema_version=polinko.manual_eval_feedback_cohorts.v1`, cohort
  identity, row/session/outcome counts, note and action coverage, explicit
  OCR-result link counts, same-session OCR context counts, and sample feedback
  row ids.
- Why: Row-level actionables are inspectable, but the operator needs a compact
  batch-selection view before curation. Cohorts are derived from explicit
  `recommended_action` text and known OCR context fields, not broad inferred
  feedback-to-OCR linkage.

## D-085: Filter manual eval feedback drilldowns by cohort read-only

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `feedback`, `triage`, `local_evidence`, `makefile`
- Decision: Open feedback actionables and cohort reports accept an optional
  cohort filter. From Make, `COHORT=<cohort_id>` narrows
  `make manual-evals-feedback-actionables` and
  `make manual-evals-feedback-cohorts`; `OUTCOME=<outcome>` and
  `LIMIT=<n>` remain terminal-native drilldown controls for row-level
  actionables. The filter is read-only and uses the same explicit
  `recommended_action` cohort classifier as the summary report.
- Why: Cohorts identify a safe batch-selection surface, but the operator still
  needs row-level evidence for a selected cohort before any OCR retry,
  curation, or closure decision. The first intended drilldown is
  `ocr_retry_evidence`, because it is the largest open cohort and has the most
  same-session OCR context.

## D-086: Packet OCR retry candidates read-only before reruns

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `local_evidence`
- Decision: `make manual-evals-ocr-retry-candidates` prints a read-only OCR
  retry candidate packet for open manual-eval feedback. The terminal report
  and JSON export expose
  `schema_version=polinko.manual_eval_ocr_retry_candidates.v1`, selected
  feedback rows, source session grouping, latest same-session OCR evidence,
  source names, OCR text preview metadata, and image asset resolution and
  thumbnail availability fields already present in `manual_evals.db`.
- Why: OCR retry work should start from a bounded evidence packet, not from
  broad same-session inference or immediate reruns. Candidate packets let the
  operator choose the first retry batch while keeping the warehouse read-only
  and preserving the distinction between explicit feedback-to-result links and
  same-session OCR context.

## D-087: Flag OCR retry packet readiness before reruns

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `readiness`
- Decision: OCR retry candidate packets use
  `schema_version=polinko.manual_eval_ocr_retry_candidates.v2` and expose a
  read-only readiness block per candidate group. Readiness flags show multiple
  same-session OCR runs, missing explicit feedback-to-result links, latest OCR
  context-only status, and missing same-session OCR context before any rerun or
  warehouse mutation. Terminal output stays bounded while JSON keeps the full
  same-session OCR context.
- Why: The operator needs to see when same-session OCR evidence is context
  rather than a confirmed case link. Readiness flags keep the first retry
  packet useful without widening linkage heuristics or launching live eval
  writes.

## D-088: Verify OCR retry source candidates before closure

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `source_verification`
- Decision: `make manual-evals-ocr-retry-source-verification` prints a
  read-only source-verification packet for selected OCR retry candidates. The
  terminal report and JSON export expose
  `schema_version=polinko.manual_eval_ocr_retry_source_verification.v1`,
  feedback note/action text, candidate source image names, OCR run IDs, OCR
  previews, readiness flags, and exact not-confirmed reasons before any rerun
  or feedback closure.
- Why: Readiness flags identify ambiguity, but manual eval curation still
  needs source-level evidence in one packet before taking action.
  Source-verification packets keep the workflow terminal-native and
  warehouse-read-only while preserving the distinction between exact
  feedback-to-result links and same-session OCR context.

## D-089: Drill into OCR retry source-history provenance read-only

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `source_provenance`
- Decision: `make manual-evals-ocr-retry-source-provenance` prints a
  read-only source-history provenance packet for selected OCR retry
  candidates. The terminal report and JSON export expose
  `schema_version=polinko.manual_eval_ocr_retry_source_provenance.v1`,
  source-history feedback messages, OCR source/result message IDs when those
  IDs are already present in the warehouse, bounded source/result previews,
  and exact feedback-result link counts.
- Why: Source-verification packets show which OCR runs are candidate context,
  but closure still needs proof of what message provenance is exact. The
  provenance packet reads only referenced source-history rows, keeps terminal
  output bounded, and preserves context-only OCR rows as not exact links.

## D-090: Packet OCR retry rerun inputs read-only

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `input_packet`
- Decision: `make manual-evals-ocr-retry-input-packet` prints a read-only OCR
  retry input packet for selected OCR retry candidates. The terminal report
  and JSON export expose
  `schema_version=polinko.manual_eval_ocr_retry_input_packet.v1`, feedback
  IDs, source sessions, source image names, resolved image status, OCR run
  IDs, feedback source-message previews, and exact-link blocker state before
  any rerun or feedback closure.
- Why: Source-verification and source-provenance packets show the evidence
  chain, but rerun/case-curation work needs a compact input surface. The input
  packet composes those reports without adding new linkage heuristics, keeps
  the warehouse read-only, and makes missing OCR source/result message
  provenance explicit.

## D-091: Manifest OCR retry source artifacts before reruns

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `rerun_manifest`
- Decision: `make manual-evals-ocr-retry-rerun-manifest` prints a read-only
  OCR retry source-artifact selection manifest for selected OCR retry inputs.
  The terminal report and JSON export expose
  `schema_version=polinko.manual_eval_ocr_retry_rerun_manifest.v1`, feedback
  IDs, source sessions, OCR run IDs, source image names, image resolution
  status, thumbnail dimensions, OCR previews, feedback source-message
  previews, and the separate feedback-closure blocker state.
- Why: The input packet proves which source artifacts are available, but a
  human go/no-go decision needs a stable artifact-selection surface before any
  rerun, curation, or feedback closure. The manifest keeps source-artifact
  selection distinct from feedback closure while OCR source/result message IDs
  and exact feedback-result links remain absent.

## D-092: Preview OCR retry rerun plans before execution

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `rerun_plan`
- Decision: `make manual-evals-ocr-retry-rerun-plan` prints a read-only OCR
  retry rerun plan for selected source artifacts. The terminal report and JSON
  export expose
  `schema_version=polinko.manual_eval_ocr_retry_rerun_plan.v1`, source
  artifact IDs, feedback IDs, source sessions, OCR run IDs, source image
  names, resolved source paths, thumbnail dimensions, source previews, and a
  payload-only command preview.
- Why: The manifest shows which resolved source artifacts are selectable, but
  execution still needs a concrete would-run payload before any OCR rerun,
  curation, feedback closure, live eval write, or warehouse mutation. The plan
  makes artifact selection explicit through stable artifact IDs and optional
  `ARTIFACT_IDS=<artifact_id>` filtering while staying preview-only.

## D-093: Shortlist OCR retry source artifacts before reruns

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `selection_review`
- Human-led: The human lead kept the manual eval workbench as the active
  research surface and chose to review OCR retry evidence before any rerun.
- Decision: `make manual-evals-ocr-retry-selection-review` prints a read-only
  OCR retry source-artifact shortlist for human selection. The terminal report
  and JSON export expose
  `schema_version=polinko.manual_eval_ocr_retry_selection_review.v1`, grouped
  source image identities, feedback IDs, OCR run IDs, source image names,
  thumbnail dimensions, source previews, candidate payload previews, and the
  allowed human dispositions: `rerun_input`, `curated_case`, or
  `context_only`.
- Why: Rerun plans can contain multiple OCR runs for the same resolved source
  image. Collapsing duplicate source artifacts into a shortlist makes the next
  human decision explicit while keeping feedback closure blocked until exact
  OCR source/result message IDs and feedback-to-result links are present.

## D-094: Template OCR retry source-artifact decisions before reruns

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `selection_template`
- Human-led: The human lead keeps the OCR retry decision as a manual eval
  workbench judgment before any automated rerun.
- Decision: `make manual-evals-ocr-retry-selection-template` prints a
  read-only human-selection template for the OCR retry shortlist. The terminal
  report and JSON export expose
  `schema_version=polinko.manual_eval_ocr_retry_selection_template.v1`,
  shortlist IDs, feedback IDs, candidate artifact IDs, OCR run IDs, source
  image names, source previews, thumbnail dimensions, and fillable decision
  fields with `selected_action=undecided`.
- Why: Selection review identifies what needs a human choice, but the next
  step needs a stable decision input shape before any OCR rerun, curation,
  feedback closure, live eval write, or warehouse mutation. The template keeps
  allowed dispositions explicit while leaving all selections undecided.

## D-095: Validate OCR retry source-artifact decisions before execution

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `selection_validation`
- Human-led: The human lead kept OCR retry choices as manual eval workbench
  decisions and asked for validation before any execution surface.
- Decision: `make manual-evals-ocr-retry-selection-validate` validates a
  local OCR retry human-selection JSON against the current source-artifact
  shortlist. The terminal report and JSON export expose
  `schema_version=polinko.manual_eval_ocr_retry_selection_validation.v1`,
  decision-source status, shortlist IDs, selected actions, selected artifact
  IDs, invalid artifact IDs, stale/missing/duplicate decision counts, and the
  existing feedback-closure blocker state.
- Why: A filled template is still local operator input, not execution proof.
  The validator catches missing, stale, duplicate, or mismatched selections
  before any OCR rerun, curation, feedback closure, live eval write, or
  warehouse mutation while keeping closure blocked until exact OCR
  source/result message IDs and feedback-to-result links exist.

## D-096: Preview OCR retry selection application before execution

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `selection_apply_preview`
- Human-led: The human lead kept OCR retry application as an inspectable
  manual eval workbench step before any execution.
- Decision: `make manual-evals-ocr-retry-selection-apply-preview` prints a
  read-only would-apply preview for local OCR retry human-selection decisions.
  The terminal report and JSON export expose
  `schema_version=polinko.manual_eval_ocr_retry_selection_apply_preview.v1`,
  validator state, validation blockers, action splits for `rerun_input`,
  `curated_case`, and `context_only`, selected artifact IDs, OCR run IDs,
  source sessions, source image names, resolved paths, payload-only previews,
  and the existing feedback-closure blocker state.
- Why: Validation proves the local decision file is well-formed, but the next
  operator step needs to inspect the exact would-apply payloads before any OCR
  rerun, curation, feedback closure, live eval write, or warehouse mutation.
  The preview only emits payloads when validation is `ok`; otherwise it shows
  blockers and stays non-executing.

## D-097: Materialize OCR retry decision drafts locally

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `selection_draft`,
  `local_tooling`
- Human-led: The human lead asked to keep OCR retry decisions in the manual
  eval workbench while tightening Polinko's local tooling pattern.
- Decision: `make manual-evals-ocr-retry-selection-draft` writes a local
  ignored OCR retry human-selection draft from the current source-artifact
  shortlist. Draft files expose
  `schema_version=polinko.manual_eval_ocr_retry_selection_decision_draft.v1`,
  the current selection-template schema version, shortlist IDs, candidate
  artifact IDs, source provenance, template fingerprints, and undecided
  fillable decision inputs. The default output path is
  `.local/manual_eval_decisions/ocr_retry_selection_draft.json`, and existing
  draft files are not overwritten unless the operator passes `FORCE=1`.
- Why: The template can already be printed, but manual operators need a
  stable local file to fill without copy/paste. Making the generator local,
  deterministic, fingerprinted, and overwrite-safe gives Polinko a reusable
  local tooling pattern: materialize local input, validate it, preview
  application, then execute only after the gates pass.

## D-098: Name the reusable local tooling contract

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `local_tooling`, `manual_evals`, `operator_input`, `polinko_tooling`
- Human-led: The human lead narrowed the refactor back to Polinko-first
  tooling while preserving source-first manual eval workflows.
- Decision: `docs/runtime/LOCAL_TOOLING.md` records the repo-local pattern for
  high-impact operator tooling: generate ignored local input, validate it
  against current source truth, preview application without mutation, and
  execute only through a separate explicit follow-up gate. Required knobs are
  an ignored local default path, explicit path override, no-overwrite default,
  `FORCE=1`, deterministic `schema_version`, source fingerprints, validation,
  and apply-preview commands.
- Why: The OCR retry decision-draft flow is useful beyond OCR, but extracting
  a shared package now would freeze the wrong abstraction. Naming the contract
  lets Polinko reuse the safe operator pattern while keeping implementation
  repo-local until repeated behavior proves the shared boundary.

## D-099: Pin OCR evidence tooling to read-only inventory before eval refresh

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `ocr`, `inventory`, `freshness`, `local_evidence`, `read_only`
- Human-led: The human lead paused live eval execution and asked to align
  Polinko governance/runtime docs before resuming toy work.
- Decision: `make ocr-inventory` and `make ocr-inventory-json` are the
  current OCR tooling pin. They inspect tracked OCR cases, local case inputs,
  local reports, manual-eval DB paths, and notebook paths without running OCR,
  launching browsers, writing eval rows, or mutating local databases. The
  inventory reports JSON shape, row-source counts, and read-only freshness
  states from existing `generated_at` metadata.
- Why: OCR generalization work should resume from known local evidence state,
  not from implicit assumptions or stale report paths. The inventory pin gives
  operators a safe map of what exists, what is stale, and what lacks freshness
  metadata before any eval refresh or live OCR execution is approved.

## D-100: Gate OCR retry execution readiness before execution

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback`, `triage`, `execution_readiness`,
  `read_only`
- Human-led: The human lead approved continuing the Polinko-first tooling
  lane while keeping live OCR/eval execution pinned.
- Decision: `make manual-evals-ocr-retry-execution-readiness` prints a
  read-only readiness report from local OCR retry human-selection decisions.
  The terminal report and JSON export expose
  `schema_version=polinko.manual_eval_ocr_retry_execution_readiness.v1`,
  validation state, apply-preview state, executable item counts, selected
  artifact source-file existence, payload-only command-preview state, and
  readiness blockers.
- Why: Apply-preview shows what would be applied, but the next operator needs
  a final non-mutating gate that answers whether selected retry/curation
  inputs are executable before any OCR rerun, feedback closure, live eval
  write, or manual eval warehouse mutation. Execution remains a separate
  explicit follow-up kernel.

## D-101: Design OCR retry execution before implementation

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `execution_gate`, `design_only`, `rollback`
- Human-led: The human lead confirmed the next kernel should still not run
  evals, and should define what the execution gate would require first.
- Decision: `docs/runtime/OCR_RETRY_EXECUTION_GATE.md` defines the future OCR
  retry execution gate as `designed-only`. The proposed command shape requires
  `SELECTION_PATH=<path>` plus `CONFIRM=ocr-retry-execute`, recomputes
  validation/apply-preview/readiness inside the same process, treats
  `context_only` as non-executing, and writes only a local ignored run bundle
  under `.local/manual_eval_runs/ocr_retry/` in the first implementation.
- Why: The readiness gate makes execution possible to reason about, but adding
  an executor before the mutation target, confirmation token, failure handling,
  and rollback story are reviewed would blur the refactor boundary. This keeps
  live OCR/eval execution pinned while making the next implementation kernel
  precise.

## D-102: Implement OCR retry execution as a local bundle first

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `execution_gate`, `local_bundle`, `rollback`
- Human-led: The human lead approved the next kernel after the execution-gate
  design while keeping eval runs out of scope.
- Decision: `make manual-evals-ocr-retry-execute` and
  `make manualdb-ocr-retry-execute` now execute selected OCR retry artifacts
  only into ignored local bundles under `.local/manual_eval_runs/ocr_retry/`.
  The command requires `SELECTION_PATH=<path>` and
  `CONFIRM=ocr-retry-execute`, recomputes validation, apply-preview, and
  execution readiness in-process, skips `context_only` selections, records
  request/response evidence, and keeps feedback closure, live eval writes,
  `manual_evals.db` refresh, and warehouse mutation out of scope.
- Why: The next safest step after readiness is a reversible local artifact
  bundle, not direct warehouse mutation. This gives the operator concrete OCR
  retry evidence to inspect while preserving the exact feedback and eval
  boundaries already established by the manual eval workbench.

## D-103: Inspect OCR retry execution bundles before mutation gates

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `execution_gate`, `local_bundle`, `inspection`
- Human-led: The human lead approved continuing the OCR retry tooling refactor
  while keeping eval runs, feedback closure, and warehouse mutation out of
  scope.
- Decision: `make manual-evals-ocr-retry-execution-report` and
  `make manualdb-ocr-retry-execution-report` now inspect one local OCR retry
  execution bundle via `RUN_DIR=<path>` without running OCR or mutating eval
  data. The report emits
  `schema_version=polinko.manual_eval_ocr_retry_execution_report.v1`, checks
  bundle files, schema versions, run ID alignment, request/response counts,
  provider failure status, stop reasons, and the local-bundle mutation
  boundary. Terminal output hides source file paths and reports only run ID,
  directory name, counts, warnings, and blockers.
- Why: The local executor creates concrete evidence, but that evidence needs a
  repeatable inspection gate before any future feedback-closure, live-eval, or
  warehouse-mutation kernel. Separating bundle inspection from mutation keeps
  the manual eval workbench reversible and reviewable.

## D-104: Preview OCR retry feedback closure before applying it

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback_closure`, `preview_only`
- Human-led: The human lead approved continuing through the next OCR retry
  tooling kernel while keeping eval runs and warehouse mutation out of scope.
- Decision: `make manual-evals-ocr-retry-feedback-closure-preview` and
  `make manualdb-ocr-retry-feedback-closure-preview` now read one inspected
  local OCR retry execution bundle via `RUN_DIR=<path>` and emit
  `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_preview.v1`.
  The report groups successful OCR retry responses by feedback ID, previews
  which feedback rows would be closeable, marks mixed provider status as
  `attention`, and blocks when bundle inspection reports structural or
  mutation-boundary errors.
- Why: Feedback closure is a mutation boundary, so it needs a preview surface
  before an apply surface. This keeps closure decisions tied to concrete local
  OCR evidence while preserving the rule that feedback status, action-taken
  text, live eval rows, and `manual_evals.db` remain unchanged until an
  explicit future apply gate exists.

## D-105: Design OCR retry feedback closure as backup-first apply

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback_closure`, `backup_first`,
  `design_only`
- Human-led: The human lead approved continuing the OCR retry tooling sequence,
  with implementation discipline kept ahead of any database mutation.
- Decision: `docs/runtime/OCR_RETRY_EXECUTION_GATE.md` now defines the future
  feedback-closure apply gate as design-only. The proposed command shape is
  `make manual-evals-ocr-retry-feedback-closure-apply RUN_DIR=<path>
  CONFIRM=ocr-retry-feedback-closure-apply`, with a
  `manualdb-ocr-retry-feedback-closure-apply` alias. The gate may be
  implemented only after the inspected execution bundle and feedback-closure
  preview both report `state=ok`, every closure item is `ready`, target
  feedback rows are still open, and the current manual eval warehouse has been
  copied under
  `.local_archive/manual-evals-feedback-closure-apply-<timestamp>/`.
- Why: Closing feedback changes the manual eval warehouse, so the apply path
  needs a backup, restore story, confirmation token, and exact mutation scope
  before code exists. The designed scope permits only feedback `status`,
  `action_taken`, and `updated_at` updates, and still excludes live eval rows,
  OCR reruns, warehouse refresh, OCR row mutation, and inferred source links.

## D-106: Implement OCR retry feedback closure as backup-first apply

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback_closure`, `backup_first`,
  `local_mutation`
- Human-led: The human lead approved proceeding from the designed apply gate
  into implementation while keeping eval runs and pulse work out of scope.
- Decision: `make manual-evals-ocr-retry-feedback-closure-apply` and
  `make manualdb-ocr-retry-feedback-closure-apply` now apply feedback closure
  from one inspected OCR retry execution bundle. The command requires
  `RUN_DIR=<path>` and `CONFIRM=ocr-retry-feedback-closure-apply`, requires the
  execution-bundle report and feedback-closure preview to both be `ok`, backs
  up the current manual eval warehouse under
  `.local_archive/manual-evals-feedback-closure-apply-<timestamp>/`, and emits
  `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply.v1`.
- Why: The preview gate proved the closeable feedback set, but closure still
  changes the manual eval warehouse. The implemented apply gate keeps that
  mutation explicit, backup-first, and limited to feedback `status`,
  `action_taken`, and `updated_at`; it still excludes live eval rows, OCR
  reruns, warehouse refresh, OCR row mutation, inferred source links, and pulse
  work.

## D-107: Verify OCR retry feedback closure after apply

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback_closure`, `verification`,
  `read_only`
- Human-led: The human lead approved continuing the OCR retry tooling sequence
  while keeping additional mutation, eval runs, and pulse work out of scope.
- Decision: `make manual-evals-ocr-retry-feedback-closure-apply-report` and
  `make manualdb-ocr-retry-feedback-closure-apply-report` now inspect the
  local apply summary from `RUN_DIR=<path>` without mutation. The report emits
  `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_apply_report.v1`,
  verifies backup DB integrity, verifies backup feedback rows remain open,
  verifies active feedback rows are closed, and verifies active action-taken
  text is present.
- Why: The apply gate is intentionally allowed to mutate a narrow feedback
  surface, so it needs a read-only post-apply verifier before manual restore
  decisions. Keeping verification separate from apply preserves backup
  confidence without adding another writer.

## D-108: Restore OCR retry feedback closure from verified apply backups

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr`, `feedback_closure`, `restore`, `backup_first`
- Human-led: The human lead chose to add the restore path before any further
  feedback-closure application, treating rollback tooling as the safest next
  kernel.
- Decision: `make manual-evals-ocr-retry-feedback-closure-restore-preview` and
  `make manualdb-ocr-retry-feedback-closure-restore-preview` now inspect one
  apply backup with `BACKUP_DIR=<path>` without mutation. The guarded restore
  targets, `make manual-evals-ocr-retry-feedback-closure-restore` and
  `make manualdb-ocr-retry-feedback-closure-restore`, require
  `BACKUP_DIR=<path>` and `CONFIRM=ocr-retry-feedback-closure-restore`, emit
  `schema_version=polinko.manual_eval_ocr_retry_feedback_closure_restore.v1`,
  write a pre-restore backup under
  `.local_archive/manual-evals-feedback-closure-restore-<timestamp>/`, and
  restore the whole manual eval warehouse from the verified apply backup.
- Why: The apply gate already writes backup-first, but a backup is incomplete
  operationally until the restore path is explicit, tested, and documented.
  The restore gate keeps rollback guarded and reversible while preserving the
  exclusions for OCR reruns, eval runs, warehouse refresh, inferred source
  links, and pulse work.

## D-109: Preserve overlay-hypothesis OCR feedback without closing it

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `feedback_reclassification`, `ocr`, `backup_first`
- Human-led: The human lead approved continuing the manual-eval cleanup while
  keeping eval runs and pulse work out of scope.
- Decision: `make manual-evals-no-context-reclassify-preview` and
  `make manualdb-no-context-reclassify-preview` now preview overlay-hypothesis
  OCR feedback rows that have no same-session OCR context and whose source
  response asked for new image evidence. The apply targets
  `make manual-evals-no-context-reclassify-apply` and
  `make manualdb-no-context-reclassify-apply` require
  `CONFIRM=manual-evals-no-context-reclassify`, back up the active manual eval
  warehouse under `.local_archive/manual-evals-feedback-no-context-*`, keep
  matching feedback rows open, and emit
  `schema_version=polinko.manual_eval_no_context_feedback_reclassify.v1`.
- Why: Some human-led overlay experiments were routed into executable OCR retry
  debt even though the useful evidence is the overlay-assisted OCR hypothesis
  itself. Reclassification preserves the feedback as open overlay evidence
  while removing it from the OCR execution queue, and limits mutation to
  feedback `recommended_action`, `action_taken`, and `updated_at`; it still
  excludes feedback closure, OCR reruns, eval runs, warehouse refresh, source
  DB mutation, inferred source links, and pulse work.

## D-110: Split mixed grounding feedback through a local plan gate

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `manual_evals`, `feedback_reclassification`, `backup_first`,
  `local_mutation`
- Human-led: The human lead clarified that old manual-eval feedback rows can
  contain different hypothesis/evidence lanes and approved preserving them in
  the correct manual-eval cohorts without running evals or pulse work.
- Decision: `make manual-evals-feedback-reclassify-preview` and
  `make manualdb-feedback-reclassify-preview` now read a local
  human-reviewed JSON plan via `PLAN_PATH=<path>` and emit
  `schema_version=polinko.manual_eval_feedback_reclassify.v1`. The apply
  targets, `make manual-evals-feedback-reclassify-apply` and
  `make manualdb-feedback-reclassify-apply`, require the same `PLAN_PATH` plus
  `CONFIRM=manual-evals-feedback-reclassify`, back up the active manual eval
  warehouse under `.local_archive/manual-evals-feedback-reclassify-*`, keep
  matching feedback rows open, and reclassify only their explicit
  `recommended_action`, `action_taken`, and `updated_at` fields.
- Why: The manual eval warehouse is mixed evidence, not one uniform execution
  queue. Plan-based reclassification keeps human-reviewed intent explicit,
  removes stale/coarse cohort labels from future OCR retry work, and preserves
  reversibility without mutating feedback closure state, OCR rows, eval rows,
  source history, inferred source links, warehouse refreshes, or pulse work.

## D-111: Make `make end` enforce clean synced main

- Date: `2026-05-21`
- Category: `operator_workflow`
- Tags: `closeout`, `git`, `main`, `safety_gate`
- Human-led: The human lead caught that `make end` could pass on a feature
  branch, which contradicted the repo closeout contract.
- Decision: `make end` runs `make end-git-check` as its final closeout gate.
  Closeout fails unless the current branch is `main`, the working tree is
  clean, and local `main` is synced with `origin/main`. `make end-git-check`
  remains available as a standalone git-only check.
- Why: Branch-local validation and final closeout are different states. A
  feature branch can pass local quality checks, but the end-of-day closeout
  should only pass after the protected-main merge flow has completed and the
  local workspace is back on clean synced `main`.

## D-112: Add read-only source context for non-OCR feedback hygiene

- Date: `2026-05-22`
- Category: `operator_workflow`
- Tags: `manual_evals`, `feedback`, `source_context`, `read_only`
- Human-led: The human lead resumed manual-eval evidence hygiene from the
  separated cohorts after PR #586 and kept eval runs and pulse work out of
  scope.
- Decision: `make manual-evals-feedback-source-context` and
  `make manualdb-feedback-source-context` now print read-only source-history
  context for selected open feedback rows. The target defaults to the
  `grounding_source_verification` fail slice, supports the same
  `COHORT=<cohort_id>`, `OUTCOME=<outcome>`, and `LIMIT=<n>` filters as open
  feedback actionables, and emits
  `schema_version=polinko.manual_eval_feedback_source_context.v1`.
- Why: After OCR and overlay feedback were separated, the remaining grounding
  row needs source-message inspection before any closure or rerun decision.
  A read-only source-context packet keeps the next manual triage step anchored
  to source history while excluding feedback closure, OCR reruns, eval writes,
  warehouse mutation, source-history mutation, inferred links, and pulse work.

## D-113: Preview human-reviewed non-OCR feedback decisions

- Date: `2026-05-22`
- Category: `operator_workflow`
- Tags: `manual_evals`, `feedback`, `source_context`, `decision_preview`,
  `read_only`
- Human-led: The human lead approved continuing the manual-eval evidence
  hygiene sequence from the remaining grounding row while keeping eval runs
  and pulse work out of scope.
- Decision: `make manual-evals-feedback-decision-preview` and
  `make manualdb-feedback-decision-preview` now read a local human-reviewed
  decision JSON through `DECISION_PATH=<path>`, validate each selected feedback
  row against the current source-context slice, and emit
  `schema_version=polinko.manual_eval_feedback_decision_preview.v1`.
- Why: The remaining grounding row should be reviewed from source context
  before any closure or reclassification mutation. A decision preview keeps
  the human decision explicit, source-anchored, and read-only while printing
  only the future gate and mutation boundary; it excludes feedback closure,
  OCR reruns, eval writes, warehouse mutation, source-history mutation,
  inferred links, and pulse work.

## D-114: Pin Starlette in the dependency input for security visibility

- Date: `2026-05-22`
- Category: `dependency_management`
- Tags: `starlette`, `pip_audit`, `pip_tools`, `requirements`, `security`
- Human-led: The human lead connected the same Starlette security issue seen
  in sibling repos to Polinko's dependency input and asked for the durable
  dependency-layer fix.
- Decision: Pin `starlette==1.0.1` directly in `requirements.in` and
  regenerate `requirements.txt` with pip-tools. Keep `pyproject.toml` free of
  runtime dependencies under the current repo policy.
- Why: `starlette` is transitive through FastAPI and MCP, but the security gate
  audits the generated lock and Dependabot watches the pip input. Pinning the
  fixed release in `requirements.in` keeps future lock regeneration,
  Dependabot updates, and `pip-audit` aligned without weakening the security
  check or adding runtime dependency metadata to `pyproject.toml`.

## D-115: Draft non-OCR feedback decisions locally before preview

- Date: `2026-05-22`
- Category: `operator_workflow`
- Tags: `manual_evals`, `feedback`, `local_input`, `decision_draft`,
  `read_only`
- Human-led: The human lead continued manual-eval evidence hygiene from the
  remaining grounding row while keeping eval runs and pulse work out of scope.
- Decision: `make manual-evals-feedback-decision-draft` and
  `make manualdb-feedback-decision-draft` now write a local ignored feedback
  decision draft for the selected source-context slice. The draft defaults to
  `.local/manual_eval_decisions/feedback_decision.json`, accepts
  `DRAFT_PATH=<path>` and `FORCE=1`, preserves source-context fingerprints,
  defaults decisions to `selected_action=undecided`, and emits
  `schema_version=polinko.manual_eval_feedback_decision_draft.v1`.
- Why: The remaining non-OCR feedback decision should be prepared as local
  human-reviewed input before previewing any future gate. A draft generator
  reduces manual JSON friction while preserving the same source-anchored,
  no-overwrite, no-mutation contract as other local operator input tooling.

## D-116: Treat overlay feedback decisions as evidence pressure

- Date: `2026-05-23`
- Category: `operator_workflow`
- Tags: `manual_evals`, `feedback_decisions`, `ocr_overlay`, `read_only`
- Human-led: The human lead clarified that the overlay experiment is part of
  the research model and should stay recorded as manual-eval evidence, not
  folded into pulse work or ungrounded OCR retry execution.
- Decision: `docs/runtime/LOCAL_TOOLING.md` now names manual feedback decision
  packets as local operator inputs and records `keep_open` as the active
  evidence posture for overlay-assisted OCR hypothesis rows that have no exact
  OCR retry execution target. `docs/runtime/RUNBOOK.md` and
  `docs/governance/STATE.md` mirror the rule.
- Why: Overlay rows can be useful hypothesis pressure without being executable
  OCR retry work. Keeping them open until there is a real OCR comparison lane
  with attached overlay/source image context preserves the evidence chain while
  excluding OCR reruns, feedback closure, live eval writes, warehouse mutation,
  inferred source links, and pulse work.

## D-117: Add read-only overlay/OCR comparison readiness

- Date: `2026-05-24`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr_overlay`, `comparison_readiness`, `read_only`
- Human-led: The human lead carried forward the overlay experiment as research
  evidence while keeping eval runs, pulse work, and ungrounded OCR reruns out
  of scope.
- Decision: `make manual-evals-overlay-comparison-readiness` and
  `make manualdb-overlay-comparison-readiness` now print a read-only
  overlay/OCR comparison readiness packet for selected overlay-assisted OCR
  hypothesis rows. The packet emits
  `schema_version=polinko.manual_eval_overlay_ocr_comparison_readiness.v1` and
  exposes source context, source-image candidates, exact blockers, and
  payload-only previews for a future overlay/OCR comparison lane.
- Why: Overlay hypothesis rows need a readiness surface before any comparison
  execution exists. The packet keeps missing overlay/source image context
  visible as a blocker while preserving the evidence chain and excluding OCR
  runs, feedback closure, live eval writes, source-history mutation, manual
  eval warehouse mutation, browser launch, and pulse work.

## D-118: Index overlay source context through local human input

- Date: `2026-05-24`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr_overlay`, `source_context`, `local_input`,
  `read_only`
- Human-led: The human lead kept the overlay experiment in Polinko research
  while asking for the safest way to attach source-image context before any OCR
  comparison work.
- Decision: `make manual-evals-overlay-comparison-readiness` can now read a
  local ignored overlay/source image context index through
  `OVERLAY_SOURCE_INDEX_PATH=<path>`, defaulting to
  `.local/manual_eval_decisions/overlay_source_context_index.json`. Index files
  use `schema_version=polinko.manual_eval_overlay_source_context_index.v1` and
  must match the current feedback ID, source session, message ID, and
  source-context fingerprint before indexed images can make a readiness item
  ready.
- Why: Overlay/source image attachment should be explicit human-reviewed local
  input, not inferred filename matching or a manual-eval warehouse mutation.
  Fingerprint matching preserves source-context freshness while keeping OCR
  runs, feedback closure, eval writes, source-history mutation, warehouse
  mutation, browser launch, and pulse work out of scope.

## D-119: Draft and validate overlay source indexes locally

- Date: `2026-05-25`
- Category: `operator_workflow`
- Tags: `manual_evals`, `ocr_overlay`, `source_context`, `local_input`,
  `validation`
- Human-led: The human lead chose to keep the overlay experiment active as
  research evidence while requiring a careful chat about the kernel before
  implementation.
- Decision: `make manual-evals-overlay-source-index-draft` now writes a local
  ignored fillable overlay/source image context index from the current
  readiness slice, and `make manual-evals-overlay-source-index-validate`
  validates that index against the current readiness packet. Draft reports use
  `schema_version=polinko.manual_eval_overlay_source_context_index_draft.v1`;
  validation reports use
  `schema_version=polinko.manual_eval_overlay_source_context_index_validation.v1`.
- Why: Human-reviewed local source image paths need a safe authoring surface
  before any overlay/OCR comparison lane exists. Drafting and validating the
  index locally preserves feedback IDs, source sessions, message IDs, and
  source-context fingerprints while keeping OCR runs, feedback closure, eval
  writes, source-history mutation, warehouse mutation, browser launch, and
  pulse work out of scope.

## D-120: Keep the manual eval health CLI as a thin entrypoint

- Date: `2026-05-25`
- Category: `architecture`
- Tags: `manual_evals`, `cli`, `dispatch`, `import_surface`, `refactor`
- Decision: Keep `tools/manual_evals_db_health.py` as the manual-eval health
  CLI entrypoint only. CLI contracts, parser construction, output handling,
  feedback dispatch, OCR retry dispatch, shared dispatch helpers, and helper
  tests live with their owning modules rather than being re-exported through
  the entrypoint.
- Why: The manual-eval command surface now carries many read-only and guarded
  local operator flows. Keeping the entrypoint thin preserves routing
  auditability, reduces import-surface ambiguity, and lets future manual-eval
  refactors stay small while preserving the no-eval, no-pulse, no-unapproved
  mutation boundaries.

## D-121: Frame README status at the research-model level

- Date: `2026-06-09`
- Category: `documentation`
- Tags: `readme`, `research_model`, `repo_family`, `positive_contract`,
  `pre_beta`
- Human-led: The human lead corrected the refactor framing from repo-level
  cleanup to the Polinko research model being staged for the next beta, and
  required the public README language to keep the original positive
  instruction shape visible.
- Decision: The root README now uses a GitHub note callout and aligned badges
  to state that the Polinko research model is being staged for the next beta.
  The status copy names an active refactor window for the model contract,
  evidence snapshots, docs, and supporting tools, while saying current builds
  are kept stable during simplification, testing, and release alignment.
- Why: The public status surface must distinguish Polinko the research model
  from Polinko the repository. Model-level status wording keeps the staged beta
  boundary visible, and positive target language keeps the refactor aligned
  with the original Polinko instruction shape.

## D-122: Keep the private portfolio mockup ignore policy current

- Date: `2026-06-17`
- Category: `documentation`
- Tags: `ia`, `portfolio`, `private_lane`, `gitignore`, `refactor`
- Human-led: The human lead kept the cleanup scope repo-wide while preserving
  the current one-kernel rhythm.
- Decision: `.gitignore` now preserves only the current private portfolio
  mockup placeholder under `docs/peanut/assets/portfolio-mockups/.gitkeep`.
  The retired `docs/peanut/assets/tumbles/portfolio/` private mockup path is
  ignored again.
- Why: The current tracked docs name `docs/peanut/assets/portfolio-mockups/` as
  the private portfolio mockup lane. Keeping ignore policy aligned with that IA
  prevents retired private paths from becoming trackable again while preserving
  the placeholder needed for the current private lane.

## D-123: Table-drive feedback reclassify dispatch

- Date: `2026-06-17`
- Category: `architecture`
- Tags: `manual_evals`, `cli`, `dispatch`, `feedback`, `refactor`
- Decision: `tools/manual_eval_cli_feedback_reclassify_dispatch.py` now uses a
  local command table for feedback reclassify preview/apply routing. The
  public coordinator remains `tools/manual_eval_cli_feedback_dispatch.py`.
- Why: The feedback reclassify command group had repeated local routing for
  no-context preview/apply and plan-based preview/apply commands. A local
  table keeps route order, report builders, formatters, no-context defaults,
  plan/confirm/backup path handling, and preview/apply status mappings explicit
  without moving mutation boundaries or widening the dispatch surface.

## D-124: Table-drive feedback overlay dispatch

- Date: `2026-06-17`
- Category: `architecture`
- Tags: `manual_evals`, `cli`, `dispatch`, `feedback`, `overlay`,
  `refactor`
- Decision: `tools/manual_eval_cli_feedback_overlay_dispatch.py` now uses a
  local command table for overlay readiness, source-index draft, and
  source-index validation routing. The public coordinator remains
  `tools/manual_eval_cli_feedback_dispatch.py`.
- Why: The overlay command group had repeated local routing for commands that
  share overlay feedback defaults but differ in path arguments and finish
  semantics. A local table keeps route order, report builders, formatters,
  overlay defaults, source-index path handling, output/force handling, and
  direct versus guarded finish behavior explicit without moving mutation
  boundaries or widening the dispatch surface.

## D-125: Table-drive feedback decision dispatch

- Date: `2026-06-18`
- Category: `architecture`
- Tags: `manual_evals`, `cli`, `dispatch`, `feedback`, `decision`,
  `refactor`
- Decision: `tools/manual_eval_cli_feedback_decision_dispatch.py` now uses a
  local command table for feedback decision draft and preview routing. The
  public coordinator remains `tools/manual_eval_cli_feedback_dispatch.py`.
- Why: The feedback decision command group had repeated local routing for two
  commands that share feedback decision defaults and guarded finish semantics
  while differing in local output, force, decision-path, formatter, and status
  mapping. A local table keeps those differences explicit without moving
  mutation boundaries or widening the dispatch surface.

## D-126: Refresh pypdf security pin

- Date: `2026-06-18`
- Category: `dependency_management`
- Tags: `requirements`, `pip_audit`, `pypdf`, `security`
- Decision: Refresh the direct `pypdf` pin from `6.13.0` to `6.13.3` in
  `requirements.in` and regenerate `requirements.txt` with pip-tools.
- Why: The local Python security gate flagged `pypdf==6.13.0` for
  `GHSA-jm82-fx9c-mx94`, with `6.13.3` listed as the fixed version. Updating
  the direct pin keeps the security gate meaningful while preserving the
  standard `requirements.in` plus generated `requirements.txt` dependency
  workflow.

## D-127: Refresh root Node security lock

- Date: `2026-06-18`
- Category: `dependency_management`
- Tags: `npm_audit`, `package_lock`, `undici`, `security`
- Decision: Refresh the root transitive `undici` lock entry from `7.25.0` to
  `7.28.0` in `package-lock.json`.
- Why: The GitHub node-security gate flagged `undici==7.25.0` for
  `GHSA-vmh5-mc38-953g` and `GHSA-pr7r-676h-xcf6`. Updating the lockfile keeps
  the Node audit gate meaningful while preserving the root tooling dependency
  workflow.

## D-128: Table-drive OCR retry feedback-closure dispatch

- Date: `2026-06-18`
- Category: `architecture`
- Tags: `manual_evals`, `cli`, `dispatch`, `ocr_retry`, `feedback_closure`,
  `refactor`
- Decision: `tools/manual_eval_cli_ocr_retry_feedback_closure_dispatch.py` now
  uses a local command table for OCR retry feedback-closure preview, apply,
  apply-report, restore-preview, and restore routing. The public OCR retry
  coordinator remains `tools/manual_eval_cli_ocr_retry_dispatch.py`.
- Why: The feedback-closure command group had repeated local routing for five
  commands that share path normalization and finish handling while differing
  in run-directory, backup-directory, confirmation-token, backup-root,
  restore-root, formatter, and status semantics. A local table keeps those
  differences explicit without moving feedback-closure mutation boundaries or
  widening the dispatch surface.

## D-129: Reduce duplicate GitHub Actions runs

- Date: `2026-06-18`
- Category: `workflow_environment`
- Tags: `github_actions`, `ci`, `dependency_review`, `noise_reduction`
- Decision: GitHub CI now runs on pull requests and on pushes to `main`
  instead of every feature-branch push, and both CI and dependency-review
  workflows cancel superseded runs for the same pull request or ref.
- Why: Recent failed-check review showed that one failing feature-branch commit
  produced duplicate red runs through both `push` and `pull_request` CI. Keeping
  pull-request checks plus post-merge `main` checks preserves the merge gate
  while reducing repeated failure noise during active branch work.

## D-130: Make shell helper contracts a named gate

- Date: `2026-06-18`
- Category: `workflow_environment`
- Tags: `shell_scripts`, `make`, `ci`, `closeout`, `hygiene`
- Decision: `make scripts-check` is the canonical shell helper hygiene gate.
  It validates tracked `tools/*.sh` shebangs, strict modes, and sourced helper
  contracts, and it runs through both `make ci-docs` and `make end`.
- Why: Script helper drift had been handled as convention. A named gate keeps
  local operators, CI wrappers, and closeout helpers aligned before longer
  validation steps run.

## D-131: Isolate startup API smoke resources

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `startup`, `api_smoke`, `vscode`, `ports`, `runtime`, `sqlite`
- Decision: Default smoke runs allocate an isolated localhost port and run-scoped
  `/tmp` database paths when smoke endpoint and DB path overrides are unset.
  Explicit smoke endpoint and DB path overrides remain available for fixed-port
  debugging.
- Why: VS Code folder-open bootstrap can overlap with a manual or automatic
  startup. A fixed default smoke port lets the second run observe the first
  server's `/health`, and shared default smoke DB paths let overlapping runs
  delete each other's local state. Per-run default resources keep startup smoke
  independent while preserving deliberate fixed-endpoint control.

## D-132: Standardise core background runner lifecycle

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `runtime`, `make`, `shell_scripts`, `server_daemon`, `eval_sidecar`,
  `hygiene`
- Decision: Core background runners now route lifecycle operations through
  their helper scripts. `server-daemon` and `eval-sidecar` use explicit
  `start`, `status`, and `stop` actions, detached `start_new_session` process
  launch, repo-owned PID files, log paths, and stale or idle state handling.
- Why: Runner PID/log handling had drifted between Make recipes and helper
  scripts. Keeping lifecycle ownership in scripts matches the existing
  `caffeinate` pattern, makes Make targets thinner, and gives tests one place
  to guard local runner behaviour.

## D-133: Add Starlette test-client compatibility dependency

- Date: `2026-06-19`
- Category: `dependency_management`
- Tags: `starlette`, `testclient`, `httpx2`, `requirements`, `closeout`
- Human-led: The human lead asked to clear small closeout blubbles after
  `make end` surfaced a Starlette test-client deprecation warning.
- Decision: Add `httpx2==2.4.0` to `requirements.in` and regenerate
  `requirements.txt` through pip-tools. Keep `httpx` in the lock for packages
  that still depend on it, and let Starlette's test client use `httpx2`
  directly.
- Why: `starlette.testclient` now prefers `httpx2` and falls back to `httpx`
  with a deprecation warning when `httpx2` is absent. Pinning the compatibility
  package in the direct dependency input removes closeout warning noise while
  preserving the standard `requirements.in` plus generated `requirements.txt`
  workflow.

## D-134: Refresh pydantic-settings security lock

- Date: `2026-06-19`
- Category: `dependency_management`
- Tags: `pip_audit`, `pydantic_settings`, `requirements`, `security`
- Human-led: The human lead asked for small closeout blubbles to be fixed, and
  the dependency audit surfaced a Python security advisory during validation.
- Decision: Refresh the transitive `pydantic-settings` lock entry from
  `2.13.1` to `2.14.2` in `requirements.txt`.
- Why: The Python security gate flagged `pydantic-settings==2.13.1` for
  `GHSA-4xgf-cpjx-pc3j`, with `2.14.2` listed as the fixed version. Updating
  the generated lock keeps the audit gate meaningful while preserving
  `requirements.in` as the direct dependency input.

## D-135: Standardise portfolio mockup runner lifecycle

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `runtime`, `make`, `portfolio`, `shell_scripts`, `hygiene`
- Human-led: The human lead asked to clear hidden runtime and script surfaces
  one surface at a time.
- Decision: `portfolio-mockups` now delegates server lifecycle work to
  `tools/run_portfolio_mockups.sh`, with explicit `start`, `status`, and
  `stop` actions, detached `start_new_session` launch, repo-owned PID/log
  paths, stale PID handling, and a Make status target.
- Why: The portfolio mockup preview was the remaining background runner with
  PID/log/start/stop behaviour embedded directly in the Make recipe. Moving
  lifecycle ownership into a helper script aligns it with the other local
  runners and gives tests one focused contract to guard.

## D-136: Centralise manual eval health Make dispatch

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `manual_evals`, `make`, `workbench`, `hygiene`
- Human-led: The human lead asked to keep cleanup focused on one script surface
  at a time and to clear small Make/runtime blubbles rather than leaving them
  as warnings.
- Decision: Manual eval health, feedback, overlay, OCR retry, and
  reclassification Make targets keep their existing public names, but now route
  through `MANUAL_EVALS_DB_HEALTH_COMMAND` and a shared Make helper in
  `makefiles/surfaces.mk`.
- Why: These targets all dispatch to `tools.manual_evals_db_health` with
  different flags and argument variables. Centralising the command entrypoint
  reduces repeated Make recipe text, makes future workbench entrypoint changes
  one-place edits, and preserves the read-only/preview/apply operator
  boundaries.

## D-137: Retarget local path-leak audit to runtime config

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `path_leak`, `local_config`, `vscode`, `devcontainer`, `hygiene`
- Human-led: The human lead asked to treat hidden scripts and local runtime
  surfaces as first-class maintenance surfaces.
- Decision: `make path-leak-audit-local` now runs
  `tools.path_leak_check --scope local-config`, scanning local runtime config
  surfaces such as `.vscode`, `.devcontainer`, pre-commit config, and the
  devcontainer setup script. The broader `--scope local` remains available for
  explicit full local scans.
- Why: Full local scans include ignored manual-eval evidence bundles and
  private peanut notes that intentionally preserve absolute source paths as
  provenance. Retargeting the Make target keeps the hidden-surface audit
  actionable without treating local evidence provenance as a failure.

## D-138: Guard base OCR transcript workflows consistently

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `ocr`, `evals`, `shell_scripts`, `hygiene`
- Human-led: The human lead asked to continue script cleanup one surface at a
  time and to resolve small warnings or blubbles rather than leaving them as
  ambient maintenance debt.
- Decision: `tools/run_ocr_base_transcript_workflow.sh` now uses
  `tools/ocr_workflow_common.sh` and `tools/eval_case_guard.sh` before
  dispatching base OCR transcript case or stability runners.
- Why: Growth, focus, and transcript-lane OCR wrappers already used the shared
  case guard, but the base transcript wrapper only checked that the case file
  existed. Routing the base wrapper through the same guard keeps missing and
  empty case-file handling consistent while preserving the existing valid-case
  runner paths.

## D-139: Make local act runner configurable

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `make`, `local_ci`, `act`, `hygiene`
- Human-led: The human lead asked to keep hidden and low-frequency tooling
  surfaces maintained rather than treating them as incidental.
- Decision: Add `ACT ?= act` to external operator tooling config and route
  `make act-list` / `make act-ci` through `$(ACT)`.
- Why: The local CI helper recipes previously hard-coded `act`. Making the
  executable configurable follows the existing Make pattern for external
  operator tools, preserves default behavior, and gives local environments one
  explicit override point.

## D-140: Narrow local privacy helper scope

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `privacy`, `local_config`, `docs`, `hygiene`
- Human-led: The human lead asked to keep hidden and safety-relevant helper
  scripts maintained so small local-state problems do not turn into future
  cleanup debt.
- Decision: `make privacy-local-on` now installs the machine-local exclude
  block without marking tracked docs as `skip-worktree`. `make
  privacy-local-off` remains able to clear legacy docs `skip-worktree` state
  if an older run left tracked docs hidden.
- Why: Tracked governance and runtime docs are canonical repo truth and must
  remain visible during normal refactor work. The local privacy helper should
  protect explicitly local files without hiding tracked project state.

## D-141: Lock devcontainer setup to repo root

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `devcontainer`, `dependencies`, `local_config`, `hygiene`
- Human-led: The human lead asked to keep hidden and low-frequency runtime
  setup scripts maintained so launch-time blubbles do not become repeated
  operator friction.
- Decision: `tools/setup_devcontainer.sh` now resolves the git top-level and
  changes to it before creating `.venv` or installing root and portfolio
  dependencies.
- Why: Devcontainer post-create commands and manual local runs should produce
  the same dependency layout even when the shell starts from a nested
  directory.

## D-142: Make portfolio browser launch explicit

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `portfolio`, `make`, `local_preview`, `hygiene`
- Human-led: The human lead asked to keep operator shortcuts predictable and
  avoid hidden browser-launch behaviour during maintenance.
- Decision: `make portfolio` keeps the default non-launching URL path, and
  `make portfolio-open` is the explicit system-browser launcher. The existing
  `make portfolio-playwright` target remains the explicit Playwright launcher.
- Why: Docs and viz helpers already separate URL-printing defaults from
  browser-opening variants. Portfolio preview should follow the same operator
  pattern.

## D-143: Align dependency lock check resolver

- Date: `2026-06-19`
- Category: `workflow_environment`
- Tags: `dependencies`, `pip_tools`, `make`, `hygiene`
- Human-led: The human lead asked to keep dependency and CI helper scripts in
  order so recurring checks do not drift into repeated failure cleanup.
- Decision: `make deps-lock-check` now passes `--resolver=backtracking`,
  matching `make deps-lock`.
- Why: The write path and validation path should use the same pip-tools
  resolver settings so lock freshness checks reflect the lock generation
  command.

## D-144: Add shell parser checks to script hygiene

- Date: `2026-06-21`
- Category: `workflow_environment`
- Tags: `shell_scripts`, `make`, `hygiene`, `closeout`
- Human-led: The human lead asked to resolve small script blubbles rather than
  leaving warnings or shell typos as ambient maintenance debt.
- Decision: `make scripts-check` now validates tracked `tools/*.sh` files with
  the matching shell parser (`bash -n` or `sh -n`) in addition to shebang,
  strict-mode, and sourced-helper contract checks.
- Why: Syntax and quoting errors should fail in the lightweight script hygiene
  gate before longer style, type, test, security, or closeout runs.

## D-145: Keep public diagram rendering source-first

- Date: `2026-06-21`
- Category: `workflow_environment`
- Tags: `docs`, `diagrams`, `d3`, `make`, `hygiene`
- Human-led: The human lead asked to continue script cleanup one surface at a
  time and avoid generated-output churn while keeping warnings and tooling
  blubbles resolved.
- Decision: `make d3-render` now renders the Evidence Sankey through a
  temporary SVG and replaces the tracked SVG only when content changes. This
  aligns the D3 renderer with the existing Mermaid manifest/hash skip behaviour.
- Why: Public diagrams should remain source-first and intentional. Routine
  renderer runs should confirm artefacts are current without creating noisy
  rewrites.

## D-146: Run tracked path-leak checks during closeout

- Date: `2026-06-21`
- Category: `workflow_environment`
- Tags: `path_leak`, `make`, `closeout`, `hygiene`
- Human-led: The human lead asked for small warnings and hidden script
  blubbles to be resolved instead of left as ambient maintenance debt.
- Decision: `make end` now runs `make path-leak-check` after
  `make scripts-check` and before longer style, type, test, and security gates.
- Why: The runtime map already treated tracked path-leak checking as part of
  closeout. Wiring the gate into the actual closeout routine keeps tracked
  docs/code free of local machine paths before clean-main closure.

## D-147: Close the full background runner family at end-of-day

- Date: `2026-06-21`
- Category: `workflow_environment`
- Tags: `runtime`, `make`, `background_runners`, `closeout`, `hygiene`
- Human-led: The human lead asked to keep script and hidden runtime surfaces
  maintained one kernel at a time, with warnings resolved rather than parked.
- Decision: `make eod-stop` now stops `eval-sidecar`,
  `portfolio-mockups`, `server-daemon`, and repo-managed `caffeinate`, then
  prints status for the same runner family.
- Why: The runtime map defines these as the core background runner family.
  Closeout should operate on the same family it reports, so stray local
  runner state cannot survive a clean end-of-day gate unnoticed.

## D-148: Document wake-lock closeout cleanup explicitly

- Date: `2026-06-21`
- Category: `workflow_environment`
- Tags: `caffeinate`, `closeout`, `pid_lifecycle`, `hygiene`
- Human-led: The human lead asked to keep runtime helper behaviour clear
  enough that small launch/closeout blubbles do not become recurring friction.
- Decision: The start/end reference now distinguishes `caffeinate-status`
  reporting from `caffeinate-off-all` cleanup. Status reports matching
  unmanaged processes without adopting their PIDs; closeout cleanup stops the
  repo-owned PID and any remaining process matching the configured wake-lock
  command pattern.
- Why: The script and tests already treated `stop-all` as a command-pattern
  cleanup path. The compact operator reference needed to describe that active
  behaviour rather than imply that explicit closeout cleanup never stops
  matching unmanaged wake-lock processes.

## D-149: Add a runtime risk-surface scan gate

- Date: `2026-06-22`
- Category: `workflow_environment`
- Tags: `risk_scan`, `runtime`, `make`, `ci`, `hygiene`
- Human-led: The human lead identified that broad script/runtime cleanup needs
  a risk scan at each kernel boundary, not only tests for already-known
  behaviour.
- Decision: Add `make risk-scan`, backed by
  `tools/check_runtime_risk_scan.py`, and run it through `make ci-docs` and
  `make end`. The gate verifies that known high-risk runtime, script, CI,
  background-runner, and local configuration surfaces remain visible in the
  tracked runtime map and Make gates.
- Why: The existing test suite checks many encoded behaviours, but it does not
  guarantee that a cleanup kernel inventoried the right surfaces before
  prioritising. A named risk-scan gate gives the refactor a lightweight guard
  against hidden-surface drift while keeping detailed implementation tests
  focused on the files that actually change.

## D-150: Guard operator aliases in CI docs and closeout

- Date: `2026-06-22`
- Category: `workflow_environment`
- Tags: `operator_aliases`, `manual_evals`, `ocr`, `make`, `hygiene`
- Human-led: The human lead asked to continue the script refactor one kernel
  at a time and keep manual eval/OCR operator surfaces from becoming hidden
  maintenance debt.
- Decision: Add `make operator-alias-check`, backed by
  `tools/check_operator_aliases.py`, and run it through `make ci-docs` and
  `make end`. The gate keeps `manual-evals-*` targets paired with their
  `manualdb-*` compatibility aliases and keeps parked OCR eval aliases out of
  automatic startup, closeout, and CI dependencies.
- Why: The manual eval workbench remains active, while OCR eval execution is
  parked. A named alias gate preserves current operator commands and catches
  future drift before alias cleanup accidentally changes execution boundaries.

## D-151: Retire deprecated `eod-stop` surface

- Date: `2026-06-22`
- Category: `workflow_environment`
- Tags: `runtime`, `make`, `closeout`, `hygiene`
- Human-led: The human lead identified that the `eod-stop` target was a
  deprecated surface that should not remain part of Polinko.
- Decision: Replace the active stop target with `make end-stop` and route the
  closeout routine through that current-name target while preserving the same
  background-runner stop behaviour.
- Why: `make end` is the canonical closeout surface. The stop helper should
  use the same current vocabulary so deprecated operator names do not linger as
  live Make targets.

## D-152: Guard current closeout vocabulary

- Date: `2026-06-22`
- Category: `workflow_environment`
- Tags: `runtime`, `risk_scan`, `make`, `closeout`, `hygiene`
- Human-led: The human lead asked to keep the cleanup exercise focused on
  current Polinko surfaces and prevent deprecated naming from lingering.
- Decision: `make risk-scan` now requires the active `end-stop` helper and
  fails if the deprecated `eod-stop` target returns. Runtime docs also state
  that `make eod` is only a compatibility alias for canonical `make end`.
- Why: Compatibility aliases can remain useful, but helper targets should use
  current closeout vocabulary. Encoding that distinction keeps future cleanup
  from reintroducing stale operator surfaces.

## D-153: Treat risk-scan gates as human-led contract checks

- Date: `2026-06-22`
- Category: `workflow_environment`
- Tags: `risk_scan`, `contract_checks`, `runtime`, `scripts`, `hygiene`
- Human-led: The human lead identified that hidden script and runtime drift
  could pass ordinary tests, and asked for risk checks that catch the surfaces
  the refactor must keep visible.
- Engineer implementation: Encode that signal as repo-owned `risk-scan` and
  contract-check gates, wired through `make ci-docs`, `make pr-preflight`, and
  closeout instead of relying on memory, review notes, or manual recall.
- Decision: Treat repo-owned risk-scan and contract-check scripts as active
  refactor gates. These checks should encode high-value runtime, script,
  closeout, CI, and operator-surface contracts that are easy to miss during
  normal feature tests.
- Why: Polinko has broad test coverage, but tests for known behaviour are not
  the same as a risk scan for hidden maintenance surfaces. Making these gates
  explicit keeps the refactor human-led while giving future kernels a concrete
  way to prevent quiet drift.

## D-154: Proactively record durable contract changes

- Date: `2026-06-22`
- Category: `collaboration_method`
- Tags: `decision_log`, `human_led`, `kernel_flow`, `governance`, `hygiene`
- Human-led: The human lead clarified that proactive decision logging is part
  of the Polinko contract, not an optional follow-up after the human catches a
  missing record.
- Engineer implementation: During implementation, Codex should identify when
  a change creates or clarifies a durable repo contract and add the matching
  decision-log entry before closing the kernel.
- Decision: Treat decision-log upkeep as part of engineering hygiene for
  durable method, workflow, runtime, evidence, and eval-contract changes.
- Why: The repository is the research object. Durable contract changes need a
  traceable governance record at the time they are made, so the human lead does
  not have to reconstruct or request the missing ledger entry afterward.

## D-155: Guard runner status reporting as a closeout contract

- Date: `2026-06-22`
- Category: `workflow_environment`
- Tags: `runtime`, `risk_scan`, `background_runners`, `closeout`, `hygiene`
- Human-led: The human lead asked for hidden script and runner surfaces to stay
  maintained, with warnings and small runtime drift treated as fixable
  engineering work rather than background noise.
- Engineer implementation: Add `session-status` to the risk-scan Make target
  requirements and current runtime map, and test that `make end-stop` ends by
  reporting each runner family's post-stop state.
- Decision: Treat `make session-status` as the consolidated background-runner
  status surface for closeout. The stop helper may clean up runners first, but
  it must finish by surfacing server, eval sidecar, portfolio mockup, and
  repo-managed wake-lock status.
- Why: Stop commands alone can make a closeout appear quiet while leaving
  stale PID files, unmanaged local processes, or wake-lock drift invisible.
  A guarded post-stop status report keeps those small runtime issues visible
  during maintenance kernels and final session closeout.

## D-156: Audit local startup config shape

- Date: `2026-06-22`
- Category: `workflow_environment`
- Tags: `startup`, `vscode`, `local_config`, `risk_scan`, `hygiene`
- Human-led: The human lead identified a VS Code startup/task warning and
  asked for hidden local runtime scripts and config to be maintained as
  first-class surfaces.
- Engineer implementation: Extend `make path-leak-audit-local` with
  `tools.check_local_runtime_config`, which validates ignored `.vscode` JSON
  and catches retired folder-open bootstrap tasks or background tasks without
  readiness signalling.
- Decision: Treat local ignored VS Code runtime config as an audited operator
  surface. Startup remains chat-led through manual `make start`, and local
  task config should not reintroduce folder-open bootstrap behaviour.
- Why: Local ignored config can break the day-start ritual without showing up
  in tracked CI. A focused local audit gives the repo a repeatable way to
  detect startup-task drift without promoting machine-local VS Code settings
  into tracked source.

## D-157: Add explicit repo-search scopes

- Date: `2026-06-22`
- Category: `workflow_environment`
- Tags: `search`, `operator_tooling`, `docs_peanut`, `hygiene`
- Human-led: The human lead asked for same-surface observations to be resolved
  before a kernel closes, while keeping one active task at a time.
- Engineer implementation: Add `make repo-search` for routine maintenance
  search and `make repo-search-full` for intentional full-surface search,
  backed by `tools.repo_search`.
- Decision: Treat repo search as an explicit operator surface with two named
  scopes. Routine search stays focused on active implementation, runtime,
  research, tests, and scripts. Full search is available when private
  transcripts, frozen eval snapshots, or long governance history are the active
  source.
- Why: Broad ad hoc searches can drown the operator in transcript archives,
  generated output, or long decision logs and obscure the active task. Named
  search scopes keep maintenance kernels readable without hiding private or
  evidence lanes when the work intentionally needs them.

## D-158: Require handoff to mention the current commit

- Date: `2026-06-22`
- Category: `workflow_environment`
- Tags: `handoff`, `closeout`, `current_truth`, `docs`, `hygiene`
- Human-led: The human lead identified that closeout freshness is not enough
  when local `SESSION_HANDOFF` still carries an older active slice.
- Engineer implementation: Extend `tools.check_end_docs` so optional local
  `docs/peanut/governance/SESSION_HANDOFF.md` must include the current short
  commit hash when it is present, and cover that contract in unit tests.
- Decision: Treat local `SESSION_HANDOFF` as a content freshness surface, not
  only a date freshness surface. `make end-docs-check` now verifies that the
  handoff points at the current repo commit before closeout can pass.
- Why: `STATE` and local `SESSION_HANDOFF` are the repo's current-truth and
  active-slice surfaces. A same-date handoff that still points to old kernels
  can pass a date-only gate while misleading the next session.

## D-159: Treat startup as a chat-first alignment pass

- Date: `2026-06-23`
- Category: `collaboration_method`
- Tags: `startup`, `alignment`, `kernel_flow`, `human_led`, `hygiene`
- Human-led: The human lead clarified that the morning ritual should preserve a
  shared chat-first map before implementation, not only a strict checklist.
- Engineer implementation: Update the `make start` rehydrate prompt, runtime
  procedure docs, and startup contract tests so startup reports context, a
  kernel map, and any attention note, then waits for human alignment before
  implementation.
- Decision: Treat the morning startup reply as the chat-first alignment pass.
  Implementation begins only after the human lead aligns on the recommended
  first kernel.
- Why: Startup should rehydrate and orient the session without becoming an
  automatic implementation trigger. Encoding the ritual in script, docs, and
  tests keeps one-kernel work traceable and prevents drift back into
  checklist-only startup.

## D-160: Centralize explicit local URL launch handling

- Date: `2026-06-23`
- Category: `workflow_environment`
- Tags: `local_urls`, `browser_launch`, `make`, `runtime`, `hygiene`
- Human-led: The human lead asked for scripts and hidden runtime surfaces to
  stay maintained so repeated helper drift does not interrupt operator work.
- Engineer implementation: Route explicit system-browser launch paths through
  `tools/open_local_url.sh`, and guard default print-only behavior plus the
  helper-owned launch path in Makefile contract tests.
- Decision: Local URL targets stay print-first by default. Explicit browser
  launch remains available, but system launch handling belongs to one
  repo-owned helper.
- Why: Duplicated `open` / `xdg-open` snippets make browser-launch behavior
  easy to drift across docs, viz, and portfolio targets. A single helper keeps
  the no-browser default and explicit-launch escape hatch auditable.

## D-161: Centralize detached runner process launch

- Date: `2026-06-23`
- Category: `runtime_engineering`
- Tags: `background_runners`, `pid_files`, `logs`, `scripts`, `hygiene`
- Human-led: The human lead asked for high-traffic scripts and hidden runtime
  surfaces to be maintained as first-class engineering work.
- Engineer implementation: Add `tools/launch_detached_process.py` for
  detached child-process launch, log redirection, and PID-file writes; route
  `server-daemon`, `eval-sidecar`, `portfolio-mockups`, and `caffeinate`
  launch paths through it.
- Decision: Background runner scripts share one detached-launch helper while
  keeping domain-specific liveness, adoption, status, and stop logic in their
  runner scripts.
- Why: Repeated Python heredocs made launch behavior harder to audit and
  maintain across the runner family. A single launcher keeps the shared
  process mechanics consistent without flattening each runner's lifecycle
  contract.

## D-162: Centralize shell repo-root resolution

- Date: `2026-06-23`
- Category: `runtime_engineering`
- Tags: `startup`, `closeout`, `devcontainer`, `shell`, `hygiene`
- Human-led: The human lead asked for hidden scripts and repeated runtime
  helper patterns to be maintained so small shell drift does not interrupt
  operator work.
- Engineer implementation: Add `tools/repo_root.sh` with shared
  `polinko_repo_root` and `polinko_cd_repo_root` helpers; route startup,
  closeout, devcontainer setup, local privacy guard, OCR workflow, eval-server
  daemon, and Playwright snapshot scripts through it; guard the helper in
  shell/runtime tests.
- Decision: Shell bootstrap and operator scripts share one repo-root helper.
  Script-specific workflow logic stays in each script, while checkout-root
  resolution is owned by `tools/repo_root.sh`.
- Why: Repeated `BASH_SOURCE` and `git rev-parse` root snippets made startup,
  closeout, and setup scripts easy to drift independently. A shared helper
  keeps root discovery consistent without broadening the kernel into Python
  path cleanup.

## D-163: Guard runtime tool reference test visibility

- Date: `2026-06-23`
- Category: `runtime_engineering`
- Tags: `tests`, `runtime`, `tooling`, `coverage`, `hygiene`
- Human-led: The human lead asked for hidden script and helper surfaces to be
  actively maintained so workflow interruptions are caught before they become
  operator-facing failures.
- Engineer implementation: Add a dynamic unit test that scans tracked runtime,
  script, docs, and config surfaces for references to tracked `tools/*.py` and
  `tools/*.sh` helpers, then verifies each referenced helper has direct test
  visibility by path, filename, stem, or module name.
- Decision: Runtime helper references must stay visible to tests. New tracked
  references from active runtime surfaces should either point to an already
  tested helper or arrive with matching direct test visibility.
- Why: Indirect helper references can bypass Make-target inventories and hide
  drift in scripts, docs, local config, or runtime helpers. A dynamic guard
  makes the inventory repeatable and fails close to the source of future drift.

## D-164: Run local runtime config checks through CI docs

- Date: `2026-06-23`
- Category: `workflow_environment`
- Tags: `startup`, `vscode`, `ci-docs`, `local_config`, `hygiene`
- Human-led: The human lead identified startup/task warnings as critical
  operator-facing issues and asked for hidden runtime scripts and config to
  stay maintained through normal workflow checks.
- Engineer implementation: Promote `tools.check_local_runtime_config` into a
  named `make local-runtime-config-check` target, wire that target into
  `make ci-docs`, and keep `make path-leak-audit-local` as the deeper local
  audit lane.
- Decision: VS Code task/config shape is part of the normal docs/runtime gate.
  Retired folder-open bootstrap behaviour and background-task readiness drift
  should fail before PR or closeout work proceeds.
- Why: The checker existed, but a startup config regression could stay outside
  the high-traffic validation path. Running it through `make ci-docs` keeps the
  startup ritual protected without adding browser launches or global editor
  settings changes.

## D-165: Align local privacy guard with current handoff

- Date: `2026-06-23`
- Category: `workflow_environment`
- Tags: `privacy`, `local_config`, `docs`, `handoff`, `hygiene`
- Human-led: The human lead asked for hidden and low-frequency runtime helper
  surfaces to stay maintained so stale local-state scripts do not interrupt
  normal operator work.
- Engineer implementation: Point `tools/local_privacy_guard.sh` at the current
  local handoff surface, `docs/peanut/governance/SESSION_HANDOFF.md`, and add a
  contract test that keeps deprecated local doc paths out of the helper.
- Decision: The local privacy helper should name the active local handoff
  surface rather than legacy local doc paths, while continuing to avoid
  `skip-worktree` for tracked docs.
- Why: The current-truth docs identify `docs/peanut/governance/SESSION_HANDOFF.md`
  as the local carryover surface. Keeping the helper aligned prevents stale
  excludes from looking like active workflow state.

## D-166: Guard ignored VS Code config against retired local docs

- Date: `2026-06-23`
- Category: `workflow_environment`
- Tags: `vscode`, `local_config`, `docs`, `hygiene`
- Human-led: The human lead asked for hidden and local runtime surfaces to stay
  maintained because ignored config drift can still interrupt operator work.
- Engineer implementation: Extend `tools.check_local_runtime_config` to reject
  retired local doc paths in ignored `.vscode` JSON and clean the local
  workspace settings that still referenced them.
- Decision: Local VS Code runtime config must not keep retired
  `docs/INSTANCE_HANDOFF.md` or `docs/POL1_COMMS.md` references. The active
  local handoff surface remains `docs/peanut/governance/SESSION_HANDOFF.md`.
- Why: Ignored local config can preserve obsolete workflow state after tracked
  docs and helper scripts have moved on. The existing local runtime config gate
  should catch that drift before startup or operator work gets confusing.

## D-167: Keep startup map aligned with chat-first ritual

- Date: `2026-06-23`
- Category: `runtime_engineering`
- Tags: `startup`, `docs`, `runtime_map`, `hygiene`
- Human-led: The human lead asked for hidden workflow drift and small startup
  blubbles to be resolved instead of left as future operator confusion.
- Engineer implementation: Rename the active runtime map startup lane from the
  retired bootstrap wording to the current alignment wording, and add a startup
  contract test that keeps the old phrase out of the active runtime map.
- Decision: Active runtime docs should describe startup as chat-first
  alignment, not workspace bootstrap. Bootstrap wording remains only as a
  guarded retired-task signal in local config validation.
- Why: The retired VS Code folder-open bootstrap path is already blocked in
  local config. Leaving its name in the active map makes stale workflow
  vocabulary look current.

## D-168: Guard active runtime map against stale tokens

- Date: `2026-06-23`
- Category: `runtime_engineering`
- Tags: `risk_scan`, `runtime_map`, `docs`, `hygiene`
- Human-led: The human lead asked for stale and hidden workflow drift to be
  caught by normal maintenance checks instead of rediscovered manually.
- Engineer implementation: Extend `tools.check_runtime_risk_scan` with
  forbidden runtime-map tokens and test coverage for retired startup wording.
- Decision: Runtime-map stale vocabulary belongs in the risk scan when it can
  make retired workflow state look active.
- Why: The runtime map is a high-traffic orientation surface. Guarding retired
  wording there keeps future cleanup kernels from relying on ad hoc text
  searches to catch the same drift.

## D-169: Keep startup repo-root contract portable

- Date: `2026-06-23`
- Category: `runtime_engineering`
- Tags: `startup`, `runbook`, `docs`, `hygiene`
- Human-led: The human lead asked for startup and hidden runtime surfaces to stay
  aligned with the chat-first ritual instead of preserving stale bootstrap
  wording or placeholders.
- Engineer implementation: Update the runbook to define the canonical repo root
  as the repo root printed by `make start`, and extend the startup contract test
  so the retired `/abs/path/to/polinko` placeholder cannot return there.
- Decision: Active runtime docs use the printed startup repo root as the
  canonical location signal. Tracked docs should not hard-code machine-local
  repo paths or placeholder roots.
- Why: A placeholder path in the runbook made stale startup guidance look active.
  The runtime contract should stay portable while still giving the operator a
  concrete repo root during `make start`.

## D-170: Guard closeout helper against parked OCR aliases

- Date: `2026-06-23`
- Category: `runtime_engineering`
- Tags: `operator_aliases`, `ocr`, `closeout`, `hygiene`
- Human-led: The human lead asked for hidden and high-traffic runtime guards to
  stay maintained so deprecated OCR/eval paths cannot drift back into normal
  operator work.
- Engineer implementation: Add `end-stop` to the operator-alias protected
  entrypoints and add a focused fixture proving parked OCR aliases fail when
  attached to the closeout helper.
- Decision: `make operator-alias-check` protects the active closeout helper, not
  only top-level automation and CI targets.
- Why: `make end` delegates background cleanup through `make end-stop`. If that
  helper can accumulate parked OCR eval aliases, closeout can drift even while
  the top-level `end` target still looks clean.

## D-171: Guard local editor config against retired doc tokens

- Date: `2026-06-23`
- Category: `workflow_environment`
- Tags: `vscode`, `local_config`, `docs`, `hygiene`
- Human-led: The human lead asked for local/editor runtime surfaces and hidden
  configuration to stay maintained because ignored workspace config can still
  interrupt operator work.
- Engineer implementation: Extend `tools.check_local_runtime_config` to reject
  retired local doc/config tokens for old mirror/adoption docs and the retired
  `docs/portfolio/raw_evidence` lane; clean the ignored local VS Code settings
  that still carried those tokens.
- Decision: Local VS Code runtime config must follow the current docs lane:
  private material belongs under `docs/peanut/`, and retired local doc or
  portfolio raw-evidence tokens should fail the local runtime config check.
- Why: Ignored editor config can preserve stale local doc lanes after tracked
  docs have moved on. Guarding those tokens keeps editor search/lint behaviour
  aligned with the active Polinko structure.

## D-172: Guard devcontainer config against retired doc tokens

- Date: `2026-06-23`
- Category: `workflow_environment`
- Tags: `devcontainer`, `local_config`, `docs`, `hygiene`
- Human-led: The human lead asked for hidden/editor/runtime configuration to stay
  maintained because stale local surfaces can interrupt normal operator work.
- Engineer implementation: Extend `tools.check_local_runtime_config` to scan
  tracked `.devcontainer/devcontainer.json` alongside ignored `.vscode` JSON,
  with focused tests proving retired doc/config tokens fail in both lanes.
- Decision: The local runtime config gate covers both ignored VS Code config and
  tracked devcontainer VS Code customizations for retired local doc/config
  tokens.
- Why: Devcontainer settings can preserve the same stale editor assumptions as
  ignored workspace settings. Checking both surfaces keeps host and container
  workflow config aligned with the current Polinko docs lane.

## D-173: Guard pre-commit hook shape through risk scan

- Date: `2026-06-23`
- Category: `workflow_environment`
- Tags: `pre_commit`, `risk_scan`, `local_config`, `hygiene`
- Human-led: The human lead asked for hidden workflow surfaces and small
  development interruptions to be maintained proactively instead of rediscovered
  manually during normal work.
- Engineer implementation: Extend `tools.check_runtime_risk_scan` to parse
  `.pre-commit-config.yaml`, enforce the lightweight repo-owned Ruff and
  markdownlint hook contract, and reject retired `isort` or `black` hook tokens.
- Decision: Pre-commit hook shape is part of the docs/runtime risk scan. The
  active hook set stays lightweight and delegates to Make targets instead of
  preserving retired formatter/import-sorter tools.
- Why: Pre-commit is a hidden workflow gate that can interrupt every commit while
  staying outside app runtime. Guarding its shape in `make ci-docs` catches hook
  drift before branch validation or closeout.

## D-174: Keep CI workflow tokens read-only

- Date: `2026-06-23`
- Category: `ci`
- Tags: `github_actions`, `permissions`, `security`, `hygiene`
- Human-led: The human lead asked for CI and dependency automation failures and
  hidden workflow risks to stay maintained proactively.
- Engineer implementation: Add explicit `contents: read` permissions to the main
  CI workflow and add a contract test that keeps CI and dependency-review
  workflow permissions read-only.
- Decision: GitHub Actions workflows that only read the repository should declare
  read-only repository token permissions instead of relying on default workflow
  permissions.
- Why: CI does not need write access to run docs, style, type, tests, package, or
  security gates. Making the token scope explicit keeps dependency automation
  aligned with current least-privilege practice.

## D-175: Add operator target for stale remote refs

- Date: `2026-06-23`
- Category: `operator_workflow`
- Tags: `git`, `branches`, `refs`, `hygiene`
- Human-led: The human lead asked for branch and ref cleanup interruptions to
  be noticed and resolved as part of normal engineering hygiene.
- Engineer implementation: Prune stale remote-tracking refs and add
  `make git-prune-stale-refs`, with Makefile contract coverage and runtime
  docs/STATE references.
- Decision: Stale `origin/*` remote-tracking branch cleanup is a repo-owned
  operator target. The target prunes deleted remote refs only and does not
  delete local branches.
- Why: Merged or deleted PR branches can remain locally as stale remote-tracking
  refs and make branch/PR hygiene look noisier than it is. A named target keeps
  that cleanup repeatable without turning it into ad hoc Git memory.

## D-176: Align runner scripts with shared repo-root helper

- Date: `2026-06-25`
- Category: `runtime_engineering`
- Tags: `runners`, `shell`, `repo_root`, `hygiene`
- Human-led: The human lead asked to continue the script/runtime cleanup one
  focused surface at a time so hidden helper drift does not interrupt operator
  work.
- Engineer implementation: Route `manage_caffeinate.sh`,
  `run_server_daemon.sh`, `run_eval_sidecar_start.sh`, and
  `run_portfolio_mockups.sh` through `tools/repo_root.sh` before resolving
  `tools/launch_detached_process.py`, and add Makefile contract coverage for
  the runner-family root setup.
- Decision: Background runner scripts use the shared repo-root helper before
  launching detached child processes or relying on repo-relative local paths.
  Runner-specific liveness, adoption, status, and stop logic remains in each
  runner script.
- Why: The runner family already shares detached launch mechanics, but each
  script still carried its own root-adjacent launcher setup. Using the shared
  root helper keeps direct script execution, Make execution, and closeout
  cleanup aligned without flattening runner-specific lifecycle behaviour.

## D-177: Make clean-main git gate repo-root aware

- Date: `2026-06-25`
- Category: `runtime_engineering`
- Tags: `closeout`, `git`, `repo_root`, `hygiene`
- Human-led: The human lead asked for runtime and script helpers that interrupt
  operator workflow to be kept in order as part of the script/runtime cleanup.
- Engineer implementation: Route `tools/check_end_git_clean.sh` through
  `tools/repo_root.sh`, add contract coverage for the root setup, and adjust
  the clean-main gate tests to install the script and root helper inside their
  temporary fixture repositories.
- Decision: The clean-main git gate resolves the checkout root before checking
  branch, cleanliness, remote configuration, and local/remote sync.
- Why: `make end-git-check` is the final closeout guard. It should behave the
  same from Make, direct script execution, and subdirectory invocation instead
  of depending on the operator's current working directory.

## D-178: Make eval report wrappers repo-root aware

- Date: `2026-06-25`
- Category: `runtime_engineering`
- Tags: `eval_reports`, `shell`, `repo_root`, `hygiene`
- Human-led: The human lead asked to continue script/runtime cleanup in the
  normal focused order, keeping Polinko context stable and avoiding broad
  wrapper changes.
- Engineer implementation: Convert `run_eval_report.sh` and
  `run_eval_reports_parallel.sh` to Bash root-helper entrypoints, add
  subdirectory invocation tests, and extend Makefile contract coverage for the
  eval report wrapper root setup.
- Decision: Eval report wrappers resolve the checkout root before creating
  default report directories or launching report modules.
- Why: Report-output defaults should behave the same from Make, direct script
  execution, and subdirectory invocation. Starting with this coherent wrapper
  pair avoids broad shell-mode churn across the parked OCR/eval wrapper family.

## D-179: Make local eval gate wrapper repo-root aware

- Date: `2026-06-25`
- Category: `runtime_engineering`
- Tags: `local_eval_gate`, `shell`, `repo_root`, `hygiene`
- Human-led: The human lead asked to continue the script/runtime cleanup in
  focused order, keeping active maintenance separate from eval execution work.
- Engineer implementation: Convert `run_local_eval_gate.sh` to a Bash
  root-helper entrypoint with repo `.venv` fallback when `PYTHON` is unset,
  add subdirectory API-smoke wrapper coverage with fake Python/curl commands,
  and extend Makefile contract coverage for the local eval gate root setup.
- Decision: Local eval gates resolve the checkout root before starting their
  fresh local server or launching gate modules, and direct invocation without
  `PYTHON` prefers the repo `.venv` interpreter when available.
- Why: `api-smoke`, `eval-smoke`, hallucination gates, and quality gates are
  high-traffic runtime checks. They should behave the same from Make, direct
  script execution, and subdirectory invocation instead of depending on the
  operator's current working directory.

## D-180: Make OCR report wrappers repo-root aware

- Date: `2026-06-25`
- Category: `runtime_engineering`
- Tags: `ocr_reports`, `shell`, `repo_root`, `hygiene`
- Human-led: The human lead approved continuing the focused script/runtime
  cleanup in normal order, with OCR eval execution still outside the active
  maintenance lane.
- Engineer implementation: Convert `run_ocr_report_workflow.sh` and
  `run_ocr_report_builder.sh` to Bash root-helper entrypoints, add
  subdirectory invocation tests for the wrapper pair, and extend Makefile
  contract coverage for the OCR report wrapper root setup.
- Decision: OCR report wrappers resolve the checkout root before validating
  local report inputs or launching report-builder modules.
- Why: OCR report commands are maintenance/reporting wrappers with repo-relative
  `.local` defaults. They should behave the same from Make, direct script
  execution, and subdirectory invocation without starting OCR eval work.

## D-181: Make OCR guard and transcript workflow entrypoints repo-root aware

- Date: `2026-06-25`
- Category: `runtime_engineering`
- Tags: `ocr_guard`, `ocr_transcripts`, `shell`, `repo_root`, `hygiene`
- Human-led: The human lead approved continuing the focused script/runtime
  cleanup in normal order while keeping OCR eval execution out of the active
  maintenance lane.
- Engineer implementation: Convert `run_guarded_ocr_case_eval.sh`,
  `run_ocr_base_transcript_workflow.sh`, and
  `run_ocr_transcript_lane_workflow.sh` to Bash root-helper entrypoints, add
  subdirectory tests that exercise the default guard/common paths without
  running evals, and extend Makefile contract coverage for the root setup.
- Decision: OCR case-guard and transcript workflow entrypoints resolve the
  checkout root before sourcing guard helpers or delegating to OCR eval
  runners.
- Why: These wrappers own missing/empty case preflight before OCR execution.
  They should behave the same from Make, direct script execution, and
  subdirectory invocation so maintenance checks do not depend on the operator's
  current working directory.

## D-182: Make OCR intake and stability orchestrator wrappers repo-root aware

- Date: `2026-06-25`
- Category: `runtime_engineering`
- Tags: `ocr_intake`, `ocr_stability`, `shell`, `repo_root`, `hygiene`
- Human-led: The human lead approved continuing the focused script/runtime
  cleanup in normal order while keeping OCR eval execution outside the active
  maintenance lane.
- Engineer implementation: Convert `run_ocr_intake_workflow.sh`,
  `run_ocr_focus_stability_workflow.sh`, `run_ocr_growth_case_workflow.sh`,
  and `run_ocr_growth_stability_workflow.sh` to Bash root-helper entrypoints,
  add subdirectory tests for default local paths and shared helper sourcing
  without running evals, and extend Makefile contract coverage for the root
  setup.
- Decision: OCR intake, focus stability, growth case, and growth stability
  orchestrator wrappers resolve the checkout root before using repo-relative
  defaults, sourcing shared guard helpers, or delegating to eval runners.
- Why: These wrappers are operator-facing orchestration surfaces around local
  OCR inputs and reports. They should behave the same from Make, direct script
  execution, and subdirectory invocation so maintenance checks do not depend on
  the operator's current working directory.
