<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-04-02

## Current Snapshot

- Runtime is local-first: FastAPI backend + CLI runner are canonical; web UI is
  archived from the active repository surface.
- OCR-forward model is active:
  - `lockset` lane is release-gating (strict green requirement)
  - `growth` lane is fail-tolerant for pass-from-fail measurement
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
- Backend runtime no longer includes API-key auth config/enforcement
  (`POLINKO_SERVER_API_KEY*` removed from active surface).
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
    `transcript-fix -> transcript-check -> doctor-env -> lint-docs -> test -> eod-stop`
- Transcript-backed OCR mining kernel is merged on `main`:
  - PRs: `#110`, `#132`, `#133`, `#134`, `#155`, `#156`, `#159`, `#160`, `#162`
  - indexer: `tools/index_cgpt_export.py`
  - miner: `tools/build_ocr_cases_from_export.py`
  - handwriting benchmark builder: `tools/build_handwriting_benchmark_cases.py`
  - miner delta reporter: `tools/report_ocr_case_mining_delta.py`
  - stability replay: `tools/eval_ocr_stability.py`
  - new make commands:
    - `make cgpt-export-index`
    - `make ocr-cases-from-export`
    - `make eval-ocr-transcript-cases`
    - `make eval-ocr-transcript-cases-growth`
    - `make eval-ocr-transcript-cases-handwriting`
    - `make eval-ocr-transcript-cases-handwriting-benchmark`
    - `make eval-ocr-transcript-cases-typed`
    - `make eval-ocr-transcript-cases-typed-benchmark`
    - `make eval-ocr-transcript-cases-illustration`
    - `make eval-ocr-transcript-cases-illustration-benchmark`
    - `make eval-ocr-transcript-stability`
    - `make eval-ocr-transcript-stability-growth`
    - `make eval-ocr-transcript-growth`
    - `make eval-ocr-transcript-stability-handwriting-benchmark`
    - `make eval-ocr-transcript-stability-typed-benchmark`
    - `make eval-ocr-transcript-stability-illustration-benchmark`
    - `make ocrdelta`
    - aliases: `make ocrwiden`, `make ocrstablegrowth`,
      `make ocrtypebench`, `make ocrillubench`,
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
    - last full transcript stability replay (pre-widening) is
      `21 stable / 0 flaky`
  - OCR matcher now also hardens one-character token drift on required
    long-form anchors (example: `CHATTIEST` vs `CHATTEST`) without
    loosening forbidden-phrase checks.
  - transcript miner now preserves compact numeric entry phrases from framed
    and code-block assistant OCR lines (for example `1745`, `200226`) so
    valid timestamp/date transcriptions are not dropped before anchoring.
  - correction-anchor hardening is active:
    - correction phrases only drive high-confidence anchors when they overlap
      with OCR transcription phrases
    - review diagnostics include `correction_overlap_signal`
    - off-topic/late correction phrases no longer pollute anchor terms
  - low-confidence review rows are now filtered to OCR-signaled episodes only
    (`ocr_literal_intent_signal`, `ocr_framing_signal`, `correction_signal`, or
    `correction_overlap_signal`)
  - OCR framing signal ignores explicit negated wording
    (`no ocr`, `not ocr`, `without ocr`, `no transcription`)
  - `make eval-ocr-transcript-stability` now self-starts `server-daemon`
    to avoid localhost preflight drift.
  - direct OCR case-eval make targets now also self-start `server-daemon`
    (strict/growth benchmark commands running `tools.eval_ocr`)
  - lane artifacts:
    - `.local/eval_cases/ocr_transcript_cases_all.json`
    - `.local/eval_cases/ocr_handwriting_from_transcripts.json`
    - `.local/eval_cases/ocr_handwriting_benchmark_cases.json`
    - `.local/eval_cases/ocr_typed_from_transcripts.json`
    - `.local/eval_cases/ocr_typed_benchmark_cases.json`
    - `.local/eval_cases/ocr_illustration_from_transcripts.json`
    - `.local/eval_cases/ocr_illustration_benchmark_cases.json`
    - `.local/eval_cases/ocr_transcript_cases_delta.md`
  - active precision baseline:
    - mined cases: `26` total
      (`handwriting=5`, `typed=11`, `illustration=10`)
    - growth cases: `39`
    - review summary: `episodes=178`
      (`high=7`, `medium=27`, `low=144`)
    - previous `55`/`29`/`25` mined outputs are legacy reference only
  - latest lane validations:
    - latest complete transcript lane (diagnostic, pre-widening):
      `21/21` PASS (`0` fail)
    - handwriting benchmark: `4/4` PASS
    - typed benchmark: `6/6` PASS
    - illustration benchmark: `3/3` PASS
  - notebook visual starter for fast local analysis:
    - `output/jupyter-notebook/ocr-eval-live-filters-starter.ipynb`
    - launch via: `make notes`
  - latest stability replay is green:
    - runs: `5/5`
    - benchmark decision stability:
      - handwriting: `4` stable, `0` flaky
      - typed: `6` stable, `0` flaky
      - illustration: `3` stable, `0` flaky
    - full transcript stability (pre-widening): `21` stable, `0` flaky
  - lockset rerun checkpoint (April 2, 2026) is green:
    - one-case provider probe (`make ocrhandbench` with fail-fast `1`) completed
      successfully
    - lockset + stability commands reran with all PASS outcomes
  - growth/focus replay commands now stream logs in real time:
    - Makefile uses unbuffered Python output for growth and focus replay
      targets to avoid false "hung" runs during slow provider windows
  - growth metrics command is active:
    - `make ocrgrowth`
    - outputs:
      - `.local/eval_reports/ocr_growth_metrics.json`
      - `.local/eval_reports/ocr_growth_metrics.md`
  - fail cohort now separates persistent FAIL cases from provider-pressure
    no-decision cases:
    - `summary.rate_limited_cases`
    - `summary.rate_limit_abort_runs`
    - `rate_limited_cases[]` list in
      `.local/eval_cases/ocr_growth_fail_cohort.json`
    - matching markdown section in
      `.local/eval_reports/ocr_growth_fail_cohort.md`
  - run-report join resolver now supports repo-root-relative `.local/...`
    report paths to avoid stale fail-cohort case mapping
  - latest aligned refresh (April 2, 2026):
    - `make ocrmine` emitted `26` strict cases, `39` growth cases
    - `make ocrstablegrowth OCR_GROWTH_STABILITY_RUNS=1`:
      - `39` cases replayed, `29` pass, `10` fail, `0` errors
      - stability: `39` stable, `0` flaky
    - `make ocrgrowth`:
      - `decision_coverage_rate=1.0000`
      - `first_pass_fail_rate=0.2821`
      - `first_error_rate=0.0000`
    - `make ocrfails`:
      - `selected_fail_cases=5`
      - `rate_limited_cases=0`
      - `rate_limit_abort_runs=0`
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
   - `make eod-stop`

