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
   - print the canonical docs to read:
     - `docs/governance/CHARTER.md`
     - `docs/governance/STATE.md`
     - `docs/governance/DECISIONS.md`
     - `docs/runtime/RUNBOOK.md`
     - `docs/runtime/ARCHITECTURE.md`
     - local `docs/peanut/governance/SESSION_HANDOFF.md` if present
   - give the 5-bullet startup read
   - name exactly one active kernel
   - do not branch, search, or edit until that is stated

Source of truth:

- [tools/start_of_day_routine.sh](../../tools/start_of_day_routine.sh)

## End

Command:

```bash
make end
```

Sequence:

1. Run the generic closeout safety path:
   - artifact repair/check
   - environment/docs/test validation
   - background-process shutdown
     - `make server-daemon-stop`
     - `make decaffeinate`
     - `make session-status`
2. Final clean-main check after merge/sync:
   - `make end-git-check`

`make end-git-check` then verifies:

- current branch is `main`
- working tree is clean
- local `main` is synced with `origin/main`

Source of truth:

- [tools/end_of_day_routine.sh](../../tools/end_of_day_routine.sh)
- [tools/check_end_git_clean.sh](../../tools/check_end_git_clean.sh)
- [Makefile](../../Makefile)
