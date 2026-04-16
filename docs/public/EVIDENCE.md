<!-- @format -->

# Evidence Guide

Polinko separates public explanation from working research infrastructure.

Use this guide to understand what counts as evidence without needing to read the
entire operator archive first.

## Evidence Layers

- Source code and tests show the runtime contract.
- Eval docs and report schemas show the evidence contract.
- Beta 1.0 materials preserve the manual/screenshot-backed transition into
  binary evals.
- Current OCR binary reports show operational fail/pass pressure.
- Mermaid diagrams, notebooks, and data-viz surfaces are repo-native visual
  research instruments.

## Beta 1.0

Beta 1.0 is not deprecated evidence. It is the transition layer.

It contains the manual evaluation context that makes the current binary gates
meaningful. In particular, it preserves OCR and manual-eval evidence from the
period where Polinko moved from qualitative review toward stricter pass/fail
semantics.

Canonical map:

- [Eval Evidence Map](../eval/README.md)

## Current / Beta 2.x

Current Polinko uses binary gates as operational eval surfaces.

The strict pass/fail signal is intentionally simple. Diagnostic notes may be
rich, but release-grade gate arithmetic remains binary so failure pressure
stays visible.

Core surfaces:

- `/viz/pass-fail`
- `/viz/pass-fail/data`
- `/portfolio/sankey-data`

## Public vs Working Docs

Public docs are curated explanations derived from the working archive.

Working docs stay tracked when they are safe and useful for continuity:

- governance docs
- runtime architecture
- runbook commands
- state and handoff snapshots
- decision history

Private/local evidence stays untracked unless explicitly promoted:

- raw databases
- local exports
- private transcripts
- scratch screenshots
- uncurated evidence dumps

## Reading Path

1. Start with [Research Frame](RESEARCH.md).
2. Review [Public Visuals](VISUALS.md).
3. Use [Eval Evidence Map](../eval/README.md) when you need the beta/eval
   detail.
4. Use runtime/governance docs only when you need implementation or process
   specifics.