## Known Constraints

- Network-dependent model calls can fail in restricted environments.
- Transient API pressure can still surface `429` during eval runs:
  - retrieval harness now supports bounded retries
    (`RETRIEVAL_REQUEST_RETRIES`, `RETRIEVAL_REQUEST_RETRY_DELAY_MS`)
  - OCR harness now supports bounded eval retries + fail-fast on sustained
    streaks (`OCR_EVAL_OCR_RETRIES`, `OCR_EVAL_OCR_RETRY_DELAY_MS`,
    `OCR_MAX_CONSEC_RATE_LIMIT_ERRORS`)
  - OCR retries now respect provider `Retry-After` on `429` when present
  - provider pressure remains intermittent; keep one-case probe first before
    full growth replay when call budget is uncertain
- Cloud deployment remains paused; local-first execution is canonical.
- Environment mutation policy:
  - verify repo path + mode + branch before changes
  - prefer repo-scoped edits
  - do not modify `~/.zshrc` or global VS Code settings without explicit in-chat approval
- Keep-awake (`caffeinate`) remains opt-in/request-triggered.
- Day-close now hard-stops background tasks:
  - `make eod-stop` stops `server-daemon` and all matching `caffeinate -d -i -m` processes.

## Immediate Next Step

- Keep OCR-forward split stable:
  - lockset lane remains strict release gate
  - growth lane remains fail-tolerant and tracked separately
- Re-run lockset and stability sequence:
  - start with a one-case OCR probe to check provider pressure before full run:
    - `make ocrhandbench OCR_EVAL_OCR_RETRIES=0 OCR_MAX_CONSEC_RATE_LIMIT_ERRORS=1`
  - `make ocrhandbench`
  - `make ocrtypebench`
  - `make ocrillubench`
  - `make ocrstablehand`
  - `make ocrstabletype`
  - `make ocrstableillu`
