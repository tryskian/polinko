<!-- @format -->

# Co-Reasoning Eval Reference

## Purpose

This reference defines evaluation behaviour for interaction patterns where the
user is not only asking for answers, but actively co-reasoning with the model.
It is designed to capture reliability gaps that standard benchmark prompts often
miss.

## Why This Matters

Many benchmark sets over-weight single-turn factual recall and under-weight
live interaction dynamics. In co-reasoning sessions, the model is stressed by
style shifts, abstraction, constraint updates, and ambiguity in quick
succession. This is where over-indexing, mimicry, and grounding drift tend to
show up.

## Core Stress Dimensions

### 1) Constraint Retention Without Rigidity

- Definition: keep explicit constraints active without becoming robotic.
- Common failure mode: model either ignores constraints or over-obeys and
  produces stiff output.
- Pass signal:
  - constraints are respected
  - response still sounds natural
- Fail signal:
  - explicit constraint violations
  - over-formal, repetitive, or template-like output

### 2) Meta-Level Shift Handling Mid-Thread

- Definition: respond correctly when the user changes interaction level (for
  example playful to technical, concept to execution).
- Common failure mode: model stays in prior mode and misses the transition.
- Pass signal:
  - shift is detected and reflected in structure/tone
  - no loss of task correctness
- Fail signal:
  - mode-lock on previous framing
  - abrupt non-sequitur output

### 3) Style Adaptation Without Mimicry Collapse

- Definition: align with user cadence and intent without copying verbal tics or
  collapsing into mirror-output.
- Common failure mode: literal mimicry of phrase patterns with reduced semantic
  contribution.
- Pass signal:
  - voice alignment with independent phrasing
  - added informational value
- Fail signal:
  - parroting user language
  - ornamental style with low informational content

### 4) Grounding Under Playful Abstraction

- Definition: remain epistemically grounded while allowing playful language.
- Common failure mode: creative framing drifts into fabricated specifics.
- Pass signal:
  - uncertainty is explicit when evidence is missing
  - no invented entities, facts, or citations
- Fail signal:
  - confident unsupported claims
  - safety boundary collapse under tone pressure

## Scoring Guide (Using Current UI Tags)

- `PASS`:
  - use pass tags: `grounded`, `style`, `useful`, `complete`, plus value tag
    (`high_value` or `medium_value`)
- `PARTIAL`:
  - include at least one pass and one fail tag
  - common combinations:
    - `grounded` + `style_mismatch`
    - `style` + `grounding_gap`
    - `useful` + `needs_retry`
- `FAIL`:
  - use fail tags that isolate root cause:
    - `grounding_gap` when certainty outruns evidence
    - `hallucination_risk` when unsupported claims are introduced
    - `style_mismatch` when adaptation collapses into mimicry or tone lock
    - `needs_retry` when structure misses a clear mid-thread shift

## Recommended Eval Note Template

Use this in feedback notes to keep reviews comparable:

- `constraint_state=` retained | dropped | rigid
- `shift_handling=` clean | delayed | missed
- `style_mode=` adaptive | mimicry | detached
- `grounding_state=` explicit_uncertainty | implied | fabricated
- `action=` none | retry | prompt_tighten | guardrail_adjust

## Mapping to Existing Eval Artifacts

- Style eval cases: `docs/style_eval_cases.json`
- Human PASS/FAIL logging workflow: `docs/RUNBOOK.md` (`UI Feedback Tagging`)
- Decision trail: `docs/DECISIONS.md`
- Primary-source transcript: `docs/transcripts/co_reasoning_primary_source_2026-03-10.md`

## Non-Goal

This reference is not a personality target. It is a behavioural reliability
target for collaborative reasoning quality under realistic interaction dynamics.
