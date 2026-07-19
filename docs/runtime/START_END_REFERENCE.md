<!-- @format -->

# Start / End Reference

This is the compact operator sheet for the canonical day-open/day-close
commands.

## Start

Command:

```bash
make start
```

Sequence:

The startup routine owns numbered step output through a single step helper, so
step labels and counts stay aligned as the routine changes.

1. Print workspace context:
   - repo root
   - active branch
   - `git status --short --branch`
2. Surface GitHub health attention:
   - `make github-health`
   - optional scope: `GITHUB_HEALTH_REPO`, `GITHUB_HEALTH_RUN_LIMIT`,
     `GITHUB_HEALTH_PR_LIMIT`
   - reported attention continues local startup
3. Run the generic startup safety path:
   - `make doctor-env`
     - reports the active Python interpreter and whether it came from Make's
       repo `.venv` selection, an override, or host fallback
   - `make caffeinate`
   - `make caffeinate-status`
4. Start the repo-managed local server:
   - `make server-daemon`
   - leaves the local API server running under repo-owned PID and log state
5. Verify the runtime smoke path:
   - `make api-smoke`
   - runs an isolated smoke server and smoke database paths for the smoke suite
6. Stop before repo action:
   - print the canonical rehydrate prompt
   - the prompt tells the agent to:
     - say morning startup is complete
     - read `CHARTER`, `STATE`, `DECISIONS`, `RUNBOOK`, `ARCHITECTURE`, and local `SESSION_HANDOFF` if present
     - reply in the morning ritual before implementation
     - include context: printed repo root, host vs devcontainer mode, active branch, clean `main` or feature branch, and runtime health
     - include a kernel map: likely lanes from current docs/state, with
       one recommended first kernel
     - include one startup note only if something needs attention
     - apply the no-guessing controls
     - use the QA browser / DevTools MCP path for rendered UI checks, while
       Playwright remains a separate explicit local-browser helper surface
     - treat the reply as the chat-first alignment pass
     - wait for human alignment before implementation
     - after alignment, run one active kernel at a time and stop before
       broadening

Source of truth:

- [tools/start_of_day_routine.sh](../../tools/start_of_day_routine.sh)

Wake-lock rule:

- `make caffeinate` records only this repo's managed PID
- `CAFFEINATE_CMD` and `CAFFEINATE_MATCH_PATTERN` are configured together so
  start, status, and stop-all inspect the same wake-lock shape
- caffeinate PID, log, ownership metadata, and activity metadata default to a
  repo-scoped runtime namespace under `CAFFEINATE_STATE_DIR`
- `make caffeinate` and companion wake-lock targets reject invalid command,
  match-pattern regex, repo-slug, activity-label, activity-target,
  active-window, and global-cleanup config before they read, report, launch,
  stop, or clean PID/activity state
- caffeinate start, stop, and activity actions reject invalid runtime output
  paths with direct diagnostics before launch, cleanup, or metadata writes
- caffeinate start, status, stop, and stop-all require process-inspection
  tooling before PID ownership classification or cleanup
- `make caffeinate` writes repo-scoped metadata for the managed wake-lock PID
  and the latest repo activity heartbeat
- `make caffeinate` reports only the start/already-running action; detailed
  PID, repo-activity, and wake-assertion output belongs to
  `make caffeinate-status`
- mutating caffeinate lifecycle actions migrate owned flat runtime files before
  launch or stop decisions and clean orphaned flat PID metadata
- high-traffic lifecycle, validation, and runtime operator work targets mark
  repo activity through the same activity metadata without starting, stopping,
  or adopting a wake-lock PID
- current background-runner start/stop targets that own local process state
  mark repo activity before lifecycle work begins
- pure status/read-only targets report state while preserving activity
  freshness
- the managed process is launched in a detached child session so it survives
  non-interactive host shell command exit
