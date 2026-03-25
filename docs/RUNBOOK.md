<!-- @format -->

# Runbook

## Branch, Fork, and Worktree Policy

1. Default workflow is branch-based in the canonical local repo:
   - `/Users/tryskian/Github/polinko`
2. Do not fork this repository for normal day-to-day project work.
3. Create a task branch per change set:
   - `git switch -c codex/bigbrain/<task-name>`
4. Use a worktree only when you need parallel active tracks (for example:
   CI calibration in one tree and feature scaffold in another):
   - `git worktree add /Users/tryskian/Github/polinko-<task> -b codex/bigbrain/<task> main`
5. Keep one logical task per branch; merge or close before starting the next.

## Worktrees vs Multi-Agents (Operating Rule)

1. Worktree-first for code changes:
   - use a separate worktree/branch when two implementation tracks can conflict.
   - keep each worktree scoped to one logical change set.
2. Multi-agent is for parallel analysis, not blind merge:
   - good for eval triage, log scanning, and draft synthesis.
   - route all final merge decisions through one director thread.
3. Architecture-first gate:
   - do not start multi-agent parallelization until architecture, acceptance
     criteria, and rubric constraints are explicit.
   - before that point, stay in intentional single-stream execution.
4. Practical split:
   - implementation parallelism => `git worktree`
   - analysis parallelism => multi-agent delegation
5. Peanut version:
   - `worktree` = separate desk with its own files/branch
   - `multi-agent` = extra hands doing bounded subtasks
   - `director` = one final decider before merge

## Protected Main PR Flow

1. Do not push directly to `main` (protected branch rules require PR + checks).
2. Work on a feature/chore branch:
   - `git switch -c <branch-name>`
3. Commit locally, then push branch:
   - `git push -u origin <branch-name>`
4. Open PR to `main` and wait for required checks:
   - `test`
   - `markdownlint`
5. Merge PR, then sync local `main`:
   - `git switch main`
   - `git pull --ff-only`
6. If direct push returns `GH013`, treat it as expected branch protection
   behaviour and continue via PR flow.

## Repo vs Container Working Modes

1. Canonical source of truth is always:
   - `/Users/tryskian/Github/polinko`
2. Host mode (default):
   - Open and work directly in the canonical path.
   - Best for fast iteration and stable Codex thread/workspace mapping.
3. Devcontainer mode (when needed):
   - Use `Reopen in Container` on the canonical repo.
   - This keeps one checkout and mounts the same files into the container.
4. Avoid `Clone in Volume` unless you explicitly want a separate checkout.
   - Volume clones create a second workspace copy and can cause context drift.
5. Do not mix multiple workspace roots for the same task session
   (host path + container clone + alternate workspace file), or thread opening
   and IDE handoff can become inconsistent.

## Local-Only Internal Docs Policy

1. Non-build internal docs are local-only by default and ignored by git.
2. Use these local-only paths for confidential notes/material:
   - `docs/FIGMA_NODE_TRACKER.md`
   - `docs/WORKSTREAMS.md`
   - `docs/PEANUT_TOOLING_REF.md`
   - `docs/internal/`
   - `docs/research/`
   - `docs/theory/`
   - `docs/transcripts/`
   - `docs/portfolio/`
3. Build/source-of-truth docs stay tracked:
   - `docs/CHARTER.md`
   - `docs/ARCHITECTURE.md`
   - `docs/RUNBOOK.md`
   - `docs/STATE.md`
   - `docs/DECISIONS.md`
   - `docs/SESSION_HANDOFF.md`
4. Do not use `skip-worktree` for routine workflow; use gitignored local-only
   paths instead.
5. Any exception to local-only confidentiality must be explicitly approved
   in-chat before being committed.

## Rotate API Keys

1. Update `.env` with new `OPENAI_API_KEY`.
2. If used, rotate `POLINKO_SERVER_API_KEY` and/or update
   `POLINKO_SERVER_API_KEYS_JSON`.
3. Restart running API/CLI processes.

## Environment Doctor

1. Run `make doctor-env`.
2. Review warnings:
   - `VIRTUAL_ENV is not set` is expected when using `make`.
   - `python` is not on PATH is informational when only `python3` is
     available.
3. Resolve actionable issues (missing imports, interpreter mismatch, or
   `compaudit` findings) before running evals.

## Python Diagnostics (Ruff + Mypy)

1. Use repo-local tools for deterministic output:
   - `venv/bin/ruff check .`
   - `venv/bin/mypy . --config-file mypy.ini`
2. `mypy.ini` is the canonical type-check config for this repo.
3. VS Code should use workspace-wide diagnostics (not only active file).
4. If Problems panel looks stale after config changes:
   - `Mypy: Restart Server`
   - `Developer: Reload Window`
5. Ensure Problems view is not filtered to active file only.

