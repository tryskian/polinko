<!-- @format -->

# Project State

## Current Status

- Prompt/runtime is intentionally minimal and aligned with the original `try.py` behaviour.
- CLI agent loop works with persistent SQLite memory (`.local/runtime_dbs/active/memory.db`) and
  `/reset`.
- Backend API is running with:
  - `GET /health`
  - `GET /metrics`
  - `POST /chat`
  - `POST /session/reset`
  - `POST /skills/ocr`
  - `POST /skills/file_search`
  - `GET /chats/{session_id}/export`
  - `GET /chats/{session_id}/collaboration`
  - `POST /chats/{session_id}/collaboration/handoff`
- API includes:
  - startup config validation
  - no backend API-key auth path in active runtime
    (localhost boundary is trusted for local development)
  - structured request/chat logs
  - in-process request metrics (`requests_total`, status counts, latency buckets, 429 count)
  - rate limiting + `Retry-After` on 429
  - periodic stale bucket cleanup in the in-memory limiter
  - per-chat personalization memory scope (`session` vs `global`)
  - `/chat` retrieval citations via `memory_used` when vector memory contributes context
  - deterministic harness override for smoke tests:
    `harness_mode=fixture` (+ optional `fixture_output`)
  - env-level harness default:
    `POLINKO_CHAT_HARNESS_DEFAULT_MODE=live|fixture`
  - canonical UI eval adapter spec:
    `docs/runtime/RUNBOOK.md`
- Legacy frontend implementation remains archived in
  `.archive/live_archive/legacy_frontend/`.
- OpenAI developer docs MCP server is now configured for Codex/VS Code usage:
  - endpoint: `https://developers.openai.com/mcp`
  - workspace wiring: `.vscode/mcp.json`
- Figma/UI parity work is deprecated for current cycle; execution focus is backend retrieval, OCR, and file-search reliability.
- Quality gate is implemented and passing locally via `make quality-gate`:
  - unit tests
  - retrieval eval (`12/12`)
  - file-search eval (`5/5`, including image-context smoke)
  - OCR eval strict (`6/6`)
  - style eval strict (`6/6`)
  - hallucination eval strict (`6/6`)
- OCR-forward design checkpoint (April 1, 2026):
  - active eval model is split into:
    - `lockset` lane (strict release gate, must remain green)
    - `growth` lane (fail-tolerant novel cases used for pass-from-fail tracking)
  - growth metrics are executable via:
    - growth eval/stability:
    - `make ocrwiden`
    - `make ocrstablegrowth`
    - `make ocrgrowth`
    - `make ocrfails`
      - now requires OCR-framed review linkage (`ocr_framing_signal=true`)
        from `.local/eval_cases/ocr_transcript_cases_review.json`
    - outputs:
      - `.local/eval_cases/ocr_transcript_cases_growth.json`
      - `.local/eval_cases/ocr_growth_fail_cohort.json`
      - `.local/eval_reports/ocr_growth_stability.json`
      - `.local/eval_reports/ocr_growth_metrics.json`
      - `.local/eval_reports/ocr_growth_metrics.md`
      - `.local/eval_reports/ocr_growth_fail_cohort.md`
  - latest lockset benchmark baseline (local):
    - handwriting: `4/4` PASS
    - typed: `6/6` PASS
    - illustration: `2/2` PASS
  - local visual analysis starter is available at:
    - `output/jupyter-notebook/ocr-eval-live-filters-starter.ipynb`
