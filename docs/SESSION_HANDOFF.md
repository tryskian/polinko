<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-20

## Current Snapshot

- Runtime: FastAPI backend + Vite UI + CLI runner.
- Prompt behavior stays minimal and aligned to legacy `try.py` style.
- Optional Responses orchestration path is available behind env flags.
- Governance and hallucination guardrails are now available behind env flags.
- Per-scope retrieval tuning is implemented and validated in API flow.
- Collaboration v1 is live with explicit role handoff endpoints + per-chat handoff timeline.
- Personalization v1 is live: per-chat retrieval memory scope (`session` or `global`).
- Personalization scope is now controllable from the web UI header (per active chat).
- `/chat` now returns `memory_used` retrieval citations when vector context is applied.
- OCR is feature-flagged:
  - `POLINKO_OCR_PROVIDER=scaffold` (default fallback)
  - `POLINKO_OCR_PROVIDER=openai` (real image OCR path)
- API now includes `/metrics` and chat export with OCR runs.
- Session/resource cleanup improved by explicitly closing per-request SQLite sessions.
- Runtime session cleanup hardened with a managed SQLite session wrapper that closes
  cross-thread connections on `close()`.
- Retrieval evaluator is now available (`make eval-retrieval`) and currently passes all 12 cases.
- OCR/PDF structured extraction now fail-open on malformed/unexpected enrichment errors.
- File-search API now returns backend/fallback classification (`backend`,
  `fallback_reason`, `candidate_count`) for deterministic client-side diagnostics.
- Hallucination eval harness now enforces session-local memory scope per case to reduce nondeterministic cross-case leakage.
- Single-command quality gate is available and passing: `make quality-gate`.
- Hallucination judge path now supports configurable key env + base URL for
  OpenAI-compatible judge providers (including Braintrust gateway wiring).
- Hallucination score threshold is now configurable with
  `HALLUCINATION_MIN_ACCEPTABLE_SCORE`; calibration helper is available via
  `make calibrate-hallucination-threshold`.
- Calibration tie-break now prefers the strictest equal-metric threshold to
  avoid under-conservative recommendations from all-pass datasets.
- P2 CLIP experiment scaffolding has started with `make eval-clip-ab` and
  report artifact mode `make eval-clip-ab-report`.
- Latest CLIP A/B expanded report (`20260310-125230`) shows positive proxy
  uplift across 4 image-context cases
  (`any_rate_delta_proxy_minus_baseline=+1.0`, `errors=0`, `skipped=0`).
- Latest CLIP readiness pair (2026-03-14) passed and returned explicit `GO`:
  - `clip-ab-20260315-143219.json`
  - `clip-ab-20260315-180942.json`
  - readiness command: `make eval-clip-ab-readiness`
- Latest targeted CLIP/file-search validation cycle (2026-03-15):
  - strict style eval: `style-strict-20260315-180637.json` (`11/11` PASS)
  - file-search report: `file-search-20260315-181109.json` (`5/5` PASS)
  - targeted API profile checks:
    `./venv/bin/python -m pytest tests/test_api.py -k "clip_proxy_profile" -q`
    -> `2 passed`
  - runtime regression baseline:
    `make test` -> `154 passed`
  - drift isolation result:
    no strict-style drift reproduced in this cycle; treat style drift as a
    monitored quality signal unless corroborated by runtime/API regressions.
- Status checkpoint (2026-03-17):
  - project is in late build-hardening phase (not early scaffold phase)
  - core runtime + binary eval flow are stable and merged on `main`
  - remaining work is concentrated in backlog triage, hybrid pilot cycle
    completion, and final portfolio evidence packaging
- Hybrid OpenAI adoption planning now has a no-risk gate command:
  - `make hybrid-openai-readiness`
  - checker source: `tools/check_hybrid_openai_readiness.py`
  - plan doc: `docs/HYBRID_OPENAI_ADOPTION_PLAN.md`
- Hybrid OpenAI adoption Phase 2 (trace artifact contract) is now implemented:
  - shared trace module: `tools/eval_trace_artifacts.py`
  - schema: `polinko.eval_trace.v1`
  - append-only evidence path:
    `docs/portfolio/raw_evidence/INBOX/eval_trace_artifacts.jsonl`
  - report-oriented eval tooling and hybrid readiness checker now append trace
    artifacts without `/chat` runtime behavior changes.
- Hybrid OpenAI adoption Phase 3 scope is now documented as tooling-only:
  offline trace/grader metadata bridge only, with runtime `/chat` and prompt
  behavior explicitly out of scope.
