# Polinko

![CI](https://github.com/tryskian/polinko/actions/workflows/ci.yml/badge.svg)
[![Polinko Model](https://img.shields.io/badge/polinko_model-staged_next_beta-4C956C)](docs/research/pre-beta-2-4-research-model-contract-2026-05-19.md)
![Eval Contract](https://img.shields.io/badge/eval-pass%2Ffail-4E79A7)
![Research Surface](https://img.shields.io/badge/research-repo_native-76B7B2)
![Model Refactor](https://img.shields.io/badge/model_refactor-active-F28E2B)

> [!NOTE]
> **Current status:** The Polinko research model is being staged for the next
> beta.
>
> This is an active refactor window for the model contract, evidence snapshots,
> docs, and supporting tools. Current builds are kept stable while the repo
> surfaces are simplified, tested, and aligned for the next release.

Polinko is a human-led research system for inspecting AI behaviour through
fail-first evaluation, evidence-preserving method work, and repo-native
publishing.

The website is a doorway. The repository is the research surface.

## Research Question

How can human-led eval work make AI failure legible enough to improve the
method without hiding risk behind polished outputs?

## Working Theory

AI responses are shaped by more than the prompt. Policy, guardrails, retrieval,
memory, context limits, tooling, and prior response residue can all bend the
path from intent to output.

Polinko treats visible mismatch as evidence. The method preserves failures,
classifies them, and uses them to update the next research boundary instead of
smoothing them away.

OCR is one pressure lane because the expected answer is externally checkable.
It is part of the theory, not the whole model.

## Current Read

- `Beta 2.3` is the frozen method snapshot.
- `pre-Beta 2.4` is staged as the next research-model contract.
- OCR is the mature green lane and is moving into generalisation pressure.
- Co-reasoning is the first promoted non-OCR lane.
- Retrieval, response behaviour, uncertainty boundary, and hallucination
  boundary are operationalised support surfaces.
- Operator burden is the active thin lane.
- The discarded run-level rollup path is not being carried forward.

## Read Next

| Surface                                      | Use                                      |
| -------------------------------------------- | ---------------------------------------- |
| [Field notes](docs/public/README.md)         | shortest reading path                    |
| [Research surface](docs/research/README.md)  | current notes, beta evidence, hypotheses |
| [Eval evidence](docs/eval/README.md)         | tracked eval snapshots                   |
| [Runbook](docs/runtime/RUNBOOK.md)           | operator procedure                       |
| [Architecture](docs/runtime/ARCHITECTURE.md) | system shape                             |
| [Decisions](docs/governance/DECISIONS.md)    | durable rationale                        |

## Run Locally

```bash
make deps-install
cp .env.example .env
# set OPENAI_API_KEY in .env
make doctor-env
make docs
```

Use `make docs-open` only when you want to launch the system browser.

---

## License

Apache-2.0. See [license](LICENSE).
