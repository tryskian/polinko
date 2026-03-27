# Minimal Config Benchmark Spec

## Objective

Validate the hypothesis that minimal configuration produces better product outcomes than configuration-heavy setups, while preserving policy safety.

## Primary Hypothesis

`H-001`: Minimal control surfaces outperform configuration-heavy workflows on quality, operator clarity, iteration speed, and maintenance overhead.

## Comparison Phases

1. Baseline A: Minimal-config CLI benchmark
- Scope: early CLI behaviour with low configuration complexity.
- Purpose: establish reference behaviour and workflow simplicity.

2. Baseline B: Traditional eval benchmark
- Scope: pre-binary eval structure and legacy gate complexity.
- Purpose: measure cost/benefit of richer but heavier eval wiring.

3. Baseline C: Binary eval benchmark (current)
- Scope: fail-closed pass/fail gate with policy-dominant logic.
- Purpose: measure clarity and execution efficiency after simplification.

## Controlled Variables

- Keep evaluation tasks/prompt sets equivalent across phases.
- Keep model/runtime configuration as stable as practical.
- Keep judgement criteria explicit and documented.
- Record deviations from control conditions as confounders.

## Evaluation Dimensions

1. Quality outcomes
- Gate pass rate on matched cases.
- Failure type distribution.

2. Decision clarity
- Ambiguity in release decision path.
- Time to determine go/no-go.

3. Iteration speed
- Time from issue detection to validated fix.
- Number of steps/tools required per cycle.

4. Maintenance overhead
- Active surface area (scripts/docs/paths to maintain).
- Frequency of artifact/gremlin cleanup.

## Evidence Mapping

- A: CLI/minimal-config artifacts and transcript evidence.
- B: Traditional eval reports and associated legacy records.
- C: Binary eval reports, current gate logs, and deterministic checks.
- Canonical binary docs:
  - `docs/EVAL_POLICY_MODEL.md`
  - `docs/EVAL_SPEC.md`
  - `docs/EVAL_BACKEND_MAP.md`

## Evidence Matrix

| Benchmark | Experiment Record | Core Evidence | Status |
| --- | --- | --- | --- |
| A: Minimal-config CLI | `docs/research/experiment_R-A_minimal_config_cli_2026-03-27.md` | CLI baseline transcripts + early eval artifacts | Planned |
| B: Traditional eval stack | `docs/research/experiment_R-B_traditional_eval_stack_2026-03-27.md` | Legacy/traditional eval reports and decision records | Planned |
| C: Binary eval stack | `docs/research/experiment_R-C_binary_eval_stack_2026-03-27.md` | Current binary eval reports + deterministic gate checks | Planned |

## Output Contract

For each benchmark phase, produce:
- one experiment record
- linked artifact paths
- pass/fail interpretation against `H-001`
- one next-action decision (`keep`, `adjust`, or `retire`)

## Product-First Guardrails

- Product delivery remains the primary track.
- Benchmarking must support implementation decisions, not replace them.
- New theory threads can be queued, but not expanded into runtime scope before product milestones are met.

## Exit Criteria

This benchmark is complete when:
- all three phases are documented with comparable evidence,
- confounders are declared,
- and `H-001` has a clear provisional verdict with next steps.