- Hybrid OpenAI Phase 3 dry-run scaffold is now implemented:
  - tool: `tools/hybrid_openai_trace_bridge.py`
  - command: `make hybrid-openai-pilot-dry-run`
  - default: flag-off skip (`HYBRID_OPENAI_PILOT_ENABLED=false`)
  - output preview:
    `docs/portfolio/raw_evidence/INBOX/openai_trace_bridge_preview.jsonl`
- Hybrid OpenAI Phase 3 now includes trace-source backfill and preview quality checks:
  - backfill: `make backfill-eval-traces`
  - preview check: `make hybrid-openai-pilot-check`
  - full cycle: `make hybrid-openai-pilot-cycle`
  - latest local result (2026-03-20): `79` source submissions ->
    `79` trace rows -> `84` transformed preview rows per run
    (`135` rows in append-only preview artifact, `OK` check)
  - payload-shape check outcome (2026-03-20):
    no metadata-field refinements required before provider-side pilot wiring
- Hybrid OpenAI Phase 3 provider-side pilot helper is now implemented (still tooling-only):
  - helper: `tools/prepare_openai_eval_pilot.py`
  - prepare-only command:
    `make hybrid-openai-prepare-pilot-payloads`
  - optional execute command:
    `make hybrid-openai-execute-pilot`
  - latest local result (2026-03-20):
    - export dataset rows: `85`
    - payload prep: `OK` (manual-first, no API calls)
- CLIP integration go/no-go criterion is now defined and documented
  (two consecutive runs, `cases_count >= 4`, proxy `any_rate >= 0.90`,
  delta `>= 0.50`, zero errors/skips).
- Minimal CLIP integration slice is now live behind explicit feature flag:
  - `POLINKO_CLIP_PROXY_FILE_SEARCH_ENABLED` (default `false`)
  - `/skills/file_search` accepts
    `retrieval_profile=clip_proxy_image_only`
  - disabled profile requests fail fast with `409` for explicit rollback-safe
    control.
- Profile behavior is API-tested:
  - disabled flag -> `409` on `clip_proxy_image_only`
  - enabled flag -> profile forces image-only retrieval even when request
    `source_types` includes only `ocr`.
- Dedicated strict hallucination gate target is available: `make hallucination-gate`.
- CI includes optional Braintrust hallucination gate wiring when
  `BRAINTRUST_OPENAI_BASE_URL` (repo var) and `BRAINTRUST_API_KEY`
  (repo secret) are configured.
- Docker smoke path is validated (`make docker-build` + `make docker-run` + `/health`).
- Devcontainer Docker connectivity is now stabilized (Docker-outside-of-Docker
  and Docker extension UI-side routing), resolving `Containers` pane connection
  mismatch in remote sessions.
- Next-session setup reminder: start with a plain-language Docker MCP refresher
  before config changes (`server` = capability provider, `client` = app allowed
  to call it, profile `push` = optional sync/share action).
- Host-side VS Code interpreter warnings were resolved by removing stale
  workspace interpreter pins to Linux container venv binaries; host sessions
  now rely on host interpreter auto-discovery/selection.
- Environment doctor is available for local sanity checks: `make doctor-env`.
- Evidence indexing now records FAIL lifecycle state (`action_taken`, `status`)
  and supports optional triage overrides until a linked PASS closes the issue.
- Portfolio metadata audit is now available via
  `make portfolio-metadata-audit` for strict evidence/docs metadata checks.
- Adaptive style-note handling now uses decay-weighted signal, near-duplicate
  note suppression, and a max of two active notes with
  `adaptive_style_notes_updated` event logging to avoid model-input
  over-indexing from repeated guidance.
- Co-reasoning interaction behaviour is now documented with primary-source and
  rubric references:
  - `docs/transcripts/co_reasoning_primary_source_2026-03-10.md`
  - `docs/research/co_reasoning_eval_reference.md`
- Style eval cases now include co-reasoning stress scenarios (constraint
  retention without rigidity, meta-shift handling, anti-mimicry adaptation, and
  grounding under playful abstraction).
- Frontend Playwright smoke E2E includes retry-variant lineage coverage
  (`source_user_message_id` flow), including variant navigation and duplicate
  user-row prevention assertions.
- Frontend attachment flow now supports paste-to-attach, client-side
  downsize/compression, per-chat image persistence across chat switches/reloads,
  and OCR follow-up turns that reuse the latest persisted image batch when no
  new image is attached.
- Frontend chat drawer now includes eval review queue controls:
  sort (`recent`, `unreviewed`, `fail_ratio`) plus `unreviewed only` filter for
  faster checkpoint triage.
- Eval feedback submissions are append-logged for binary outcomes
  (`PASS`/`FAIL`) to
  `docs/portfolio/raw_evidence/INBOX/eval_submissions.jsonl` with inbox monitor
  command `make eval-inbox`.
