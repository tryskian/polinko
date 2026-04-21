<!-- @format -->

# Polinko Charter

## Mission

Build a human-led, AI-assisted research system for evaluating human-AI
interaction, OCR reliability, and failure signals through inspectable software,
tests, diagrams, and evidence.

## Durable Rules

- Backend-first runtime is canonical:
  - FastAPI API + CLI are the execution surfaces.
  - presentation layers must not redefine eval policy.
- Treat the repository as the research object:
  - tracked docs/code/tests/evals remain canonical
  - public-facing docs are derived views, not replacements
  - local/private lanes stay local unless explicitly approved for publication
- The public website is a doorway, not the research system:
  - `GET /` redirects to `GET /portfolio`
  - the site should point into the repo/work, not recreate it
- Eval semantics remain strictly binary:
  - `pass`/`fail` only
  - lockset lane is release-gating
  - growth lane is fail-tolerant and signal-seeking
- Prefer deterministic, testable changes.
- Fail fast on config/auth/runtime issues.
- Keep one canonical command surface per operator action.
- Inspect evidence before interpretation:
  - source files, logs, screenshots, transcripts, and reports win over summary
  - if a named source has not been inspected, do not speak as if it has
- Preserve evidence chains:
  - do not replace raw evidence with recursive summaries
  - archive before delete

## Working Model

- Human lead owns:
  - hypotheses
  - scope boundaries
  - acceptance criteria
  - meaning-level trade-offs
  - go/no-go decisions
- Engineer owns:
  - implementation
  - validation
  - Git/branch/PR flow
  - proactive hygiene/drift cleanup
  - execution recommendations
- Default execution model:
  - feature branch per change set
  - protected-main PR flow
  - end-of-day finishes merged and clean on `main`
- Parallelism rule:
  - worktrees for parallel code changes
  - multi-agent only after architecture and acceptance criteria are explicit

## Documentation Governance

- `docs/governance/DECISIONS.md`
  - append-only durable decisions
  - process, engineering/tooling, runtime/API, dependency/workflow, and eval
    governance only
- `docs/governance/STATE.md`
  - current truth
  - no daily logs
- `docs/governance/SESSION_HANDOFF.md`
  - next-session operating context
  - current only
- `docs/runtime/RUNBOOK.md`
  - procedures and command ownership
- `docs/runtime/ARCHITECTURE.md`
  - stable system shape and contracts
- `docs/peanut/`
  - local-only exploration lane for transcripts, design refs, theory, and
    working notes

## Current Scope

- In scope:
  - local-first backend/runtime work
  - OCR-forward eval hardening
  - repo-native evidence/reporting surfaces
  - lean public doorway pointing into the repo
  - static D3/SVG evidence diagrams beside Mermaid when added
- Out of scope for the public site right now:
  - full portfolio rebuild
  - animation-first exploration
  - interactive evidence dashboards as a portfolio burden
  - presentation-layer changes that alter backend/eval contracts

## Security / Ops Baseline

- `OPENAI_API_KEY` is required at startup.
- Localhost runtime is the trusted development boundary.
- `/chat` remains rate-limited.
- Run `make doctor-env` when the environment looks suspicious.
