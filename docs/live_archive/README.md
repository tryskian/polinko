# Live Archive

This is the active reference surface for deprecated implementation context.

## Purpose

- Keep legacy context visible for inspection.
- Keep legacy context out of active runtime/eval execution.
- Provide one predictable place for historical implementation references.

## Lanes

- `legacy_eval/`: previous eval records/logic patterns that are no longer authoritative.
- `legacy_frontend/`: archived UI context retained only for reference.

## Usage Rules

- Reference-only: do not wire anything in this folder into active runtime gates.
- Active contracts remain binary (`pass`/`fail`) and backend-first.
- If an item is moved here, update `docs/DECISIONS.md` and `docs/STATE.md`.

## Canonical Active Sources

- Eval policy: `docs/EVAL_POLICY_MODEL.md`
- Eval API/storage contract: `docs/EVAL_SPEC.md`
- Runtime architecture: `docs/ARCHITECTURE.md`