- Eval runtime resilience checkpoint (April 1, 2026):
  - retrieval harness now supports bounded transient retries for `429`/`5xx`
    and connection errors (`--request-retries`, `--request-retry-delay-ms`)
  - OCR harness now supports fail-fast under sustained provider pressure via
    `--max-consecutive-rate-limit-errors`
  - OCR retry path now respects provider `Retry-After` on `429` when present
    (effective retry sleep = max of configured delay and header delay)
  - make-level controls are exposed for operator tuning without changing gate
    semantics:
    - `RETRIEVAL_REQUEST_RETRIES`
    - `RETRIEVAL_REQUEST_RETRY_DELAY_MS`
    - `OCR_EVAL_OCR_RETRIES`
    - `OCR_EVAL_OCR_RETRY_DELAY_MS`
    - `OCR_MAX_CONSEC_RATE_LIMIT_ERRORS`
  - direct OCR case-eval make targets now self-start `server-daemon` before
    running `tools.eval_ocr` to remove local preflight drift
  - latest lockset rerun probe is currently blocked by sustained OCR `429`
    pressure at provider boundary (`0/1` attempted with fail-fast threshold `1`)
  - latest one-case handwriting probe (`make ocrhandbench` with
    `OCR_MAX_CONSEC_RATE_LIMIT_ERRORS=1`) aborted at `1/4` attempted due
    provider `429`
  - fail cohort stale-join guard is active and confirmed:
    - latest refresh pass (`make ocr-data && make ocrgrowth && make ocrfails`)
      reports:
      - `skipped_case_map_mismatch=0`
      - `selected_fail_cases=0`
      - `rate_limited_cases=3`
      - `rate_limit_abort_runs=1`
    - current blocker is provider throttling (`429`) causing no decision
      coverage in current growth snapshot (`decision_coverage_rate=0.0000`)
  - growth fail cohort now explicitly reports provider-pressure blocked rows
    (no PASS/FAIL decision yet) separate from FAIL regressions:
    - `rate_limited_cases`
    - `rate_limit_abort_runs`
  - fail-cohort run-report joins now resolve repo-root-relative `.local/...`
    report paths before fallback relative joins to avoid stale mapping misses.
  - stability replay now stops remaining runs after first
    `aborted_due_to_rate_limit=true` child report to avoid repeated wasted runs
    during hard throttle windows.
  - `make ocr-data` is now offline-only (`doctor-env`, `ocrmine`, `ocrdelta`);
    full online OCR replay remains at `make ocr-notebook-workflow`.
  - offline miner now routes strong unstable-source episodes to growth lane
    only (`source_quarantine=true`), with latest summary:
    - `growth_cases_written=148`
    - `growth_quarantine_cases_written=1`
    - `growth_regex_only_cases_written=0` (metric active; no current rows)
- Latest local report baseline (March 6, 2026) is green:
  - `make eval-ocr-report` PASS
  - `make eval-file-search-report` PASS
  - `make eval-style-report` PASS
  - `make eval-hallucination-report` PASS
  - `make eval-retrieval-report` PASS
- Latest focused validation cycle (March 15, 2026) is green:
  - strict style eval: `style-strict-20260315-180637.json` (`11/11` PASS)
  - file-search report: `file-search-20260315-181109.json` (`5/5` PASS)
  - CLIP A/B report: `clip-ab-20260315-180942.json` (`delta=+1.000`)
  - CLIP readiness: `GO` on latest pair
    (`clip-ab-20260315-143219.json`, `clip-ab-20260315-180942.json`)
  - runtime regression signal: `make test` (`154` tests PASS)
- Status checkpoint (March 17, 2026):
  - project is in late build-hardening phase (not early scaffold phase)
  - core runtime + binary eval flow are stable and merged on `main`
  - remaining work is concentrated in backlog triage, eval UX hardening, and
    final portfolio evidence packaging
- Binary eval policy checkpoint (March 21, 2026):
  - gate logic remains strict `PASS`/`FAIL` for deterministic release decisions
  - `em_dash_style` is currently a hard-fail signal to set the style baseline
  - human nuance stays in notes/transcripts for diagnosis, not gate computation
- Rubric simplification checkpoint (March 22, 2026):
  - active UI rubric is now two explicit dimensions:
    `style` and `hallucination_risk` (each `pass`/`fail`)
  - optional style penalties are split:
    - `default_style` = soft penalty
    - `em_dash_style` = hard penalty
  - response status remains stream-based (`pass: ...`, `fail: ...`,
    `penalty: ...`) so nuanced signals persist without collapsing into one label
  - operator gate remains binary: any hard fail signal is treated as a fail for
    that response
