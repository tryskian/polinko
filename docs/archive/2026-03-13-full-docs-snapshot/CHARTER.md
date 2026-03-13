# Nautorus Charter (Reset Baseline)

## Mission

Build a reliable human-AI collaboration system that is grounded, testable, and easy to iterate.

## Operating Rules

1. Human sets intent and constraints; implementation follows measured outcomes.
2. Safety and grounding constraints are hard boundaries.
3. Style adaptation is soft and evidence-driven.
4. Every meaningful change must be validated by automated checks.
5. `main` remains the trusted release line (PR + required checks).

## Engineering Principles

- Prefer small, reversible slices over broad rewrites.
- Keep runtime behavior deterministic where possible.
- Capture evidence continuously (tests, eval reports, and checkpoints).
- Preserve continuity via `docs/STATE.md` and `docs/SESSION_HANDOFF.md`.

## In Scope (Current)

- Eval operations workflow in UI (checkpoints, retries, review queue).
- Hallucination/grounding guardrails and regression cases.
- OCR ambiguity/recovery evaluation pipeline.

## Out of Scope (Current)

- Large architecture rewrites unrelated to active eval operations.
- Production cloud migration execution (planning can continue).
