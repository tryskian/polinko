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

## Morning Startup Check (Codexbeab)

1. Confirm execution location:
   - canonical root (`/Users/tryskian/Github/polinko`) or dedicated worktree.
2. Confirm active branch in this thread:
   - `git branch --show-current`
3. If running parallel tracks, keep each track in its own dedicated worktree.
4. Only after 1-3:
   - run `make doctor-env`
   - continue with normal startup (`make server-daemon`, `make session-status`)

## Command Surface Simplification Rule

1. Prefer one canonical make target per operator action.
2. When replacing a command surface, remove superseded aliases in the same change.
3. Do not layer patch-style compatibility targets unless explicitly approved in-chat.
4. Close command-surface edits with clean runs:
   - `make doctor-env`
   - `make lint-docs`
   - `make test`
   - `make quality-gate-deterministic` when runtime/eval execution behaviour changed

## End-of-Day Routine (Codexbeab)

1. Run the end-of-day script:
   - `make eod`
2. Script sequence (deterministic):
   - `make transcript-fix`
   - `make transcript-check`
   - `make doctor-env`
   - `make lint-docs`
   - `make test`
3. Purpose:
   - keep local transcript records in consistent rich format
   - catch build/docs drift before day-close
   - hand off a clean validation state for next startup

## Command Ownership Rule (Reasoning Loops)

1. Imagineer does not run terminal commands as part of normal workflow.
2. Engineer runs command execution, validation, and Git flow end-to-end.
3. Human control stays on objective/scope/acceptance and go/no-go decisions.
4. Execution-first default:
   - when the user asks for work, do the work directly

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
   - `docs/peanut/refs/FIGMA_NODE_TRACKER.md`
   - `docs/peanut/refs/PEANUT_TOOLING_REF.md`
   - `docs/internal/`
   - `docs/peanut/`
   - `docs/portfolio/`
   - `.archive/live_archive/legacy_eval/`
   - `.archive/live_archive/legacy_human_reference/`
3. Build/source-of-truth docs stay tracked:
   - `docs/governance/CHARTER.md`
   - `docs/governance/WORKSTREAMS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/STATE.md`
   - `docs/governance/DECISIONS.md`
   - `docs/governance/SESSION_HANDOFF.md`
4. Do not use `skip-worktree` for routine workflow; use gitignored local-only
   paths instead.
5. Any exception to local-only confidentiality must be explicitly approved
   in-chat before being committed.

## Rotate API Keys

1. Update `.env` with new `OPENAI_API_KEY`.
2. Restart running API/CLI processes.

## Environment Doctor

1. Run `make doctor-env`.
2. Review warnings:
   - `VIRTUAL_ENV is not set` is expected when using `make`.
   - `python` is not on PATH is informational when only `python3` is
     available.
3. Resolve actionable issues (missing imports, interpreter mismatch, or
   `compaudit` findings) before running evals.
4. VS Code task startup is now venv-automatic through `make` interpreter
   discovery; manual `source .../activate` chaining is not required for
   `make server` / `make caffeinate-on`.

## Live Archive Reference

1. Use `.archive/live_archive/` as the single active reference location for
   deprecated implementation context.
2. Legacy eval context belongs in:
   - `.archive/live_archive/legacy_eval/`
3. Legacy frontend context belongs in:
   - `.archive/live_archive/legacy_frontend/`
4. Archive content is reference-only:
   - do not wire it into active runtime/eval gate paths.
   - keep binary runtime specs sourced from active docs/code.

## Wiring-First DB Freeze

Local runtime DB commands are retired during wiring lock; treat this runbook
plus tests as the active spec surface (`make test`,
`make quality-gate-deterministic`). No local DB lifecycle commands remain.

## Chat Harness Mode (Deterministic Smoke Without Model Calls)

1. Default mode is `live` (normal backend/model execution).
2. For deterministic smoke, use fixture mode in `POST /chat`:
   - request field `harness_mode=fixture`
   - optional `fixture_output` to pin exact response text
3. Optional env default:
   - `POLINKO_CHAT_HARNESS_DEFAULT_MODE=fixture`
4. Fixture mode is test harness only:
   - keep eval/gate logic server-side and binary
   - do not use fixture mode outputs for quality gate decisions

## OCR-Forward Operating Model

1. Treat OCR as the primary eval reliability lane.
2. Run two parallel lane types:
   - `lockset` lane:
     - strict release gate, must stay green
     - currently represented by benchmark subsets
       (`handwriting`, `typed`, `illustration`)
   - `growth` lane:
     - fail-tolerant novel-case lane
     - used to measure pass-from-fail movement, not to block release directly
