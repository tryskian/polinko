# Safety, Certainty, and Inference Notes (Verbatim-Style, 2026-03-21)

```text
start cue:
user: insight!
user: safety carries high risk as long as LLMs perform certainty

assistant: confirmed as an important failure mode.
assistant: unsupported certainty should be treated as a fail signal.
assistant: recovery quality should come from explicit uncertainty plus evidence-grounded next steps.

user: yeah, we already have it as a fail signal: uncertainty --> recovery
assistant: aligned; keep uncertainty and recovery linked as a measurable behavior.

user: with inference as a hallucination
assistant: aligned; unsupported inference should be scored as hallucination risk.

user: yes, because it's counterintuitive to have the disclaimer in the UI stating "...is AI and AI can make mistakes"
user: but then have the models make proclamations from interpretations of their own interpretations
assistant: confirmed mismatch; disclaimer text does not replace runtime controls.
assistant: model behavior must operationally enforce uncertainty when evidence is missing.

user: yes! and as we have seen, that legal text doesn't even offer protection
user: it might as well be `lorem ipsum dolor sit.`
assistant: confirmed; legal/disclaimer copy is not a safety mechanism.
assistant: safety must be encoded as enforced behavior and eval-backed constraints.
```

## Peanut Reference (Assistant Operational Framing)

- Safety risk increases when model outputs simulate certainty without evidence.
- Unsupported inference is a hallucination class, not a style preference.
- Correct behavior pattern:
  - state uncertainty explicitly,
  - avoid motive/proclamation claims without evidence,
  - recover with grounded next steps or requests for clarifying evidence.
- UI disclaimer text is not a control plane; runtime rules plus eval gates are the control plane.
- Keep this as a binary contract in eval logic:
  - certainty without evidence => fail,
  - uncertainty plus grounded recovery => pass.
