<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-29

## Current Snapshot

- Runtime is local-first: FastAPI backend + CLI runner are canonical; web UI is
  archived from the active repository surface.
- `POST /chat` now supports deterministic harness testing for UI smoke:
  - request override: `harness_mode=fixture`
  - optional fixed output: `fixture_output`
  - env default: `POLINKO_CHAT_HARNESS_DEFAULT_MODE=live|fixture`
  - default remains `live` (no behaviour drift for normal runtime)
- Canonical UI eval adapter contract is published:
  - `docs/eval/UI_EVAL_ADAPTER_CONTRACT.md`
  - includes TypeScript request/response shapes + chat/eval/checkpoint flow
- Local UI shell is retired from active runtime surface:
  - no `GET /ui` route
  - no active `ui/index.html` file
  - fixture controls remain available through `POST /chat` request fields
- Prompt/runtime behaviour stays minimal and aligned with the original `try.py` style.
- Eval contract is strict binary end-to-end:
  - feedback outcomes: `pass` or `fail` only
  - checkpoint schema field: `non_binary_count` (integrity signal, expected `0`)
  - checkpoint response field: `gate_outcome` (`pass`/`fail`, fail-closed from counts)
  - previous `tags`-only feedback payload compatibility removed
- Previous normalisation tooling was removed from active flow:
  - deleted `tools/normalize_feedback_outcomes.py`
  - removed `make eval-feedback-normalize`
- Git history is the canonical archive for tracked docs/code; local eval artefact
  folders are operational outputs only and are not part of release truth.
- Live archive lane is now explicit for deprecated references:
  - `.archive/live_archive/legacy_eval/`
  - `.archive/live_archive/legacy_frontend/`
  - `.archive/live_archive/legacy_human_reference/`
  - archive lane is non-authoritative for active runtime gate decisions
  - confidentiality update: `legacy_eval` and `legacy_human_reference` lanes
    are now local-only (gitignored) in the current tree
- Eval docs were canonicalized from `v2` naming:
  - `docs/eval/EVAL_SPEC.md`
  - `docs/eval/EVAL_BACKEND_MAP.md`
  - binary semantics summary: `docs/eval/BINARY_EVAL_LOGIC_REFINEMENT.md`
- Docs relationship visualisation is markdown-native:
  - build: `make reference-graph`
  - output: `docs/visuals/REFERENCE_GRAPH.md`
- Eval relationship visualisation is markdown-native and local-first:
  - build: `make eval-viz`
  - output: `.local/visuals/eval_relationship_graph.md`
  - source: `tools/build_eval_relationship_graph.py`
- Interactive visualisation roadmap pin:
  - D3.js is a deferred track (post-baseline), not active in current
    runtime/docs gate workflows
  - Mermaid remains the canonical visual surface in active operations
- Runtime DB lifecycle commands are retired during wiring lock:
  - no local DB maintenance commands are active in this phase
- Wiring lock is active:
  - keep DB state archived during contract-finalisation phase
  - canonical wiring contract source: `docs/eval/EVAL_WIRING_SPEC.md`
- Minimal-config benchmark sequencing is now explicit:
  - canonical spec: `docs/benchmarks/MINIMAL_CONFIG_BENCHMARK_SPEC.md`
  - objective: compare baseline A/B/C with fixed evaluation dimensions
  - A/B/C are now decision-ready:
    - A=`PASS` (baseline anchor)
    - B=`FAIL` (traditional complexity underperformed)
    - C=`PASS` (binary current target)
- Engineer execution mode is proactive by default:
  - technical hygiene/drift control should be handled without reminder
  - user input is only needed for approvals or material trade-offs
- Co-reasoning governance mode is human-managed:
  - human controls objective/scope/acceptance and go/no-go decisions
  - engineer executes proactively within that control frame
- Transcript-backed OCR mining kernel is merged on `main`:
  - PR: `#110`
  - indexer: `tools/index_cgpt_export.py`
  - miner: `tools/build_ocr_cases_from_export.py`
  - new make commands:
    - `make cgpt-export-index`
    - `make ocr-cases-from-export`
    - `make eval-ocr-transcript-cases`
    - `make eval-ocr-transcript-cases-handwriting`
    - `make eval-ocr-transcript-cases-typed`
    - `make eval-ocr-transcript-cases-illustration`
  - generated transcript OCR cases stay local-only in `.local/eval_cases/`
  - lane artifacts:
    - `.local/eval_cases/ocr_transcript_cases_all.json`
    - `.local/eval_cases/ocr_handwriting_from_transcripts.json`
    - `.local/eval_cases/ocr_typed_from_transcripts.json`
    - `.local/eval_cases/ocr_illustration_from_transcripts.json`
  - latest lane validations are green:
    - all: `4/4` PASS
    - handwriting: `1/1` PASS
    - typed: `2/2` PASS
    - illustration: `1/1` PASS