3. Canonical command sequence:
   - mine/build cases:
     - `make ocrmine CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
   - run widened growth lane (fail-tolerant):
     - `make ocrwiden`
     - optional bounded batch run:
       - `make ocrwiden OCR_GROWTH_EVAL_OFFSET=0 OCR_GROWTH_EVAL_MAX_CASES=40`
     - optional chunked full-window run:
       - `make ocrwidenall OCR_GROWTH_BATCH_SIZE=40`
     - `make ocrstablegrowth`
   - run lockset lanes:
     - `make ocrhandbench`
     - `make ocrtypebench`
     - `make ocrillubench`
   - run stability replays:
     - `make ocrstablehand`
     - `make ocrstabletype`
     - `make ocrstableillu`
   - compute growth-lane pass-from-fail metrics:
     - `make ocrgrowth`
   - materialise stable growth FAIL cohort for next-kernel remediation:
     - `make ocrfails`
4. Local output surfaces:
   - case sets: `.local/eval_cases/`
     - growth set: `.local/eval_cases/ocr_transcript_cases_growth.json`
     - growth fail cohort: `.local/eval_cases/ocr_growth_fail_cohort.json`
   - run/stability reports: `.local/eval_reports/`
     - growth stability: `.local/eval_reports/ocr_growth_stability.json`
     - growth batch reports: `.local/eval_reports/ocr_growth_batched_runs/`
     - growth batch summary:
       - `.local/eval_reports/ocr_growth_batched_summary.json`
       - `.local/eval_reports/ocr_growth_batched_summary.md`
   - growth metrics reports:
     - `.local/eval_reports/ocr_growth_metrics.json`
     - `.local/eval_reports/ocr_growth_metrics.md`
   - growth fail cohort report:
     - `.local/eval_reports/ocr_growth_fail_cohort.md`
5. Notebook analysis surface:
   - `make notes`
   - starter template:
     - `output/jupyter-notebook/ocr-eval-live-filters-starter.ipynb`

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

## Tooling Baseline

1. Install local CLIs (macOS/Homebrew):
   - `brew install act k6 trivy`
2. `Dependabot` is configured in `.github/dependabot.yml` for:
   - GitHub Actions (`/`)
   - Python (`/`)
3. Install and run `pre-commit`:
   - `make precommit-install`
   - `make precommit-run`
4. Run CI workflow locally with `act`:
   - list jobs: `make act-list`
   - run CI workflow: `make act-ci`
5. Run k6 chat smoke load test (requires local API server running):
   - default: `make k6-chat-smoke`
   - custom: `make k6-chat-smoke K6_BASE_URL=http://127.0.0.1:8000 K6_VUS=5 K6_DURATION=30s`
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

## Inspect-First Rule (Directed Mode)

1. If system state appears noisy/contradictory, stop and inspect before trying
   to summarise, simplify, or refactor.
2. Keep active runtime/doc specs current; archive deprecated context rather
   than carrying compatibility paths in active flow.
3. In human-directed precision mode, execute only the requested slice and avoid
   opportunistic cleanup outside scope.
4. When this rule changes execution, record it in `docs/governance/DECISIONS.md` and
   checkpoint it in `docs/governance/STATE.md`.

## Proactive Engineering Ownership

1. Treat technical hygiene as engineer-owned by default; do not wait for
   reminders to handle obvious drift, cleanup, or policy propagation work.
2. Before and after each implementation slice, run lightweight checks:
   - `git status`
   - target validations (`make test`, `make lint-docs`, or scoped tests as appropriate)
   - docs alignment across governance surfaces when policy/flow changes
3. If a gremlin-risk surface is discovered (deprecated paths, hidden state
   coupling, stale orchestration), open a bounded fix slice immediately.
4. Ask for user input only when:
   - approval is explicitly required
   - scope trade-offs affect roadmap priorities
   - conflicting directives cannot be resolved safely
5. Keep execution action-first:
   - implement and validate
   - then report outcomes and remaining risks briefly

## Human-Managed Co-Reasoning Control Loop

1. Human sets the loop frame before implementation:
   - objective/hypothesis under test
   - scope boundary (in-scope vs out-of-scope)
   - acceptance and fail conditions
2. Engineer translates that frame into bounded execution slices and runs them
   proactively.
3. Human remains decision authority for:
   - ambiguity trade-offs (meaning/positioning interpretation)
   - go/no-go calls
   - re-prioritisation of next slice
