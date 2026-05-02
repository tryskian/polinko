<!-- @format -->

# Evidence

This note defines what counts as evidence, which beta eras matter, and how
Polinko separates public proof from working material.

## Evidence Layers

- Method and authorship docs define claim ownership.
- Source code and tests define the runtime contract.
- Eval docs and report schemas define the evidence contract.
- Beta 1.0 materials preserve the transition from manual review to binary evals.
- Current OCR reports show operational fail/pass pressure.
- Diagrams are research instruments, not decoration.
- Notebook/query outputs stay local unless explicitly curated.

## Beta 1.0

Beta 1.0 is the transition layer. It preserves the manual and screenshot-backed
context that makes the current binary gates meaningful.

Canonical map:

- [Eval Evidence Map](../eval/README.md)

## Current / Beta 2.x

Current Polinko uses binary gates as operational eval surfaces. Diagnostic
notes may be rich, but release-grade gate arithmetic stays binary so failure
pressure remains visible.

Core surfaces:

- `/viz/pass-fail`
- `/viz/pass-fail/data`
- `/portfolio/sankey-data`

## Research Notes vs Working Docs

Tracked public notes are curated. Working material stays tracked only when it is
safe and useful for continuity:

- governance docs
- runtime architecture
- runbook commands
- tracked state snapshots
- decision history

Private/local evidence stays untracked unless explicitly promoted:

- raw databases
- local exports
- private transcripts
- scratch screenshots
- uncurated evidence dumps

## Reading Path

1. Start with [Hypothesis](HYPOTHESIS.md).
2. Review [Diagrams](DIAGRAMS.md).
3. Use [Eval Evidence Map](../eval/README.md) for beta/eval detail.
4. Use runtime/governance docs only for implementation or process specifics.
