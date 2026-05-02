<!-- @format -->

# Polinko in Brief

Polinko is a human-led, repo-native research lab for inspecting AI behavior
through failure, OCR reliability, and human-AI collaboration.

It is not mainly a website or a demo app. The website is a doorway. The
repository is the research surface.

## What Polinko Fundamentally Is

Polinko is a fail-first research instrument. It uses binary eval gates, OCR
reliability loops, transcript-backed insight capture, and evidence-preserving
docs to study when model behavior is grounded and when it drifts.

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
- Public presentation follows the method:
  - the website is a doorway
  - the repo carries the evidence

## Current Research Instrument Set

- FastAPI + CLI runtime
- OCR lockset and growth-lane eval architecture
- transcript-mined OCR case generation
- manual eval warehouse and runtime history stores
- binary pass/fail reports and fail-signal visualizations
- Mermaid and D3 evidence diagrams
- transcript + structured-insight corpus
- governance and runbook surfaces that keep the method operational

## Current OCR Read

- latest tracked OCR kernel on `2026-05-01` is green:
  - transcript-backed growth set: `25/25` stable
  - fail-history cohort: `0` active cases
  - remaining signal: exploratory output variability
- tracked snapshot:
  - [docs/research/ocr-progress-20260501.md](../research/ocr-progress-20260501.md)

## One-Sentence Read

Polinko is a fail-first research instrument for studying when model confidence
outruns evidence, and how artifact-grounded evaluation changes that.
