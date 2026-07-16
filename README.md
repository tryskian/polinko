# Polinko

![CI](https://github.com/tryskian/polinko/actions/workflows/ci.yml/badge.svg)
[![Polinko Model](https://img.shields.io/badge/polinko_model-staged_next_beta-4C956C)](docs/research/pre-beta-2-4-research-model-contract-2026-05-19.md)
![Eval Contract](https://img.shields.io/badge/eval-pass%2Ffail-4E79A7)
![Research Surface](https://img.shields.io/badge/research-repo_native-76B7B2)
![Model Refactor](https://img.shields.io/badge/model_refactor-active-F28E2B)

> [!NOTE]
> **Current status:** Polinko is being staged for the next beta.
>
> The research model is stable enough to keep building on, but the repo is in
> an active refactor window. The model contract, evidence snapshots, docs,
> helper scripts, and local tooling are being tightened so the next beta has a
> cleaner surface to build from.
>
> Refactor map: [method](docs/public/diagrams/refactor-method.md) ·
> [journey](docs/public/diagrams/refactor-journey.md).

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
It is one part of the broader research model.

## Current Position

- `Beta 2.3` is the frozen method snapshot.
- `pre-Beta 2.4` is staged as the next research-model contract.
- OCR is the mature green lane and is moving into generalisation pressure.
- Co-reasoning is the first promoted non-OCR lane.
- Retrieval, response behaviour, uncertainty boundary, and hallucination
  boundary are operationalised support surfaces.
- Operator burden is the active thin lane.
- Lean binary evaluation is staged as a sustainability question: whether reduced
  context clutter and correction churn can reduce unnecessary inference, with
  energy use, cooling demand, and water impact as downstream resource
  implications.
- Source-first row and case evidence is the pre-Beta 2.4 method foundation.

## Refactor Map

The current refactor is being handled as a staged path. The diagrams show the
working loop and the route each major surface has taken through the cleanup.

- [Refactor method](docs/public/diagrams/refactor-method.md): alignment,
  kernel scope, validation, docs, PR, merge, and clean main.
- [Refactor journey](docs/public/diagrams/refactor-journey.md): evidence
  baseline, runtime/package movement, manual eval workbench, and docs closeout.

## Read Next

| Surface                                             | Use                                      |
| --------------------------------------------------- | ---------------------------------------- |
| [Field notes](docs/public/README.md)                | shortest reading path                    |
| [Research surface](docs/research/README.md)         | current notes, beta evidence, hypotheses |
| [Eval evidence](docs/eval/README.md)                | tracked eval snapshots                   |
| [Refactor diagrams](docs/public/diagrams/README.md) | method and journey maps                  |
| [Runbook](docs/runtime/RUNBOOK.md)                  | operator procedure                       |
| [Architecture](docs/runtime/ARCHITECTURE.md)        | system shape                             |
| [Decisions](docs/governance/DECISIONS.md)           | durable rationale                        |

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
