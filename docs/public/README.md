<!-- @format -->

# Polinko Public Guide

Polinko is a repo-native research project for evaluating model behaviour with
lightweight binary gates, OCR reliability loops, and human-AI workflow evidence.

This public guide is a derived entrypoint. It does not replace the canonical
governance, runtime, or eval documentation.

## Start Here

- Research question: what happens when model evaluation is treated as a
  lightweight, fail-signal-forward system instead of a pass-rate dashboard?
- Evidence model: Beta 1.0 preserves the manual/screenshot-backed transition
  into binary evals; current Polinko operationalises that transition with
  strict OCR gates and report streams.
- Runtime model: FastAPI backend, CLI workflow, SQLite-backed local state,
  deterministic make targets, and pytest/markdownlint quality gates.
- Visual model: notebooks, Mermaid diagrams, screenshots, and data-viz surfaces
  belong with the repo as research artifacts. The public website stays a lean
  identity/contact doorway into the work.

## How To Read This Repo

- [README](../../README.md): project overview, setup, commands, and API
  surface.
- [Eval Evidence Map](../eval/README.md): how Beta 1.0, Beta 2.0, manual evals,
  and current OCR binary gates relate.
- [Public Visuals](VISUALS.md): Mermaid diagrams and notebook pointers.
- [Architecture](../runtime/ARCHITECTURE.md): runtime flow, data surfaces, and
  placement rules.
- [Runbook](../runtime/RUNBOOK.md): operator commands and workflow contracts.
- [Charter](../governance/CHARTER.md): collaboration, engineering, and
  documentation governance.

## What Counts As Proof

- Source code and tests show the runtime contract.
- Eval docs and report schemas show the evidence contract.
- Local databases are treated as private raw materials unless explicitly
  promoted through curated docs or derived public artifacts.
- Notebooks and Mermaid diagrams are visual research instruments, not website
  decoration.

## Current Public Boundary

The public website should say who built Polinko, what Polinko is investigating,
and where to inspect the work. It should not attempt to reproduce the full
research system.

The repo is the portfolio.