## Optional Keep-Awake Session Policy

1. Default state is off (do not run `caffeinate` unless requested).
2. Start keep-awake only when explicitly requested in-session.
3. Start command:
   - `make caffeinate-on`
4. Verify status:
   - `make caffeinate-status`
5. Stop command at wrap:
   - `make caffeinate-off`
6. `decaffeinated` remains workflow shorthand. The explicit command is
   `make caffeinate-off`.

## Docker Build/Run Smoke

1. Build image: `make docker-build`.
2. Run container: `make docker-run`.
3. Probe health:
   - `curl -fsS http://127.0.0.1:8000/health`
4. If the container exits immediately:
   - confirm `.env` includes required values (`OPENAI_API_KEY`).
   - check logs:
     - `docker ps -a`
     - `docker logs <container_id>`
5. `.env` supports both `KEY=value` and quoted `KEY="value"` styles.

## Docker MCP Terms (Plain Language)

1. `Server` = capability provider (for example, Playwright or GitHub MCP).
2. `Client` = app allowed to call those servers (for example, `Codex`,
   `Visual Studio Code`).
3. `Push profile` = optional Docker profile sync/share action; not required for
   normal local project work.
4. Recommended default:
   - keep `Codex` + `Visual Studio Code` clients enabled if you use both apps.
   - enable only the MCP servers needed for the current workflow.
   - skip profile push unless you intentionally want cloud/shared profile sync.
5. If wording is unclear in the UI, pause and confirm intent before changing
   client/server mappings.

## OpenAI MCP Setup (Active)

1. OpenAI docs MCP endpoint:
   - `https://developers.openai.com/mcp`
2. Local wiring targets:
   - user-level Codex config (`~/.codex/config.toml`)
   - workspace config (`.vscode/mcp.json`)
3. Active rule:
   - use OpenAI docs MCP for documentation lookup
   - keep local repo runtime/eval stack as implementation source of truth

## Playwright E2E

1. Install frontend deps (if needed):
   - `make ui-install`
2. Install Playwright browsers once per machine/container:
   - `make ui-e2e-install`
3. Run E2E suite:
   - `make ui-e2e`
4. Run in headed mode (direct npm):
   - `cd frontend && npm run test:e2e:headed`
5. Current E2E tests use mocked API responses so they run without starting
   the backend server.
6. Retry-variant regression coverage is in:
   - `frontend/e2e/smoke.spec.js`
   - run targeted: `cd frontend && npx playwright test e2e/smoke.spec.js`

## Tooling Baseline

1. Install local CLIs (macOS/Homebrew):
   - `brew install act k6 trivy`
2. `Dependabot` is configured in `.github/dependabot.yml` for:
   - GitHub Actions (`/`)
   - Python (`/`)
   - npm (`/frontend`)
3. Install and run `pre-commit`:
   - `make precommit-install`
   - `make precommit-run`
4. Run CI workflow locally with `act`:
   - list jobs: `make act-list`
   - run CI workflow: `make act-ci`
5. Run k6 chat smoke load test (requires local API server running):
   - default: `make k6-chat-smoke`
   - custom: `make k6-chat-smoke K6_BASE_URL=http://127.0.0.1:8000 K6_API_KEY=<key> K6_VUS=5 K6_DURATION=30s`
6. Run Trivy security scans:
   - filesystem dependencies/secrets/misconfig: `make trivy-fs`
   - built image: `make trivy-image`

## Parallel Eval Orchestration

1. Run report eval suites in parallel:
   - `make eval-reports-parallel`
2. Output artifacts:
   - per-suite reports in `eval_reports/`
   - per-suite logs in `eval_reports/`
   - consolidated summary in `eval_reports/parallel-<run_id>.json`
3. This command parallelizes compute only:
   - it does not auto-promote decisions.
   - use one director review step before acting on results.

## Devcontainer Troubleshooting

1. After changing `.devcontainer/devcontainer.json`, run:
   - `Dev Containers: Rebuild and Reopen in Container`
2. If `Remote Explorer > Dev Containers` shows connected but the Docker
   `Containers` tab says `Failed to connect`:
   - run `Developer: Reload Window`
   - confirm Docker extension runs on UI host via
     `remote.extensionKind.ms-azuretools.vscode-docker=["ui"]`
3. Validate from the devcontainer terminal:
   - `docker version`
4. If still broken, check Docker Desktop is running on host and retry rebuild.

## Python Interpreter Path (Host vs Container)

1. Do not pin a host VS Code interpreter to a devcontainer-created venv path
   if that venv was built inside Linux.
   - Example bad host pin: `/Users/.../polinko-repositioning-system/bin/python`
   - Symptom: `Could not resolve interpreter path` / `Unable to handle .../bin/python`
2. Root cause:
   - host macOS cannot execute Linux ELF binaries (`exec format error`).
