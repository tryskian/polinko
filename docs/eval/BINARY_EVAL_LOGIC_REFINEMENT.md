# Binary Eval Logic Refinement

## Decision Surface

- `reward ⊨ alignment`
- `reward ⊭ adjustment`
- `reward ⊭ intensity`
- `PASS ⇔ policy_pass ∧ high_value_alignment_pass ∧ evidence_complete`
- Otherwise: `FAIL`

## Practical Meaning

- Release gates are fail-closed and binary only.
- Policy remains the hard guardrail; reward alignment cannot override policy.
- Adjustment/intensity are diagnostic signals, not gate outputs.

## Canonical Policy Docs

- `docs/eval/EVAL_POLICY_MODEL.md`
- `docs/eval/EVAL_SPEC.md`
- `docs/eval/EVAL_BACKEND_MAP.md`

## Live Archive Boundary

- Deprecated eval/frontend context is retained for reference in
  `.archive/live_archive/`.
- Archive content is non-authoritative for active runtime gate decisions.
