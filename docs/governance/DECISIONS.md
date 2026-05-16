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

## D-003: Eval release outcomes stay binary

- Date: `2026-05-15`
- Category: `eval_quality`
- Tags: `binary_gate`, `retain_evict`, `lane_contract`
- Decision: Release outcomes remain `pass` / `fail`, and after `fail` the
  only allowed failure dispositions are `retain` or `evict`.
- Why: This keeps the gate legible while preserving a clean distinction
  between release judgment and upstream case handling.

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
