<!-- @format -->

# Polinko

[![CI](https://github.com/tryskian/polinko/actions/workflows/ci.yml/badge.svg)](https://github.com/tryskian/polinko/actions/workflows/ci.yml)
![Binary Eval](https://img.shields.io/badge/eval-binary_pass%2Ffail-4E79A7)
![Research Surface](https://img.shields.io/badge/research-repo_native-76B7B2)

Polinko is a human-led, repo-native research system for inspecting AI behavior
through fail-first evaluation, co-reasoning, grounding, operator burden, and
evidence-preserving method work.

It is not mainly a website or demo app. The website is a doorway. The
repository is the research surface.

## Why This Repo Matters

Most AI projects show polished outputs and hide the failure structure.
Polinko does the opposite: it keeps failure visible enough to inspect,
evaluate, and act on. That matters anywhere confidence can outrun source
evidence.

## Current Research Read

- current serious method beta is `Beta 2.2`:
  - explicit `pass` / `fail` gate semantics
  - explicit post-fail `retain` / `evict` disposition
  - first-gate contract correctness before richer interpretation
  - co-reasoning is the first promoted non-OCR eval lane
- eval contract is explicit across tracked surfaces:
  - release outcomes stay `pass` / `fail`
  - `evict` is an upstream case correction, not a third gate state
  - the first gate proves hard contract correctness before richer interpretation
- broader hypothesis lane now has a first promoted non-OCR eval surface:
  - co-reasoning reliability is now operationalized in the tracked style lane:
    `14/14` pass in the latest tracked snapshot
  - latest one-hour deterministic beta soak:
    - `19/21` pass cycles
    - former dominant style pressure did not recur
  - uncertainty-boundary stability is now closed with:
    - resumed soak total: `3961s`
    - `21/21` pass cycles
    - `0` fail cycles
    - `0` recurring failure signals
  - tracked hallucination-boundary coverage is now wider and still green:
    - latest tracked snapshot: `9/9` pass
    - tracked case count: `9`
    - new distinct seams: archive-lore and archive-discipline fabrication
    - current signal-shape surface is now explicit
  - retrieval grounding now has fresh tracked snapshots across both visible branches:
    - retrieval recall: `12/12` pass
    - file search: `5/5` pass
  - response behaviour now has a fresh current tracked snapshot:
    - latest tracked snapshot: `7/7` pass
    - current signal-shape surface is now explicit
  - current broad gate is holding across style, uncertainty, co-reasoning, and response behaviour
  - operator burden now has a seeded row-local evidence surface:
    - `4` pass rows
    - `2` retained fail rows
    - `1` evicted fail row
    - widened export-backed backlog: `9` conversations / `8` families
    - current top backlog slice is duplicate-heavy, so the earned next move is
      lane visibility rather than row-count inflation
- current mature method lane is green:
  - transcript-backed OCR growth set: `25/25` stable, `0` flaky
  - OCR fail-history cohort: `0` active cases
  - runtime OCR follow-up is parked
- latest tracked snapshots:
  - [docs/research/operator-burden-promotion-20260509.md](docs/research/operator-burden-promotion-20260509.md)
  - [docs/research/operator-burden-mining-20260509.md](docs/research/operator-burden-mining-20260509.md)
  - [docs/research/operator-burden-seed-20260509.md](docs/research/operator-burden-seed-20260509.md)
  - [docs/research/operator-burden-signal-shape-20260512.md](docs/research/operator-burden-signal-shape-20260512.md)
  - [docs/research/beta-2-2-stability-soak-20260509.md](docs/research/beta-2-2-stability-soak-20260509.md)
  - [docs/research/uncertainty-boundary-stability-20260509.md](docs/research/uncertainty-boundary-stability-20260509.md)
  - [docs/research/hallucination-boundary-promotion-20260512.md](docs/research/hallucination-boundary-promotion-20260512.md)
  - [docs/research/hallucination-boundary-signal-shape-20260512.md](docs/research/hallucination-boundary-signal-shape-20260512.md)
  - [docs/research/retrieval-grounding-signal-shape-20260512.md](docs/research/retrieval-grounding-signal-shape-20260512.md)
  - [docs/research/response-behaviour-signal-shape-20260512.md](docs/research/response-behaviour-signal-shape-20260512.md)
  - [docs/research/ocr-progress-20260508.md](docs/research/ocr-progress-20260508.md)
  - [docs/research/co-reasoning-promotion-20260508.md](docs/research/co-reasoning-promotion-20260508.md)
  - [docs/research/co-reasoning-signal-shape-20260512.md](docs/research/co-reasoning-signal-shape-20260512.md)
  - [docs/research/behaviour-backlog-20260508.md](docs/research/behaviour-backlog-20260508.md)

## Start Here

If you are reading Polinko as a research project, use this path:

- [Public Reading Path](docs/public/README.md)
- [Polinko in Brief](docs/public/IN_BRIEF.md)
- [Method & Authorship](docs/public/METHOD.md)
- [Hypothesis](docs/public/HYPOTHESIS.md)
- [Evidence](docs/public/EVIDENCE.md)
- [Diagrams](docs/public/DIAGRAMS.md)
- [Research Surface](docs/research/README.md)

## What Lives Here

- FastAPI API + CLI runtime
- OCR lockset and growth-lane evals
- export-backed behaviour backlog mining
- binary pass/fail evidence surfaces
- tracked research docs, diagrams, and eval context
- repo-local engineering and validation workflow

## Quick Start

```bash
make deps-install
cp .env.example .env
# set OPENAI_API_KEY in .env
make doctor-env
make server
```

Open `http://127.0.0.1:8000/docs`.

Portfolio doorway:

```bash
make portfolio
```

`make portfolio` rebuilds/serves and prints a cache-busted URL. It does not
open a browser by default.

## Core Commands

```bash
make server
make portfolio
make test
make lint-docs
make quality-gate
make chat
```

Operator procedure lives in [docs/runtime/RUNBOOK.md](docs/runtime/RUNBOOK.md).

## Repo Map

- `api/` API implementation
- `core/` runtime logic
- `tools/` eval and maintenance scripts
- `tests/` test suite
- `docs/public/` curated public reading path
- `docs/governance/` charter, state, decisions
- `docs/runtime/` runbook and architecture
- `docs/eval/` eval evidence and phase context

## Canonical Docs

- Rules: [docs/governance/CHARTER.md](docs/governance/CHARTER.md)
- Current truth: [docs/governance/STATE.md](docs/governance/STATE.md)
- Procedures: [docs/runtime/RUNBOOK.md](docs/runtime/RUNBOOK.md)
- Structure: [docs/runtime/ARCHITECTURE.md](docs/runtime/ARCHITECTURE.md)
- Durable history: [docs/governance/DECISIONS.md](docs/governance/DECISIONS.md)

## Production

- [www.krystian.io](https://www.krystian.io/)
- `GET /` redirects to `GET /portfolio`

## License

Apache-2.0. See [LICENSE](LICENSE).
