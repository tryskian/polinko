<!-- @format -->

# Polinko

[![CI](https://github.com/tryskian/polinko/actions/workflows/ci.yml/badge.svg)](https://github.com/tryskian/polinko/actions/workflows/ci.yml)
![Eval Contract](https://img.shields.io/badge/eval-pass%2Ffail-4E79A7)
![Research Surface](https://img.shields.io/badge/research-repo_native-76B7B2)
![Maintenance](https://img.shields.io/badge/maintenance-in%20progress-F28E2B)

> **Maintenance in progress.** Documentation and research surfaces are being
> standardized before this repo is shared as a stable reference.

Polinko is a human-led research system for inspecting AI behavior through
fail-first evaluation, evidence-preserving method work, and repo-native
publishing.

The website is a doorway. The repository is the research surface.

## Why This Exists

Most AI projects foreground polished outputs and hide the failure structure.
Polinko keeps failure visible enough to inspect, classify, and improve. That
matters anywhere confidence can outrun source evidence.

The method is intentionally small and strict: preserve the artifact, decide
`pass` or `fail`, retain useful failures, evict noise, and let the tracked
evidence change the next run.

## Current Read

`Beta 2.3` is the frozen method snapshot. `pre-Beta 2.4` is now staged
as the next research-model contract before new evidence is cut.

The active read is:

- OCR is the mature green lane, stabilized on the current image set and moving
  into broader generalization pressure.
- The discarded run-level rollup path is not being carried forward; the next
  research-model question is how source artifacts, row/case judgment, manual
  evals, lane summaries, and repeated lane signal can carry claims.
- Co-reasoning is the first promoted non-OCR lane, supported by tracked style
  and soak evidence.
- Retrieval, response behaviour, uncertainty boundary, and hallucination
  boundary are operationalized support surfaces.
- Operator burden is the active thin lane because it is still producing
  distinct evidence pressure.
- The research surface is open: current lane status is explicit, but the method
  claim is still under pressure.

For the maintained research map, start with
[docs/research/README.md](docs/research/README.md).

## Start Here

Use the public path when you want the shortest reviewer-facing read:

- [Polinko in Brief](docs/public/IN_BRIEF.md)
- [Method & Authorship](docs/public/METHOD.md)
- [Hypothesis](docs/public/HYPOTHESIS.md)
- [Evidence](docs/public/EVIDENCE.md)
- [Diagrams](docs/public/DIAGRAMS.md)

Use the operator path when you need to run, inspect, or change the system:

- [Docs Map](docs/README.md)
- [Runbook](docs/runtime/RUNBOOK.md)
- [Architecture](docs/runtime/ARCHITECTURE.md)
- [Current State](docs/governance/STATE.md)
- [Decisions](docs/governance/DECISIONS.md)

## What Lives Here

- FastAPI API and CLI runtime
- Manual eval workbench: notebooks, local evidence databases, chat artifacts,
  feedback, checkpoints, and exports
- Fail-first eval surfaces
- OCR and non-OCR method lanes
- Export-backed behaviour backlog mining
- Tracked research docs, diagrams, and eval context
- Repo-local engineering and validation workflow

## Quick Start

```bash
make deps-install
cp .env.example .env
# set OPENAI_API_KEY in .env
make doctor-env
make server
```

Open `http://127.0.0.1:8000/docs`.

## Repo Map

- `main.py` runs the CLI chat entrypoint.
- `server.py` exposes the FastAPI ASGI app and chat-facing manual eval
  workbench endpoints.
- `pyproject.toml` and `src/polinko/` provide the editable-install rail for the
  runtime package.
- `src/polinko/config.py` contains the canonical config implementation; root
  `config.py` is a compatibility shim.
- `src/polinko/api/` contains the canonical API implementation; root `api/`
  contains compatibility shims.
- `src/polinko/core/` contains canonical runtime logic; root `core/` contains
  compatibility shims.
- `tools/` contains eval and maintenance scripts.
- `tests/` contains the test suite.
- `docs/public/` contains the curated public reading path.
- `docs/research/` contains the compact research surface.
- `docs/eval/` contains eval evidence and phase context.
- `docs/governance/` contains charter, state, and decisions.
- `docs/runtime/` contains runbook and architecture.

## License

Apache-2.0. See [LICENSE](LICENSE).
