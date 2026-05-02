<!-- @format -->

# Polinko

[![CI](https://github.com/tryskian/polinko/actions/workflows/ci.yml/badge.svg)](https://github.com/tryskian/polinko/actions/workflows/ci.yml)
![Binary Eval](https://img.shields.io/badge/eval-binary_pass%2Ffail-4E79A7)
![Research Surface](https://img.shields.io/badge/research-repo_native-76B7B2)

Polinko is a human-led, repo-native research system for inspecting AI behavior
through failure, OCR reliability, and evidence-preserving evaluation.

It is not mainly a website or demo app. The website is a doorway. The
repository is the research surface.

## Current OCR Read

- transcript-backed growth set: `25/25` stable, `0` flaky
- fail-history cohort: `0` active cases
- remaining OCR signal: exploratory output variability
- latest tracked snapshot:
  - [docs/research/ocr-progress-20260501.md](docs/research/ocr-progress-20260501.md)

## Start Here

If you are reading Polinko as a research project, use this path:

- [Public Reading Path](docs/public/README.md)
- [Polinko in Brief](docs/public/IN_BRIEF.md)
- [Method & Authorship](docs/public/METHOD.md)
- [Hypothesis](docs/public/HYPOTHESIS.md)
- [Research](docs/public/RESEARCH.md)
- [Diagrams](docs/public/DIAGRAMS.md)
- [Research Surface](docs/research/README.md)

## What Lives Here

- FastAPI API + CLI runtime
- OCR lockset and growth-lane evals
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
