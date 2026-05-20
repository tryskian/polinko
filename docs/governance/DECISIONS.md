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
