<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-26

## Current Snapshot

- Runtime remains local-first: FastAPI backend + Vite frontend + CLI runner.
- Prompt/runtime behaviour is intentionally minimal and aligned to legacy `try.py` style.
- Eval feedback/checkpoint write contract is now binary-first (`pass`/`fail`).
- Legacy stored outcomes are still readable; API/UI normalise non-`pass` values to `fail`.
- Eval-v2 backend hardening slice is implemented on a branch and pending merge:
  - branch: `codex/bigbrain/eval-v2-backend-map-20260326`
  - commit: `7a2af33`
  - outcome:
    - checkpoint submit now fail-closes (`409`) when non-binary outcomes exist
    - explicit legacy normalisation utility added
      (`python -m tools.normalize_feedback_outcomes` /
      `make eval-feedback-normalize`)
    - validation passed on the slice (`107` targeted tests, `167` full-suite tests)
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
- Legacy eval intake structure is archived from active tooling (March 26, 2026):
  - `make evidence-index` now reads active buckets only
    (`PASS`/`FAIL`/`INBOX`)
  - operator-facing checkpoint copy uses `non_binary` language for blocked
    rows; no active UI label uses legacy `other` naming
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
- Reasoning Loops collaboration model is now explicit (March 26, 2026):
  - this is the canonical term for human-AI collaboration in this project
  - imagineer leads hypothesis/theory framing + eval operation
  - engineer leads implementation/tooling/validation + execution recommendations
- Build block audit guardrail is now active (March 26, 2026):
  - README refreshed to current build/API blocks
  - `make build-audit` added for repeatable drift checks
  - local markdown lint now matches CI scope (`README.md` + `docs/**/*.md`)
  - `eval-cleanup` now degrades safely when local-only helper is absent

## Latest Local Commit

- `63c713c` on `main` (local docs baseline at session start)
- Active implementation branch pending merge:
  - `codex/bigbrain/eval-v2-backend-map-20260326` @ `7a2af33`
- Core outcome:
  - docs + operating policy remain aligned on `main`
  - eval-v2 fail-closed checkpointing + legacy normalisation tooling are ready
    in branch for PR/merge

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

- Merge the completed eval-v2 backend hardening slice, then run one post-merge
  validation cycle:
  - merge branch `codex/bigbrain/eval-v2-backend-map-20260326` (`7a2af33`)
  - run `make test`
  - run `make quality-gate`
  - if legacy non-binary rows exist, run `make eval-feedback-normalize`

## Peanut Pin (Tomorrow Start)

- First, merge the ready backend slice that enforces fail-closed binary
  checkpointing.
- Then run one clean validation pass on `main`.
- Then continue backend map block-by-block (next smallest deterministic slice).

## Next Session Focus (Lean Agenda)

1. Merge eval-v2 fail-closed backend slice and verify on `main`.
2. Confirm legacy outcome migration path with `eval-feedback-normalize` where needed.
3. Continue backend mapping with one additional small deterministic slice.
4. Re-run local validation gates and archive fresh evidence.
5. Update `STATE` + `DECISIONS` + `SESSION_HANDOFF` with only material deltas.

## Copy/Paste Rehydrate Prompt

`Read docs/CHARTER.md, docs/ARCHITECTURE.md, docs/RUNBOOK.md, docs/STATE.md, docs/DECISIONS.md, and docs/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, and confirm active git branch. Apply no-guessing controls: prefer repo-scoped edits and do not modify ~/.zshrc or global VS Code settings unless explicitly approved in-chat. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behaviour drift and full test/build validation.`