- `make decaffeinate` stops the repo-owned PID with bounded
  terminate/escalate cleanup before owned runtime metadata is removed
- `make caffeinate-status` is read-only; it reports `ACTIVE`, `QUIET`,
  `STALE`, or `OFF` from PID ownership, metadata, and activity freshness, and
  reports matching unmanaged `caffeinate` processes without adopting their PIDs;
  stopped/zombie managed PIDs are treated as stale
- `make caffeinate-off-all` is repo-scoped by default: it cleans the managed
  PID and current repo runtime metadata, while global matching-process cleanup
  requires explicit operator opt-in

Runner lifecycle rule:

- `make server-daemon`, `make server-daemon-status`, and
  `make server-daemon-stop` delegate lifecycle actions to
  `tools/run_server_daemon.sh`
  - PID and log defaults live under repo-scoped `SERVER_STATE_DIR`, and status
    reports repo context plus PID/log paths before liveness
  - explicit `SERVER_REPO_SLUG` config is validated before repo-scoped
    PID/log paths are derived
  - launch port, health URL, repo-slug, and readiness config uses defaults only
    when unset; explicit blank config fails before launch or state derivation
  - matching local `uvicorn server:app` processes without PID files are
    adopted on start, surfaced by status, and stopped during closeout recovery
  - matching servers that remain active after startup readiness failure, stop
    signal, or interpreter-mismatch restart preserve the PID file when present
    and fail the action instead of hiding the still-live server
  - start reports success only after the configured local `/health` endpoint is
    reachable within the bounded readiness wait
  - HTTP readiness checks require `curl` before launch work begins, so a
    missing local probe command fails as a prerequisite error instead of a
    generic startup timeout
- `make eval-sidecar-start`, `make eval-sidecar-status`, and
  `make eval-sidecar-stop` delegate lifecycle actions to
  `tools/run_eval_sidecar_start.sh`
  - PID and log defaults live under repo-scoped `EVAL_SIDECAR_STATE_DIR`, and
    status reports repo context plus PID/log/current-file paths before liveness
  - explicit `EVAL_SIDECAR_REPO_SLUG` config is validated before repo-scoped
    PID/log paths are derived
  - missing current-file state is surfaced by start/status, while stop still
    cleans the repo-managed PID for closeout
  - `EVAL_SIDECAR_TARGET` and `EVAL_SIDECAR_MIN_SECONDS` are validated before
    detached launch; unset duration config uses the default, while explicit
    blank duration config fails before PID/log state is written
  - readiness attempt and sleep config uses defaults only when unset; explicit
    blank readiness config fails before launch
  - live PID files are treated as managed only when the process matches
    `tools.eval_sidecar run`; unrelated live PIDs are cleaned from the PID file
    without being stopped
  - matching sidecars that remain active after startup readiness failure or
    stop signal preserve the PID file and fail the action instead of hiding the
    still-live runner
  - start reports success only after the current-run status file exists within
    the bounded readiness wait
- Portfolio app, static output, preview/mockup helpers, and Netlify config live
  under `.archive/quarantine/portfolio-2026-06-29/` for porting to the separate
  `krystian.io` repo. Active runtime, Make, CI, dependency, and closeout
  surfaces stay backend/manual-eval/API centred.
- Make targets stay thin; helper scripts own PID files, log paths, stale state,
  idle state, and detached child-session launch behaviour
- shared shell command checks live in `tools/shell_command_common.sh`, so
  command availability and missing-command diagnostics stay consistent across
  runtime shell wrappers
- shared PID inspection requires `ps` before lifecycle scripts make managed
  PID-state decisions, so missing local process-inspection tooling fails as a
  prerequisite error instead of misleading liveness state
- shared shell PID checks require positive-integer PID values before liveness or
  stop decisions, so malformed, zero, or negative PID-file values are rejected
  as live runner processes
