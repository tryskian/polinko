<!-- @format -->

# Automation Spec

## Status

- Current mode: `paused`
- Effective policy: single execution lane (`manual/autonomous engineer` only)
- Scheduled automation is disabled until explicit in-chat go/no-go to re-enable.

## Purpose

Define one canonical automation contract so autonomous scheduled runs do not
drift from manual kernel execution.

## Canonical Scope (When Re-enabled)

1. Input docs:
   - `docs/governance/CHARTER.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/STATE.md`
   - `docs/governance/DECISIONS.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Startup checks:
   - repo/worktree path confirmation
   - branch confirmation
   - host vs devcontainer confirmation
   - environment health via `make doctor-env`
3. Execution policy:
   - execute one deterministic backend kernel per run
   - no parallel implementation tracks in the same run
   - no environment/global-dotfile changes without explicit approval
4. Validation policy:
   - required: `make build-audit`, `make lint-docs`, `make test`,
     `make quality-gate-deterministic`
   - OCR kernels also require lane eval validation commands
5. Git policy:
   - task branch per run
   - PR with validation evidence
   - merge only after required checks are green
6. Governance updates:
   - update `STATE`, `DECISIONS`, and `SESSION_HANDOFF` only for material deltas

## Re-enable Gate

Automation may be re-enabled only when all are true:

1. This spec remains the single canonical source.
2. Startup prompt/brief for automation is aligned to this spec.
3. Worktree isolation is confirmed for any concurrent manual lane.
4. Human go/no-go is explicit in-chat.

## Pause/Resume Rule

- Pause automation immediately if outputs diverge from the canonical spec or
  duplicate manual active work.
- Resume only after spec/prompt alignment is corrected and human go/no-go is
  reconfirmed.
