# Workstreams: Theory, Research, Portfolio

This repo now treats these as separate but linked tracks.

## 1) Theory (hypothesis lane)

Goal:

- Define conceptual models and falsifiable hypotheses.

Includes:

- Concept definitions
- Assumptions and boundaries
- Hypothesis statements
- Falsification criteria

Does not include:

- Production claims
- Shipping impact claims
- "Proof" language

Output type:

- Propositions to test

Primary location:

- `docs/theory/`

## 2) Research (validation lane)

Goal:

- Test theory hypotheses with reproducible protocols and evidence.

Includes:

- Experiment protocol
- Eval runs and metrics
- PASS/FAIL observations
- Error analysis and corrective action

Output type:

- Supported/refuted/inconclusive results

Primary locations:

- `docs/research/`
- `eval_reports/`
- `docs/portfolio/raw_evidence/`

## 3) Portfolio (demonstration lane)

Goal:

- Present implemented outcomes with evidence links.

Includes:

- Case narratives
- Build decisions and tradeoffs
- Curated evidence citations from research artifacts

Output type:

- Demonstrated capability and engineering quality

Primary location:

- `docs/portfolio/`

## Promotion Rules

Theory -> Research requires:

- A falsifiable hypothesis
- Observable signals
- A concrete protocol

Research -> Portfolio requires:

- At least one reproducible artifact
- Clear outcome (`PASS`/`FAIL`/`MIXED`)
- Linked evidence IDs and source files

## ID Conventions

- Theory hypothesis IDs: `H-###`
- Research experiment IDs: `R-YYYYMMDD-###`
- Portfolio claim IDs: existing portfolio IDs (for example `S3-01`)

## Immediate implication for your paper pipeline

- "Authentic Intelligence" and "Tensor Proprioception: The Mechanics of Meaning"
  belong to Theory first.
- Engineering evals are Research artifacts that test theory claims.
- Portfolio consumes validated research evidence; it does not define theory.
