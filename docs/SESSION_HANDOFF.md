<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-27

## Current Snapshot

- Runtime is local-first: FastAPI backend + CLI runner are canonical; web UI is deprecated for active operations.
- Prompt/runtime behaviour stays minimal and aligned with the original `try.py` style.
- Eval contract is strict binary end-to-end:
  - feedback outcomes: `pass` or `fail` only
  - checkpoint schema field: `non_binary_count` (integrity signal, expected `0`)
  - previous `tags`-only feedback payload compatibility removed
- Previous normalisation tooling was removed from active flow:
  - deleted `tools/normalize_feedback_outcomes.py`
  - removed `make eval-feedback-normalize`
- Git history is the canonical archive for tracked docs/code; local eval artefact
  folders are operational outputs only and are not part of release truth.
- Human-reference flow remains offline/query-first:
  - rebuild: `make human-reference-db`
  - queries: `make human-reference-latest|transcripts|changes|relationships`
- Engineer execution mode is proactive by default:
  - technical hygiene/drift control should be handled without reminder
  - user input is only needed for approvals or material trade-offs
- Co-reasoning governance mode is human-managed:
  - human controls objective/scope/acceptance and go/no-go decisions
  - engineer executes proactively within that control frame

## Latest Branch Context

- Active implementation branch:
  - `main`
- Canonical repo path:
  - `/Users/tryskian/Github/polinko`

## Key Files To Read First

- `docs/CHARTER.md`
- `docs/STATE.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/RUNBOOK.md`
- `api/app_factory.py`
- `core/history_store.py`
- `tests/test_api.py`

## Quick Validation (Local)

1. `make doctor-env`
2. `make lint-docs`
3. `make test`
4. `make quality-gate-deterministic`
5. optional archive-maintenance checks only:
   - `npm --prefix frontend run -s test`
   - `npm --prefix frontend run -s build`

## Known Constraints

- Network-dependent model calls can fail in restricted environments.
- Cloud deployment automation remains paused; local-first execution is canonical.
- Environment mutation policy:
  - verify repo path + mode + branch before changes
  - prefer repo-scoped edits
  - do not modify `~/.zshrc` or global VS Code settings without explicit in-chat approval
- Keep-awake (`caffeinate`) remains opt-in/request-triggered.

## Immediate Next Step

- Finish binary hard-cutover validation and merge flow:
  - run full backend validation
  - open PR from `codex/bigbrain/app-beta-refactor`
  - merge after checks pass
  - close with governance-surface sync when policy/flow changes
  - ensure loop framing is explicit (objective/scope/acceptance) before each
    new implementation slice

## Peanut Pin (Tomorrow Start)

- Start from strict binary contract as baseline (`pass`/`fail` only).
- Review latest eval outputs and prioritise one deterministic backend slice.
- Update `STATE` + `DECISIONS` + `SESSION_HANDOFF` only with material deltas.

## Copy/Paste Rehydrate Prompt

`Read docs/CHARTER.md, docs/ARCHITECTURE.md, docs/RUNBOOK.md, docs/STATE.md, docs/DECISIONS.md, and docs/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, and confirm active git branch. Apply no-guessing controls: prefer repo-scoped edits and do not modify ~/.zshrc or global VS Code settings unless explicitly approved in-chat. Run in proactive engineer mode: execute obvious hygiene/cleanup/validation work without waiting for reminders, and ask only when approvals/trade-offs require it. Apply human-managed co-reasoning control: confirm objective/scope/acceptance and keep go/no-go decisions human-led. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behaviour drift and full test/build validation.`
