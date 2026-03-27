# Eval Spec

## Objective

Define one unambiguous binary eval spec for backend, tooling, and reports.

Wiring-phase source-of-truth:

- `docs/EVAL_WIRING_SPEC.md` (gate topology and phase policy)

Binary means:

- one eval record resolves to exactly one outcome (`pass` or `fail`)
- checkpoint aggregates are mutually exclusive and deterministic
- active file artefacts are local operational outputs; retention is Git-native

## Non-Goals

- redesigning model prompts
- changing product UX in this draft
- deleting historical evidence artefacts
- provisioning fresh runtime DB files before wiring sign-off

## Canonical Outcome Model

### Allowed outcomes

- `pass`
- `fail`

### Outcome ownership

- `outcome` is canonical and final for checkpoint arithmetic
- reason tags provide diagnostics only
- reason tags must not override or duplicate outcome counting

### Reason tags

Positive reason tags:

- quality/execution strengths (`accurate`, `grounded`, `high_value`, etc.)

Negative reason tags:

- defect/risk reasons (`ocr_miss`, `hallucination_risk`, etc.)

Rules:

1. `pass` requires at least one positive reason tag.
2. `fail` requires at least one negative reason tag.
3. `fail` may include positive reason tags for partial quality signal.
4. checkpoint pass/fail counts are derived from `outcome` only.

## Canonical Checkpoint Arithmetic

Given `N` feedback entries in scope:

- `total_count = N`
- `pass_count = count(outcome == "pass")`
- `fail_count = count(outcome == "fail")`
- `non_binary_count = 0` for valid datasets (non-zero is a data-integrity violation)

Invariant:

- `pass_count + fail_count + non_binary_count == total_count`

This replaces v1 dual-stream tag counting.

## Storage Spec

### SQLite (authoritative runtime store)

- `message_feedback` remains the canonical row store for per-message eval.
- `eval_checkpoints` remains canonical for checkpoint summaries.

Required row fields (logical spec):

- `session_id`
- `message_id`
- `outcome` (`pass`|`fail`)
- `positive_tags[]`
- `negative_tags[]`
- `status` (`closed` for pass, `open` for fail)
- timestamps

### File artefacts (append-only evidence)

These remain append-only local evidence outputs, not primary runtime truth:

- `eval_reports/eval_trace_artifacts.jsonl`
- optional local submission/checkpoint JSONL snapshots under `eval_reports/*`

## API Spec Impact

Existing endpoints can remain stable:

- `POST /chats/{session_id}/feedback`
- `POST /chats/{session_id}/feedback/checkpoints`

Required behaviour updates in implementation phase:

1. enforce outcome-driven checkpoint counting
2. maintain current tag validation constraints
3. expose schema/version marker in checkpoint responses for auditability
4. do not accept legacy `tags`-only payloads; require `positive_tags`/`negative_tags`

## Eval Harness Spec

All eval tools must emit report payloads that can be reduced to binary gate outcomes:

- retrieval
- file-search
- OCR
- style
- hallucination
- clip-ab readiness (if used as gate)

Each harness output should resolve to:

- `suite_name`
- `run_id`
- `passed` (boolean)
- `failed_cases`
- `summary`

Case-level report rows should include:

- `status` (suite-local execution status)
- `gate_outcome` (`pass` or `fail`, fail-closed)
- `gate_reasons[]` (gate diagnostics)

Summary payloads should include:

- `gate_passed`
- `gate_failed`

## Acceptance Criteria

1. No runtime path accepts or produces `mixed` as an outcome.
2. Checkpoint arithmetic satisfies invariant for all test fixtures.
3. Existing feedback endpoints reject non-binary payloads at write time.
4. `make backend-gate` passes with deterministic quality gate.
5. Archived artefacts never drive active gate decisions.

## Open Decisions (Need Peanut + Beab Sign-Off)

1. Whether to add an explicit `spec_version` column to `message_feedback` now or in a follow-up migration.
2. Whether `clip-ab` readiness is informational or release-blocking.