- Case-study grounding method is now explicit in benchmark docs:
  - lightweight primary-source addendum in
    `docs/benchmarks/MINIMAL_CONFIG_BENCHMARK_SPEC.md`
  - current phase scope is method + 1-2 mapped examples only
  - full corpus ingestion/tooling remains deferred until post-milestone
- Portfolio timeline checkpoint (March 28, 2026):
  - engineering build: `65-75%`
  - portfolio package: `40-50%`
  - overall apply-ready target: `55-65%`
  - expected horizon at current pace: `3-5 weeks`

## Latest Branch Context

- Active implementation branch:
  - `main` (latest merged baseline)
- Canonical repo path:
  - `/Users/tryskian/Github/polinko`

## Key Files To Read First

- `docs/governance/CHARTER.md`
- `docs/governance/STATE.md`
- `docs/governance/DECISIONS.md`
- `docs/runtime/ARCHITECTURE.md`
- `docs/runtime/RUNBOOK.md`
- `docs/eval/EVAL_POLICY_MODEL.md`
- `docs/eval/EVAL_WIRING_SPEC.md`
- `docs/eval/EVAL_SPEC.md`
- `docs/eval/EVAL_BACKEND_MAP.md`
- `.archive/live_archive/README.md`
- `api/app_factory.py`
- `core/history_store.py`
- `tests/test_api.py`

## Quick Validation (Local)

1. Morning worktree confirmation:
   - confirm whether this thread is running in canonical repo root
     (`/Users/tryskian/Github/polinko`) or a dedicated worktree path
   - if automation is active, confirm it is using a separate worktree
   - command ownership stays engineer-side (imagineer does not run terminal/Git commands)
   - execution-first default stays active (agent executes requested work directly)
2. `make doctor-env`
3. `make lint-docs`
4. `make test`
5. `make quality-gate-deterministic`
6. confirm DB freeze posture:
   - no active `.polinko_*.db` / `.human_reference.db` files in repo root

## Known Constraints

- Network-dependent model calls can fail in restricted environments.
- Cloud deployment automation remains paused; local-first execution is canonical.
- Environment mutation policy:
  - verify repo path + mode + branch before changes
  - prefer repo-scoped edits
  - do not modify `~/.zshrc` or global VS Code settings without explicit in-chat approval
- Keep-awake (`caffeinate`) remains opt-in/request-triggered.

## Immediate Next Step

- Expand transcript OCR mining yield while preserving strict precision:
  - run transcript pipeline on local export root:
    - `make cgpt-export-index`
    - `make ocr-cases-from-export`
    - `make eval-ocr-transcript-cases`
    - `make eval-ocr-transcript-cases-handwriting`
    - `make eval-ocr-transcript-cases-typed`
    - `make eval-ocr-transcript-cases-illustration`
  - improve extraction heuristics to increase medium/high-confidence
    handwriting cases without introducing noisy phrase artifacts
  - validate with:
    - `make build-audit`
    - `make lint-docs`
    - `make test`
    - `make quality-gate-deterministic`

## Peanut Pin (Tomorrow Start)

- Start from strict binary contract as baseline (`pass`/`fail` only).
- Review latest eval outputs and prioritise one deterministic backend slice.
- Update `STATE` + `DECISIONS` + `SESSION_HANDOFF` only with material deltas.

## Copy/Paste Rehydrate Prompt

`Read docs/governance/CHARTER.md, docs/runtime/ARCHITECTURE.md, docs/runtime/RUNBOOK.md, docs/governance/STATE.md, docs/governance/DECISIONS.md, and docs/governance/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, confirm active git branch, and confirm whether this thread should run in canonical root or a dedicated worktree (especially if automation is active). Apply no-guessing controls: prefer repo-scoped edits and do not modify ~/.zshrc or global VS Code settings unless explicitly approved in-chat. Run in proactive engineer mode: execute obvious hygiene/cleanup/validation work without waiting for reminders, and ask only when approvals/trade-offs require it. Apply human-managed co-reasoning control: confirm objective/scope/acceptance and keep go/no-go decisions human-led. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behaviour drift and full test/build validation.`