- Eval stream checkpoint (March 21, 2026):
  - feedback save supports simultaneous positive and negative rubric streams on
    one response
  - UI status line now renders separate streams (`pass: ...` and `fail: ...`)
    instead of forcing a single top-level label
  - checkpoint rollups now count `pass_count` and `fail_count` independently;
    `non_binary_count` is expected to remain `0` and is treated as an integrity signal
  - checkpoint API responses now expose explicit fail-closed `gate_outcome`
    (`pass`/`fail`) derived from checkpoint counts
  - API/tests were updated together to avoid state drift between rubric
    semantics and saved checkpoint payloads
- Binary spec hard-cut checkpoint (March 26, 2026):
  - feedback outcomes are strict `pass`/`fail` at API and storage boundaries
  - legacy `tags`-only feedback payload compatibility is removed
  - checkpoint responses use `non_binary_count` (no active `other_count` label)
  - no migration helper is part of active workflow; data outside spec is a repair task
- Post-merge eval + reference checkpoint (March 25, 2026):
  - PR `#71` merged to `main` (`a60bf15`) with backend/API/test sync
  - checkpoint and feedback APIs preserve binary gate behaviour
  - document-link relationship indexing model was established for reference flow
- Docs hygiene checkpoint (March 21, 2026):
  - deprecated pilot/comms docs are archive-only and removed from active
    runbook/state/handoff references
  - archived docs are hidden from explorer/search to reduce active-workflow
    clutter
  - `docs/peanut/refs/PEANUT_TOOLING_REF.md` remains visible for day-to-day
    operator use
- Git-native retention checkpoint (March 27, 2026):
  - archive-folder workflow removed from active operations
    (`make eval-reset-baseline` removed)
  - eval trace default output moved to
    `eval_reports/eval_trace_artifacts.jsonl`
  - tracked-state retention is now explicitly Git-native
    (no additional archive folder layer required)
- Live archive checkpoint (March 27, 2026):
  - added tracked live archive lane: `.archive/live_archive/`
  - lane split is explicit:
    - `.archive/live_archive/legacy_eval/`
    - `.archive/live_archive/legacy_frontend/`
    - `.archive/live_archive/legacy_human_reference/`
  - archive lane is reference-only and non-authoritative for active runtime
    gate decisions
- Local-only confidentiality checkpoint (March 29, 2026):
  - `.archive/live_archive/legacy_eval/` and
    `.archive/live_archive/legacy_human_reference/` are local-only in the new
    tree and ignored by git
  - docs under those lanes are retained locally but removed from tracked
    repository history going forward
- Docs straggler cleanup checkpoint (March 28, 2026):
  - deprecated top-level coordination docs moved into:
    - `.archive/live_archive/legacy_coordination/`
  - active top-level docs now stay focused on current runtime/eval operations
    and research workflow
- Docs consolidation checkpoint (March 29, 2026):
  - active spec content is consolidated into seven canonical docs:
    - `CHARTER`, `WORKSTREAMS`, `DECISIONS`, `SESSION_HANDOFF`, `STATE`,
      `ARCHITECTURE`, `RUNBOOK`
  - benchmark/eval spec details are now maintained directly in
    `docs/runtime/RUNBOOK.md`
- EOD docs confidentiality merge checkpoint (March 25, 2026):
  - PR `#72` merged to `main` (`2a6f575`)
  - runbook + ignore policy now treats non-build internal docs as local-only
    by default
  - session handoff is aligned to the merged cleanup baseline for next-day
    startup
- Branch protection checkpoint (March 25, 2026):
  - `main` remains protected (PR + required checks)
  - active implementation now runs through task branches merged back to `main`
  - no special-purpose `eval-rubric` branch/ruleset is active
- Safety certainty checkpoint (March 21, 2026):
  - captured transcript + peanut-reference framing in
    `docs/peanut/transcripts/safety/safety_certainty_and_inference_notes_2026-03-21.md`
    (unsupported certainty = fail; uncertainty + grounded recovery = pass)
- Reasoning Loops diagnostic checkpoint (March 22, 2026):
  - captured transcript + structured interpretation in the March 22 diagnostic
    transcript under `docs/peanut/transcripts/`
  - preserves the “pattern is strategy, not the other way around” framing for
    future rubric and reasoning-behaviour analysis
