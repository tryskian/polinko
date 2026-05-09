<!-- @format -->

# Polinko in Brief

Polinko is a human-led, repo-native research lab for inspecting AI behavior
through fail-first evaluation, grounding, co-reasoning, operator burden, and
human-AI collaboration.

It is not mainly a website or a demo app. The website is a doorway. The
repository is the research surface.

## What Polinko Fundamentally Is

Polinko is a fail-first research instrument. It uses binary eval gates, OCR
reliability loops, transcript-backed insight capture, and evidence-preserving
docs to study grounded behavior and drift.

## Governing Theory

The strongest signal is in failure and in what is not yet well-defined.
Binary `pass` / `fail` gates preserve that signal instead of smoothing it away.

Reliability improves when the system re-grounds in source evidence or the
artifact itself instead of trusting:

- stale memory
- carried priors
- compressed summaries
- confident continuation without evidence

In short: confidence must not outrun evidence.

## What Makes It Distinct

- Failure is the main signal, not a side effect.
- The transcript lane is primary-source research material, not just notes.
- Human authorship stays explicit:
  - Krystian owns theory, judgment, and publication decisions.
  - Codex supports implementation, validation, and repo maintenance.
- The website is a doorway; the repo carries the evidence.

## Current Research Instrument Set

- FastAPI + CLI runtime
- OCR lockset and growth-lane eval architecture
- transcript-mined OCR case generation
- manual eval warehouse and runtime history stores
- binary pass/fail reports and fail-signal visualizations
- Mermaid and D3 evidence diagrams
- transcript + structured-insight corpus
- governance and runbook surfaces that keep the method operational

## Current Beta Read

- current serious method beta is `Beta 2.2`
- release outcomes stay binary:
  - `pass`
  - `fail`
- after `fail`, failure disposition is:
  - `retain`
  - `evict`
- `retain` keeps the failure as in-scope evidence
- `evict` is upstream case correction, not a third release state
- co-reasoning is now the first promoted non-OCR lane:
  - tracked style stress surface: `14/14` pass
- current mature method lane is still green:
  - transcript-backed OCR growth set: `25/25` stable
  - fail-history cohort: `0` active cases
- tracked snapshots:
  - [Beta 2.2 snapshot](../research/beta-2-2-20260508.md)
  - [Co-reasoning promotion snapshot](../research/co-reasoning-promotion-20260508.md)
  - [OCR progress snapshot](../research/ocr-progress-20260508.md)

## One-Sentence Read

Polinko is a fail-first research instrument for studying when model confidence
outruns evidence, and how artifact-grounded evaluation changes that.
