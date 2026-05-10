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

1. Print the canonical docs to read:
   - `docs/governance/CHARTER.md`
   - `docs/governance/STATE.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/runtime/ARCHITECTURE.md`
   - local `docs/peanut/governance/SESSION_HANDOFF.md` if present
2. Print workspace context:
   - repo root
   - active branch
   - `git status --short --branch`
3. Run the generic startup safety path:
   - `make doctor-env`
   - `make caffeinate`
   - `make caffeinate-status`
   - `make api-smoke`

Source of truth:

- [tools/start_of_day_routine.sh](../../tools/start_of_day_routine.sh)

## End

Command:

```bash
make end
```

Sequence:

1. Run the generic closeout safety path:
   - sanity/repair checks
   - docs/build validation
   - test validation
   - background-process shutdown
2. Final shutdown command:
   - `make end-stop`
3. Final clean-main check after merge/sync:
   - `make end-git-check`

`make end-stop` then runs:

- `make server-daemon-stop`
- `make caffeinate-off-all`
- `make session-status`

`make end-git-check` then verifies:

- current branch is `main`
- working tree is clean
- local `main` is synced with `origin/main`

Source of truth:

- [tools/end_of_day_routine.sh](../../tools/end_of_day_routine.sh)
- [tools/check_end_git_clean.sh](../../tools/check_end_git_clean.sh)
- [Makefile](../../Makefile)
