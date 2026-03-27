# Legacy Eval Reference

This lane stores legacy eval context for inspection only.

## What belongs here

- Deprecated eval-record structures that are not part of active release gates.
- Historical notes about previous non-binary logic/wiring.
- Legacy operator flows preserved only for traceability.
- Legacy helper scripts (archived, not run):
  - `docs/live_archive/legacy_eval/cleanup_eval_chats.py`

## What does not belong here

- Active gate contracts.
- Runtime wiring used by `core/history_store.py`.
- Any artefact used as authoritative release evidence.

## Active baseline

- Binary outcomes only: `pass` or `fail`.
- Policy and high-value alignment drive gate outcomes.
- Active implementation/docs:
  - `docs/EVAL_POLICY_MODEL.md`
  - `docs/EVAL_SPEC.md`
  - `docs/EVAL_BACKEND_MAP.md`
