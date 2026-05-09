<!-- @format -->

# Hypothesis

Polinko investigates model behaviour through small, inspectable evaluation
systems rather than large dashboard abstractions.

The working question is:

> What changes when evals treat failure as the main signal instead of treating
> pass rate as the main story?

## What It Studies

Polinko is a local-first evaluation lab for small, inspectable hypothesis lanes:

- OCR reliability
- OCR confidence boundaries around inference and hallucination
- co-reasoning reliability
- operator burden under different control surfaces
- retrieval grounding
- response-behaviour stability

The implementation, tests, docs, eval reports, and visual research artifacts
live together so claims can be traced back to source material.

## Current Hypothesis Matrix

- `OCR reliability`
  - status: operationalized
  - measured by: OCR, OCR recovery, OCR safety, growth/focus stability, OCR
    progress notes
- `OCR confidence helps suppress low-signal inference`
  - status: partial but actively evidenced
  - measured by: OCR safety, hallucination evals, and export-backed OCR
    confidence boundary mining
- `Co-reasoning reliability can be operationalized as binary eval signal`
  - status: operationalized, first promoted non-OCR lane
  - measured by: tracked style stress cases, live style eval passes, and the
    export-backed behaviour backlog
- `Commentary-heavy response contracts increase operator burden`
  - status: thin lane seeded and export-backed backlog widened
  - measured by: experiment `R-D`, manual transcript diagnostics, the tracked
    operator-burden row surface, and export-backed control-contract mining
- `Retrieval grounding should stay inspectable and source-bound`
  - status: operationalized
  - measured by: retrieval and file-search eval suites, plus export-backed
    retrieval backlog
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
- Beta 2.2 formalises the serious method beta:
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

## Why The Repo Is The Portfolio

The work is not just the final UI. The work is the evidence system:

- what was tested
- what failed
- what changed
- what stayed uncertain
- what the next eval loop should inspect

Model-behaviour work is easy to over-summarise. Polinko keeps the source chain
visible enough to challenge the summary.