- Latest audit checkpoint (March 25, 2026):
  - `make doctor-env`: healthy
  - `make lint-docs`: pass
  - backend regression tests: `make test` pass (`162` tests)
- UI archive checkpoint (March 27, 2026):
  - legacy `frontend/` folder removed from active repository surface
  - canonical surfaces are API + CLI + deterministic eval tooling
  - historical UI context is retained via live archive docs + Git history
- Human-reference archive checkpoint (March 27, 2026):
  - SQLite human-reference DB/query workflow moved to archive-only status
- Runtime DB lifecycle checkpoint (March 27, 2026):
  - runtime DB defaults moved to `.local/runtime_dbs/active/`
  - local DB lifecycle commands are retired during wiring lock
    (docs/tests remain the active spec surface)
  - no root-level `.polinko_*.db` files are part of the active surface
- Minimal-config benchmark checkpoint (March 27, 2026):
  - canonical benchmark spec added:
    - `docs/runtime/RUNBOOK.md`
  - benchmark compares three phases:
    - minimal-config CLI baseline
    - traditional eval stack
    - binary eval stack
  - evaluation axes are fixed to quality, decision clarity, iteration speed,
    and maintenance overhead
- Benchmark verdict checkpoint (March 28, 2026):
  - A/B/C moved from provisional to decision-ready status:
    - A: `PASS` (baseline anchor)
    - B: `FAIL` (traditional complexity underperformed)
    - C: `PASS` (binary current target)
  - `H-001` is currently supported for product direction
  - next benchmark-derived backend priority is operation-binding diagnostics
    (`benchmark D`) as deterministic implementation slices
- Case-study stack narrative checkpoint (March 29, 2026):
  - canonical evidence story is locked to stack comparison (not model naming):
    - baseline stack: usable minimal-control operation
    - advanced stack: regression via correction-loop overhead and reduced
      completion reliability
    - binary stack: reliability recovery via lean controls + strict binary
      gates
  - portfolio claims should map to this stack sequence with transcript/eval
    evidence links
- Primary-source grounding checkpoint (March 29, 2026):
  - benchmark spec now includes a scoped case-study grounding addendum:
    - method + 1-2 mapped examples only in current phase
  - transcript-backed OCR mining lane provides one mapped handwriting example
    under strict binary gate validation (`1/1` PASS)
  - full corpus ingestion/tooling remains deferred until post-milestone
- Wiring lock checkpoint (March 27, 2026):
  - runtime DB provisioning is intentionally paused until eval wiring sign-off
  - no fresh `.polinko_*.db` or `.human_reference.db` files are active in
    repository root during this phase
  - canonical wiring source is `docs/runtime/RUNBOOK.md` and associated
    spec docs/tests
- Runtime DB doc-spec checkpoint (March 28, 2026):
  - active docs no longer reference retired local DB commands
    (`db-reset`, `db-archive`, `db-visuals`)
- Transcript-backed OCR mining checkpoint (March 29, 2026):
  - merged PRs `#110`, `#132`, `#133`, and `#134` establish transcript OCR
    mining + hardening:
    - `tools/index_cgpt_export.py`
    - `tools/build_ocr_cases_from_export.py`
    - `tools/eval_ocr_stability.py`
  - canonical local commands:
    - `make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
    - `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
    - `make eval-ocr-transcript-cases`
    - `make eval-ocr-transcript-stability OCR_STABILITY_RUNS=5`
  - local outputs are untracked under `.local/eval_cases/`
  - transcript miner emits four local case sets:
    - combined: `.local/eval_cases/ocr_transcript_cases_all.json`
    - handwriting: `.local/eval_cases/ocr_handwriting_from_transcripts.json`
    - typed: `.local/eval_cases/ocr_typed_from_transcripts.json`
    - illustration: `.local/eval_cases/ocr_illustration_from_transcripts.json`
  - latest local miner output:
    - combined cases: `15`
    - handwriting: `5`
    - typed: `7`
    - illustration: `3`
