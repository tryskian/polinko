<!-- @format -->

# Current Hypotheses

This note records the current hypotheses inside Polinko's broader
[research surface](RESEARCH.md). A hypothesis is a research claim at its current
evidence boundary. Its status describes what evidence has been earned.
Supported hypotheses can be stated as conclusions at that evidence boundary.

Polinko investigates model behaviour through small, inspectable evaluation
systems rather than large dashboard abstractions.

The working question is:

> What changes when evals treat failure as the main signal instead of treating
> pass rate as the main story?

## What It Studies

Polinko is a local-first evaluation lab for small, inspectable research lanes:

- OCR reliability
- OCR confidence boundaries around inference and hallucination
- co-reasoning reliability
- source-first research-model evidence
- operator burden under different control surfaces
- reasoning reliability, compute efficiency, and sustainability pressure under
  lean binary structure
- retrieval grounding
- response-behaviour stability

The implementation, tests, docs, eval reports, and visual research artefacts
live together so claims can be traced back to source material.

## Current Hypothesis Matrix

- `Lean binary evaluation may improve reasoning reliability and compute
efficiency by reducing context clutter and correction churn`
  - status: staged, extending the base Polinko binary hypothesis into compute
    and energy pressure
  - sustainability frame: unnecessary inference creates compute work; compute
    work consumes energy; energy-intensive infrastructure creates cooling demand;
    cooling can require water depending on the system
  - measured by: paired equivalent task shapes, token usage, retry count,
    validation reruns, human correction burden, and output length against
    accepted answer quality
- `OCR reliability`
  - status: operationalised
  - measured by: OCR, OCR recovery, OCR safety, growth/focus stability, OCR
    progress notes
- `OCR confidence helps suppress low-signal inference`
  - status: operationalised through uncertainty-boundary and
    hallucination-boundary coverage
  - measured by: OCR safety, hallucination evals, and export-backed OCR
    confidence boundary mining
- `Co-reasoning reliability can be operationalised as binary eval signal`
  - status: promoted, first tracked non-OCR lane
  - measured by: tracked style stress cases, live style eval passes, and the
    export-backed behaviour backlog
- `Source-first evidence can carry non-OCR method claims`
  - status: staged for pre-Beta 2.4
  - measured by: manual eval workbench evidence, notebooks, local evidence
    databases, tracked row/case judgements, exclusions, and lane summaries
- `Commentary-heavy response contracts increase operator burden`
  - status: thin lane
  - measured by: experiment `R-D`, manual transcript diagnostics, the tracked
    operator-burden row surface, and export-backed control-contract mining
- `Retrieval grounding should stay inspectable and source-bound`
  - status: operationalised
  - measured by: retrieval and file-search eval suites, the tracked retrieval
    grounding snapshot, plus export-backed retrieval backlog
- `Response-behaviour stability should stay direct and source-bound`
  - status: operationalised
  - measured by: response-behaviour eval suite and the tracked
    response-behaviour stability snapshot
- `Failure should stay the main signal across lanes`
  - status: governing method
  - measured by: binary gates, fail reports, decisions, and representative
    research notes

## What Changed Across Betas

- Beta 1.0 captured the transition from manual/screenshot-backed evaluation
  into binary eval semantics.
- Beta 2.0 operationalised that transition with stricter OCR gate reports,
  integrated eval surfaces, and repeatable local commands.
- Beta 2.1 reframes the project as repo-as-research: the website becomes a
  doorway, and the repository carries the evidence.
- Beta 2.2 formalises the method beta:
  - explicit `pass` / `fail` gate contract
  - explicit post-fail `retain` / `evict` disposition
  - explicit post-fail gate stack:
    - `pass / fail`
    - if `fail`, then `retain / evict`
    - rerun
    - `pass / fail`
  - first-gate contract correctness before richer interpretation
  - co-reasoning promoted as the first tracked non-OCR lane
  - operator burden seeded as the first row-local thin lane
  - future non-OCR promotion requires:
    - distinct task-shape pressure
    - recurring seam shape
    - real method consequence
  - no additional non-OCR lane currently meets that threshold
- Beta 2.3 carries the OCR lane into fresh generalisation pressure:
  - stabilised same-image OCR is the starting base
  - transcript mining now refreshes the OCR data surface
  - OCR-ready candidates widen intake beyond transcript-shaped asks
  - OCR failures now use explicit `retain` / `evict` case governance
  - the lane now tests transfer under harder visual conditions
- pre-Beta 2.4 stages the next research-model contract:
  - OCR stays case-level `pass` / `fail`
  - source-first row and case evidence is the method shape
  - row and case evidence stay inspectable before any lane-level claim is
    promoted

## Why The Repo Is The Surface

The work includes the final UI and the evidence system:

- what was tested
- what failed
- what changed
- what stayed uncertain
- what the next eval loop should inspect

Model-behaviour work is easy to over-summarise. Polinko keeps the source chain
visible enough to challenge the summary.
