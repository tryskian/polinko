<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-26

## Current Snapshot

- Runtime is local-first: FastAPI backend + Vite frontend + CLI runner.
- Prompt/runtime behaviour stays minimal and aligned with the original `try.py` style.
- Eval contract is strict binary end-to-end:
  - feedback outcomes: `pass` or `fail` only
  - checkpoint schema field: `non_binary_count` (integrity signal, expected `0`)
  - legacy `tags`-only feedback payload compatibility removed
- Legacy normalisation tooling was removed from active flow:
  - deleted `tools/normalize_feedback_outcomes.py`
  - removed `make eval-feedback-normalize`
- Active evidence intake remains `PASS` / `FAIL` / `INBOX`; archive-only structures do not drive runtime gates.
- Human-reference flow remains offline/query-first:
  - rebuild: `make human-reference-db`
  - queries: `make human-reference-latest|transcripts|changes|relationships`

## Latest Branch Context

- Active implementation branch:
  - `codex/bigbrain/eval-binary-hard-cutover-20260326`
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
- `frontend/src/eval-rubric.js`
- `tests/test_api.py`

## Quick Validation (Local)

1. `make doctor-env`
2. `make lint-docs`
3. `make test`
4. `npm --prefix frontend run -s test`
5. `npm --prefix frontend run -s build`

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
  - run full backend/frontend validation
  - open PR from `codex/bigbrain/eval-binary-hard-cutover-20260326`
  - merge after checks pass

## Peanut Pin (Tomorrow Start)

- Start from strict binary contract as baseline (`pass`/`fail` only).
- Review latest eval outputs and prioritise one deterministic backend slice.
- Update `STATE` + `DECISIONS` + `SESSION_HANDOFF` only with material deltas.

## Copy/Paste Rehydrate Prompt

`Read docs/CHARTER.md, docs/ARCHITECTURE.md, docs/RUNBOOK.md, docs/STATE.md, docs/DECISIONS.md, and docs/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, and confirm active git branch. Apply no-guessing controls: prefer repo-scoped edits and do not modify ~/.zshrc or global VS Code settings unless explicitly approved in-chat. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behaviour drift and full test/build validation.`