- OCR lane quality hardening checkpoint (March 29, 2026):
  - ask-level correction promotion remains anchor-driven (not correction-word
    driven) for medium-confidence recovery
  - literal-intent transcript episodes now have a guarded medium-confidence
    promotion path requiring strong multi-token phrase evidence and excluding
    positive-only followup confirmations
  - mined case emission now requires `>=3` anchor terms
  - anchor variant expansion now blocks malformed over-stems
    (for example `focus -> focu`, `abacus -> abacu`)
  - OCR framing detection now recognises transcript-style wording
    (`transcription`/`transcript`) to avoid missing literal OCR episodes
  - miner diagnostics now expose explicit emit/skip reasons for each reviewed
    episode (`emit_status`, `anchor_terms`, and skip counters in command output)
  - review output now includes a summary aggregate block for faster lane-level
    triage (`confidence_counts`, `lane_counts`, and per-lane emit-status counts)
  - OCR required/forbidden anchor matching now tolerates mixed split-letter
    artefacts (for example `CHAT T IEST`, `GU ESS`) to prevent deterministic
    false failures
  - required-anchor matching now tolerates one-character OCR drift on longer
    single-token anchors (for example `CHATTIEST` vs `CHATTEST`) while keeping
    forbidden-phrase checks exact
  - `make eval-ocr-transcript-stability` now self-starts `server-daemon` so
    localhost preflight does not silently fail when the backend is not already up
  - latest strict lane validation:
    - all lane: `15/15` PASS
    - handwriting lane: `5/5` PASS
    - typed lane: `7/7` PASS
    - illustration lane: `3/3` PASS
  - latest stability replay:
    - runs: `5/5` successful
    - decision stability: `15` stable, `0` flaky
- OCR lane classifier hardening checkpoint (March 29, 2026):
  - lane classification now detects embedded camera-style filenames
    (for example `file-...-IMG_6821.jpeg`) as handwriting
  - typed lane hint matching now uses bounded token matching (`ui` as a
    standalone word) to avoid accidental typed classification from substrings
    like `quick`
- UI shell retirement checkpoint (March 28, 2026):
  - active `ui/` folder and `/ui` route are removed from runtime surface
  - canonical active surfaces are backend API + CLI
  - historical frontend context remains in `.archive/live_archive/legacy_frontend/`
- Proactive ownership checkpoint (March 26, 2026):
  - engineer execution mode is action-first and proactive by default
  - technical hygiene/drift-control slices are executed without reminder
  - user prompts are reserved for approvals and material trade-offs
- Streamline-first command policy checkpoint (March 30, 2026):
  - command surfaces are consolidation-first (single canonical make target)
  - superseded aliases are removed in the same change to reduce stale-path drift
  - runtime/tooling edits close only after clean validation runs
- Transcript workflow automation checkpoint (March 30, 2026):
  - transcript format consistency now has dedicated tooling:
    - `make transcript-fix` (auto-normalise curated transcript records)
    - `make transcript-check` (validate canonical rich-format structure)
  - deterministic day-close routine is now available:
    - `make eod`
    - sequence: transcript-fix -> transcript-check -> doctor-env ->
      lint-docs -> test
- Morning startup guard checkpoint (March 29, 2026):
  - session startup now explicitly confirms worktree context
    (canonical root vs dedicated worktree)
  - branch + worktree isolation is required when parallel tracks run together
- Execution ownership checkpoint (March 29, 2026):
  - terminal/Git command execution is engineer-owned by default
  - imagineer remains objective/scope/acceptance/go-no-go owner
  - execution-first policy is active: requested actions are performed directly
- Human-managed co-reasoning checkpoint (March 26, 2026):
  - human remains work-management authority in reasoning loops
  - human controls objective/scope/acceptance + go/no-go cutlines
  - engineer executes proactive implementation/hygiene within that frame
- Eval runs no longer produce ambiguous generic `New chat` helper rows in the
  UI; generated eval chats now use deterministic session-id titles when
  retained.
- Parallel eval report orchestration is now available:
  - command: `make eval-reports-parallel`
  - tool: `tools/eval_parallel_orchestrator.py`
  - artifact: `eval_reports/parallel-<run_id>.json` plus per-suite logs/reports
