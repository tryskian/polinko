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
- unmanaged `caffeinate` processes are reported but never adopted or stopped

## End

Command:

```bash
make end
```

Sequence:

1. Run the generic closeout safety path:
   - artifact repair/check
   - tracked path leak check
   - local path leak audit
   - environment/docs/test validation
   - background-process shutdown
     - `make server-daemon-stop`
     - `make decaffeinate`
     - `make session-status`
2. Final clean-main check after merge/sync:
   - `make end-git-check`

Preflight:

- `make end-preflight`
- runs the validation and background-stop path without requiring clean synced
  `main`

`make end-git-check` then verifies:

- current branch is `main`
- working tree is clean
- local `main` is synced with `origin/main`

Source of truth:

- [tools/end_of_day_routine.sh](../../tools/end_of_day_routine.sh)
- [tools/check_end_git_clean.sh](../../tools/check_end_git_clean.sh)
- [Makefile](../../Makefile)
