<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-26

## Current Snapshot

- Runtime remains local-first: FastAPI backend + Vite frontend + CLI runner.
- Prompt/runtime behaviour is intentionally minimal and aligned to legacy `try.py` style.
- Eval feedback/checkpoint write contract is now binary-first (`pass`/`fail`).
- Legacy stored outcomes are still readable; API/UI normalise non-`pass` values to `fail`.
- Backend eval paths were refreshed on `main` (PR `#71`) and include:
  - stricter outcome normalisation (`pass`/`fail` only on write)
  - stream-summary checkpoint aggregation helper
  - API regression coverage updates in `tests/test_api.py`
- Frontend eval UX remains aligned to binary gate flow and includes base eval prompt presets.
- Human-reference flow is simplified to offline/query-first:
  - rebuild: `make human-reference-db`
  - query presets: `make human-reference-latest|transcripts|changes|relationships`
  - relationship semantics are FK-backed in `.human_reference.db`.
- Legacy local portfolio docs were archived out of active root paths:
  - `docs/portfolio/archive/2026-03-25-legacy-positioning-workbench`
- Active raw-evidence intake is binary-first:
  - keep `PASS`/`FAIL`/`INBOX` active
  - keep `MIXED` and trace-artifact intake as archive-only legacy
- Docs confidentiality + legacy cleanup is merged on `main` (PR `#72`):
  - local-only internal docs policy enforced in runbook + ignore rules
  - legacy tracked transcript de-tracked and kept local
  - end-of-day docs are aligned for clean next-session startup
- OpenAI developer docs MCP is configured for local workflows:
  - endpoint: `https://developers.openai.com/mcp`
  - workspace config: `.vscode/mcp.json`
- Active operating mode stays deterministic and local-first:
  - implementation in repo
  - validation via local test/build gates
  - docs as the handoff source of truth
- Inspect-first collaboration mode is active (March 26, 2026):
  - pause and inspect when context is noisy/ambiguous
  - preserve legacy context (including MCP/server wiring) until explicit
    migration cutline
  - execute directed precision slices; avoid out-of-scope cleanup
- Build block audit guardrail is now active (March 26, 2026):
  - README refreshed to current build/API blocks
  - `make build-audit` added for repeatable drift checks
  - local markdown lint now matches CI scope (`README.md` + `docs/**/*.md`)
  - `eval-cleanup` now degrades safely when local-only helper is absent

## Latest Local Commit

- `031380e` (merge commit on `main`)
- PR: `#74` (`codex/bigbrain/housekeeping-docs-local-tracking-20260326`)
- Core outcome:
  - docs and local-only tracking policy are merged on `main`
  - branch-protected PR flow remains the canonical merge path
  - housekeeping baseline is clean for block-by-block audit execution

## Key Files To Read First

- `docs/CHARTER.md`
- `docs/STATE.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/RUNBOOK.md`
- `api/app_factory.py`
- `tests/test_api.py`
- `docs/HUMAN_REFERENCE_DB.md`

## Quick Validation (Local)

1. `make doctor-env`
2. `make lint-docs`
3. `make build-audit`
4. `make test`
5. `npm --prefix frontend run -s test`
6. `npm --prefix frontend run -s build`
7. `make human-reference-db`
8. `make human-reference-relationships`

## Known Constraints

- Network-dependent model calls can fail in restricted environments.
- Cloud deployment automation remains intentionally paused; local-first execution is canonical.
- Environment mutation policy is strict:
  - verify repo path + mode + branch before changes
  - prefer repo-scoped edits
  - do not modify `~/.zshrc` or global VS Code settings without explicit in-chat approval
- Keep-awake (`caffeinate`) remains opt-in/request-triggered.
- Legacy context is not auto-pruned:
  - do not remove legacy MCP/server wiring unless explicitly directed in-chat.

## Immediate Next Step

- Start eval-v2 refactor planning with a no-artifact baseline:
  - define the target binary eval data contract and aggregation semantics
  - preserve legacy rows as read-only compatibility input
  - map minimal API/UI changes needed for the first v2 slice
  - run full local validation after the first implementation slice

## Peanut Pin (Tomorrow Start)

- First, lock the eval-v2 shape in plain terms:
  - one clear pass/fail outcome
  - legacy rows still readable, but not driving new behaviour
- Then ship one small backend slice for that contract (no big-bang rewrite).
- Then align the UI to that slice and run full local checks before moving on.

## Next Session Focus (Lean Agenda)

1. Lock eval-v2 contract and migration boundaries (binary-first, legacy-read compatible).
2. Implement one backend slice with minimal behaviour drift.
3. Align frontend eval UI/state with the new backend slice.
4. Re-run local validation gates and archive fresh evidence.
5. Update `STATE` + `DECISIONS` + `SESSION_HANDOFF` with only material deltas.

## Copy/Paste Rehydrate Prompt

`Read docs/CHARTER.md, docs/ARCHITECTURE.md, docs/RUNBOOK.md, docs/STATE.md, docs/DECISIONS.md, and docs/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, and confirm active git branch. Apply no-guessing controls: prefer repo-scoped edits and do not modify ~/.zshrc or global VS Code settings unless explicitly approved in-chat. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behaviour drift and full test/build validation.`
