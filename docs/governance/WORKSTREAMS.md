# Workstreams: Theory, Research, Portfolio

This project runs three linked lanes with a clear human-AI split.

## Collaboration model

- Model: `Reasoning Loops`.
- Human (`imagineer`) owns hypothesis direction, objective/scope/acceptance,
  and go/no-go decisions.
- AI (`engineer`) owns implementation, instrumentation, validation execution,
  and drift control.

## 1) Theory lane (imagineer-led)

Goal:

- Define conceptual models and falsifiable hypotheses.

Includes:

- Concept definitions and boundaries.
- Hypothesis statements.
- Falsification criteria.
- Positioning language and visual-culture framing.

Does not include:

- Product performance claims.
- Shipping claims.
- Proof-language without test evidence.

Output:

- Testable propositions.

Primary location:

- `docs/theory/`

## 2) Research lane (engineer-executed, human-directed)

Goal:

- Test theory hypotheses with reproducible protocols and binary outcomes.

Includes:

- Experiment protocol and run conditions.
- Eval runs and metrics.
- Binary observations (`pass`/`fail`).
- Error analysis and corrective actions.

Output:

- Supported/refuted/inconclusive findings.

Primary locations:

- `docs/research/`
- `docs/transcripts/`
- `eval_reports/` (local operational artefacts)

## 3) Portfolio lane (joint synthesis)

Goal:

- Present implemented outcomes with traceable evidence and clear claims.

Includes:

- Case-study narrative.
- Engineering decisions and trade-offs.
- Evidence links back to research and transcripts.

Output:

- Demonstrated capability with reproducible references.

Primary source inputs (in-repo):

- `docs/research/`
- `docs/transcripts/`
- `docs/DECISIONS.md`
- `docs/STATE.md`

## Promotion rules

Theory -> Research requires:

- A falsifiable hypothesis.
- Observable signals.
- A concrete protocol.

Research -> Portfolio requires:

- At least one reproducible artefact.
- Clear binary result (`pass`/`fail`) for the tested claim.
- Linked evidence source files.

## ID conventions

- Theory hypothesis IDs: `H-###`
- Research experiment IDs: `R-YYYYMMDD-###`
- Portfolio claim IDs: existing portfolio claim IDs (for example `S3-01`)

## Practical implication

- Theory proposes.
- Research tests.
- Portfolio demonstrates.
