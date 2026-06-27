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

1. Print workspace context:
   - repo root
   - active branch
   - `git status --short --branch`
2. Run the generic startup safety path:
   - `make doctor-env`
     - reports the active Python interpreter and whether it came from Make's
       repo `.venv` selection, an override, or host fallback
   - `make caffeinate`
   - `make caffeinate-status`
   - `make api-smoke`
3. Stop before repo action:
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
- the managed process is launched in a detached child session so it survives
  non-interactive host shell command exit
- `make decaffeinate` stops the repo-owned PID
- `make caffeinate-status` reports matching unmanaged `caffeinate` processes
  without adopting their PIDs
- `make caffeinate-off-all` is closeout cleanup: it stops the repo-owned PID,
  then clears any remaining process that matches the configured wake-lock
  command pattern

Runner lifecycle rule:

- `make server-daemon`, `make server-daemon-status`, and
  `make server-daemon-stop` delegate lifecycle actions to
  `tools/run_server_daemon.sh`
  - matching local `uvicorn server:app` processes without PID files are
    adopted on start, surfaced by status, and stopped during closeout recovery
- `make eval-sidecar-start`, `make eval-sidecar-status`, and
  `make eval-sidecar-stop` delegate lifecycle actions to
  `tools/run_eval_sidecar_start.sh`
  - missing current-file state is surfaced by start/status, while stop still
    cleans the repo-managed PID for closeout
  - live PID files are treated as managed only when the process matches
    `tools.eval_sidecar run`; unrelated live PIDs are cleaned from the PID file
    without being stopped
- `make portfolio-mockups`, `make portfolio-mockups-status`, and
  `make portfolio-mockups-stop` delegate mockup-server lifecycle actions to
  `tools/run_portfolio_mockups.sh`
- Make targets stay thin; helper scripts own PID files, log paths, stale state,
  idle state, and detached child-session launch behaviour
- the shared detached launcher stops a started child process if the PID file
  cannot be written, so failed starts do not leave unmanaged background
  processes behind
- `make session-status` is the consolidated status surface for the runner
  family. `make end-stop` runs it after stop cleanup so closeout reports the
  post-stop state without hiding individual runner drift.

Active kernel validation:

- During active refactor kernels, use focused checks for the touched surface
- Use `make local-runtime-config-check` when a kernel changes VS Code task or
  local runtime config shape
- Use `make risk-scan` when a kernel changes runtime maps, Make gates, CI,
  background runners, startup/closeout, or local configuration surfaces
- Use `make pr-preflight` before publishing a PR when you need the local
  CI-equivalent gate plus whitespace diff check
- Use `make end-preflight` when the kernel is broad enough to need the full
  branch-local quality suite
- End each kernel summary with the recommended next kernel
- Do not run `make end` after every kernel; reserve it for real session
  closeout only

## End

Command:

```bash
make end
```

Aliases:

- `make eod`
  - compatibility alias for `make end`; closeout helper targets use
    current-name `end-*` vocabulary

Sequence:

| Step | Action | Command |
| --- | --- | --- |
| 1 | Verify current-truth docs freshness | `make end-docs-check` |
| 2 | Run transcript repair | `make transcript-fix` |
| 3 | Validate curated transcripts | `make transcript-check` |
| 4 | Verify the environment | `make doctor-env` |
| 5 | Validate shell helper contracts | `make scripts-check` |
| 6 | Check tracked docs/code for local path leaks | `make path-leak-check` |
| 7 | Verify runtime risk-surface coverage | `make risk-scan` |
| 8 | Verify operator alias boundaries | `make operator-alias-check` |
| 9 | Run Python style checks | `make ci-python-style` |
| 10 | Run Python type checks | `make ci-python-type-check` |
| 11 | Lint docs | `make lint-docs` |
| 12 | Smoke-test editable package import | `make package-install-check` |
| 13 | Run tests | `make test` |
| 14 | Check diff whitespace | `git diff --check` |
| 15 | Run dependency security checks | `make security-checks` |
| 16 | Stop background tasks | `make end-stop` |
| 17 | Verify current branch must be `main` and synced | `make end-git-check` |

Preflight:

- `make end-preflight`
- runs branch-local validation without stopping background tasks
- skips final clean-main Git closeout because it is not the real day close

Explicit companion checks:

- `make end-docs-check`
  - verifies `STATE` and local `SESSION_HANDOFF` were refreshed today
  - when local `SESSION_HANDOFF` exists, verifies it names the current short
    commit so same-date stale handoffs fail closeout
- `make scripts-check`
  - validates tracked shell helper shebangs, strict modes, sourced helper
    contracts, and root-helper coverage for executable operator scripts
- `make path-leak-check`
  - checks tracked text surfaces for local machine path leaks
- `make local-runtime-config-check`
  - validates VS Code task/config shape, extension recommendation drift, and
    devcontainer config/setup-script drift through
    `tools.check_local_runtime_config`
- `make risk-scan`
  - checks runtime map, Make, CI, runner, and local configuration coverage for
    known high-risk surfaces
- `make operator-alias-check`
  - checks manual eval compatibility aliases and keeps parked OCR eval aliases
    out of automatic startup, closeout, and CI dependencies
- `make security-checks`
  - runs local Python, root Node, and portfolio Node dependency audits
- `make api-smoke`
  - uses isolated default localhost port and DB paths unless `SMOKE_PORT`,
    `SMOKE_BASE_URL`, and smoke DB paths are set explicitly
- `make refresh-deps`
  - refreshes local Python, root npm, and portfolio npm dependency surfaces
    after Dependabot or dependency metadata changes
- `make type-check`
  - runs mypy against active `src/` and `tools/` Python surfaces
- `make end-git-check`
  - also available as a standalone git-only closeout check
  - verifies current branch is `main`
  - verifies the working tree is clean
  - verifies local `main` is synced with `origin/main`
- `make git-prune-stale-refs`
  - prunes stale `origin/*` remote-tracking refs after merged or deleted PR
    branches
  - does not delete local branches

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
- [Makefile](../../Makefile)
