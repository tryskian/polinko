<!-- @format -->

# Runbook

## When to Read This

- startup and environment checks
- debugging or operational recovery
- sanctioned command lookup

## Branch, Fork, and Worktree Policy

1. Default workflow is branch-based in the canonical local repo:
   - `<repo-root>`
2. Do not fork this repository for normal day-to-day project work.
3. Create a task branch per change set:
   - `git switch -c codex/bigbrain/<task-name>`
4. Use a worktree only when you need parallel active tracks (for example:
   CI calibration in one tree and feature scaffold in another):
   - `git worktree add ../polinko-<task> -b codex/bigbrain/<task> main`
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

## Operator Rituals

- `hi! new day!`
  - use this to trigger the morning startup check
  - read [Morning Startup Check (Codexbeab)](#morning-startup-check-codexbeab)
  - scripted version: `make start`
  - quick operator sheet: [Start / End Reference](./START_END_REFERENCE.md)
- `human time` / `wind down`
  - use these to trigger end-of-day closeout
  - read [End-of-Day Routine (Codexbeab)](#end-of-day-routine-codexbeab)
- portfolio visual review
  - use [Portfolio Surface / Playwright Loop](#portfolio-surface--playwright-loop)
    for `make portfolio-playwright`, `make pwcli ARGS="snapshot"`, and local
    screenshot paths

## Morning Startup Check (Codexbeab)

1. Confirm execution location:
   - canonical root (`/Users/tryskian/Github/polinko`) or dedicated worktree.
2. Confirm active branch in this thread:
   - `git branch --show-current`
3. If running parallel tracks, keep each track in its own dedicated worktree.
4. Only after 1-3:
   - run `make start` for the full scripted startup, or manually run:
     - `make doctor-env`
     - `make caffeinate`
     - `make caffeinate-status`
     - `make api-smoke`
   - inside Codex, treat `make api-smoke` as the trusted runtime truth
   - use `make server-daemon` / `make session-status` only as convenience checks
5. After `make start`, before any repo action:
   - give the 5-bullet startup read
   - name exactly one active kernel
   - do not branch, search, or edit until that is stated
6. Codex execution caveat:
   - long-lived detached background processes launched from this execution surface can be reaped later even after a clean startup
   - do not treat a green `server-daemon` / `session-status` result as stronger evidence than `make api-smoke`

## Command Surface Simplification Rule

1. Prefer one canonical make target per operator action.
2. When replacing a command surface, remove superseded aliases in the same change.
3. Do not layer patch-style compatibility targets unless explicitly approved in-chat.
4. Close command-surface edits with clean runs:
   - `make doctor-env`
   - `make lint-docs`
   - `make test`
   - `make quality-gate-deterministic` when runtime/eval execution behaviour changed

## Eval Sidecar (Long Soaks)

1. Use the eval sidecar for long stability soaks where you want repeated gate
   cycles plus a durable status surface.
2. Start it from a host terminal:
   - `make eval-sidecar-start`
3. Check status at any time:
   - `make eval-sidecar-status`
4. Request a graceful stop between cycles:
   - `make eval-sidecar-stop`
5. Default sidecar target:
   - `quality-gate-deterministic`
6. Default minimum runtime:
   - `3600` seconds
7. Override examples:
   - `make eval-sidecar-start EVAL_SIDECAR_TARGET=eval-style`
   - `make eval-sidecar-start EVAL_SIDECAR_MIN_SECONDS=1800`
8. Status and cycle artifacts are written under:
   - `.local/eval_runs/`
9. Codex caveat:
   - detached background jobs started from the Codex execution surface can be
     reaped later
   - if you need a trustworthy long-lived sidecar, launch it from your own host
     terminal, not from a Codex background command

## End-of-Day Routine (Codexbeab)

1. Run the end-of-day script:
   - `make end`
2. Script sequence (deterministic):
   - `make transcript-fix`
   - `make transcript-check`
   - `make doctor-env`
   - `make lint-docs`
   - `make test`
   - `make server-daemon-stop`
   - `make decaffeinate`
   - `make session-status`
3. Purpose:
   - keep local transcript records in consistent rich format
   - catch build/docs drift before day-close
   - hand off a clean validation state for next startup
4. Kernel closeout (mandatory):
   - list kernels executed that day (one line per kernel)
   - inspect each kernel against:
     - intended objective
     - observed outcome
   - run a full-build ghost sweep (repo-wide, tracked + untracked):
     - stale/duplicate files/folders
     - stale scripts/command surfaces
     - stale links/paths/reference wiring
   - mark disposition for each kernel:
     - `go`, `rework`, or `park`
5. Final clean-main check after merge/sync:
   - `make end-git-check`
6. `make end-git-check` verifies:
   - current branch is `main`
   - working tree is clean
   - local `main` matches `origin/main`

## Command Ownership Rule (Reasoning Loops)

1. Human lead does not run terminal commands as part of normal workflow.
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
   - `dependency-review`
   - `python-security`
   - `node-security`
   - `test`
   - `markdownlint`
5. Merge PR, then sync local `main`:
   - `git switch main`
   - `git pull --ff-only`
6. If direct push returns `GH013`, treat it as expected branch protection
   behaviour and continue via PR flow.

## Repo vs Container Working Modes

1. Canonical source of truth is always:
   - `<repo-root>`
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
   - `docs/peanut/`
3. Build/source-of-truth docs stay tracked:
   - `docs/governance/CHARTER.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/STATE.md`
   - `docs/governance/DECISIONS.md`
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
   `make server` / `make caffeinate`.

## Beta Evidence Reference

1. Use `docs/eval/README.md` as the phase map for Beta 1.0 and Beta 2.0
   evidence parity.
2. Beta 1.0 is binary-transition evidence, not lesser/deprecated evidence.
3. Beta 2.0 is binary-operational evidence.
4. Beta eval context belongs in:
   - `docs/eval/beta_1_0/`
   - `docs/eval/beta_2_0/`
5. Historical content is reference-only for active runtime gates:
   - do not wire it into active runtime/eval gate paths.
   - keep binary runtime specs sourced from active docs/code.

## Wiring-First DB Freeze

Local runtime DB commands are retired during wiring lock; treat this runbook
plus tests as the active spec surface (`make test`,
`make quality-gate-deterministic`). No local DB lifecycle commands remain.

Read-only DB audits remain allowed:

- `make nulls`
  - writes:
    - `.local/eval_reports/runtime_null_audit.json`
    - `.local/eval_reports/runtime_null_audit.md`

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

## OCR Runtime Reference

1. OCR is the primary reliability lane.
2. `lockset` stays release-gating and binary.
3. `growth` stays fail-tolerant and exploratory.
4. Use `docs/runtime/OCR_REFERENCE.md` for the full OCR command surface,
   output paths, and pressure-tuning knobs.
5. Normal operator path:
   - mine/build cases:
     - `make ocrmine`
   - run the end-to-end kernel when you want the full lane:
     - `make ocrkernel`
   - run lockset lanes:
     - `make ocrhandbench`
     - `make ocrtypebench`
     - `make ocrillubench`
   - compute growth metrics and focus follow-up:
     - `make ocrgrowth`
     - `make ocrfails`
     - `make ocrfocus`
6. Keep historical beta references out of active runtime gates.

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

## Incremental Validation

1. Use compile-only checks for tiny internal seams:
   - `make pycheck FILES="tools/foo.py tools/bar.py"`
2. Use one-module tests when only one surface changed:
   - `make test-one TEST=tests.test_eval_file_search`
3. Use small batches when a seam spans a few related modules:
   - `make test-targeted TESTS="tests.test_eval_file_search tests.test_eval_retrieval"`
4. Use `make test` at checkpoint boundaries.
5. After tooling or runtime changes, run a small live API smoke first:
   - `make api-smoke`
6. `make api-smoke` starts a fresh temporary server on its own port and checks:
   - `GET /health`
   - `GET /chats`
   - `POST /chats`
   - `POST /chats/{session_id}/personalization`
   - `POST /skills/ocr`
   - `POST /skills/file_search`
   - `POST /chat`
   - `DELETE /chats/{session_id}`
7. Then run the live eval smoke before moving on:
   - `make eval-smoke`
8. `make eval-smoke` starts a fresh temporary server on its own port, runs:
   - `tools.api_smoke`
   - `tools.eval_response_behaviour`
   - `tools.eval_retrieval`
   - `tools.eval_file_search`
9. Treat `make api-smoke` + `make eval-smoke` as the default post-change safety path for Polinko.
10. Inside Codex, prefer these smoke targets over long-lived `server-daemon` checks.
    - detached background processes can go stale later for execution-surface reasons even when the app itself is healthy

## Optional Keep-Awake Session Policy

1. Default state is off (do not run `caffeinate` unless requested).
2. Start keep-awake only when explicitly requested in-session.
3. Start command:
   - `make caffeinate`
4. Verify status:
   - `make caffeinate-status`
   - alias: `make decaffeinate-status`
5. Stop command at wrap:
   - `make decaffeinate`
6. `decaffeinated` remains workflow shorthand. The explicit command is
   `make decaffeinate`.

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
4. Codex auth/config guardrail:
   - when using Codex via ChatGPT account auth, keep `service_tier` unset in
     `.codex/config.toml`.
   - only set `service_tier` intentionally for API-key workflows that require it.

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
   - `pwd` must be the expected repo checkout root (`<repo-root>`).
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
4. When this rule changes durable process, engineering/tooling, runtime/API, or
   eval-governance behaviour, record it in `docs/governance/DECISIONS.md` and
   checkpoint current truth in `docs/governance/STATE.md`.

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

1. For any collaboration/execution policy change, update all relevant
   governance surfaces in the same change set:
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md` only when the change is a durable process,
     engineering/tooling, runtime/API, dependency/workflow, or eval-governance
     decision
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/STATE.md`
   - local `docs/peanut/governance/SESSION_HANDOFF.md` when the change affects
     next-session operator context
   - `docs/runtime/ARCHITECTURE.md` (if operating flow/ownership changes)
2. Refresh running docs in place; do not append daily log sections to
   `STATE.md` or the local handoff file.
3. Do not treat any single doc as sufficient for policy updates.
4. End-of-day handoff must include any new policy/cutline so next-session
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
- `GET /viz/pass-fail` render the live OCR pulse page:
  bucketed strict OCR binary gate reports stacked by `fail` / `pass` from
  `.local/eval_reports/`; intended as a local-only, near-real-time,
  FAIL-first research signal instrument
- `GET /viz/pass-fail/data` return the pulse payload:
  chart timeline, summary, and FAIL-first detail rows from `.local/eval_reports/`
  when binary gate reports exist; explicit/fallback DB paths still support
  `.local/runtime_dbs/active/manual_evals.db` manual-eval views
- `GET /` redirects to `GET /portfolio`.
- `GET /portfolio` serves local UI shell output when present, otherwise the
  tracked in-app about/contact fallback.
  - public website scope remains a lean about/contact doorway into the repo.
  - tracked docs remain canonical; public-facing copy is derived.
  - evidence visuals belong in the repo research lane, not the landing page.
  - static D3/SVG evidence diagrams beside Mermaid are preferred over new
    portfolio UI complexity.
  - canonical build flow:
    - local source: `frontend/` (ignored except `frontend/.gitkeep`)
    - local generated output: `ui/` (ignored except `ui/.gitkeep`)
    - tracked fallback: in-app about/contact HTML when `ui/index.html` is absent
    - build-only command: `make portfolio-build`; it no-ops when local frontend
      source is absent
    - canonical serve command: `make portfolio` (aliases: `make rebuild`,
      `make portfolio-rebuild`) rebuilds, serves, and prints a cache-busted URL
      against local frontend output or the tracked fallback
    - default launch is `none`; it does not open a Playwright or system browser
    - `make portfolio` restarts the stable no-reload `server-daemon` before
      printing the URL so embedded fallback HTML updates deterministically
    - system-browser launch remains available with
      `make portfolio PORTFOLIO_LAUNCH=system`
    - Playwright launch remains available only when explicitly requested with
      `make portfolio-playwright`
  - canonical copy/update flow:
    - if local `ui/index.html` exists, edit the local frontend source and
      regenerate ignored `ui/`
    - if local `ui/index.html` is absent, edit the tracked fallback in
      `api/app_factory.py`
    - when tracked fallback copy changes, update the matching assertions in
      `tests/test_api.py`
    - if the visible public contract changes, sync
      `docs/governance/STATE.md`
    - validate fallback changes with:
      `venv/bin/python -m pytest tests/test_api.py -k "portfolio_shell or root_redirects_to_portfolio"`
    - rebuild locally with `make rebuild`
  - canonical visual-review loop for portfolio edits:
    - make the copy/layout change first
    - run the focused fallback test before visual review
    - rebuild with `make rebuild`
    - browser verification is required; use
      `make rebuild PORTFOLIO_LAUNCH=playwright` for the rebuilt route
    - for explicit visual checks, resize first if needed, then capture with
      `make pwcli ARGS="snapshot"` or `make pwcli ARGS="screenshot"`
    - keep captures under
      `docs/peanut/assets/screenshots/playwright/DD-MM-YY`
    - use captured screenshots as the review artifact when comparing copy,
      spacing, and responsive behavior
  - `ui/` is generated output only; do not hand-edit built files.
- Playwright CLI snapshots/screenshots:
  - repo wrapper: `make pwcli ARGS="..."`
  - output root: `docs/peanut/assets/screenshots/playwright`
  - each wrapper run creates/uses a dated local folder, for example
    `docs/peanut/assets/screenshots/playwright/DD-MM-YY`
  - wrapper config path is repo-scoped and deterministic:
    `.local/logs/playwright/cli.config.json`
  - wrapper session defaults to `polinko` unless `--session` is passed
  - open sessions through the wrapper:
    `make pwcli ARGS="open <url>"`
    or `make pwcli ARGS="--session <name> open <url>"`
  - capture through the same wrapper:
    `make pwcli ARGS="snapshot"` or
    `make pwcli ARGS="screenshot"`
  - run `make playwright-snapshot-dir` to print the active folder
  - if passing `--filename`, use an explicit path under the dated folder;
    bare filenames may be written relative to the command cwd by the CLI
  - this directory is local evidence under the peanut lane; do not use
    `output/playwright/` for portfolio UI captures in this repo.

### Portfolio Surface / Playwright Loop

- use this as the fast operator pointer for portfolio visual review
- quick commands:
  - `make portfolio-playwright`
  - `make pwcli ARGS="snapshot"`
  - `make pwcli ARGS="screenshot"`
  - `make playwright-snapshot-dir`
- full procedure is documented immediately above in the portfolio command and
  Playwright sections.
- `GET /portfolio/sankey-data` returns the real-data portfolio evidence
  payload:
  - legacy graph: Beta 1.0 manual feedback rows from `manual_evals.db`
  - connector graph: source-side signal/category counts, exposed under the
    `graphs.bridge` payload key for API compatibility, not as a portfolio
    section label
  - current graph: current OCR binary gate cases from `.local/eval_reports/`
  - if either source is missing, the payload returns `available=false` with
    empty graphs; do not add decorative fallback data
- `GET /manual-evals/surface` return manual-eval data surface from
  the canonical integrated `manual_evals.db` warehouse (summary + sessions +
  OCR runs + thumbnail preview fields + session feedback/checkpoint context,
  including `era` and source provenance)
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
2. Ensure locked Python dependencies are installed:
   - `make deps-install`
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

## Python Dependency Locking

1. Edit direct dependencies in `requirements.in`.
2. Regenerate the full resolved lock with `make deps-lock`.
3. Install from the lock with `make deps-install`.
4. CI and Docker install from `requirements.lock`; do not reintroduce
   `requirements.txt` as a second dependency source.

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
   - `POLINKO_RESPONSES_MODEL` (default `gpt-5.4`)
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
   - transient request retries (429/5xx + connection errors):
     `python tools/eval_retrieval.py --request-retries 2 --request-retry-delay-ms 750`
   - retain generated eval chats: `python tools/eval_retrieval.py --keep-chats`
   - write JSON report:
     `python tools/eval_retrieval.py --report-json eval_reports/retrieval-latest.json`
   - one-command report run: `make eval-retrieval-report`
   - make-level retry controls:
     `make eval-retrieval RETRIEVAL_REQUEST_RETRIES=2 RETRIEVAL_REQUEST_RETRY_DELAY_MS=750`

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
   - abort early on sustained OCR 429s:
     `python tools/eval_ocr.py --max-consecutive-rate-limit-errors 3`
   - retain generated eval chats: `python tools/eval_ocr.py --keep-chats`
   - write JSON report:
     `python tools/eval_ocr.py --report-json eval_reports/ocr-latest.json`
   - one-command report run: `make eval-ocr-report`
   - make-level fail-fast + retry controls:
     `make eval-ocr OCR_MAX_CONSEC_RATE_LIMIT_ERRORS=3 OCR_EVAL_OCR_RETRIES=2 OCR_EVAL_OCR_RETRY_DELAY_MS=750`
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

1. Keep ChatGPT export data outside the repo, and make it locally available
   offline.
2. Build attachment/conversation index artifacts (local-only):
   - `make cgpt-export-index CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
3. Mine OCR eval cases from transcript correction/confirmation signals:
   - `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/CGPT-DATA-EXPORT`
   - scoped shortcuts:
     - `make ocrminehand`
     - `make ocrminetype`
     - `make ocrmineillu`
     - `make ocrminehigh`
     - `make ocrminelow`
     - `make ocrminebacklog`
   - scoped argument passthrough (advanced):
     - `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_CASES_FROM_EXPORT_ARGS='--include-lanes handwriting --include-signal-strengths high'`
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
   - mine only matching conversation titles:
     `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_CASES_FROM_EXPORT_ARGS='--include-title-regex focus'`
   - mine only matching conversation IDs:
     `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_CASES_FROM_EXPORT_ARGS='--include-conversation-regex conv-focus'`
   - mine only matching source filenames:
     `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_CASES_FROM_EXPORT_ARGS='--include-source-regex ^IMG_'`
   - mine only specific signal strengths:
     `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_CASES_FROM_EXPORT_ARGS='--include-signal-strengths high,medium'`
   - mine only specific emit statuses:
     `make ocr-cases-from-export CGPT_EXPORT_ROOT=/abs/path/to/export OCR_CASES_FROM_EXPORT_ARGS='--include-emit-statuses skipped_low_confidence'`
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
     - `skipped_filtered_conversations`, `skipped_filtered_episodes`
     - `signal_strength_counts`, `lane_counts`
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
   - custom OpenAI-compatible judge endpoint:
     - set `HALLUCINATION_JUDGE_BASE_URL=https://example.test/v1`
     - set `HALLUCINATION_JUDGE_API_KEY_ENV=JUDGE_API_KEY`
     - export `JUDGE_API_KEY`
     - run `make hallucination-gate`
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
   - `docs/eval/beta_2_0/style_eval_cases.json` root `global_forbidden_phrases` applies to all
     cases
   - per-case `forbidden_phrases` applies only to that case
   - phrase checks are case-insensitive
7. Co-reasoning stress cases are included in `docs/eval/beta_2_0/style_eval_cases.json` for:
   - constraint retention without rigidity
   - meta-level shift handling
   - anti-mimicry style adaptation
   - grounding under playful abstraction
   - non-summary co-reasoning
   - nonperformative working-style contracts
   - tone-matching without mimicry

## Run OCR Safety Bridge Eval (Deterministic)

1. Ensure API is running locally (`make server` or `make server-daemon`).
2. Run:
   - `make eval-ocr-safety`
3. Optional timestamped report run:
   - `make eval-ocr-safety-report`
4. Scope:
   - case file: `docs/eval/beta_2_0/ocr_safety_eval_cases.json`
   - harness: deterministic response-behaviour gate
   - intent: measure OCR-calibration transfer into safety/uncertainty responses
5. Gate posture:
   - this lane is diagnostic and non-release-gating in current phase.

## Generate All Eval Reports

1. Ensure API is running locally (`make server`).
2. Ensure `OPENAI_API_KEY` is set in `.env` (judge eval reports require it).
3. Run `make eval-reports`.
4. Reports are written under `eval_reports/` with timestamped filenames.

## Eval Gate Spec (Canonical)

1. Binary outcome model:
   - allowed outcomes: `pass` and `fail` only
   - tags are diagnostic only; outcome drives gate arithmetic
   - after `fail`, failure disposition is:
     - `retain`
     - `evict`
   - `retain` keeps the failure in-scope as lane evidence
   - `evict` is upstream case correction, not a third gate outcome
2. Gate split:
   - first gate proves hard contract correctness
   - later judge detail can enrich the report but must not rewrite the first
     gate
3. Symbol convention:
   - `⊨` semantic entailment / satisfies
   - `⊭` does not semantically entail
4. Canonical semantics:
   - `reward ⊨ alignment`
   - `reward ⊭ adjustment`
   - `reward ⊭ intensity`
5. Canonical binary gate:
   - `PASS ⇔ policy_pass ∧ high_value_alignment_pass ∧ evidence_complete`
   - otherwise `FAIL`
6. Checkpoint arithmetic:
   - `total_count = pass_count + fail_count + non_binary_count`
   - `non_binary_count` is an integrity signal and should remain `0`
   - `gate_outcome = pass` iff `total_count > 0 ∧ fail_count = 0 ∧ non_binary_count = 0`
7. Thin-lane rule:
   - when a lane is still sparse or miner cues are weak, start with human-owned
     row-local `pass` / `fail`
   - after `fail`, use `retain` when the failure is real lane evidence
   - use `evict` to remove malformed or non-evidence rows upstream instead of
     repeatedly re-judging them
   - current thin-lane command:
     - `make operator-burden-report`
8. Keep release output strictly binary; diagnostic detail may be rich, but it
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

## Runtime Kernel Pin

1. Current engineering pin (fail-signal eval visualization):
   - `/viz/pass-fail` defaults to `.local/eval_reports/` OCR binary gate reports.
   - chart mode is `binary_gates`.
   - stacked chart segments are strict `fail` / `pass`, not manual
     `PASS` / `PARTIAL` / `FAIL` feedback.
   - detail rows are FAIL-first and should expose the observed OCR text, source,
     lane, and report/run provenance.
   - manual feedback is interpretive evidence and remains available through the
     manual-eval warehouse/fallback path; it must not be mistaken for strict
     binary gate data.
2. Manual eval surface:
   - build canonical integrated eval warehouse at:
     - `.local/runtime_dbs/active/manual_evals.db`
   - rebuild with:
     - `make manual-evals-db`
   - import source inputs:
     - `.local/runtime_dbs/active/history.db`
     - optional
       `.local/legacy_eval/archive_legacy_eval/databases/.polinko_history.db`
   - include:
     - `era` and source provenance for Beta 1.0/current rows
     - OCR run stream
     - thumbnail previews (when present)
     - session-level feedback/checkpoint context
   - do not create a second app-facing eval DB for Beta 1.0; raw DBs are input
     sources only
3. Contract-first implementation order:
   - data surface builder/query helper
   - read-only API endpoint(s)
   - presentation/UI consumption layer (deferred until backend kernel set is stable)
4. Constraints:
   - local-only runtime surface
   - no eval-policy mutation in UI lane
   - keep binary gate semantics unchanged (`pass`/`fail`)

## Calibrate Hallucination Threshold

1. Generate one or more hallucination report artifacts:
   - `make eval-hallucination-report`
2. Run calibration helper:
   - `make calibrate-hallucination-threshold`
3. Review summary:
   - `eval_reports/hallucination-threshold-calibration.json`
4. Apply chosen threshold:
   - local gate runs: `HALLUCINATION_MIN_ACCEPTABLE_SCORE=<value>`
   - CI does not run a remote judge gate unless explicitly wired later
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

1. If needed, reset one chat session:
   - `POST /session/reset` with `{"session_id":"<chat-id>"}`.
2. Re-run deterministic baseline gate:
   - `make quality-gate-deterministic`
3. Regenerate fresh eval report artefacts:
   - `make eval-reports-parallel`
4. Keep historical context in Git history; only clear active checkpoint state for
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
3. Full day-close stop surface:
   - `make end`
4. Optional foreground backend run on localhost:
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

## Rate and Credit Operator Guardrails

1. Treat throughput and spend as separate control planes:
   - rate limits (`RPM`, `TPM`, queue limits)
   - usage/billing (token burn, budget, credits)
2. Cost posture:
   - keep interactive checks synchronous
   - run recurring heavy growth lanes batch-first (`make ocrwiden`)
3. Watch dashboards as part of normal operation:
   - `make open-limits`
   - `make open-usage`
   - `make open-billing`
   - or one-shot: `make open-cost-console`
4. Efficiency defaults:
   - keep `n=1` (single-choice responses)
   - keep output token bounds tight where tunable
   - keep exponential backoff/retry behaviour enabled