- Recompute growth-lane pass-from-fail metrics:
  - if growth cases were rematerialised (`make ocrmine`), run
    `make ocrstablegrowth` before `make ocrgrowth`/`make ocrfails` so metrics
    are aligned to the current case map.
  - `make ocrwiden`
  - `make ocrstablegrowth`
  - `make ocrgrowth`
  - `make ocrfails`
    - review `rate_limited_cases` + `rate_limit_abort_runs` before treating
      empty fail cohorts as clean OCR-quality signals
    - fail cohort now enforces OCR-framed review linkage
      (`ocr_framing_signal=true`) using
      `.local/eval_cases/ocr_transcript_cases_review.json`
    - ensure `OCR_STABILITY_RUNS` matches observed run window in
      `.local/eval_reports/ocr_growth_stability.json` (for example `3` vs `5`)
      to avoid false-empty cohorts
    - if `skipped_case_map_mismatch > 0`, treat cohort as stale-join protected
      and rerun `make ocrstablegrowth` on refreshed growth cases before
      precision patch decisions
    - current aligned baseline (April 2, 2026):
      - growth cases: `39`
      - latest stability replay: `29/39` pass, `10/39` fail, `0` errors
      - fail cohort selection (`require_ocr_framing=true`): `5` cases
  - focused remediation replay (fail-first subset):
    - `make ocrfocuscases`
    - `make eval-ocr-focus-stability`
    - one-shot chain:
      - `make ocrfocus`
    - tuning knobs:
      - `OCR_FOCUS_MAX_CASES`
      - `OCR_FOCUS_INCLUDE_FAIL_HISTORY`
      - `OCR_FOCUS_RUNS`
      - `OCR_FOCUS_CASE_DELAY_MS`
      - `OCR_FOCUS_RATE_LIMIT_COOLDOWN_MS`
  - run read-only runtime null audit for DB observability:
    - `make nulls`
    - review `.local/eval_reports/runtime_null_audit.md`
- If eval runs hit sustained `429` streaks:
  - keep binary pass/fail semantics unchanged
  - tune retry/fail-fast knobs only (do not relax gate criteria)
  - focused replay auto-skips during configured backoff after recent
    rate-limit abort:
    - `OCR_FOCUS_SKIP_RECENT_RATE_LIMIT`
    - `OCR_FOCUS_RATE_LIMIT_BACKOFF_SECONDS`
  - stability replays now stop after first run with
    `aborted_due_to_rate_limit=true` (prevents multi-run call waste under hard
    provider throttle)
  - continue offline data refresh with:
    - `make ocr-data CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
    - review `growth_quarantine_cases_written` in miner summary; quarantined
      growth cases are expected and remain excluded from strict transcript set
    - review `growth_regex_only_cases_written` to track growth rows constrained
      by phrase regex when anchor/order terms are empty
- If lockset regresses, apply one precision-safe miner/matcher kernel only,
  then rerun full sequence before merge.
- Use notebook starter for fast local triage when needed:
  - `make notes`
  - open `output/jupyter-notebook/ocr-eval-live-filters-starter.ipynb`
- Validate closure:
  - `make lint-docs`
  - `make test`
  - `make quality-gate-deterministic`

## Peanut Pin (Tomorrow Start)

- Start from strict binary spec as baseline (`pass`/`fail` only).
- Review latest eval outputs and prioritise one deterministic backend slice.
- Update `STATE` + `DECISIONS` + `SESSION_HANDOFF` only with material deltas.

## Copy/Paste Rehydrate Prompt

`Read docs/governance/CHARTER.md, docs/governance/WORKSTREAMS.md, docs/runtime/ARCHITECTURE.md, docs/runtime/RUNBOOK.md, docs/governance/STATE.md, docs/governance/DECISIONS.md, and docs/governance/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, confirm active git branch, and confirm whether this thread should run in canonical root or a dedicated worktree. Apply no-guessing controls: prefer repo-scoped edits and do not modify ~/.zshrc or global VS Code settings unless explicitly approved in-chat. Run in proactive engineer mode: execute obvious hygiene/cleanup/validation work without waiting for reminders, and ask only when approvals/trade-offs require it. Apply human-managed co-reasoning control: confirm objective/scope/acceptance and keep go/no-go decisions human-led. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behaviour drift and full test/build validation.`