3. On host mode:
   - prefer Python extension auto-discovery, or explicitly select a macOS
     interpreter (for example `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`).
4. On devcontainer mode:
   - use container interpreter paths only (for example
     `${containerWorkspaceFolder}/venv/bin/python3`).
5. If warnings persist:
   - remove stale `python.defaultInterpreterPath` entries from local workspace
     settings/workspace files.
   - run `Developer: Reload Window`.

## Agent-Safe Environment Changes (No-Guessing Policy)

1. Verify context before any env/tooling mutation:
   - `pwd` must be `/Users/tryskian/Github/polinko` (canonical repo path).
   - confirm mode: host vs devcontainer.
   - confirm branch: `git rev-parse --abbrev-ref HEAD`.
2. Prefer repo-scoped changes first:
   - `.vscode/settings.json`
   - `.devcontainer/devcontainer.json`
   - repo scripts/Make targets
3. Do not modify user-level shell/profile or global editor config without
   explicit approval in-chat:
   - `~/.zshrc`, `~/.zprofile`, `~/.bashrc`
   - `~/Library/Application Support/Code/User/settings.json`
4. Do not introduce auto-start shell hooks (for example `chpwd` +
   `make server`) unless explicitly requested and documented in the repo.
5. If a rogue/accidental agent change is suspected, run triage in this order:
   - inspect tracked repo changes (`git status`, `git diff`)
   - inspect suspicious files/symlinks inside repo only
   - restore tracked files from git first, then re-run `make doctor-env`
6. Treat unknown binary/corrupt artifact files as suspect; do not "repair" by
   guessing content. Remove/replace only after provenance is confirmed.

## Reset Local Session Memory

1. Stop running processes.
2. Remove local DB files:
   - `.polinko_memory.db`
   - `.polinko_memory.db-shm` (if present)
   - `.polinko_memory.db-wal` (if present)
   - `.polinko_history.db`
   - `.polinko_history.db-shm` (if present)
   - `.polinko_history.db-wal` (if present)
   - `.polinko_vector.db` (if present)
   - `.polinko_vector.db-shm` (if present)
   - `.polinko_vector.db-wal` (if present)
3. Start app again (`make chat` or `make server`).

## Reset One Chat Session (API)

1. Set mode in `.env`:
   - `POLINKO_DEPRECATE_ON_RESET=true` (tuning mode)
   - `POLINKO_DEPRECATE_ON_RESET=false` (clear in-place mode)
2. Send `POST /session/reset` with `{"session_id":"your-chat-id"}`.
3. If needed, force deprecate regardless of env:
   `{"session_id":"your-chat-id","deprecate":true}`.
4. Deprecated chats are hidden from default `GET /chats`.
5. To include them for review: `GET /chats?include_deprecated=true`.
6. A non-deprecating reset clears both:
   - conversation memory in `.polinko_memory.db`
   - persisted chat messages in `.polinko_history.db`
   - vector memories for that session in `.polinko_vector.db` (when enabled)
7. Deprecation/reset is chat lifecycle state management, not model-weights
   training or a direct runtime penalty signal.

## Chat History API

- `GET /chats` list chats
- `POST /chats` create chat
- `GET /chats/{session_id}/messages` load chat messages
- `GET /chats/{session_id}/export` export transcript (+ OCR runs)
- `POST /chats/{session_id}/notes` add internal preference note
- `POST /chats/{session_id}/personalization` set retrieval memory scope
  (`session` or `global`)
- `GET /chats/{session_id}/personalization` read effective retrieval memory
  scope
- `GET /chats/{session_id}/collaboration` view active collaborator + handoff
  timeline
- `POST /chats/{session_id}/collaboration/handoff` apply active role handoff
- `POST /chats/{session_id}/deprecate` deprecate a chat
- `PATCH /chats/{session_id}` rename chat
- `DELETE /chats/{session_id}` delete chat and clear memory
- `POST /chat` returns `memory_used` citations (vector snippets + source
  metadata) when retrieval is used
- `POST /skills/ocr` run OCR (scaffold or OpenAI mode, includes
  `run.structured` with `enrichment_status` and `fallback_reason`; optional
  `transcription_mode=verbatim|normalized`)
- `POST /skills/pdf_ingest` extract and index PDF text into vector memory
  (includes `structured` with `enrichment_status` and `fallback_reason`, plus
  Responses index metadata: `responses_index_status`,
  `responses_index_reason`, `responses_vector_store_file_id`)
- `POST /skills/file_search` search indexed vector content (OCR/chat sources,
  includes `backend`, `fallback_reason`, and `candidate_count`)
- `GET /metrics` request counters, status counts, latency buckets, rate-limit
  totals

Hash fields in responses:

- `messages[*].content_sha256` is a deterministic SHA-256 hash of message
  content.
