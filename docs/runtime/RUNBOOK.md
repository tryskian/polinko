<!-- @format -->

# Runbook

## When to Read This

Use this doc for operator procedure.

- `docs/governance/CHARTER.md`
  - durable rules and role split
- `docs/runtime/ARCHITECTURE.md`
  - stable system shape
- `docs/governance/STATE.md`
  - tracked current truth
- local `docs/peanut/governance/SESSION_HANDOFF.md`
  - active kernel and next-session carryover

## Branch, Worktree, and Scope Policy

1. Canonical repo root is:
   - `/abs/path/to/polinko`
2. Default workflow is one feature branch per change set:
   - `git switch -c codex/bigbrain/<task-name>`
3. Start edits from a feature branch.
4. Use a worktree only when you need parallel active implementation tracks.
5. Keep one logical task per branch; merge or close before starting the next.
6. Use worktrees for parallel code changes.
7. Use parallel agents only for bounded analysis after architecture,
   acceptance criteria, and rubric constraints are explicit.

## Command Surface Rule

1. Keep one atomic command per operator action.
2. Keep operator thinking in procedure and keep wrapper targets mechanical.
3. Procedure lives in this runbook.
4. Mechanical checks live in `make` targets.

## Morning Startup Ritual

1. Read in this order:
   - `docs/governance/CHARTER.md`
   - `docs/governance/STATE.md`
   - local `docs/peanut/governance/SESSION_HANDOFF.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/runtime/ARCHITECTURE.md`
2. Confirm execution location:
   - canonical repo root or dedicated worktree
3. Confirm active branch:
   - `git branch --show-current`
4. If on `main`, create or switch to a feature branch before edits.
5. If parallel tracks are active, keep each track in its own worktree.
6. Give the startup breakdown before implementation:
   - current state
   - risks
   - next kernel
   - repo/worktree context
   - active branch
7. After steps 1-6, run:
   - `make doctor-env`
   - `make caffeinate`
   - `make caffeinate-status`
   - `make api-smoke`

## Environment Doctor

1. Run:
   - `make doctor-env`
2. It checks:
   - Python path
   - venv
   - package imports
   - shell setup
3. Resolve actionable issues before runtime or eval work.

## Inspect-First Rule

1. If a file, path, screenshot, log, report, or transcript is named, inspect
   it before interpretation.
2. Use source evidence as the basis for interpretation.
3. State inspection status plainly.

## Command Ownership

1. Human lead owns:
   - objective
   - scope
   - acceptance criteria
   - meaning-level trade-offs
   - go/no-go decisions
2. Engineer owns:
   - implementation
   - validation
   - command execution
   - Git and PR flow
   - proactive hygiene
3. Default mode is execution-first:
   - do the work directly when asked

## Protected Main PR Flow

1. Work on a feature branch.
2. Commit locally.
3. Push the branch.
4. Open a PR to `main`.
5. Wait for required checks.
6. Merge through the protected-main flow.
7. Sync local `main`:
   - `git switch main`
   - `git pull --ff-only`
8. Final local repo state must be clean and synced with `origin/main`.

## End-of-Day Ritual

1. Finish branch-local validation before merge:
   - `make doctor-env`
   - `make lint-docs`
   - `make test`
   - `git diff --check`
2. Package the branch when the kernel is ready.
3. Merge through the protected-main PR flow.
4. After merge, switch back to `main` and pull fast-forward only.
5. Run closeout checks:
   - `make decaffeinate`
   - `make decaffeinate-status`
   - `make end-git-check`
6. Update tracked current truth and local handoff before stopping.
7. End state must be:
   - merged
   - clean local `main`
   - synced with `origin/main`

## Local-Only Docs Policy

1. `docs/peanut/` is the local-only lane.
2. Use it for:
   - transcripts
   - theory
   - design refs
   - working notes
   - operator handoff
3. Tracked docs remain canonical project truth.
4. Keep local-only files in the local lane and keep tracked repo truth in the
   tracked docs surface.

## Atomic Commands

- `make doctor-env`
  - environment health check
- `make caffeinate`
  - start repo-managed wake lock
- `make caffeinate-status`
  - report repo-managed wake-lock status
- `make decaffeinate`
  - stop repo-managed wake lock
- `make decaffeinate-status`
  - report closeout wake-lock status
- `make api-smoke`
  - live backend smoke check
- `make lint-docs`
  - docs lint
- `make test`
  - test suite
- `make end-git-check`
  - clean-main closeout check
