<!-- @format -->

# Polinko

[![CI](https://github.com/tryskian/polinko/actions/workflows/ci.yml/badge.svg)](https://github.com/tryskian/polinko/actions/workflows/ci.yml)
![Eval Contract](https://img.shields.io/badge/eval-pass%2Ffail_%2B_retain%2Fevict-4E79A7)
![Research Surface](https://img.shields.io/badge/research-repo_native-76B7B2)

Polinko is a human-led, repo-native research system for inspecting AI behavior
through fail-first evaluation and evidence-preserving method work.

The website is a doorway. The repository is the research surface.

## Why This Repo Matters

Most AI projects show polished outputs and hide the failure structure.
Polinko does the opposite: it keeps failure visible enough to inspect,
evaluate, and act on. That matters anywhere confidence can outrun source
evidence.

## Current Research Read

- `Beta 2.2` is the current serious method beta:
  - release outcomes stay `pass` / `fail`
  - post-fail disposition stays `retain` / `evict`
  - the first gate proves contract correctness before richer interpretation
- OCR is the mature green lane:
  - stable and parked
- co-reasoning is the first promoted non-OCR lane:
  - promoted through tracked style and soak evidence
- uncertainty-boundary and hallucination-boundary surfaces are currently green
- operator burden is the active thin lane:
  - active because it is still producing distinct evidence pressure

## Start Here

If you are reading Polinko as a research project, use this path:

- [Public Reading Path](docs/public/README.md)
- [Polinko in Brief](docs/public/IN_BRIEF.md)
- [Method & Authorship](docs/public/METHOD.md)
- [Hypothesis](docs/public/HYPOTHESIS.md)
- [Evidence](docs/public/EVIDENCE.md)
- [Diagrams](docs/public/DIAGRAMS.md)
- [Research Surface](docs/research/README.md)

## Current Tracked Reads

- [Beta 2.2 stability soak](docs/research/beta-2-2-stability-soak-20260509.md)
- [Uncertainty-boundary stability](docs/research/uncertainty-boundary-stability-20260509.md)
- [Hallucination-boundary promotion](docs/research/hallucination-boundary-promotion-20260512.md)
- [Co-reasoning promotion](docs/research/co-reasoning-promotion-20260508.md)
- [Operator burden signal shape](docs/research/operator-burden-signal-shape-20260512.md)
- [OCR progress snapshot](docs/research/ocr-progress-20260508.md)

## What Lives Here

- FastAPI API + CLI runtime
- fail-first eval surfaces
- OCR and non-OCR method lanes
- export-backed behaviour backlog mining
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

## Repo Map

- `api/` API implementation
- `core/` runtime logic
- `tools/` eval and maintenance scripts
- `tests/` test suite
- `docs/public/` curated public reading path
- `docs/governance/` charter, state, decisions
- `docs/runtime/` runbook and architecture
- `docs/eval/` eval evidence and phase context

## Operator Surface

- procedure: [docs/runtime/RUNBOOK.md](docs/runtime/RUNBOOK.md)
- current truth: [docs/governance/STATE.md](docs/governance/STATE.md)
- structure: [docs/runtime/ARCHITECTURE.md](docs/runtime/ARCHITECTURE.md)
- decisions: [docs/governance/DECISIONS.md](docs/governance/DECISIONS.md)

## Production

- [www.krystian.io](https://www.krystian.io/)
- `GET /` redirects to `GET /portfolio`

## License

Apache-2.0. See [LICENSE](LICENSE).
