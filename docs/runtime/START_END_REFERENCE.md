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
     - read `CHARTER`, `STATE`, `DECISIONS`, `RUNBOOK`, `ARCHITECTURE`, and local `SESSION_HANDOFF` if present
     - return 5 bullets covering current state, risks, and next kernel
     - confirm repo path, host vs devcontainer mode, active branch, and whether the thread is on clean `main` or a feature branch
     - apply the no-guessing controls
     - run one active kernel at a time
     - execute the `Next Slice` from `SESSION_HANDOFF` with full validation

Source of truth:

- [tools/start_of_day_routine.sh](../../tools/start_of_day_routine.sh)

Wake-lock rule:

- `make caffeinate` records only this repo's managed PID
- the managed process is launched in a detached child session so it survives
  non-interactive host shell command exit
- `make decaffeinate` stops the repo-owned PID
- unmanaged `caffeinate` processes are reported but never adopted or stopped

## End

Command:

```bash
make end
```

Aliases:

- `make eod`
- `make end-preflight`

Sequence:

1. Verify the Git closeout state:
   - `make end-git-check`
   - current branch must be `main`
   - working tree must be clean
   - local `main` must be synced with `origin/main`
2. Run transcript repair:
   - `make transcript-fix`
3. Validate curated transcripts:
   - `make transcript-check`
4. Verify the environment:
   - `make doctor-env`
5. Run Python style checks:
   - `make ci-python-style`
6. Run Python type checks:
   - `make ci-python-type-check`
7. Lint docs:
   - `make lint-docs`
8. Run tests:
   - `make test`
9. Run dependency security checks:
   - `make security-checks`
10. Stop background tasks:
    - `make eod-stop`
      - `make server-daemon-stop`
      - `make caffeinate-off-all`
      - `make session-status`

Preflight:

- `make end-preflight`
- runs the same literal closeout routine as `make end`

Explicit companion checks:

- `make end-docs-check`
  - verifies `STATE` and local `SESSION_HANDOFF` were refreshed today
- `make security-checks`
  - runs local Python and Node dependency audits
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
