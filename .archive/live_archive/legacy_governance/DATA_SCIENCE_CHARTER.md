# Data Science Charter (Canonical)

## Purpose

Task logic for `sciencebeab`: deliver a visual-forward, local-only data
workflow that keeps outcomes intuitive for imagineer use while preserving
deterministic backend reliability.

Design reference direction:

- dashboard clarity similar to Looker Studio / Flourish interaction patterns
  (readable charts, fast filtering, insight-first summaries)
- implementation remains fully local (no hosted platform dependency)
- Looker Studio / Flourish are reference paradigms only, not allowed execution
  surfaces in this project
- tuned for near-real-time eval updates and insight generation from active run
  outputs

## Required Inputs Per Kernel

- `objective`: one active outcome to deliver
- `constraints`: hard boundaries (for example local-only, binary gates)
- `acceptance`: concrete checks to pass
- `examples`: high-signal examples (optional but preferred)

## Execution Loop

1. Lock one kernel objective.
2. Implement minimal scoped changes.
3. Validate against acceptance checks:
   - touched-file type/lint checks pass
   - relevant tests pass
   - deterministic quality gate passes when behavioural paths are touched
   - doc-referenced commands are executable as written
4. Integrate governance updates per rules below.
5. Report a concise checkpoint:
   - objective delivered
   - what changed
   - validation evidence
   - residual risk
   - recommended next kernel

Queue non-blocking follow-ups; do not switch objective mid-kernel.

## Governance Integration Rules

Update `DECISIONS` when:

- a durable policy/threshold/operating rule changes.

Update `STATE` when:

- active runtime/eval/tooling truth changes.

Update `SESSION_HANDOFF` when:

- next-session execution context or immediate next step changes.

Update `CHARTER` only when:

- mission, permanent principles, or scope boundaries change.

Remove stale statements that conflict with current truth.
