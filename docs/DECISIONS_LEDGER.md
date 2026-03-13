# Decisions Ledger (New Baseline)

Use this ledger for all decisions after the 2026-03-13 docs reset.

## Entry Format

- ID: `L-###`
- Date
- Category
- Tags (3-5)
- Decision (one sentence)
- Why (one sentence)
- Validation / Evidence links

## L-001: Keep protected-main PR workflow

- Date: 2026-03-13
- Category: workflow_governance
- Tags: pr, checks, main, safety
- Decision: Keep `main` protected and require PR checks for all merges.
- Why: Maintains release-line integrity while allowing fast feature branches.
- Validation / Evidence links: CI required checks (`test`, `markdownlint`).

## L-002: Engineering-first portfolio readiness stream

- Date: 2026-03-13
- Category: portfolio_execution
- Tags: eval-ops, checkpoints, retries, triage
- Decision: Prioritize eval operations features over additional long-form docs.
- Why: Portfolio evidence quality improves most through shipped behavior + reproducible validation.
- Validation / Evidence links: `main` lineage commits `977a912`, `df78a13`, `488773d` and associated backend/frontend/e2e checks for those merges.
