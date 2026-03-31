<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-30

## Current Snapshot

- Runtime is local-first: FastAPI backend + CLI runner are canonical; web UI is
  archived from the active repository surface.
- `POST /chat` now supports deterministic harness testing for UI smoke:
  - request override: `harness_mode=fixture`
  - optional fixed output: `fixture_output`
  - env default: `POLINKO_CHAT_HARNESS_DEFAULT_MODE=live|fixture`
  - default remains `live` (no behaviour drift for normal runtime)
- Canonical UI eval adapter spec is published:
  - `docs/runtime/RUNBOOK.md`
  - includes TypeScript request/response shapes + chat/eval/checkpoint flow
- Local UI shell is retired from active runtime surface:
  - no `GET /ui` route
  - no active `ui/index.html` file
  - fixture controls remain available through `POST /chat` request fields
- Prompt/runtime behaviour stays minimal and aligned with the original `try.py` style.
- Eval spec is strict binary end-to-end:
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
- Eval and benchmark specs are consolidated in:
  - `docs/runtime/RUNBOOK.md`
- Runtime DB lifecycle commands are retired during wiring lock:
  - no local DB maintenance commands are active in this phase
- Wiring lock is active:
  - keep DB state archived during spec-finalisation phase
  - canonical wiring spec source: `docs/runtime/RUNBOOK.md`
- Minimal-config benchmark sequencing is now explicit:
  - canonical spec: `docs/runtime/RUNBOOK.md`
  - objective: compare baseline A/B/C with fixed evaluation dimensions
  - A/B/C are now decision-ready:
    - A=`PASS` (baseline anchor)
    - B=`FAIL` (traditional complexity underperformed)
    - C=`PASS` (binary current target)
- Streamline-first command surface policy is active:
  - prefer one canonical make target per operator action
  - remove superseded aliases in the same change (no patch layering)
  - require clean-run closure for runtime/tooling edits
- Engineer execution mode is proactive by default:
  - technical hygiene/drift control should be handled without reminder
  - user input is only needed for approvals or material trade-offs
- Co-reasoning governance mode is human-managed:
  - human controls objective/scope/acceptance and go/no-go decisions
  - engineer executes proactively within that control frame
- Transcript format workflow is tooling-backed:
  - `make transcript-fix` auto-normalises curated transcript records
  - `make transcript-check` enforces canonical rich-format structure
  - `make eod` now runs deterministic day-close sequence:
    `transcript-fix -> transcript-check -> doctor-env -> lint-docs -> test`
- Transcript-backed OCR mining kernel is merged on `main`:
  - PRs: `#110`, `#132`, `#133`, `#134`, `#155`, `#156`
  - indexer: `tools/index_cgpt_export.py`
  - miner: `tools/build_ocr_cases_from_export.py`
  - handwriting benchmark builder: `tools/build_handwriting_benchmark_cases.py`
  - miner delta reporter: `tools/report_ocr_case_mining_delta.py`
  - stability replay: `tools/eval_ocr_stability.py`
  - new make commands:
    - `make cgpt-export-index`
    - `make ocr-cases-from-export`
    - `make eval-ocr-transcript-cases`
    - `make eval-ocr-transcript-cases-handwriting`
    - `make eval-ocr-transcript-cases-handwriting-benchmark`
    - `make eval-ocr-transcript-cases-typed`
    - `make eval-ocr-transcript-cases-typed-benchmark`
    - `make eval-ocr-transcript-cases-illustration`
    - `make eval-ocr-transcript-cases-illustration-benchmark`
    - `make eval-ocr-transcript-stability`
    - `make eval-ocr-transcript-stability-handwriting-benchmark`
    - `make eval-ocr-transcript-stability-typed-benchmark`
    - `make eval-ocr-transcript-stability-illustration-benchmark`
    - `make ocrdelta`
    - aliases: `make ocrtypebench`, `make ocrillubench`,
      `make ocrstabletype`, `make ocrstableillu`
  - generated transcript OCR cases stay local-only in `.local/eval_cases/`
  - miner diagnostics are now explicit in command output and review records:
    - counters: `emitted_cases`, `skipped_low_confidence`,
      `skipped_duplicate_image_path`, `skipped_insufficient_anchor_terms`
    - review fields: `emit_status`, `anchor_terms`, `anchor_terms_count`
    - review summary block:
      `confidence_counts`, `lane_counts`, `emit_status_counts`,
      `lane_emit_status_counts`
  - OCR eval matcher now hardens mixed split-letter anchor variants:
    - required one-of matching handles forms like `CHAT T IEST`
    - forbidden whole-word matching handles forms like `GU ESS`
    - stability replay is back to `15 stable / 0 flaky`
  - OCR matcher now also hardens one-character token drift on required
    long-form anchors (example: `CHATTIEST` vs `CHATTEST`) without
    loosening forbidden-phrase checks.
  - `make eval-ocr-transcript-stability` now self-starts `server-daemon`
    to avoid localhost preflight drift.
  - lane artifacts:
    - `.local/eval_cases/ocr_transcript_cases_all.json`
    - `.local/eval_cases/ocr_handwriting_from_transcripts.json`
    - `.local/eval_cases/ocr_handwriting_benchmark_cases.json`
    - `.local/eval_cases/ocr_typed_from_transcripts.json`
    - `.local/eval_cases/ocr_typed_benchmark_cases.json`
    - `.local/eval_cases/ocr_illustration_from_transcripts.json`
    - `.local/eval_cases/ocr_illustration_benchmark_cases.json`
    - `.local/eval_cases/ocr_transcript_cases_delta.md`
  - latest lane validations are green:
    - all: `18/18` PASS
    - handwriting: `6/6` PASS
    - handwriting benchmark: `6/6` PASS
    - typed: `8/8` PASS
    - illustration: `4/4` PASS
  - latest stability replay is green:
    - runs: `5/5`
    - all-lane decision stability: `18` stable, `0` flaky
    - handwriting benchmark stability: `6` stable, `0` flaky