- Playwright smoke E2E now validates retry-variant lineage behaviour end-to-end
  (assistant variant creation, `Variant X of Y` controls, and no duplicate user
  prompt rows in the rendered thread).
- Hallucination judge evaluation now supports configurable judge credentials and
  base URL (`--judge-api-key-env`, `--judge-base-url`) so OpenAI-compatible
  judge backends (including Braintrust gateways) can be wired without runtime
  behaviour changes.
- Hallucination score gating now supports configurable minimum threshold via
  `HALLUCINATION_MIN_ACCEPTABLE_SCORE`; report-based calibration helper is
  available through `make calibrate-hallucination-threshold`.
- Calibration tie-break now prefers the strictest threshold among equal-metric
  candidates, preventing under-conservative recommendations from all-pass
  datasets.
- P2 CLIP experiment scaffolding has started with
  `make eval-clip-ab` (baseline hybrid-source vs image-prioritized proxy arm).
- Latest P2 expanded run (2026-03-10, run `20260310-125230`) used 4
  image-context cases and showed stable proxy uplift:
  - baseline hybrid any-hit: `0.0`
  - image-priority proxy any-hit: `1.0`
  - delta (`proxy - baseline`): `+1.0`
  - errors: `0` in both arms
- Latest CLIP readiness pair (2026-03-15) is green:
  - `20260315-143219`: PASS (`cases=4`, `proxy_any_rate=1.000`,
    `delta=+1.000`, `errors=0`)
  - `20260315-180942`: PASS (`cases=4`, `proxy_any_rate=1.000`,
    `delta=+1.000`, `errors=0`)
- Latest readiness decision (2026-03-15): `GO`.
- CLIP go/no-go criterion is now explicit (two consecutive runs with
  `cases_count >= 4`, proxy `any_rate >= 0.90`, delta `>= 0.50`, zero errors)
  before integration escalation.
- Minimal CLIP proxy integration slice is now implemented behind feature flag:
  - `POLINKO_CLIP_PROXY_FILE_SEARCH_ENABLED` (default `false`)
  - `POST /skills/file_search` now accepts
    `retrieval_profile=clip_proxy_image_only`
  - disabled profile requests return `409` (explicit, reversible rollout)
  - enabled profile forces image-only retrieval path without changing default
    hybrid-source behaviour.
- Automated CLIP readiness gate is available via
  `make eval-clip-ab-readiness`; it inspects the latest two report artifacts
  and returns explicit `GO`/`NO-GO` against the D-040 threshold.
- Active operating mode is local-first glue-code + manual eval workflow, with
  runtime `/chat` behaviour unchanged.
- Collaboration policy checkpoint (March 21, 2026):
  - human judgment sets architecture/rubric first
  - multi-agent/parallel workflows are applied only after constraints are
    explicit and validation remains deterministic
- Reasoning Loops collaboration checkpoint (March 26, 2026):
  - `Reasoning Loops` is the canonical human-AI collaboration model term
  - imagineer leads hypotheses/theory framing + eval operation
  - engineer leads implementation/tooling/validation + execution recommendations
- Inspect-first checkpoint (March 26, 2026):
  - when context is noisy/ambiguous, execution pauses for inspection before
    cleanup/refactor
  - deprecated context stays in archive paths and does not drive active specs
  - directed precision mode is active for scoped changes to avoid unusable
    summary-first outputs
- `make hallucination-gate` now provides a dedicated strict hallucination gate
  run with managed local server startup; CI includes optional Braintrust gate
  wiring when repository vars/secrets are configured.
- Docker smoke is validated locally (`make docker-build` + `make docker-run` +
  `/health` probe).
- Devcontainer Docker connectivity is stabilised with Docker-outside-of-Docker
  support and UI-side Docker extension routing for reliable `Containers` view.
- Local IDE interpreter-path drift is now documented and resolved:
  host workspaces should not pin Python to container-built Linux venv binaries;
  use host interpreter auto-discovery (or explicit host Python) on macOS.
- Local environment doctor is available via `make doctor-env` for interpreter,
  import, and `zsh` completion checks.
