<!-- @format -->

# Method & Authorship

Polinko is a human-led research and engineering collaboration.

The research framework, hypotheses, judgement, evidence selection, and final
claims are authored by Krystian Fernando. AI systems are used as research and
engineering instruments inside that process, not as independent authors or
source authority.

## Tooling Disclosure

Polinko uses OpenAI Codex as a repo-local engineering collaborator for
implementation, refactoring, validation, and documentation maintenance. OpenAI
Platform APIs are used where Polinko makes model-backed calls for OCR, evals,
retrieval, and runtime experiments.

These tools are part of the research-engineering workflow. They do not define
the research claims, interpret the evidence, or own publication decisions.

Supporting tooling is used for reproducibility and inspection: SQLite for local
evidence stores, Docker/devcontainers for environment portability, Playwright
for browser-based verification and visual capture, Jupyter for local analysis,
pytest and markdownlint for validation, GitHub Actions for CI, and Make for
repeatable operator workflows.

## Collaboration Model

Polinko moves from human research direction to technical implementation:

1. Krystian defines the behavioural objective, constraints, evidence boundary,
   and acceptance criteria.
2. AI collaborators support structured dialogue, synthesis, reframing, and
   stress-testing of ideas.
3. Codex translates approved objectives into technical mechanisms: API
   surfaces, eval harnesses, retrieval controls, reliability gates, docs, and
   validation workflows.
4. Krystian makes final decisions about interpretation, evidence inclusion,
   exclusion, and publication.

## What AI Does Here

AI assistance is method support:

- structured dialogue
- synthesis support
- reframing and stress-testing ideas
- implementation support
- organisation support in Notion and repository workflows

AI outputs are treated as artefacts within the research process. They can be
useful, inspectable, wrong, or rejected.

## Responsibility Boundary

- Concept formation remains human-owned.
- Judgment and selection remain human-owned.
- Final claims remain human-owned.
- AI assistance is cited as part of the method, not treated as source
  authority.

## Practical Rule

Polinko uses a transcript-first workflow so claims can be traced back to source
evidence before they enter public explanation, eval logic, or implementation.
