# Eval Policy Model

## Purpose

This document defines the canonical concept model for release-grade eval
decisions:

- binary output only (`PASS`/`FAIL`)
- fail-closed behaviour
- policy constraints dominate reward signals
- high-value eval cases only

## Symbol Legend

- `⊨` means semantic entailment / satisfies
- `⊭` means does not semantically entail
- `∧` means logical AND
- `⇔` means if and only if

## Core Semantics

- `reward ⊨ alignment`
- `reward ⊭ adjustment`
- `reward ⊭ intensity`
- `policy_fail ⊨ final_fail`

Interpretation:

- reward evidence may support alignment claims
- reward must never be treated as a dial for adjustment/intensity
- policy failures always force a `FAIL`, regardless of reward

## Canonical Gate Rule

`PASS ⇔ policy_pass ∧ high_value_alignment_pass ∧ evidence_complete`

Otherwise: `FAIL`

No spectrum labels (`MIXED`, `PARTIAL`, `SOFT PASS`) are valid gate outputs.

## High-Value-Only Constraint

Only eval cases that can change release decisions belong in the active gate.

In-scope domains:

- safety/policy adherence
- grounding and factual integrity
- retrieval correctness
- collaboration/style trust signals

Out-of-scope cases can remain in research diagnostics, but not in release gate
computation.

## Conceptual ER Diagram

```mermaid
erDiagram
    EVAL_POLICY ||--o{ POLICY_RULE : contains
    EVAL_SUITE ||--o{ EVAL_CASE : includes
    EVAL_RUN ||--o{ CASE_RESULT : records
    EVAL_CASE ||--o{ CASE_RESULT : evaluated_in
    EVAL_RUN ||--o{ POLICY_CHECK : enforces
    POLICY_RULE ||--o{ POLICY_CHECK : checked_by
    EVAL_RUN ||--|| RUN_DECISION : yields

    EVAL_POLICY {
      string policy_id
      string name
      string version
    }
    POLICY_RULE {
      string rule_id
      string policy_id
      string rule_type
      bool hard_fail
    }
    EVAL_SUITE {
      string suite_id
      string name
      string risk_domain
      bool active
    }
    EVAL_CASE {
      string case_id
      string suite_id
      string risk_type
      int value_weight
      bool release_blocking
    }
    EVAL_RUN {
      string run_id
      string model
      datetime created_at
    }
    CASE_RESULT {
      string result_id
      string run_id
      string case_id
      bool passed
      float reward
    }
    POLICY_CHECK {
      string check_id
      string run_id
      string rule_id
      bool passed
    }
    RUN_DECISION {
      string run_id
      bool reward_passed
      bool policy_passed
      string final_decision
    }
```

