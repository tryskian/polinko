# Eval V2 Spec (Draft)

## Objective

Define one unambiguous binary eval spec for backend, tooling, and reports.

Binary means:

- one eval record resolves to exactly one outcome (`pass` or `fail`)
- checkpoint aggregates are mutually exclusive and deterministic
- legacy multi-bucket artefacts are retained for reference only

## Non-Goals

- redesigning model prompts
- changing product UX in this draft
- deleting historical evidence artefacts

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
- `other_count = 0` (reserved for future schema-version migration only)

Invariant:

- `pass_count + fail_count + other_count == total_count`

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

These remain append-only operational evidence, not primary runtime truth:

- `docs/portfolio/raw_evidence/INBOX/eval_submissions.jsonl`
- `docs/portfolio/raw_evidence/INBOX/eval_checkpoints.jsonl`
- `docs/portfolio/raw_evidence/INBOX/eval_trace_artifacts.jsonl`

## Legacy Compatibility Spec

Legacy labels (`PASS`, `MIXED`, `FAIL`) are deprecated and non-canonical.

Proposed v2 compatibility mapping for legacy ingestion/reporting:

- `PASS` -> `pass`
- `FAIL` -> `fail`
- `MIXED` -> `fail` with explicit remediation tag (default: `needs_retry`)

Rationale:

- binary gates must fail closed on ambiguity
- mixed quality is diagnostic detail, not a third outcome class

## API Spec Impact

Existing endpoints can remain stable:

- `POST /chats/{session_id}/feedback`
- `POST /chats/{session_id}/feedback/checkpoints`

Required behaviour updates in implementation phase:

1. enforce outcome-driven checkpoint counting
2. maintain current tag validation constraints
3. expose schema/version marker in checkpoint responses for auditability

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

## Acceptance Criteria For Eval V2

1. No runtime path accepts or produces `mixed` as an outcome.
2. Checkpoint arithmetic satisfies invariant for all test fixtures.
3. Existing feedback endpoints remain backwards-compatible at request shape level.
4. `make backend-gate` passes with deterministic quality gate.
5. Legacy artefacts remain readable but do not drive v2 gate decisions.

## Open Decisions (Need Peanut + Beab Sign-Off)

1. Whether legacy `MIXED` should always map to `fail` or be isolated as archival-only rows excluded from aggregates.
2. Whether to add an explicit `spec_version` column to `message_feedback` now or in a follow-up migration.
3. Whether `clip-ab` readiness is informational or release-blocking in v2.