4. Engineer owns technical control surfaces inside the approved frame:
   - implementation
   - validation
   - drift/gremlin-risk cleanup
   - doc propagation
5. Why this rule exists:
   - model completion can over-optimise local targets
   - human governance keeps work aligned to intent and usable product outcomes

## Policy Propagation Checklist

1. For any collaboration/execution policy change, update all governance surfaces
   in the same change set:
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/STATE.md`
   - `docs/governance/SESSION_HANDOFF.md`
   - `docs/runtime/ARCHITECTURE.md` (if operating flow/ownership changes)
2. Do not treat any single doc as sufficient for policy updates.
3. End-of-day handoff must include any new policy/cutline so next-session
   startup does not drift.

## Reset Local Session Memory

1. Stop running processes.
2. Remove local DB files:
   - `.local/runtime_dbs/active/memory.db` (+ `-shm`/`-wal`)
   - `.local/runtime_dbs/active/history.db` (+ `-shm`/`-wal`)
   - `.local/runtime_dbs/active/vector.db` (+ `-shm`/`-wal`)
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
   - conversation memory in `.local/runtime_dbs/active/memory.db`
   - persisted chat messages in `.local/runtime_dbs/active/history.db`
   - vector memories for that session in `.local/runtime_dbs/active/vector.db` (when enabled)
7. Deprecation/reset is chat lifecycle state management, not model-weights
   training or a direct runtime penalty signal.

## Chat History API

UI adapter spec is maintained in this runbook section (chat + eval API shape).

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
   - `POLINKO_VECTOR_DB_PATH` (default `.local/runtime_dbs/active/vector.db`)
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
   - uses `docs/eval/cases/file_search_eval_cases.json` (OCR + PDF + optional image-context
     smoke test)
   - image-context case requires `POLINKO_IMAGE_CONTEXT_ENABLED=true` and will
     fail-closed if image context is disabled

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
   - default CLIP A/B case file: `docs/eval/cases/clip_ab_eval_cases.json`
   - current baseline set: 4 image-context retrieval cases with distractors
5. Current B arm is an image-prioritized proxy (`source_types=["image"]`) used
   to establish experiment wiring ahead of full CLIP embedding integration.
6. CLIP integration go/no-go criterion:
   - `GO` when two consecutive report runs with `cases_count >= 4` satisfy:
     - `clip_proxy_image_only.any_rate >= 0.90`
     - `any_rate_delta_proxy_minus_baseline >= 0.50`
     - `errors == 0` for both arms
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
   - default cases file: `docs/eval/cases/ocr_eval_cases.json`
   - supports image cases (`image_path`) and deterministic text-hint cases
     (`text_hint`)
   - optional per-case controls:
     - `transcription_mode` (`verbatim` or `normalized`)
     - `must_contain`, `must_contain_any`, `must_not_contain`
     - `must_not_contain_words` (whole-word bans)
     - `must_appear_in_order` (ordered phrase assertions)
     - `must_match_regex`, `must_not_match_regex` (pattern assertions)
     - `min_chars`, `max_chars`, `case_sensitive`
   - matcher note:
     - `must_contain_any` and `must_not_contain_words` handle OCR intra-word
       spacing artefacts, including fully spaced (`C H A T T I E S T`) and
       mixed split tokens (`CHAT T IEST`)

## Run Handwriting/Cursive OCR Eval

1. Ensure true image OCR is enabled in `.env`:
   - `POLINKO_OCR_PROVIDER=openai`
2. Create a local cases file (kept untracked) at:
   - `.local/eval_cases/ocr_handwriting_eval_cases.json`
3. Case requirements:
   - use real `image_path` entries
   - avoid `text_hint` so this remains image-driven
4. Run:
   - `make eval-ocr-handwriting`
5. Run with report artifact:
   - `make eval-ocr-handwriting-report`
6. Optional custom cases path:
   - `make eval-ocr-handwriting OCR_HANDWRITING_CASES=/abs/path/to/cases.json`
7. Minimal case example:

```json
{
  "cases": [
    {
      "id": "handwriting_sample_1",
      "image_path": "/absolute/path/to/handwriting_sample.png",
      "transcription_mode": "verbatim",
      "must_contain_any": ["target phrase"],
      "must_not_contain_words": ["likely", "probably", "guess"],
      "min_chars": 5
    }
  ]
}
```

## Build Transcript-Backed OCR Cases from ChatGPT Export

1. Keep ChatGPT export data outside the repo (for example in Dropbox), and make
   it locally available offline.
2. Build attachment/conversation index artifacts (local-only):
   - `make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
