# Polinko Workflow

## Purpose

Use this when you want answers, planning, or interpretation without triggering
implementation flow.

## Routing Rules

- Use this thread (codexbeab) for:
  - product/runtime/governance context
  - architecture/process judgement
  - decisions tied to active Polinko build state
- Use a separate agent/thread for:
  - non-blocking side questions
  - external site/content work (`krystian.io`, portfolio copy, narrative framing)
  - tool-specific learning tracks (SQLite Intelliview workflows, notebook UX)

## Ask Format (No-Execution)

Use this 5-line format when you want answer-only mode:

```text
Mode: answer-only
Objective: <what you need>
Scope: <files/tools/context to use>
Constraints: no code changes, no git actions, no implementation steps
Output: short guidance + examples only
```

## Ask Format (Execution)

Use this format when you want implementation:

```text
Mode: execute
Objective: <change to make>
Scope: <where to change>
Acceptance: <how done is measured>
```

## Copy/Paste Prompts

### SQLite Intelliview (answer-only)

```text
Mode: answer-only
Objective: teach me how to query SQLite Intelliview for Polinko eval/runtime DBs
Scope: this repo context only
Constraints: no code changes, no git actions
Output: 8-12 practical queries, what each query tells me, and common mistakes
```

### `krystian.io` landing-page refresh (strategy first)

```text
Mode: answer-only
Objective: define a content and structure refresh plan for krystian.io
Scope: role narrative, portfolio positioning, information architecture
Constraints: no code changes yet
Output: page outline, section copy direction, CTA strategy, and visual tone guidance
```

## When To Split Into A New Agent

- Split when the question does not require current branch/runtime state.
- Split when you want uninterrupted implementation to continue here.
- Split when topic is content/research-heavy and not build-critical.

## Ownership Boundary

- Imagineer sets objective, scope, and go/no-go.
- Engineer executes implementation when mode is `execute`.
- In `answer-only` mode, response stays advisory and non-operational.
