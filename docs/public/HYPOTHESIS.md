<!-- @format -->

# Hypothesis

Polinko is a human-led research and engineering collaboration. It investigates
model behaviour through small, inspectable evaluation systems rather than large
dashboard abstractions.

The working question is:

> What changes when evals treat failure as the main signal instead of treating
> pass rate as the main story?

## What Polinko Is

Polinko is a local-first evaluation lab for:

- binary pass/fail gates
- OCR reliability
- fail-signal observability
- manual evaluation notes
- human-AI workflow evidence

It began as theory and became engineering through a collaboration loop:
human-authored research direction, constraints, and acceptance criteria are
translated into technical mechanisms, tested against evidence, then accepted,
reworked, or rejected by human judgement.

It is also a working repository. The implementation, tests, docs, eval reports,
database contracts, and visual research artifacts live together so claims can
be traced back to source material.

## What Changed Across Betas

- Beta 1.0 captured the transition from manual/screenshot-backed evaluation
  into binary eval semantics.
- Beta 2.0 operationalised that transition with stricter OCR gate reports,
  integrated eval surfaces, and repeatable local commands.
- Beta 2.1 reframes the project as repo-as-research: the website becomes a
  doorway, and the repository carries the evidence.

## Why The Repo Is The Portfolio

The work is not just the final UI. The work is the system of evidence:

- what was tested
- what failed
- what changed
- what stayed uncertain
- what the next eval loop should inspect

That structure matters because model behaviour work is easy to over-summarise.
Polinko keeps the source chain visible enough to challenge the summary.
