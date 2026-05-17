<!-- @format -->

# Polinko Charter

## Mission

Build a human-led, repo-native research system for inspecting AI behavior
through fail-first evaluation, grounding, co-reasoning, operator burden, and
evidence-preserving method work.

## Durable Rules

- Backend-first runtime is canonical:
  - FastAPI API + CLI are the execution surfaces
  - presentation layers stay aligned with backend and eval policy
- Treat the repository as the research object:
  - tracked docs, code, tests, and reports are canonical truth
  - public-facing writing is the derived publication layer from repo truth
  - local/private lanes stay local, with explicit approval for any wider scope
- The public website is a doorway into the research system:
  - `GET /` redirects to `GET /portfolio`
  - the public surface points into the work
- Eval semantics stay scoped:
  - OCR case outcomes are `pass` / `fail`
  - broader manual and non-OCR lanes may still use `retain` / `evict` after
    `fail` as upstream case curation
  - `retain` keeps that broader failure pressure as active evidence
  - `evict` removes malformed or stale cases upstream
- Failure is primary signal:
  - pass-rate reporting keeps unresolved failure pressure visible
- Prefer deterministic, testable changes.
- Fail fast on config, auth, and runtime issues.
- Inspect evidence before interpretation.
- Preserve evidence chains:
  - archive before delete
  - keep summaries anchored to raw evidence

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
  - Git and PR flow
  - proactive hygiene
  - execution recommendations
- OpenAI Codex is the primary repo-local coding agent and engineering
  collaborator.
- Default execution model:
  - one feature branch per change set
  - protected-main PR flow
  - clean synced `main` as the tracked stop state
- Parallelism rule:
  - worktrees for parallel code changes
  - multi-agent only after architecture and acceptance criteria are explicit

## Documentation Governance

- `docs/governance/DECISIONS.md`
  - append-only durable decisions
- `docs/governance/STATE.md`
  - tracked current truth
- `docs/runtime/RUNBOOK.md`
  - operator procedure
- `docs/runtime/ARCHITECTURE.md`
  - stable system shape
- `docs/research/`
  - curated tracked research notes
- `docs/peanut/`
  - local-only exploration lane

## Current Scope

- Local-first backend and runtime work
- Fail-first eval hardening across lanes
- Co-reasoning reliability
- Operator burden measurement
- Repo-native evidence and reporting surfaces
- Lean public doorway pointing into the repo
- Public site focus:
  - single clear doorway
  - stable identity surface
  - direct path into the repo and research docs

## Security / Ops Baseline

- `OPENAI_API_KEY` is required at startup.
- Localhost runtime is the trusted development boundary.
- `/chat` remains rate-limited.
- Run `make doctor-env` when the environment looks suspicious.