- lifecycle launch ports and readiness-loop bounds are validated before
  process launch, adoption, status, or readiness checks; `server-daemon`
  validates its launch port globally, while local eval gates validate
  smoke-only and gate-only port overrides inside the active suite
- HTTP runner probe URLs must include an explicit port matching the launched
  server port before readiness, adoption, status, or launch work depends on the
  URL; this covers `SERVER_HEALTH_URL`, `SMOKE_BASE_URL`, and `GATE_BASE_URL`
- the shared detached launcher rejects empty, missing, non-launchable commands,
  and output-path failures with direct diagnostics before PID ownership is
  recorded, and stops the started child process group on PID-file write failure
- runner-specific `*_LAUNCHER_PYTHON` overrides are validated before manager
  exec or detached launch, so bad launcher interpreters fail before PID state is
  written
- `make session-status` is the consolidated status surface for the runner
  family. It delegates to `tools/session_status.sh`, which owns the runner
  labels and explicit status dispatch. The helper reports every runner family
  and returns a non-zero status if any child status surface reports runner
  drift. `make end-stop` runs it after stop cleanup so closeout reports the
  post-stop state without hiding individual runner drift.

Active kernel validation:

- During active refactor kernels, use focused checks for the touched surface
- Use `make local-runtime-config-check` when a kernel changes VS Code task or
  local runtime config shape
- Local eval gates start a temporary server for each gate run and use bounded
  cleanup; if that server remains active after the stop signal, the wrapper
  fails clearly instead of waiting indefinitely
- Local eval gates require `curl` before their HTTP readiness probe and use
  configurable `LOCAL_EVAL_GATE_START_ATTEMPTS` /
  `LOCAL_EVAL_GATE_START_SLEEP_SECONDS` bounds for the shell `while`
  readiness loop, avoiding an extra `seq` dependency
- Local eval gate readiness config uses defaults only when unset; explicit
  blank readiness config fails before runner startup work begins
- Lifecycle readiness bounds are validated before runner startup work begins
- Use `make risk-scan` when a kernel changes runtime maps, Make gates, CI,
  background runners, startup/closeout, or local configuration surfaces
  - this includes direct command-probe routing through the shared shell command
    helper surfaces
- Use `make runtime-tool-reference-check` when a kernel changes runtime,
  Make, CI, or docs references to `tools/*.py` or `tools/*.sh` helpers
- Use `make build-hygiene-core` for the CI core hygiene gate that covers
  environment, transcript, and whitespace surfaces
- Use `make build-hygiene` for the local PR-safe aggregate gate over the core
  hygiene target plus build, docs, dependency, and test surfaces; it repeats
  the whitespace diff check after the leaf gates
- Use `make pr-preflight` before publishing a PR as the local readiness command for
  `make build-hygiene`
- Use `make github-pr-create` with `GITHUB_PR_BODY_FILE=-` and a quoted heredoc
  for one-off PR Markdown; file paths are for durable body files, and PR bodies
  with code spans or backticks go through `--body-file`
- Use `make end-preflight` when the kernel is broad enough to need the full
  branch-local quality suite
- End each kernel summary with the recommended next kernel
- Reserve `make end` for real session closeout only

## End

Command:

```bash
make end
```

Sequence:

| Step | Action | Command |
| --- | --- | --- |
| 1 | Verify current-truth docs freshness and path safety | `make end-docs-check` |
| 2 | Run transcript repair | `make transcript-fix` |
| 3 | Validate curated transcripts | `make transcript-check` |
| 4 | Verify the environment | `make doctor-env` |
| 5 | Validate shell helper contracts | `make scripts-check` |
| 6 | Check tracked docs/code for local path leaks | `make path-leak-check` |
| 7 | Verify runtime risk-surface coverage | `make risk-scan` |
| 8 | Verify runtime tool reference coverage | `make runtime-tool-reference-check` |
| 9 | Verify operator command boundaries | `make operator-command-check` |
| 10 | Run Python style checks | `make ci-python-style` |
| 11 | Run Python type checks | `make ci-python-type-check` |
| 12 | Lint docs | `make lint-docs` |
| 13 | Smoke-test editable package import | `make package-install-check` |
| 14 | Run tests | `make test` |
| 15 | Check diff whitespace | `git diff --check` |
| 16 | Run dependency security checks | `make security-checks` |
| 17 | Stop background tasks | `make end-stop` |
| 18 | Surface GitHub health attention | `make github-health` |
| 19 | Prune stale remote-tracking refs | `make git-prune-stale-refs` |
| 20 | Verify current branch must be `main` and synced | `make end-git-check` |

