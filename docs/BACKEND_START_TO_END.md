# Backend Start-to-End Flow

Purpose: run the backend from first principles in a fixed order so we can keep
iterating without resetting the repo.

## One Command

```bash
make backend-gate
```

This executes the full backend baseline in order:

1. `make doctor-env`
2. `make build-audit`
3. `make test`
4. `make quality-gate-deterministic`

## Why This Order

1. `doctor-env` checks local runtime health first.
2. `build-audit` catches contract drift before runtime-heavy checks.
3. `test` validates backend code paths quickly.
4. `quality-gate-deterministic` validates end-to-end backend behaviour with
   deterministic eval gating.

## What Each Stage Verifies

## 1) Environment

- Python interpreter selection and import availability.
- Basic local shell safety (`compaudit`) and runtime readiness.

## 2) Build Contracts

- README API surface matches live FastAPI routes.
- Makefile tool targets resolve to real modules.
- Local markdown lint scope matches CI scope.
- Local-only eval cleanup behaviour is explicitly guarded.

## 3) Backend Regression

- Unit/integration tests across API, runtime, retrieval, eval persistence, and
  personalization/collaboration surfaces.

## 4) Deterministic End-to-End Quality

- retrieval eval
- file-search eval
- OCR strict eval
- style strict eval
- hallucination strict eval (deterministic mode)

## Optional Extensions

Use these after `backend-gate` when needed:

```bash
make evidence-refresh
make human-reference-db
make human-reference-latest
make docker-build
```

## Failure Handling Rule

If any stage fails:

1. fix the failing stage only
2. re-run from that stage
3. run full `make backend-gate` again before moving forward

This keeps the debugging surface small and prevents layered drift.
