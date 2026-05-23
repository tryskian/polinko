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
- Decision: `make end` now runs `make end-git-check` as its first step.
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