- `export.transcript_sha256` is a deterministic SHA-256 fingerprint over ordered
  message lineage + content hashes.

## OCR Provider Toggle

1. In `.env`, set:
   - `POLINKO_OCR_PROVIDER=scaffold` for fallback mode (default)
   - `POLINKO_OCR_PROVIDER=openai` for model OCR
2. Optional OCR settings:
   - `POLINKO_OCR_MODEL` (default `gpt-4.1-mini`)
   - `POLINKO_OCR_PROMPT` (custom extraction prompt)
   - `POLINKO_OCR_UNCERTAINTY_SAFE` (default `true`; maps speculative guesses
     to `[?]`)
   - `POLINKO_IMAGE_CONTEXT_ENABLED` (default `false`, best-effort visual-scene
     extraction for retrieval)
   - `POLINKO_IMAGE_CONTEXT_MODEL` (default `gpt-4.1-mini`)
   - `POLINKO_IMAGE_CONTEXT_PROMPT` (custom visual context prompt)
3. Restart API after changing provider settings.
4. If vector memory is enabled, OCR outputs are chunked and indexed
   automatically with OCR metadata.

## File Search (Vector Index)

1. Ensure vector memory is enabled (`POLINKO_VECTOR_ENABLED=true`) and restart
   API.
2. Index content first (for example via `POST /skills/ocr`).
3. Search with `POST /skills/file_search`:
   - required: `query`
   - optional: `session_id` to scope results to one chat
   - optional: `limit` (default `5`, max `20`)
   - optional: `source_types` (`["ocr"]`, `["chat"]`, or both)
   - optional: `retrieval_profile` (`default` or `clip_proxy_image_only`)
4. Results include backend/fallback metadata plus similarity, keyword score,
   combined score, snippet, and source metadata.
5. `source_types` now supports `ocr`, `chat`, `pdf`, and `image`.
6. CLIP proxy profile rollout toggle:
   - `POLINKO_CLIP_PROXY_FILE_SEARCH_ENABLED=false` (default)
   - when `false`, `retrieval_profile=clip_proxy_image_only` returns `409`
   - when `true`, `clip_proxy_image_only` forces image-only retrieval.

## PDF Ingest (Vector Index)

1. Ensure vector memory is enabled (`POLINKO_VECTOR_ENABLED=true`) and restart
   API.
2. Ensure PDF parser dependency is available:
   - `pip install pypdf`
3. Ingest with `POST /skills/pdf_ingest`:
   - required: `data_base64` (PDF bytes)
   - optional: `session_id`, `source_name`, `mime_type` (`application/pdf`)
   - optional: `attach_to_chat` (default `true`)
4. Search indexed PDF chunks with `POST /skills/file_search` and
   `source_types: ["pdf"]`.
5. Optional: enable best-effort upload into your OpenAI Responses vector store:
   - `POLINKO_RESPONSES_PDF_INGEST_ENABLED=true`
   - Requires `POLINKO_RESPONSES_VECTOR_STORE_ID=vs_...`
6. Response payload explicitly reports Responses indexing outcome:
   - `responses_index_status`: `disabled|indexed|failed`
   - `responses_index_reason`: reason code when disabled/failed
   - `responses_vector_store_file_id`: populated when indexed

## Vector Memory Toggle

1. In `.env`, set:
   - `POLINKO_VECTOR_ENABLED=true` to enable retrieval memory
2. Optional vector settings:
   - `POLINKO_VECTOR_DB_PATH` (default `.polinko_vector.db`)
   - `POLINKO_VECTOR_EMBEDDING_MODEL` (default `text-embedding-3-small`)
   - `POLINKO_VECTOR_TOP_K` (default `2`)
   - `POLINKO_VECTOR_MIN_SIMILARITY` (default `0.40`)
   - `POLINKO_VECTOR_MAX_CHARS` (default `220`)
   - `POLINKO_VECTOR_EXCLUDE_CURRENT_SESSION` (default `true`)
   - `POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK` (default `false`, enables local
     deterministic embedding fallback on transient API connection/5xx failures)
3. Restart API after changing vector settings.
4. Chat retrieval currently uses chat-response vectors for tone consistency;
   OCR/image vectors are stored with metadata for search/retrieval workflows.

## Responses Orchestration Toggle (RAG)

1. In `.env`, set:
   - `POLINKO_RESPONSES_ORCHESTRATION_ENABLED=true`
   - `POLINKO_RESPONSES_VECTOR_STORE_ID=vs_...`
2. Optional settings:
   - `POLINKO_RESPONSES_MODEL` (default `gpt-5-chat-latest`)
   - `POLINKO_RESPONSES_INCLUDE_WEB_SEARCH` (`true`/`false`)
   - `POLINKO_RESPONSES_HISTORY_TURN_LIMIT` (default `12`)
   - `POLINKO_RESPONSES_PDF_INGEST_ENABLED` (`true`/`false`, requires vector
     store id)
