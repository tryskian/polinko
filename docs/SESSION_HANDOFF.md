<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-28

## Current Snapshot

- Runtime is local-first: FastAPI backend + CLI runner are canonical; local UI
  shell is active at `/ui`.
- `POST /chat` now supports deterministic harness testing for UI smoke:
  - request override: `harness_mode=fixture`
  - optional fixed output: `fixture_output`
  - env default: `POLINKO_CHAT_HARNESS_DEFAULT_MODE=live|fixture`
  - default remains `live` (no behaviour drift for normal runtime)
- Canonical UI eval adapter contract is published:
  - `docs/UI_EVAL_ADAPTER_CONTRACT.md`
  - includes TypeScript request/response shapes + chat/eval/checkpoint flow
- Local UI shell is now active:
  - route: `GET /ui`
  - file: `ui/index.html`
  - scope: chat thread + binary eval submit + checkpoint render/create
  - OCR attachments supported in composer:
    - upload image files
    - paste images directly into prompt input
    - attachment filenames are normalised for readable operator labels
  - fixture mode controls are available for deterministic UI smoke
- Prompt/runtime behaviour stays minimal and aligned with the original `try.py` style.
- Eval contract is strict binary end-to-end:
  - feedback outcomes: `pass` or `fail` only
  - UI flow submits binary outcome without reason tags
  - backend accepts empty tag arrays for binary submissions
  - checkpoint schema field: `non_binary_count` (integrity signal, expected `0`)
  - checkpoint response field: `gate_outcome` (`pass`/`fail`, fail-closed from counts)
  - previous `tags`-only feedback payload compatibility removed
- Previous normalisation tooling was removed from active flow:
  - deleted `tools/normalize_feedback_outcomes.py`
  - removed `make eval-feedback-normalize`
- Git history is the canonical archive for tracked docs/code; local eval artefact
  folders are operational outputs only and are not part of release truth.
- Live archive lane is now explicit for deprecated references:
  - `docs/live_archive/legacy_eval/`
  - `docs/live_archive/legacy_frontend/`
  - `docs/live_archive/legacy_human_reference/`
  - archive lane is non-authoritative for active runtime gate decisions
- Eval docs were canonicalized from `v2` naming:
  - `docs/EVAL_SPEC.md`
  - `docs/EVAL_BACKEND_MAP.md`
  - binary semantics summary: `docs/BINARY_EVAL_LOGIC_REFINEMENT.md`
- Docs relationship visualisation is markdown-native:
  - build: `make reference-graph`
  - output: `docs/REFERENCE_GRAPH.md`
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
  - canonical wiring contract source: `docs/EVAL_WIRING_SPEC.md`
- Minimal-config benchmark sequencing is now explicit:
  - canonical spec: `docs/MINIMAL_CONFIG_BENCHMARK_SPEC.md`
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

## Latest Branch Context

- Active implementation branch:
  - `main` (latest merged baseline)
- Canonical repo path:
  - `/Users/tryskian/Github/polinko`

## Key Files To Read First

- `docs/CHARTER.md`
- `docs/STATE.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/RUNBOOK.md`
- `docs/EVAL_POLICY_MODEL.md`
- `docs/EVAL_WIRING_SPEC.md`
- `docs/EVAL_SPEC.md`
- `docs/EVAL_BACKEND_MAP.md`
- `docs/live_archive/README.md`
- `api/app_factory.py`
- `core/history_store.py`
- `tests/test_api.py`

## Quick Validation (Local)

1. `make doctor-env`
2. `make lint-docs`
3. `make test`
4. `make quality-gate-deterministic`
5. confirm DB freeze posture:
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

- Run one manual OCR-eval smoke through `/ui` under the binary-only contract:
  - attach image via file upload and via clipboard paste
  - submit `PASS` and `FAIL` evals without reason tags
  - create checkpoint and verify fail-closed gate rendering
  - validate with `make build-audit`, `make lint-docs`, `make test`,
    `make quality-gate-deterministic`

## Peanut Pin (Tomorrow Start)

- Start from strict binary contract as baseline (`pass`/`fail` only).
- Review latest eval outputs and prioritise one deterministic backend slice.
- Update `STATE` + `DECISIONS` + `SESSION_HANDOFF` only with material deltas.

## Copy/Paste Rehydrate Prompt

`Read docs/CHARTER.md, docs/ARCHITECTURE.md, docs/RUNBOOK.md, docs/STATE.md, docs/DECISIONS.md, and docs/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, and confirm active git branch. Apply no-guessing controls: prefer repo-scoped edits and do not modify ~/.zshrc or global VS Code settings unless explicitly approved in-chat. Run in proactive engineer mode: execute obvious hygiene/cleanup/validation work without waiting for reminders, and ask only when approvals/trade-offs require it. Apply human-managed co-reasoning control: confirm objective/scope/acceptance and keep go/no-go decisions human-led. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behaviour drift and full test/build validation.`
