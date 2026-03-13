<!-- @format -->

# Session Handoff (Rehydrate Brief)

## Date

- 2026-03-11

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
- CLIP integration go/no-go criterion is now defined and documented
  (two consecutive runs, `cases_count >= 4`, proxy `any_rate >= 0.90`,
  delta `>= 0.50`, zero errors/skips).
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
- Eval feedback submissions are append-logged for every outcome
  (`PASS`/`PARTIAL`/`FAIL`) to
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

- `7bfd1b1` on `main` (local branch currently ahead of `origin/main` by 4
  commits)
- Summary: docs: track interpersonal motive-guess hallucination case in state

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
- Session policy constraint: keep-awake is opt-in and code-phrase triggered
  only (`hi! new day!`), with explicit stop at wrap (`pkill -f "caffeinate -d -i -m"`).
- Terminology constraint: when Docker MCP wording is ambiguous, confirm intent
  in-chat before applying config changes.

## Immediate Next Step

- Add automated criterion check for CLIP escalation readiness:
  - implement a small script/target to compare latest two CLIP A/B reports
  - return explicit `GO`/`NO-GO` based on D-040 thresholds
  - run full validation (`tests + make eval-clip-ab-report`) and capture output

## Copy/Paste Rehydrate Prompt

`Read docs/CHARTER.md, docs/STATE.md, docs/DECISIONS.md, and docs/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next milestone. Before starting implementation, confirm environment/workspace context: canonical repo path is /Users/tryskian/Github/polinko, confirm host vs devcontainer mode, and confirm active git branch. Apply no-guessing controls: prefer repo-scoped edits and do not modify ~/.zshrc or global VS Code settings unless explicitly approved in-chat. Then execute the Immediate Next Step from SESSION_HANDOFF with minimal behavior drift and full test/build validation.`
