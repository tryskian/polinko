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
   - `make caffeinate`
   - `make caffeinate-status`
   - `make api-smoke`
3. Stop before repo action:
   - print the canonical rehydrate prompt
   - the prompt tells the agent to:
     - say morning startup is complete
     - read `CHARTER`, `STATE`, `DECISIONS`, `RUNBOOK`, `ARCHITECTURE`, and local `SESSION_HANDOFF` if present
     - reply in the morning ritual
     - include context: printed repo root, host vs devcontainer mode, active branch, clean `main` or feature branch, and runtime health
     - include kernel candidates: likely lanes from current docs/state, with
       one recommended first kernel
     - include one startup note only if something needs attention
     - apply the no-guessing controls
     - after alignment, run one active kernel at a time and stop before
       broadening
     - pause for alignment with the human lead before implementation

Source of truth:

- [tools/start_of_day_routine.sh](../../tools/start_of_day_routine.sh)

Wake-lock rule:

- `make caffeinate` records only this repo's managed PID
- the managed process is launched in a detached child session so it survives
  non-interactive host shell command exit
- `make decaffeinate` stops the repo-owned PID
- unmanaged `caffeinate` processes are reported but never adopted or stopped

Runner lifecycle rule:

- `make server-daemon`, `make server-daemon-status`, and
  `make server-daemon-stop` delegate lifecycle actions to
  `tools/run_server_daemon.sh`
- `make eval-sidecar-start`, `make eval-sidecar-status`, and
  `make eval-sidecar-stop` delegate lifecycle actions to
  `tools/run_eval_sidecar_start.sh`
- `make portfolio-mockups`, `make portfolio-mockups-status`, and
  `make portfolio-mockups-stop` delegate mockup-server lifecycle actions to
  `tools/run_portfolio_mockups.sh`
- Make targets stay thin; helper scripts own PID files, log paths, stale state,
  idle state, and detached child-session launch behaviour

## End

Command:

```bash
make end
```

Aliases:

- `make eod`

Sequence:

1. Verify current-truth docs freshness:
   - `make end-docs-check`
2. Run transcript repair:
   - `make transcript-fix`
3. Validate curated transcripts:
   - `make transcript-check`
4. Verify the environment:
   - `make doctor-env`
5. Validate shell helper contracts:
   - `make scripts-check`
6. Check tracked docs/code for local path leaks:
   - `make path-leak-check`
7. Run Python style checks:
   - `make ci-python-style`
8. Run Python type checks:
   - `make ci-python-type-check`
9. Lint docs:
   - `make lint-docs`
10. Smoke-test editable package import:
    - `make package-install-check`
11. Run tests:
    - `make test`
12. Check diff whitespace:
    - `git diff --check`
13. Run dependency security checks:
    - `make security-checks`
14. Stop background tasks:
    - `make eod-stop`
        - `make eval-sidecar-stop`
        - `make portfolio-mockups-stop`
        - `make server-daemon-stop`
        - `make caffeinate-off-all`
        - `make session-status`
15. Verify the Git closeout state:
    - `make end-git-check`
    - current branch must be `main`
    - working tree must be clean
    - local `main` must be synced with `origin/main`

Preflight:

- `make end-preflight`
- runs branch-local validation without stopping background tasks
- skips final clean-main Git closeout because it is not the real day close

Explicit companion checks:

- `make end-docs-check`
  - verifies `STATE` and local `SESSION_HANDOFF` were refreshed today
- `make scripts-check`
  - validates tracked shell helper shebangs, strict modes, and sourced helper
    contracts
- `make path-leak-check`
  - checks tracked text surfaces for local machine path leaks
- `make security-checks`
  - runs local Python and Node dependency audits
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
