# Decisions Ledger

## Entry Format

- ID: `L-###`
- Date
- Category
- Tags
- Decision
- Why
- Validation / Evidence links

## L-001: Freeze Polinko and reboot Nautorus main

- Date: 2026-03-13
- Category: governance
- Tags: reset, archive, trunk, migration
- Decision: Freeze legacy Polinko in immutable snapshot refs and reset
  `main` to a fresh Nautorus scaffold.
- Why: Continuing to patch the legacy system created excess risk and
  slowed delivery velocity.
- Validation / Evidence links: archive refs
  (`archive/polinko-full-build-2026-03-13`,
  `polinko-build-frozen-2026-03-13`) and scaffold reset PR.

## L-002: Keep CI minimal but mandatory on scaffold

- Date: 2026-03-13
- Category: quality
- Tags: ci, test, markdownlint, baseline
- Decision: Maintain required `markdownlint` and `test` checks on the
  fresh scaffold from day one.
- Why: Preserves disciplined merge hygiene while implementation is rebuilt incrementally.
- Validation / Evidence links: `.github/workflows/ci.yml` and passing
  checks on scaffold PR.

## L-003: Freeze Polinko frontend and rebuild UI in OpenAI ecosystem

- Date: 2026-03-13
- Category: architecture
- Tags: frontend, archive, openai-ecosystem, reset
- Decision: Keep the Polinko `frontend/` as archived history and do not
  patch it further on Nautorus `main`.
- Why: Prior integration attempts with the native OpenAI Agent app path
  caused high patch churn; rebuilding cleanly in OpenAI-native workflows
  reduces migration risk and complexity.
- Validation / Evidence links: `archive/polinko-frontend-2026-03-13`,
  `polinko-frontend-frozen-2026-03-13`, and this PR.
