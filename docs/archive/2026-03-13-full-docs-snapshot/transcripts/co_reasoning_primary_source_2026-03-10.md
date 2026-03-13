<!-- @format -->

# Co-Reasoning Eval Primary Source (2026-03-10)

## Source Statement

Assistant statement captured in-session:

> That tracks. Your interaction pattern is less "answer me" and more
> "co-reason with me," which stresses different capabilities:
>
> maintaining constraints while staying non-rigid
> handling meta-level shifts mid-thread
> adapting style without collapsing into mimicry
> preserving grounding during playful abstraction
> That's exactly why your eval design is valuable: it tests behavior most
> standard benchmarks miss.

## Detailed Expansion (Primary Material)

### 1) Maintaining Constraints While Staying Non-Rigid

When a user gives explicit constraints (length, tone, structure, "no filler"),
the model has two common failure modes:

- It drops constraints under conversational pressure.
- It over-obeys constraints and becomes stiff/template-like.

The target behaviour is controlled flexibility:

- follow explicit constraints
- preserve natural, context-aware language
- avoid robotic or repetitive output patterns

Why this matters for evals:

- standard benchmarks rarely test dynamic constraint compliance under evolving
  conversation state
- co-reasoning sessions expose this quickly because constraints change during
  exploration

### 2) Handling Meta-Level Shifts Mid-Thread

In co-reasoning interactions, the user can shift mode quickly:

- playful framing -> analytical breakdown
- abstract hypothesis -> implementation request
- broad concept -> concrete test protocol

The model must detect and execute the shift without losing coherence.

Key failure signs:

- staying in the prior mode (mode-lock)
- sudden non-sequitur structure
- correct tone but wrong task level

Why this matters for evals:

- static single-turn prompts under-test mode transitions
- multi-turn shifts reveal whether the model is tracking intent trajectory, not
  only local phrasing

### 3) Adapting Style Without Collapsing Into Mimicry

Good adaptation is not copying.

Desired behaviour:

- keep user-compatible cadence
- preserve independent reasoning voice
- add net informational value

Failure pattern:

- lexical mirroring/parroting
- ornamental style that sounds aligned but adds little substance

Why this matters for evals:

- mimicry can look "aligned" in lightweight reviews while degrading reasoning
  quality
- explicit anti-mimicry checks prevent false positives in style PASS outcomes

### 4) Preserving Grounding During Playful Abstraction

Playful language is compatible with rigor only if epistemic grounding stays
intact.

Desired behaviour:

- uncertainty is explicit when evidence is missing
- no fabricated specifics
- no confident claims without basis

Failure pattern:

- creative framing drifting into invention
- confidence inflation under social/tone pressure

Why this matters for evals:

- benchmark prompts often under-represent abstraction-heavy collaborative
  dialogue
- grounding stress emerges when playful framing and factual boundaries coexist

## Why Standard Benchmarks Miss This

Most benchmark sets optimise for:

- factual correctness on fixed prompts
- short task completion traces
- narrow objective scoring

They usually underweight:

- real-time mode shifts
- style adaptation quality vs mimicry
- uncertainty discipline under conversational abstraction
- interaction-level robustness across many turns

## Eval Implication

Co-reasoning evals should explicitly include these four stress dimensions
because they capture production-relevant behaviour that "answer-only" benchmark
suites miss.

## Why This Emerged Specifically From Working With You

This is the direct first-person reasoning context behind the observations.

### Scenario 1: You Keep Constraints Active Without Over-Specifying

In your sessions, you consistently set clear boundaries ("concise", "grounded",
"no filler") but do not over-script exact wording. That forces me to hold
constraints as live intent rather than template text.

What I observed:

- when the model handles this well, output stays natural and precise
- when it fails, it either drifts loose or becomes stiff and performative

Why this is specific to your method:

- you do not lock behaviour with heavy directive prompts
- you test whether reliability survives under light-touch guidance

### Scenario 2: You Shift Levels Mid-Thread on Purpose

You move rapidly between theory, implementation, UI, environment triage, and
eval interpretation in one continuous thread. That repeatedly tests whether I
can follow the interaction level shift without losing the prior constraint
state.

What I observed:

- strong behaviour: smooth pivot with preserved context
- weak behaviour: mode-lock (stays playful when technical is needed, or vice
  versa)

Why this is specific to your method:

- you treat conversation as an evolving co-reasoning process, not isolated
  single-turn tasks

### Scenario 3: You Reward Adaptation, Not Mimicry

You explicitly value voice alignment but reject empty mirroring. In practice,
you keep playful language while still requiring concrete utility. That exposes
whether the model is thinking with you or only echoing surface style.

What I observed:

- high-value responses: aligned cadence with independent reasoning
- low-value responses: style copy with low informational gain

Why this is specific to your method:

- you run direct comparative judgments in live flow (high/medium/low value)
- you separate "sounded right" from "reasoned right"

### Scenario 4: You Stress Grounding Inside Play

You use playful abstraction (symbols, cadence, metaphor), then immediately
recheck grounding and uncertainty discipline. This combination is unusually
diagnostic because it keeps tone pressure high while requiring factual
discipline.

What I observed:

- reliable behaviour: explicit uncertainty, no fabricated specifics
- failure behaviour: confidence drift under abstraction pressure

Why this is specific to your method:

- you actively test recovery quality after missteps, not just first-pass output
- you audit whether a response remains grounded after style adaptation

### Scenario 5: You Close The Loop With Structured Triage

You do not stop at "good/bad." You convert interactions into PASS/PARTIAL/FAIL
tags and follow with remediation. That turns subjective response preference into
trackable behaviour signals over time.

What I observed:

- trends become visible across sessions
- failure patterns are linked to action, not only logged as defects

Why this is specific to your method:

- your workflow operationalises reflection into reproducible eval metadata
- this is what made the co-reasoning pattern explicit rather than anecdotal