- Case-study grounding method is now explicit in benchmark docs:
  - lightweight primary-source addendum in
    `docs/runtime/RUNBOOK.md`
  - current phase scope is method + 1-2 mapped examples only
  - full corpus ingestion/tooling remains deferred until post-milestone
- Portfolio timeline checkpoint (March 28, 2026):
  - engineering build: `65-75%`
  - portfolio package: `40-50%`
  - overall apply-ready target: `55-65%`
  - expected horizon at current pace: `3-5 weeks`

## Latest Branch Context

- Active implementation branch:
  - `main` (canonical baseline as of latest update)
- Canonical repo path:
  - `/Users/tryskian/Github/polinko`

## Key Files To Read First

- `docs/governance/CHARTER.md`
- `docs/governance/WORKSTREAMS.md`
- `docs/governance/STATE.md`
- `docs/governance/DECISIONS.md`
- `docs/runtime/ARCHITECTURE.md`
- `docs/runtime/RUNBOOK.md`

## Quick Validation (Local)

1. Morning worktree confirmation:
   - confirm whether this thread is running in canonical repo root
     (`/Users/tryskian/Github/polinko`) or a dedicated worktree path
   - if parallel tracks are active, confirm each uses a separate worktree
   - command ownership stays engineer-side (imagineer does not run terminal/Git commands)
   - execution-first default stays active (agent executes requested work directly)
2. `make doctor-env`
3. `make lint-docs`
4. `make test`
5. `make quality-gate-deterministic`
6. confirm DB freeze posture:
   - no active `.polinko_*.db` / `.human_reference.db` files in repo root

## Day-Close Routine (Local)

1. Run deterministic end-of-day routine:
   - `make eod`
2. Included checks:
   - `make transcript-fix`
   - `make transcript-check`
   - `make doctor-env`
   - `make lint-docs`
   - `make test`

## Known Constraints

- Network-dependent model calls can fail in restricted environments.
- Cloud deployment remains paused; local-first execution is canonical.
- Environment mutation policy:
  - verify repo path + mode + branch before changes
  - prefer repo-scoped edits
  - do not modify `~/.zshrc` or global VS Code settings without explicit in-chat approval
- Keep-awake (`caffeinate`) remains opt-in/request-triggered.

## Immediate Next Step

- Keep transcript OCR baseline locked at
  (`handwriting=5`, `typed=7`, `illustration=3`) with strict green gates:
  - rerun:
    - `make ocr-cases-from-export`
    - `make eval-ocr-transcript-cases`
    - `make eval-ocr-transcript-cases-handwriting`
    - `make eval-ocr-transcript-cases-typed`
    - `make eval-ocr-transcript-cases-illustration`
    - `make eval-ocr-transcript-stability OCR_STABILITY_RUNS=5`
  - use review `summary` + `episodes` diagnostics to prioritise exactly one
    precision-safe medium-confidence promotion kernel
  - preserve malformed-anchor/single-token/conversational-noise guards
  - validate with:
    - `make lint-docs`
    - `make test`
    - `make quality-gate-deterministic`

## Peanut Pin (Tomorrow Start)

- Start from strict binary spec as baseline (`pass`/`fail` only).
- Review latest eval outputs and prioritise one deterministic backend slice.
- Update `STATE` + `DECISIONS` + `SESSION_HANDOFF` only with material deltas.

## Copy/Paste Rehydrate Prompt

`Read docs/governance/CHARTER.md, docs/governance/WORKSTREAMS.md, docs/runtime/ARCHITECTURE.md, docs/runtime/RUNBOOK.md, docs/governance/STATE.md, docs/governance/DECISIONS.md, and docs/governance/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, confirm active git branch, and confirm whether this thread should run in canonical root or a dedicated worktree. Apply no-guessing controls: prefer repo-scoped edits and do not modify ~/.zshrc or global VS Code settings unless explicitly approved in-chat. Run in proactive engineer mode: execute obvious hygiene/cleanup/validation work without waiting for reminders, and ask only when approvals/trade-offs require it. Apply human-managed co-reasoning control: confirm objective/scope/acceptance and keep go/no-go decisions human-led. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behaviour drift and full test/build validation.`