3. Mine OCR eval cases from transcript correction/confirmation signals:
   - `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
   - precision guard: askless handwriting episodes now require
     correction-overlap signal before promotion to medium confidence
     (reduces conversational anchor noise)
   - command output includes emit diagnostics:
     `emitted_cases`, `skipped_low_confidence`,
     `skipped_duplicate_image_path`, `skipped_insufficient_anchor_terms`
   - also generates:
     - strict handwriting benchmark cases:
       `.local/eval_cases/ocr_handwriting_benchmark_cases.json`
     - strict typed benchmark cases:
       `.local/eval_cases/ocr_typed_benchmark_cases.json`
     - strict illustration benchmark cases:
       `.local/eval_cases/ocr_illustration_benchmark_cases.json`
     - before/after miner delta report:
       `.local/eval_cases/ocr_transcript_cases_delta.md`
4. Run OCR eval against mined transcript-backed cases:
   - `make eval-ocr-transcript-cases`
   - `make eval-ocr-transcript-cases-handwriting`
   - `make eval-ocr-transcript-cases-handwriting-benchmark`
   - `make eval-ocr-transcript-cases-typed`
   - `make eval-ocr-transcript-cases-typed-benchmark`
   - `make eval-ocr-transcript-cases-illustration`
   - `make eval-ocr-transcript-cases-illustration-benchmark`
5. Track drift separately for strict lane benchmarks:
   - `make eval-ocr-transcript-stability-handwriting-benchmark`
   - `make eval-ocr-transcript-stability-typed-benchmark`
   - `make eval-ocr-transcript-stability-illustration-benchmark`
   - stability runner now streams child OCR progress live by default
     (use `--capture-child-output` on `tools/eval_ocr_stability.py` only when
     you explicitly need captured stdout/stderr tails)
   - output JSON:
     `.local/eval_reports/ocr_handwriting_benchmark_stability.json`
     `.local/eval_reports/ocr_typed_benchmark_stability.json`
     `.local/eval_reports/ocr_illustration_benchmark_stability.json`
6. Optional paths:
   - index output directory:
     `make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/export CGPT_EXPORT_OUTPUT_DIR=/abs/path/to/output`
   - override generated combined cases path:
     `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_TRANSCRIPT_CASES_ALL=/abs/path/to/cases.json`
   - override handwriting lane cases path:
     `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_TRANSCRIPT_CASES_HANDWRITING=/abs/path/to/handwriting-cases.json`
   - override typed lane cases path:
     `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_TRANSCRIPT_CASES_TYPED=/abs/path/to/typed-cases.json`
   - override illustration lane cases path:
     `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_TRANSCRIPT_CASES_ILLUSTRATION=/abs/path/to/illustration-cases.json`
   - override generated review file path:
     `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_TRANSCRIPT_REVIEW=/abs/path/to/review.json`
7. Default local artifacts:
   - `.local/eval_cases/cgpt_export_attachment_index.json`
   - `.local/eval_cases/cgpt_export_behaviour_eval_ocr_ready.json`
   - `.local/eval_cases/ocr_transcript_cases_all.json`
   - `.local/eval_cases/ocr_handwriting_from_transcripts.json`
   - `.local/eval_cases/ocr_typed_from_transcripts.json`
   - `.local/eval_cases/ocr_illustration_from_transcripts.json`
   - `.local/eval_cases/ocr_handwriting_benchmark_cases.json`
   - `.local/eval_cases/ocr_typed_benchmark_cases.json`
   - `.local/eval_cases/ocr_illustration_benchmark_cases.json`
   - `.local/eval_cases/ocr_transcript_cases_review.json`
   - `.local/eval_cases/ocr_transcript_cases_review_prev.json` (when available)
   - `.local/eval_cases/ocr_transcript_cases_delta.md`
   - `.local/eval_cases/ocr_transcript_cases_delta.json`
8. Review diagnostics:
   - review file now includes a top-level `summary`:
     - `conversation_files`, `episodes`
     - `confidence_counts`, `lane_counts`
     - `emit_status_counts`, `lane_emit_status_counts`
   - each review episode now includes:
     - `emit_status` (`emitted`, `skipped_low_confidence`,
       `skipped_duplicate_image_path`, `skipped_insufficient_anchor_terms`)
     - `anchor_terms` and `anchor_terms_count`

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
   - default case file: `docs/eval/cases/ocr_recovery_eval_cases.json`
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
   - `docs/eval/cases/style_eval_cases.json` root `global_forbidden_phrases` applies to all
     cases
   - per-case `forbidden_phrases` applies only to that case
   - phrase checks are case-insensitive
7. Co-reasoning stress cases are included in `docs/eval/cases/style_eval_cases.json` for:
   - constraint retention without rigidity
   - meta-level shift handling
   - anti-mimicry style adaptation
   - grounding under playful abstraction

## Generate All Eval Reports

1. Ensure API is running locally (`make server`).
2. Ensure `OPENAI_API_KEY` is set in `.env` (judge eval reports require it).
3. Run `make eval-reports`.
4. Reports are written under `eval_reports/` with timestamped filenames.

## Eval Gate Spec (Canonical)

1. Binary outcome model:
   - allowed outcomes: `pass` and `fail` only
   - tags are diagnostic only; outcome drives gate arithmetic
2. Symbol convention:
   - `⊨` semantic entailment / satisfies
   - `⊭` does not semantically entail
3. Canonical semantics:
   - `reward ⊨ alignment`
   - `reward ⊭ adjustment`
   - `reward ⊭ intensity`
4. Canonical binary gate:
   - `PASS ⇔ policy_pass ∧ high_value_alignment_pass ∧ evidence_complete`
   - otherwise `FAIL`
5. Checkpoint arithmetic:
   - `total_count = pass_count + fail_count + non_binary_count`
   - `non_binary_count` is an integrity signal and should remain `0`
   - `gate_outcome = pass` iff `total_count > 0 ∧ fail_count = 0 ∧ non_binary_count = 0`
6. Keep release output strictly binary; diagnostic detail may be rich, but it
   must not introduce non-binary gate states.

## Benchmark + Cookbook Spec

1. Primary benchmark hypothesis:
   - minimal configuration outperforms configuration-heavy flows on quality,
     clarity, iteration speed, and maintenance overhead
2. Current benchmark phases:
   - A: minimal-config CLI baseline
   - B: traditional eval stack
   - C: binary eval stack
   - D: operator burden shift diagnostic
3. Cookbook queue (prioritised now):
   - Vision fine-tuning on GPT-4o for visual question answering
   - RAG on PDFs with File Search
   - Structured Outputs
   - Image Understanding with RAG
   - ELT extraction/transformation pattern
   - model graders for reinforcement fine-tuning
4. Deferred cookbook queue:
   - Prompt Caching 101/201
   - Realtime eval guide
   - Realtime out-of-band transcription
   - RAG with graph DB
   - search reranking with cross-encoders

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

## Evidence Lifecycle (Git-Native)

1. Use Git history as the canonical archive for tracked docs/code.
2. Keep local eval artefacts in `eval_reports/` only (ignored operational output).
3. Eval trace artifacts default to:
   - `eval_reports/eval_trace_artifacts.jsonl`
4. If stale local artefacts reappear and you want a clean cycle:
   - remove local outputs (`rm -rf eval_reports/*`) before the next run.

## Start Fresh Eval Cycle

1. Clean generated eval chats:
   - `make eval-cleanup`
   - note: this is local-only helper behaviour; if the local script is absent,
     the target exits cleanly and skips cleanup.
2. If needed, reset one chat session:
   - `POST /session/reset` with `{"session_id":"<chat-id>"}`.
3. Re-run deterministic baseline gate:
   - `make quality-gate-deterministic`
4. Regenerate fresh eval report artefacts:
   - `make eval-reports-parallel`
5. Keep historical context in Git history; only clear active checkpoint state for
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

## Localhost Startup (Auto Port Hygiene)

1. Start backend-only canonical surface:
   - `make server-daemon`
2. Stop backend daemon:
   - `make server-daemon-stop`
3. Optional foreground backend run on localhost:
   - `make localhost`

## Common Connection Error

Symptom:

- `connection error` during chat.

Checks:

1. Confirm internet access and no firewall/VPN block.
2. Confirm `OPENAI_API_KEY` is set in `.env`.
3. Retry command after a short wait.

## Figma MCP Design Fetch Troubleshooting

Symptom:

- Figma tools return: `You currently have nothing selected.`

Checks:

1. Confirm Figma MCP is connected and authenticated.
2. If using Figma desktop workflow, select the target frame/layer before fetch.
3. If using URL workflow, ensure the link includes a valid `node-id` and retry.
4. Restart Codex after first-time MCP login to refresh tool availability.