- Hallucination eval corpus now includes interpersonal motive-guess regression
  case `cautious_no_relationship_motive_guess` to catch speculative
  relationship-attribution claims.
- Branch rules now enforce PR + required checks (`test`, `markdownlint`) on
  default branch (`main`) while allowing normal push/PR workflow on feature
  branches.
- `docs/FIGMA_NODE_TRACKER.md` is now intentionally local-only and gitignored
  for proprietary/live node-tracking use.
- Environment troubleshooting now follows a verification-first, no-guessing
  policy: verify repo path/mode/branch first, prefer repo-scoped config
  changes, and do not mutate `~/.zshrc` or global VS Code settings without
  explicit in-chat approval.
- Ruff housekeeping is green (`ruff check .`) after preserving
  `server.Runner` for test patch compatibility and resolving import placement.
- Mypy housekeeping is now stable and repo-scoped via `mypy.ini`; workspace
  diagnostics are bound to `venv/bin/mypy` + `--config-file mypy.ini`.
- Dependabot dependency-order note: `openai-agents==0.11.1` (PR `#13`) requires
  `openai>=2.26.0`; merge PR `#5` (`openai` bump) before retrying PR `#13`.

## Latest Local Commit

- `5557809` on `main` (local branch synced with `origin/main`)
- Summary: Merge pull request #51 from
  tryskian/codex/bigbrain/openai-evals-exporter

## Key Files To Read First

- `docs/CHARTER.md`
- `docs/STATE.md`
- `docs/DECISIONS.md`
- `api/app_factory.py`
- `config.py`
- `tests/test_api.py`

## Quick Validation (Local)

1. `make quality-gate`
2. `make quality-gate-deterministic` (if judge key is unavailable)
3. `make hallucination-gate HALLUCINATION_EVAL_MODE=deterministic`
4. `make doctor-env`
5. `make eval-inbox`
6. `cd frontend && npm run build`
7. `make portfolio-metadata-audit`
8. `cd frontend && npx playwright test e2e/smoke.spec.js`
9. `make server` and spot-check `/health`, `/chat`, `/skills/ocr`

## Known Constraint

- No open high-priority runtime constraints currently tracked.
- Workflow constraint: user-level shell/profile and global editor settings are
  immutable by default during normal repo troubleshooting.
- Dependency-management constraint: open Dependabot updates can fail CI when
  resolver-coupled pins land out of order; verify transitive constraints before
  merging isolated bump PRs.
- Session policy constraint: keep-awake is opt-in and request-triggered,
  managed with `make caffeinate-on`, checked with `make caffeinate-status`,
  and explicitly stopped at wrap via
  `make caffeinate-off`.
- Terminology constraint: when Docker MCP wording is ambiguous, confirm intent
  in-chat before applying config changes.

## Immediate Next Step

- Execute one provider-side pilot pass (no runtime migration):
  - keep current runtime/API behavior unchanged
  - run `make hybrid-openai-prepare-pilot-payloads`
  - run `make hybrid-openai-execute-pilot` (or provide
    `HYBRID_OPENAI_PILOT_FILE_ID=<file_id>` to skip upload)
  - capture returned `eval_id`, `run_id`, and `report_url` in evidence docs

## Peanut Pin (Tomorrow Start)

- Merge watch first:
  - check PR status + CI on `#38` (CLIP proxy file-search slice)
- If you want fast human-reference lookup without SQL editor:
  - `make human-reference-latest`
  - `make human-reference-transcripts`
  - `make human-reference-changes`
- Keep startup lightweight:
  - confirm repo path + branch + host/devcontainer mode
  - then continue with the Immediate Next Step above

## Next Session Focus (Lean Agenda)

1. Confirm environment baseline:
   canonical repo path, host vs devcontainer mode, active branch.
2. Merge/sync hygiene:
   ensure docs PR state is settled, then `main` is clean and up to date.
3. Execute CLIP readiness loop:
   produce artifacts + readiness decision and store evidence.
4. Decide hybrid OpenAI tooling scope (no runtime migration yet):
   evals/tracing/optimizer adoption plan with zero behavior drift.
5. Document only material decisions:
   update `STATE` + `DECISIONS` + `SESSION_HANDOFF` with concise diffs.

## Copy/Paste Rehydrate Prompt

`Read docs/CHARTER.md, docs/STATE.md, docs/DECISIONS.md, and docs/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, and confirm active git branch. Apply no-guessing controls: prefer repo-scoped edits and do not modify ~/.zshrc or global VS Code settings unless explicitly approved in-chat. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behavior drift and full test/build validation.`