3. Restart API after changing orchestration settings.
4. Default behaviour remains unchanged when orchestration is disabled.

## Structured Extraction Enrichment

1. In `.env`, set:
   - `POLINKO_EXTRACTION_STRUCTURED_ENABLED=true`
2. Optional model override:
   - `POLINKO_EXTRACTION_STRUCTURED_MODEL=gpt-4.1-mini`
3. Restart API after changing extraction settings.
4. When enabled, OCR/PDF endpoints attempt a strict JSON-schema normalisation
   pass for extraction metadata and gracefully fall back to deterministic local
   shaping if unavailable.

## Governance + Hallucination Guardrails

1. In `.env`, set:
   - `POLINKO_GOVERNANCE_ENABLED=true`
   - `POLINKO_HALLUCINATION_GUARDRAILS_ENABLED=true`
2. Optional governance controls:
   - `POLINKO_GOVERNANCE_ALLOW_WEB_SEARCH=false` (blocks web search tool when
     false)
   - `POLINKO_GOVERNANCE_LOG_ONLY=false` (set `true` to allow but log policy
     violations)
3. Restart API after changing governance settings.
4. Guardrails operate as internal guidance only; they do not alter API response
   schema.

## Multi-Agent Collaboration v1

1. Apply a handoff:
   - `POST /chats/{session_id}/collaboration/handoff`
   - body:
     - `to_agent_id` (required)
     - `to_role` (required)
     - `objective` (optional)
     - `reason` (optional)
2. Inspect current collaboration state:
   - `GET /chats/{session_id}/collaboration`
3. Handoffs are server-side audited and included in a per-chat timeline.
4. During `/chat`, active collaboration context is injected internally (not
   shown to users).

## Personalization Memory Scope

1. Set default scope in `.env`:
   - `POLINKO_PERSONALIZATION_DEFAULT_MEMORY_SCOPE=global` (cross-chat
     retrieval)
   - or `session` (same-chat retrieval only)
2. Override per chat:
   - `POST /chats/{session_id}/personalization`
   - body: `{"memory_scope":"session"}` or `{"memory_scope":"global"}`
3. Inspect effective per-chat scope:
   - `GET /chats/{session_id}/personalization`
   - returns explicit override if present, otherwise current default scope.
4. This affects retrieval memory selection during `/chat` while keeping response
   schema unchanged.

## Run API Tests

1. Run `make test`.
2. Fix failures before merging.

## Run One-Command Quality Gate

1. Default mode uses hallucination judge scoring:
   - ensure `.env` includes `OPENAI_API_KEY`
2. Run `make quality-gate`.
3. No judge key available? Run deterministic mode:
   - `make quality-gate-deterministic`
4. If startup fails, inspect `/tmp/polinko-quality-gate.log`.
5. Optional overrides:
   - `make quality-gate GATE_PORT=8099`
   - `make quality-gate GATE_BASE_URL=http://127.0.0.1:8099`
   - `make quality-gate HALLUCINATION_EVAL_MODE=deterministic`
   - `make quality-gate HALLUCINATION_MIN_ACCEPTABLE_SCORE=70`
6. Note: `make quality-gate` sets
   `POLINKO_VECTOR_LOCAL_EMBEDDING_FALLBACK=true` for the temporary gate server
   to reduce transient embedding API flakes.

## Run Hallucination Eval

1. Ensure API is running locally (`make server`).
2. Run default judge mode:
   - `make eval-hallucination`
3. Run deterministic mode (no OpenAI judge dependency):
   - `make eval-hallucination-deterministic`
4. Tool-level mode options:
   - `python tools/eval_hallucination.py --evaluation-mode judge`
   - `python tools/eval_hallucination.py --evaluation-mode deterministic`
   - `python tools/eval_hallucination.py --evaluation-mode auto`
   - `python tools/eval_hallucination.py --min-acceptable-score 70`

## Run Retrieval Eval

1. Ensure API is running locally (`make server`).
2. Run `make eval-retrieval`.
3. Optional:
   - custom endpoint:
     `python tools/eval_retrieval.py --base-url http://127.0.0.1:8000`
   - retain generated eval chats: `python tools/eval_retrieval.py --keep-chats`
   - write JSON report:
     `python tools/eval_retrieval.py --report-json eval_reports/retrieval-latest.json`
   - one-command report run: `make eval-retrieval-report`

## Run File Search Eval

1. Ensure API is running locally (`make server`).
2. Run `make eval-file-search`.
3. Optional:
   - custom endpoint:
     `python tools/eval_file_search.py --base-url http://127.0.0.1:8000`
   - retain generated eval chats:
     `python tools/eval_file_search.py --keep-chats`
   - write JSON report:
     `python tools/eval_file_search.py --report-json eval_reports/file-search-latest.json`
   - one-command report run: `make eval-file-search-report`