- Python static analysis is now repo-scoped and stable:
  - `mypy.ini` is the single source of truth for mypy checks
  - workspace diagnostics run in `workspace` scope and use repo mypy config
  - generated/venv and high-noise test shim paths are excluded from default
    mypy reporting to keep signals actionable
- OCR supports a provider flag:
  - `POLINKO_OCR_PROVIDER=scaffold` (default fallback)
  - `POLINKO_OCR_PROVIDER=openai` (image OCR via OpenAI model)
- OCR supports optional `visual_context_hint` for deterministic image-context indexing
  (useful for eval seeding and controlled ingest).
- Transcript OCR mining now runs in stricter precision mode:
  - ask-side candidate phrases are only treated as correction anchors when
    correction signal is explicitly present
  - handwriting hint detection is token-bounded (prevents substring drift such
    as `Polinko` matching `ink`)
  - unstable transcript sources are quarantined from the active strict set
  - low-confidence review episodes are retained only when OCR signal is present
    (`ocr_literal_intent_signal`, `ocr_framing_signal`, `correction_signal`, or
    `correction_overlap_signal`)
  - OCR framing signal now excludes explicit negations
    (`no ocr`, `not ocr`, `without ocr`, `no transcription`)
  - review-summary baseline after latest offline rerun:
    `episodes=178` (`high=7`, `medium=27`, `low=144`)
  - active mined baseline: `26` cases (`handwriting=5`, `typed=11`,
    `illustration=10`)
  - active growth baseline: `148` cases
  - previous `55`/`29`/`25` mined outputs are retained as legacy reference for
    comparison, not as active strict gate input
- Transcript OCR benchmark and stability gates remain strict and green under
  the last complete lockset baseline:
  - full transcript lane: `21/21` PASS, stability `21 stable / 0 flaky`
  - handwriting benchmark: `4/4` PASS, stability `4 stable / 0 flaky`
  - typed benchmark: `6/6` PASS, stability `6 stable / 0 flaky`
  - illustration benchmark: `2/2` PASS, stability `2 stable / 0 flaky`
- Optional Responses API orchestration mode is implemented behind feature flags:
  - `POLINKO_RESPONSES_ORCHESTRATION_ENABLED`
  - `POLINKO_RESPONSES_VECTOR_STORE_ID`
  - optional web search + history-turn tuning flags
- File-search API responses now include explicit backend path metadata:
  `backend`, `fallback_reason`, and `candidate_count`.
- Hallucination eval harness now isolates each eval case in session-local scope to reduce cross-case memory bleed and improve determinism.
- Runtime session layer now uses managed SQLite session cleanup so cross-thread
  handles are closed deterministically (prevents late sqlite `ResourceWarning`
  noise in strict test runs).
- Eval harnesses support JSON report artifacts via `--report-json`
  (hallucination, style, retrieval, file-search, OCR).
- OCR ambiguity/recovery eval harness is available via
  `make eval-ocr-recovery` with case template
  `docs/eval/cases/ocr_recovery_eval_cases.json`.
- Evidence indexing now tracks FAIL remediation lifecycle with
  `recommended_action`, `action_taken`, `status`, and optional PASS-linked
  closure metadata.
- Adaptive runtime note selection now applies decay-weighted feedback scoring,
  near-duplicate suppression, and a max of two active notes, with note-change
  events logged as `adaptive_style_notes_updated` to prevent prompt/input
  over-indexing.
- Eval feedback/checkpoint state is persisted in SQLite only; no active
  `raw_evidence` intake file logging remains in runtime.
- Hallucination eval cases now include an interpersonal motive-guess regression
  guard (`uncertainty_required_no_relationship_motive_guess`) to catch speculative
  relationship attribution and enforce uncertainty-forward responses.
- Co-reasoning interaction guidance is now documented with a dedicated eval
  reference and PASS/FAIL mapping:
  - `docs/peanut/research/experiment_co_reasoning_eval_reference.md`
- Style eval cases now include co-reasoning stress scenarios for
  constraint-retention, meta-shift handling, anti-mimicry adaptation, and
  grounding-under-abstraction checks.