Preflight:

- `make end-preflight`
- runs branch-local validation without stopping background tasks
- exercises the same labelled core closeout step dispatch as `make end`
- leaves final clean-main Git closeout for the real session close

Explicit companion checks:

- `make end-docs-check`
  - checks tracked text surfaces for local machine path leaks
  - verifies `STATE` and local `SESSION_HANDOFF` were refreshed today
  - when local `SESSION_HANDOFF` exists, verifies it names the current short
    commit so same-date stale handoffs fail closeout
- `make scripts-check`
  - validates tracked shell helper shebangs, strict modes, sourced helper
    contracts, `$()` command substitution in active shell surfaces, and
    root-helper coverage for executable operator scripts
  - supports literal Markdown code spans through quoted heredoc output
  - keeps shared command helper surfaces registered for runtime shell wrappers
- `make path-leak-check`
  - checks tracked text surfaces for local machine path leaks
- `make local-runtime-config-check`
  - validates VS Code task/config shape, extension recommendation drift, and
    devcontainer config/setup-script drift through
    `tools.check_local_runtime_config`
- `make risk-scan`
  - checks runtime map, Make, CI, runner, and local configuration coverage for
    known high-risk surfaces
  - verifies direct command probes route through approved shared shell helper
    surfaces
- `make runtime-tool-reference-check`
  - checks runtime references to tracked `tools/*.py` and `tools/*.sh` helpers
- `make operator-command-check`
  - checks current operator command names and keeps parked OCR eval shortcuts
    out of automatic startup, closeout, and CI dependencies
- `make security-checks`
  - runs local Python and root Node dependency audits
- `make api-smoke`
  - uses isolated default localhost port and DB paths unless `SMOKE_PORT`,
    `SMOKE_BASE_URL`, and smoke DB paths are set explicitly
- `make deps-refresh`
  - refreshes local Python and root npm dependency surfaces after Dependabot
    or dependency metadata changes
- `make type-check`
  - runs mypy against active `src/` and `tools/` Python surfaces
- `make end-git-check`
  - also available as a standalone git-only closeout check
  - uses default closeout branch and remote only when config is unset
  - rejects explicit blank closeout branch or remote config before Git work
  - verifies current branch is `main`
  - verifies the working tree is clean
  - verifies local `main` is synced with `origin/main`
- `make git-prune-stale-refs`
  - runs during `make end` immediately before the final clean-main Git check
  - uses default closeout remote only when config is unset
  - rejects explicit blank closeout remote config before Git work
  - prunes stale remote-tracking refs for the configured closeout remote after
    merged or deleted PR branches
  - leaves local branches in place

Read-only tooling pin:

- `make ocr-inventory`
  - print OCR local evidence shape and freshness without running evals
- `make ocr-inventory-json`
  - print the same OCR inventory as JSON
- `FRESHNESS_DAYS=<days>`
  - override the OCR inventory freshness threshold

Source of truth:

- [tools/end_of_day_routine.sh](../../tools/end_of_day_routine.sh)
- [tools/check_end_git_clean.sh](../../tools/check_end_git_clean.sh)
- [tools/git_prune_stale_refs.sh](../../tools/git_prune_stale_refs.sh)
- [Makefile](../../Makefile)