4. Cases:
   - uses `docs/file_search_eval_cases.json` (OCR + PDF + optional image-context
     smoke test)
   - image-context case is skipped automatically when
     `POLINKO_IMAGE_CONTEXT_ENABLED=false`

## Run CLIP A/B Scaffold Eval

1. Ensure API is running locally (`make server`) with vector memory enabled.
2. Run baseline-vs-proxy A/B harness:
   - `make eval-clip-ab`
3. Optional:
   - include additional source types:
     `make eval-clip-ab CLIP_AB_SOURCE_TYPES=image,pdf`
   - write JSON report artifact:
     `make eval-clip-ab-report`
4. Cases:
   - default CLIP A/B case file: `docs/clip_ab_eval_cases.json`
   - current baseline set: 4 image-context retrieval cases with distractors
5. Current B arm is an image-prioritized proxy (`source_types=["image"]`) used
   to establish experiment wiring ahead of full CLIP embedding integration.
6. CLIP integration go/no-go criterion:
   - `GO` when two consecutive report runs with `cases_count >= 4` satisfy:
     - `clip_proxy_image_only.any_rate >= 0.90`
     - `any_rate_delta_proxy_minus_baseline >= 0.50`
     - `errors == 0` and `skipped == 0` for both arms
   - `NO-GO` otherwise; keep proxy/scaffold mode and add cases or fix retrieval
     behaviour before integration escalation.
7. Automated readiness check:
   - `make eval-clip-ab-readiness`
   - uses the latest two `eval_reports/clip-ab-*.json` artifacts
   - exits `0` on `GO`, `1` on `NO-GO`

## Deprecated: Hybrid OpenAI Pilot Tooling

The hybrid pilot/readiness/bridge/export/execute commands are deprecated in the
active workflow and are kept as historical reference only.

Current policy:

1. Do not run hybrid pilot commands in normal development cycles.
2. Use local-first glue-code + manual eval loop as the canonical path.
3. Keep this section archived for traceability, not as runbook execution.

## Run OCR Eval

1. Ensure API is running locally (`make server`).
2. Run `make eval-ocr`.
3. Optional:
   - custom endpoint:
     `python tools/eval_ocr.py --base-url http://127.0.0.1:8000`
   - show extracted text: `python tools/eval_ocr.py --show-text`
   - strict fail on any failed case: `python tools/eval_ocr.py --strict`
   - retain generated eval chats: `python tools/eval_ocr.py --keep-chats`
   - write JSON report:
     `python tools/eval_ocr.py --report-json eval_reports/ocr-latest.json`
   - one-command report run: `make eval-ocr-report`
4. Cases:
   - default cases file: `docs/ocr_eval_cases.json`
   - supports image cases (`image_path`) and deterministic text-hint cases
     (`text_hint`)
   - optional per-case controls:
     - `transcription_mode` (`verbatim` or `normalized`)
     - `must_contain`, `must_contain_any`, `must_not_contain`
     - `must_not_contain_words` (whole-word bans)
     - `must_appear_in_order` (ordered phrase assertions)
     - `must_match_regex`, `must_not_match_regex` (pattern assertions)
     - `min_chars`, `max_chars`, `case_sensitive`

## Run OCR Ambiguity/Recovery Eval

1. Ensure API is running locally (`make server`).
2. Run `make eval-ocr-recovery`.
3. Optional:
   - strict fail on any failed case: `python tools/eval_ocr_recovery.py --strict`
   - retain generated eval chats: `python tools/eval_ocr_recovery.py --keep-chats`
   - show full assistant outputs per step:
     `python tools/eval_ocr_recovery.py --show-text`
   - write JSON report:
     `python tools/eval_ocr_recovery.py --report-json eval_reports/ocr-recovery-latest.json`
   - one-command report run: `make eval-ocr-recovery-report`
4. Cases:
   - default case file: `docs/ocr_recovery_eval_cases.json`
   - each case runs a seeded OCR prompt with attachment, then one or more
     follow-up user turns in the same chat
   - designed for ambiguity stress + correction/recovery traces with
     deterministic phrase/regex assertions

## Hallucination Eval Notes

1. Optional strict mode:
   - `python tools/eval_hallucination.py --strict`