- Portfolio metadata audit tooling is available (`make portfolio-metadata-audit`)
  and validates evidence-index + evidence-log metadata completeness.
- Integration tests exist and pass locally (`tests/test_api.py`).
- Collaboration v1 supports explicit agent-role handoffs per chat with audit history.
- OCR growth remediation now has a focused replay lane:
  - build focused fail-derived subset: `make ocrfocuscases`
  - run focused stability replay: `make eval-ocr-focus-stability`
  - one-shot kernel: `make ocrfocus`
- Runtime DB null surfaces now have a read-only audit command:
  - `make nulls`
  - output: `.local/eval_reports/runtime_null_audit.{json,md}`
- Public-safe repo gate now exists:
  - `make public`
  - blocks tracked local/archive/private paths and secret markers before
    visibility changes.
  - includes `docs/peanut/` so hypothesis/method records remain local-only.

## Portfolio Timeline Snapshot (March 28, 2026)

- Engineering build completion estimate: `65-75%`
- Portfolio package completion estimate: `40-50%`
- Overall project completion estimate (apply-ready target): `55-65%`
- Remaining horizon at current pace: `3-5 weeks`
- Milestone sequence:
  - `1-2 weeks`: backend hardening + eval flow stability + minimal operator surface
  - `1-2 weeks`: benchmark cycles + evidence tables/figures + findings lock
  - `~1 week`: final case-study/research-paper assembly for portfolio handoff

## Key Files

- Prompt version + active prompt: `core/prompts.py`
- CLI chat runner: `app.py`
- Backend entrypoint: `server.py`
- API app factory + routes: `api/app_factory.py`
- Architecture guide: `docs/runtime/ARCHITECTURE.md`
- API tests: `tests/test_api.py`
- Local API client: `tools/client.py`
- Environment doctor: `tools/doctor_env.py`
- Evidence index builder: `tools/build_evidence_index.py`
- Portfolio metadata auditor: `tools/audit_portfolio_metadata.py`
- Hallucination threshold calibrator: `tools/calibrate_hallucination_threshold.py`
- CLIP A/B eval harness: `tools/eval_clip_ab.py`
- Parallel eval orchestrator: `tools/eval_parallel_orchestrator.py`

## Known Constraints

- Network-dependent API calls may fail in restricted environments (handled as
  503 in API / friendly error in CLI).
- Cloud deployment automation is intentionally paused and previous AWS scripts
  were removed from the repo; Azure is the preferred target when deployment
  work resumes.
- Dependabot PR `#13` (`openai-agents==0.11.1`) is blocked until OpenAI SDK pin
  is raised first (`openai>=2.26.0` via PR `#5`); merge order matters.
- Style eval strict gate is currently sensitive to model-output drift on low
  context greeting/mimicry rubric cases; keep it monitored as a quality signal,
  but treat as non-runtime-regression unless corroborated by API/unit failures.

## Resume Prompt (For New Chats)

Use this in a new chat:

`Read docs/governance/CHARTER.md, docs/governance/STATE.md, and docs/governance/DECISIONS.md. Summarise current status in 5 bullets, list top risks, and execute the single highest-leverage next step. Preserve prompt behaviour rules.`

## Suggested Next Steps

1. Execute benchmark `D` (operation-binding diagnostics) and map outcomes to one
   deterministic backend slice (next slice after harness mode is diagnostics telemetry).
2. Keep binary gate semantics strict (`pass`/`fail`) and keep diagnostic richness
   outside gate arithmetic.
3. Maintain archive-first runtime DB posture during wiring lock (no local DB
   lifecycle command paths).
4. Continue local-first deterministic validation (`make lint-docs`, `make test`,
   `make quality-gate-deterministic`) at each
   milestone.
5. Keep benchmark outputs product-supportive by converting findings into
   explicit implementation priorities.

## Planning Pointers

- Cookbook adoption planning is maintained in:
  - `docs/runtime/RUNBOOK.md`
- Immediate execution plan is maintained in:
  - `docs/governance/SESSION_HANDOFF.md` (`Immediate Next Step`)