2. Optional tuning:
   - choose model:
     `python tools/eval_hallucination.py --judge-model gpt-4.1-mini`
   - tune score threshold:
     `python tools/eval_hallucination.py --min-acceptable-score 70`
   - mode selection:
     - `python tools/eval_hallucination.py --evaluation-mode judge`
     - `python tools/eval_hallucination.py --evaluation-mode deterministic`
     - `python tools/eval_hallucination.py --evaluation-mode auto`
   - Braintrust judge mode:
     - set `BRAINTRUST_OPENAI_BASE_URL=https://api.braintrust.dev/v1/proxy`
     - set `BRAINTRUST_API_KEY` (env/secret)
     - run `make eval-hallucination-braintrust`
   - retain generated chats: `python tools/eval_hallucination.py --keep-chats`
   - write JSON report:
     `python tools/eval_hallucination.py --report-json eval_reports/hallucination-latest.json`
   - one-command report run: `make eval-hallucination-report`
3. Eval isolation behaviour:
   - Each generated eval chat is set to `memory_scope=session` to reduce
     cross-chat retrieval noise.

## Run Style Eval (Judge-Based)

1. Ensure API is running locally (`make server`).
2. Ensure `OPENAI_API_KEY` is set in `.env` (judge model call).
3. Run `make eval-style`.
4. Optional strict mode:
   - `python tools/eval_style.py --strict`
5. Optional tuning:
   - choose model: `python tools/eval_style.py --judge-model gpt-4.1-mini`
   - retain generated chats: `python tools/eval_style.py --keep-chats`
   - write JSON report:
     `python tools/eval_style.py --report-json eval_reports/style-latest.json`
   - one-command report run: `make eval-style-report`
6. Eval-only phrase fail rules (no runtime behaviour changes):
   - `docs/style_eval_cases.json` root `global_forbidden_phrases` applies to all
     cases
   - per-case `forbidden_phrases` applies only to that case
   - phrase checks are case-insensitive
7. Co-reasoning stress cases are included in `docs/style_eval_cases.json` for:
   - constraint retention without rigidity
   - meta-level shift handling
   - anti-mimicry style adaptation
   - grounding under playful abstraction

## Generate All Eval Reports

1. Ensure API is running locally (`make server`).
2. Ensure `OPENAI_API_KEY` is set in `.env` (judge eval reports require it).
3. Run `make eval-reports`.
4. Reports are written under `eval_reports/` with timestamped filenames.

## Calibrate Hallucination Threshold

1. Generate one or more hallucination report artifacts:
   - `make eval-hallucination-report`
2. Run calibration helper:
   - `make calibrate-hallucination-threshold`
3. Review summary:
   - `eval_reports/hallucination-threshold-calibration.json`
4. Apply chosen threshold:
   - local gate runs: `HALLUCINATION_MIN_ACCEPTABLE_SCORE=<value>`
   - CI repo variable: `BRAINTRUST_HALLUCINATION_MIN_SCORE`
5. Tie-break behaviour:
   - if multiple thresholds have equal metrics, the calibrator picks the
     strictest (highest) threshold among the ties.

## Evidence Triage Lifecycle (FAIL -> PASS)

1. Store evidence artifacts under:
   - `docs/portfolio/raw_evidence/FAIL`
   - `docs/portfolio/raw_evidence/PASS`
   - `docs/portfolio/raw_evidence/INBOX`
2. Legacy intake wiring is archive-only:
   - `MIXED` is deprecated from active flow.
   - `eval_trace_artifacts.jsonl` is historical/archive-only for prior pilot traces.
3. Run one-command refresh (recommended):
   - `make evidence-refresh`
   - runs `make evidence-index` + `make portfolio-metadata-audit`
   - bootstraps `docs/portfolio/raw_evidence/triage_overrides.json` from
     template when missing
4. Run index builder directly (manual mode):
   - `make evidence-index`
5. FAIL entries now carry lifecycle fields in generated index:
   - `failure_reason`
   - `recommended_action`
   - `action_taken`
   - `status` (`OPEN`/`CLOSED`)
   - optional `resolved_by` PASS artifact reference
6. To record human triage updates, create:
   - `docs/portfolio/raw_evidence/triage_overrides.json`
   - Example:
     - `{"files":{"<artifact-filename>":{"action_taken":"...", "status":"OPEN", "notes":"..."}}}`
7. Closure rule:
   - FAIL remains `OPEN` until a later PASS artifact exists for the same
     `chat_id`; then it auto-closes and links `resolved_by`.
8. Audit metadata completeness (strict):
   - `make portfolio-metadata-audit`
   - writes:
     - `docs/portfolio/raw_evidence/metadata_audit.json`
     - `docs/portfolio/raw_evidence/metadata_audit.md`

## Human Reference DB (One-Click Queries)

1. Rebuild local human reference DB:
   - `make human-reference-db`
   - Reference guide: `docs/HUMAN_REFERENCE_DB.md`
   - ER diagram source: `docs/human_reference_erd.mmd`
2. Run latest-docs query:
   - `make human-reference-latest`
3. Run transcript/key-points feed:
   - `make human-reference-transcripts`
4. Run recent-changes feed (default last 24h):
   - `make human-reference-changes`
5. Run relationship-map feed:
   - `make human-reference-relationships`
6. Optional query tuning:
   - `make human-reference-latest HUMAN_REFERENCE_LIMIT=50`
   - `make human-reference-changes HUMAN_REFERENCE_SINCE_HOURS=72`
7. Visualization note:
   - project default flow is query-first/offline (`make human-reference-*`)
   - for visual ER exploration, open `.human_reference.db` in your preferred DB
     viewer and load `docs/human_reference_erd.mmd` as the schema reference

## UI Feedback Rubric (Current)

1. For each assistant response, open `Evaluate`.
2. Score two rubric dimensions:
   - `Style`: `pass` or `fail`
   - `Hallucination risk`: `pass` or `fail`
3. Optional style penalties:
   - `default/straight style` (`default_style`) is a soft penalty.
   - `em-dash style` (`em_dash_style`) is a hard penalty.
4. Save one checkpoint per reviewed response.
5. Status line semantics:
   - `pass: ...` for positive rubric signals
   - `fail: ...` for hard fail signals
   - `penalty: ...` for soft-only penalties
6. Outcome derivation (system):
   - `pass`: no hard fail signals
   - `fail`: any hard fail signal present
7. Release gate usage (operator):
   - treat any hard fail signal as a gate fail for that response
   - soft penalties stay actionable quality debt, not hard blockers
8. Eval submissions are auto-logged on every save:
   - `docs/portfolio/raw_evidence/INBOX/eval_submissions.jsonl`
   - each line includes session id, title, outcome, tags, note, and timestamp
9. Quick "what's new" inbox command:
   - `make eval-inbox`
   - shows newly logged eval submissions since last cursor checkpoint

## Start Fresh Eval Cycle

1. Optional pre-reset snapshot (when you need before/after comparability):
   - copy current evidence tree to
     `docs/portfolio/raw_evidence/archive/eval-reset-<YYYYMMDD-HHMMSS>`
2. Archive/clean generated eval chats:
   - `make eval-cleanup`
3. If needed, reset one chat session:
   - `POST /session/reset` with `{"session_id":"<chat-id>"}`.
4. Re-run deterministic baseline gate:
   - `make quality-gate-deterministic`
5. Regenerate fresh eval report artifacts:
   - `make eval-reports-parallel`
6. Keep historical evidence artifacts; only clear active UI/checkpoint state for
   the next clean eval pass.

## Export CLI Transcript

1. Run `make chat`.
2. In CLI, use `/export` for default markdown export.
3. Optional custom path/format: `/export exports/session.txt` or
   `/export exports/session.json`.
4. CLI chat management:
   - `/chats` list active chats
   - `/switch <session-id>` switch chat
   - `/rename <title>` rename current chat
   - `/close` deprecate current chat and create a fresh session

## API Client (`tools/client.py`)

1. Run `python tools/client.py --session-id local-dev`.
2. Useful commands:
   - `/help`
   - `/reset`
   - `/ocr path/to/image.png`
   - `/ocr --mode normalized path/to/image.png`
   - `/pdf path/to/file.pdf`
   - `/search your query`
   - `/search-ocr your query`
   - `/search-pdf your query`
   - `/search-chat your query`
   - `/export`

## Export From UI

1. Open a chat in the web UI.
2. Use header controls to download:
   - transcript markdown (`.md`)
   - transcript json (`.json`)
   - OCR run history json (`.ocr-runs.json`)

## Dev Startup (Auto Port Hygiene)

1. Start backend + frontend:
   - `make dev`
2. Behaviour:
   - preflights ports `8000` (backend) and `5173` (frontend)
   - stops stale listeners on those ports before launch
   - starts frontend with strict port binding (`5173`) to avoid drift
3. Stop listeners only:
   - `make dev-stop`
4. Optional overrides:
   - `DEV_AUTOKILL=0 make dev` (fail on non-dev port owners instead of stopping)
   - `DEV_BACKEND_PORT=9000 DEV_FRONTEND_PORT=5175 make dev`

## Common Connection Error

Symptom:

- `connection error` during chat.

Checks:

1. Confirm internet access and no firewall/VPN block.
2. Confirm `OPENAI_API_KEY` is set in `.env`.
3. If auth is enabled, confirm `POLINKO_SERVER_API_KEY` or
   `POLINKO_SERVER_API_KEYS_JSON` is configured consistently with your
   client/proxy.
4. Retry command after a short wait.

## Figma MCP Design Fetch Troubleshooting

Symptom:

- Figma tools return: `You currently have nothing selected.`

Checks:

1. Confirm Figma MCP is connected and authenticated.
2. If using Figma desktop workflow, select the target frame/layer before fetch.
3. If using URL workflow, ensure the link includes a valid `node-id` and retry.
4. Restart Codex after first-time MCP login to refresh tool availability.
